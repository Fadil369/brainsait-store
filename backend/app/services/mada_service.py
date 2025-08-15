"""
Mada Payment Service for Saudi Arabia

Mada is the national payment system of Saudi Arabia, handling local debit card transactions.
This service provides integration with Mada payment gateways for processing local payments.
"""

import logging
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field, validator

from app.core.config import settings

logger = logging.getLogger(__name__)


class MadaCardInfo(BaseModel):
    """Mada card information for payment processing"""
    card_number: str = Field(..., regex=r'^5[0-9]{15}$')  # Mada cards start with 5
    expiry_month: str = Field(..., regex=r'^(0[1-9]|1[0-2])$')
    expiry_year: str = Field(..., regex=r'^20[2-9][0-9]$')
    cvv: str = Field(..., regex=r'^[0-9]{3}$')
    cardholder_name: str = Field(..., min_length=2, max_length=50)

    @validator('card_number')
    def validate_mada_card(cls, v):
        """Validate Mada card number using Luhn algorithm"""
        if not cls._luhn_check(v):
            raise ValueError('Invalid Mada card number')
        return v

    @staticmethod
    def _luhn_check(card_number: str) -> bool:
        """Luhn algorithm for card validation"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0


class MadaPaymentRequest(BaseModel):
    """Mada payment request structure"""
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="SAR")
    order_id: str = Field(..., min_length=1, max_length=50)
    customer_info: Dict[str, Any]
    card_info: MadaCardInfo
    return_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('currency')
    def validate_currency(cls, v):
        if v != "SAR":
            raise ValueError('Mada only supports SAR currency')
        return v


class MadaPaymentResponse(BaseModel):
    """Mada payment response structure"""
    transaction_id: str
    payment_id: str
    status: str
    amount: Decimal
    currency: str
    reference_number: Optional[str]
    approval_code: Optional[str]
    response_code: str
    response_message: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MadaRefundRequest(BaseModel):
    """Mada refund request structure"""
    transaction_id: str
    amount: Optional[Decimal] = None  # Partial refund if specified
    reason: str = Field(..., min_length=5, max_length=200)


class MadaRefundResponse(BaseModel):
    """Mada refund response structure"""
    refund_id: str
    transaction_id: str
    amount: Decimal
    status: str
    reference_number: Optional[str]
    created_at: datetime


class MadaService:
    """
    Mada Payment Gateway Service
    
    Provides integration with Mada payment processing for Saudi Arabia market.
    Handles card payments, refunds, and transaction verification.
    """

    def __init__(self):
        self.base_url = settings.MADA_API_URL or "https://api.mada.com.sa"
        self.merchant_id = settings.MADA_MERCHANT_ID
        self.api_key = settings.MADA_API_KEY
        self.secret_key = settings.MADA_SECRET_KEY
        self.environment = settings.MADA_ENVIRONMENT or "sandbox"
        
        if not all([self.merchant_id, self.api_key, self.secret_key]):
            logger.warning("Mada credentials not fully configured")

    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Generate HMAC signature for Mada API requests"""
        # Sort parameters by key
        sorted_params = sorted(data.items())
        query_string = urlencode(sorted_params)
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature

    def _make_request(
        self, 
        endpoint: str, 
        data: Dict[str, Any], 
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Make authenticated request to Mada API"""
        url = f"{self.base_url}{endpoint}"
        
        # Add merchant info and timestamp
        data.update({
            "merchant_id": self.merchant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "nonce": str(uuid.uuid4())
        })
        
        # Generate signature
        signature = self._generate_signature(data)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Mada-Signature": signature,
            "Content-Type": "application/json",
            "User-Agent": "BrainSAIT-Store/1.0"
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
            logger.error(f"Mada API request failed: {e}")
            raise Exception(f"Mada payment request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Mada API call: {e}")
            raise

    async def process_payment(
        self, 
        payment_request: MadaPaymentRequest
    ) -> MadaPaymentResponse:
        """
        Process payment through Mada gateway
        
        Args:
            payment_request: Payment details and card information
            
        Returns:
            MadaPaymentResponse with transaction details
        """
        logger.info(f"Processing Mada payment for order {payment_request.order_id}")
        
        # Prepare payment data
        payment_data = {
            "amount": float(payment_request.amount),
            "currency": payment_request.currency,
            "order_id": payment_request.order_id,
            "card_number": payment_request.card_info.card_number,
            "expiry_month": payment_request.card_info.expiry_month,
            "expiry_year": payment_request.card_info.expiry_year,
            "cvv": payment_request.card_info.cvv,
            "cardholder_name": payment_request.card_info.cardholder_name,
            "customer_name": payment_request.customer_info.get("name"),
            "customer_email": payment_request.customer_info.get("email"),
            "customer_phone": payment_request.customer_info.get("phone"),
            "return_url": payment_request.return_url,
            "metadata": payment_request.metadata
        }
        
        try:
            # Make payment request
            response_data = self._make_request("/v1/payments", payment_data)
            
            # Parse response
            mada_response = MadaPaymentResponse(
                transaction_id=response_data["transaction_id"],
                payment_id=response_data["payment_id"],
                status=response_data["status"],
                amount=Decimal(str(response_data["amount"])),
                currency=response_data["currency"],
                reference_number=response_data.get("reference_number"),
                approval_code=response_data.get("approval_code"),
                response_code=response_data["response_code"],
                response_message=response_data["response_message"],
                created_at=datetime.fromisoformat(response_data["created_at"]),
                metadata=response_data.get("metadata", {})
            )
            
            logger.info(f"Mada payment processed: {mada_response.transaction_id} - {mada_response.status}")
            return mada_response
            
        except Exception as e:
            logger.error(f"Mada payment processing failed: {e}")
            raise

    async def verify_transaction(self, transaction_id: str) -> MadaPaymentResponse:
        """
        Verify transaction status with Mada gateway
        
        Args:
            transaction_id: Mada transaction ID to verify
            
        Returns:
            MadaPaymentResponse with current transaction status
        """
        logger.info(f"Verifying Mada transaction: {transaction_id}")
        
        try:
            response_data = self._make_request(
                f"/v1/transactions/{transaction_id}", 
                {}, 
                method="GET"
            )
            
            return MadaPaymentResponse(
                transaction_id=response_data["transaction_id"],
                payment_id=response_data["payment_id"],
                status=response_data["status"],
                amount=Decimal(str(response_data["amount"])),
                currency=response_data["currency"],
                reference_number=response_data.get("reference_number"),
                approval_code=response_data.get("approval_code"),
                response_code=response_data["response_code"],
                response_message=response_data["response_message"],
                created_at=datetime.fromisoformat(response_data["created_at"]),
                metadata=response_data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Mada transaction verification failed: {e}")
            raise

    async def refund_payment(
        self, 
        refund_request: MadaRefundRequest
    ) -> MadaRefundResponse:
        """
        Process refund through Mada gateway
        
        Args:
            refund_request: Refund details
            
        Returns:
            MadaRefundResponse with refund details
        """
        logger.info(f"Processing Mada refund for transaction {refund_request.transaction_id}")
        
        refund_data = {
            "transaction_id": refund_request.transaction_id,
            "reason": refund_request.reason
        }
        
        if refund_request.amount:
            refund_data["amount"] = float(refund_request.amount)
        
        try:
            response_data = self._make_request("/v1/refunds", refund_data)
            
            return MadaRefundResponse(
                refund_id=response_data["refund_id"],
                transaction_id=response_data["transaction_id"],
                amount=Decimal(str(response_data["amount"])),
                status=response_data["status"],
                reference_number=response_data.get("reference_number"),
                created_at=datetime.fromisoformat(response_data["created_at"])
            )
            
        except Exception as e:
            logger.error(f"Mada refund processing failed: {e}")
            raise

    def validate_webhook_signature(
        self, 
        payload: bytes, 
        signature: str, 
        timestamp: str
    ) -> bool:
        """
        Validate Mada webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Signature from Mada
            timestamp: Timestamp from webhook headers
            
        Returns:
            bool: True if signature is valid
        """
        try:
            # Create signature string
            sig_string = f"{timestamp}.{payload.decode('utf-8')}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                sig_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Webhook signature validation failed: {e}")
            return False

    async def get_supported_banks(self) -> List[Dict[str, Any]]:
        """
        Get list of supported Mada banks
        
        Returns:
            List of bank information
        """
        try:
            response_data = self._make_request("/v1/banks", {}, method="GET")
            return response_data.get("banks", [])
        except Exception as e:
            logger.error(f"Failed to fetch Mada banks: {e}")
            return []

    def format_amount_for_api(self, amount: Decimal) -> int:
        """
        Format amount for Mada API (convert SAR to halalas)
        
        Args:
            amount: Amount in SAR
            
        Returns:
            int: Amount in halalas (SAR * 100)
        """
        return int(amount * 100)

    def format_amount_from_api(self, amount: int) -> Decimal:
        """
        Format amount from Mada API (convert halalas to SAR)
        
        Args:
            amount: Amount in halalas
            
        Returns:
            Decimal: Amount in SAR
        """
        return Decimal(amount) / 100

    def is_mada_card(self, card_number: str) -> bool:
        """
        Check if card number is a valid Mada card
        
        Args:
            card_number: Card number to check
            
        Returns:
            bool: True if valid Mada card
        """
        # Remove spaces and check format
        clean_number = card_number.replace(" ", "")
        
        # Mada cards start with 5 and are 16 digits
        if not (clean_number.startswith("5") and len(clean_number) == 16):
            return False
        
        # Check if it's in Mada BIN ranges (simplified check)
        mada_bin_ranges = [
            (508160, 508199),  # National Bank of Kuwait
            (521141, 521160),  # SABB
            (530906, 530906),  # Arab National Bank
            (558538, 558538),  # Banque Saudi Fransi
            # Add more BIN ranges as needed
        ]
        
        card_prefix = int(clean_number[:6])
        return any(start <= card_prefix <= end for start, end in mada_bin_ranges)


# Global instance
mada_service = MadaService()