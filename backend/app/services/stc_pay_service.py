"""
STC Pay Digital Wallet Service for Saudi Arabia

STC Pay is a leading digital wallet and mobile payment solution in Saudi Arabia.
This service provides integration with STC Pay APIs for processing digital payments.
"""

import logging
import hashlib
import hmac
import json
import uuid
import base64
import qrcode
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from io import BytesIO

import httpx
from pydantic import BaseModel, Field, validator

from app.core.config import settings

logger = logging.getLogger(__name__)


class STCPayPaymentRequest(BaseModel):
    """STC Pay payment request structure"""
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="SAR")
    order_id: str = Field(..., min_length=1, max_length=50)
    customer_phone: str = Field(..., regex=r'^\+966[5][0-9]{8}$')
    description: str = Field(..., min_length=5, max_length=200)
    return_url: Optional[str] = None
    webhook_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('currency')
    def validate_currency(cls, v):
        if v != "SAR":
            raise ValueError('STC Pay only supports SAR currency')
        return v

    @validator('expires_at', pre=True, always=True)
    def set_default_expiry(cls, v):
        if v is None:
            return datetime.utcnow() + timedelta(minutes=15)  # Default 15 min expiry
        return v


class STCPayPaymentResponse(BaseModel):
    """STC Pay payment response structure"""
    payment_id: str
    status: str
    amount: Decimal
    currency: str
    qr_code: Optional[str]  # Base64 encoded QR code image
    qr_code_text: Optional[str]  # QR code text for custom rendering
    payment_url: Optional[str]  # Deep link URL for STC Pay app
    expires_at: datetime
    reference_number: Optional[str]
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class STCPayRefundRequest(BaseModel):
    """STC Pay refund request structure"""
    payment_id: str
    amount: Optional[Decimal] = None  # Partial refund if specified
    reason: str = Field(..., min_length=5, max_length=200)


class STCPayRefundResponse(BaseModel):
    """STC Pay refund response structure"""
    refund_id: str
    payment_id: str
    amount: Decimal
    status: str
    reference_number: Optional[str]
    created_at: datetime


class STCPayWalletInfo(BaseModel):
    """STC Pay wallet information"""
    phone_number: str
    status: str  # active, inactive, blocked
    balance: Optional[Decimal]
    daily_limit: Optional[Decimal]
    monthly_limit: Optional[Decimal]


class STCPayService:
    """
    STC Pay Digital Wallet Service
    
    Provides integration with STC Pay for digital wallet payments in Saudi Arabia.
    Supports QR code payments, deep links, and wallet management.
    """

    def __init__(self):
        self.base_url = settings.STC_PAY_API_URL or "https://api.stcpay.com.sa"
        self.app_id = settings.STC_PAY_APP_ID
        self.app_secret = settings.STC_PAY_APP_SECRET
        self.merchant_id = settings.STC_PAY_MERCHANT_ID
        self.environment = settings.STC_PAY_ENVIRONMENT or "sandbox"
        
        if not all([self.app_id, self.app_secret, self.merchant_id]):
            logger.warning("STC Pay credentials not fully configured")

    def _generate_signature(self, data: Dict[str, Any], timestamp: str) -> str:
        """Generate signature for STC Pay API requests"""
        # Sort parameters and create signature string
        sorted_params = sorted(data.items())
        params_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sig_string = f"{timestamp}|{params_string}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            sig_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature

    def _make_request(
        self, 
        endpoint: str, 
        data: Dict[str, Any], 
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Make authenticated request to STC Pay API"""
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(datetime.utcnow().timestamp()))
        
        # Add merchant info
        data.update({
            "app_id": self.app_id,
            "merchant_id": self.merchant_id,
            "timestamp": timestamp,
            "nonce": str(uuid.uuid4())[:16]
        })
        
        # Generate signature
        signature = self._generate_signature(data, timestamp)
        
        headers = {
            "Authorization": f"STC-Pay {self.app_id}:{signature}",
            "Content-Type": "application/json",
            "X-STC-Timestamp": timestamp,
            "User-Agent": "BrainSAIT-Store/1.0",
            "Accept": "application/json"
        }
        
        try:
            with httpx.Client(timeout=30) as client:
                if method.upper() == "POST":
                    response = client.post(url, json=data, headers=headers)
                else:
                    response = client.get(url, params=data, headers=headers)
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"STC Pay API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response content: {e.response.text}")
            raise Exception(f"STC Pay request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in STC Pay API call: {e}")
            raise

    def _generate_qr_code(self, payment_data: str) -> str:
        """Generate QR code for STC Pay payment"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(payment_data)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            return None

    async def create_payment(
        self, 
        payment_request: STCPayPaymentRequest
    ) -> STCPayPaymentResponse:
        """
        Create payment request with STC Pay
        
        Args:
            payment_request: Payment details and customer information
            
        Returns:
            STCPayPaymentResponse with payment details and QR code
        """
        logger.info(f"Creating STC Pay payment for order {payment_request.order_id}")
        
        # Prepare payment data
        payment_data = {
            "amount": float(payment_request.amount),
            "currency": payment_request.currency,
            "order_id": payment_request.order_id,
            "customer_phone": payment_request.customer_phone,
            "description": payment_request.description,
            "return_url": payment_request.return_url,
            "webhook_url": payment_request.webhook_url,
            "expires_at": payment_request.expires_at.isoformat(),
            "metadata": payment_request.metadata
        }
        
        try:
            # Create payment request
            response_data = self._make_request("/v2/payments", payment_data)
            
            # Generate QR code for payment
            qr_data = {
                "payment_id": response_data["payment_id"],
                "amount": float(payment_request.amount),
                "merchant_id": self.merchant_id,
                "description": payment_request.description
            }
            qr_text = json.dumps(qr_data)
            qr_image = self._generate_qr_code(qr_text)
            
            # Generate deep link URL
            payment_url = f"stcpay://pay?id={response_data['payment_id']}"
            
            # Parse response
            stc_response = STCPayPaymentResponse(
                payment_id=response_data["payment_id"],
                status=response_data["status"],
                amount=Decimal(str(response_data["amount"])),
                currency=response_data["currency"],
                qr_code=qr_image,
                qr_code_text=qr_text,
                payment_url=payment_url,
                expires_at=datetime.fromisoformat(response_data["expires_at"]),
                reference_number=response_data.get("reference_number"),
                created_at=datetime.fromisoformat(response_data["created_at"]),
                metadata=response_data.get("metadata", {})
            )
            
            logger.info(f"STC Pay payment created: {stc_response.payment_id} - {stc_response.status}")
            return stc_response
            
        except Exception as e:
            logger.error(f"STC Pay payment creation failed: {e}")
            raise

    async def verify_payment(self, payment_id: str) -> STCPayPaymentResponse:
        """
        Verify payment status with STC Pay
        
        Args:
            payment_id: STC Pay payment ID to verify
            
        Returns:
            STCPayPaymentResponse with current payment status
        """
        logger.info(f"Verifying STC Pay payment: {payment_id}")
        
        try:
            response_data = self._make_request(
                f"/v2/payments/{payment_id}", 
                {}, 
                method="GET"
            )
            
            return STCPayPaymentResponse(
                payment_id=response_data["payment_id"],
                status=response_data["status"],
                amount=Decimal(str(response_data["amount"])),
                currency=response_data["currency"],
                qr_code=response_data.get("qr_code"),
                qr_code_text=response_data.get("qr_code_text"),
                payment_url=response_data.get("payment_url"),
                expires_at=datetime.fromisoformat(response_data["expires_at"]),
                reference_number=response_data.get("reference_number"),
                created_at=datetime.fromisoformat(response_data["created_at"]),
                metadata=response_data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"STC Pay payment verification failed: {e}")
            raise

    async def refund_payment(
        self, 
        refund_request: STCPayRefundRequest
    ) -> STCPayRefundResponse:
        """
        Process refund through STC Pay
        
        Args:
            refund_request: Refund details
            
        Returns:
            STCPayRefundResponse with refund details
        """
        logger.info(f"Processing STC Pay refund for payment {refund_request.payment_id}")
        
        refund_data = {
            "payment_id": refund_request.payment_id,
            "reason": refund_request.reason
        }
        
        if refund_request.amount:
            refund_data["amount"] = float(refund_request.amount)
        
        try:
            response_data = self._make_request("/v2/refunds", refund_data)
            
            return STCPayRefundResponse(
                refund_id=response_data["refund_id"],
                payment_id=response_data["payment_id"],
                amount=Decimal(str(response_data["amount"])),
                status=response_data["status"],
                reference_number=response_data.get("reference_number"),
                created_at=datetime.fromisoformat(response_data["created_at"])
            )
            
        except Exception as e:
            logger.error(f"STC Pay refund processing failed: {e}")
            raise

    async def check_wallet_status(self, phone_number: str) -> STCPayWalletInfo:
        """
        Check STC Pay wallet status for a phone number
        
        Args:
            phone_number: Saudi phone number (+966XXXXXXXXX)
            
        Returns:
            STCPayWalletInfo with wallet status
        """
        logger.info(f"Checking STC Pay wallet status for {phone_number}")
        
        wallet_data = {
            "phone_number": phone_number
        }
        
        try:
            response_data = self._make_request("/v2/wallets/status", wallet_data)
            
            return STCPayWalletInfo(
                phone_number=response_data["phone_number"],
                status=response_data["status"],
                balance=Decimal(str(response_data["balance"])) if response_data.get("balance") else None,
                daily_limit=Decimal(str(response_data["daily_limit"])) if response_data.get("daily_limit") else None,
                monthly_limit=Decimal(str(response_data["monthly_limit"])) if response_data.get("monthly_limit") else None
            )
            
        except Exception as e:
            logger.error(f"STC Pay wallet status check failed: {e}")
            raise

    def validate_webhook_signature(
        self, 
        payload: bytes, 
        signature: str, 
        timestamp: str
    ) -> bool:
        """
        Validate STC Pay webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Signature from STC Pay
            timestamp: Timestamp from webhook headers
            
        Returns:
            bool: True if signature is valid
        """
        try:
            # Create signature string
            sig_string = f"{timestamp}|{payload.decode('utf-8')}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                self.app_secret.encode('utf-8'),
                sig_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Webhook signature validation failed: {e}")
            return False

    async def send_payment_notification(
        self, 
        phone_number: str, 
        payment_id: str,
        amount: Decimal,
        merchant_name: str = "BrainSAIT Store"
    ) -> bool:
        """
        Send payment notification to customer via STC Pay
        
        Args:
            phone_number: Customer phone number
            payment_id: Payment ID
            amount: Payment amount
            merchant_name: Merchant display name
            
        Returns:
            bool: True if notification sent successfully
        """
        logger.info(f"Sending STC Pay notification to {phone_number}")
        
        notification_data = {
            "phone_number": phone_number,
            "payment_id": payment_id,
            "amount": float(amount),
            "merchant_name": merchant_name,
            "message": f"Payment request from {merchant_name} for {amount} SAR"
        }
        
        try:
            response_data = self._make_request("/v2/notifications", notification_data)
            return response_data.get("status") == "sent"
            
        except Exception as e:
            logger.error(f"STC Pay notification failed: {e}")
            return False

    def format_amount_for_api(self, amount: Decimal) -> int:
        """
        Format amount for STC Pay API (convert SAR to halalas)
        
        Args:
            amount: Amount in SAR
            
        Returns:
            int: Amount in halalas (SAR * 100)
        """
        return int(amount * 100)

    def format_amount_from_api(self, amount: int) -> Decimal:
        """
        Format amount from STC Pay API (convert halalas to SAR)
        
        Args:
            amount: Amount in halalas
            
        Returns:
            Decimal: Amount in SAR
        """
        return Decimal(amount) / 100

    def is_valid_saudi_phone(self, phone_number: str) -> bool:
        """
        Validate Saudi phone number format for STC Pay
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            bool: True if valid Saudi mobile number
        """
        import re
        pattern = r'^\+966[5][0-9]{8}$'
        return bool(re.match(pattern, phone_number))

    async def get_transaction_history(
        self, 
        phone_number: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history from STC Pay
        
        Args:
            phone_number: Filter by customer phone
            from_date: Start date for transactions
            to_date: End date for transactions
            limit: Maximum number of transactions
            
        Returns:
            List of transaction records
        """
        logger.info("Fetching STC Pay transaction history")
        
        query_data = {
            "limit": limit
        }
        
        if phone_number:
            query_data["phone_number"] = phone_number
        if from_date:
            query_data["from_date"] = from_date.isoformat()
        if to_date:
            query_data["to_date"] = to_date.isoformat()
        
        try:
            response_data = self._make_request("/v2/transactions", query_data, method="GET")
            return response_data.get("transactions", [])
            
        except Exception as e:
            logger.error(f"STC Pay transaction history fetch failed: {e}")
            return []

    def generate_payment_link(
        self, 
        payment_id: str, 
        amount: Decimal,
        description: str
    ) -> str:
        """
        Generate STC Pay deep link for mobile app
        
        Args:
            payment_id: Payment ID
            amount: Payment amount
            description: Payment description
            
        Returns:
            str: Deep link URL
        """
        return f"stcpay://pay?id={payment_id}&amount={amount}&desc={description}"


# Global instance
stc_pay_service = STCPayService()