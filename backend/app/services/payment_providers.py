"""
Payment Provider Services for Saudi Arabia market
Supporting Mada, STC Pay, and Stripe integrations
"""

import asyncio
import hashlib
import hmac
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

import httpx
import stripe
from fastapi import HTTPException

from app.core.config import settings
logger = logging.getLogger(__name__)


class StripeService:
    """Stripe payment service"""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe

    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "SAR",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create Stripe payment intent"""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                metadata=metadata or {},
            )
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": intent.status,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment intent creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))


class MadaService:
    """Mada payment service for Saudi domestic debit cards"""

    def __init__(self):
        self.api_key = settings.MADA_API_KEY
        self.merchant_id = settings.MADA_MERCHANT_ID
        self.endpoint = settings.MADA_ENDPOINT
        self.client = httpx.AsyncClient()

    async def create_payment(
        self,
        amount: float,
        currency: str = "SAR",
        reference: str = None,
        return_url: str = None,
        customer_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create Mada payment transaction"""
        try:
            # Generate unique payment ID
            payment_id = str(uuid4())
            
            # Prepare payment data
            payment_data = {
                "merchant_id": self.merchant_id,
                "payment_id": payment_id,
                "amount": amount,
                "currency": currency,
                "reference": reference,
                "return_url": return_url,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if customer_info:
                payment_data["customer"] = customer_info

            # Add signature for security
            payment_data["signature"] = self._generate_signature(payment_data)

            # For development/testing, return mock response
            if not self.api_key or self.api_key == "test":
                return self._mock_mada_response(payment_id, amount, currency)

            # Make API call to Mada
            response = await self.client.post(
                f"{self.endpoint}/v1/payments",
                json=payment_data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                logger.error(f"Mada API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=400, detail="Mada payment creation failed"
                )

            result = response.json()
            return {
                "payment_id": result.get("payment_id", payment_id),
                "redirect_url": result.get("redirect_url"),
                "status": result.get("status", "pending"),
                "reference": reference,
            }

        except httpx.RequestError as e:
            logger.error(f"Mada payment request failed: {e}")
            raise HTTPException(status_code=500, detail="Mada service unavailable")

    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Generate HMAC signature for Mada API"""
        if not self.api_key:
            return "test_signature"
        
        # Create signature string from sorted data
        signature_string = "&".join(
            f"{k}={v}" for k, v in sorted(data.items()) if k != "signature"
        )
        
        return hmac.new(
            self.api_key.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()

    def _mock_mada_response(self, payment_id: str, amount: float, currency: str) -> Dict[str, Any]:
        """Generate mock response for testing"""
        return {
            "payment_id": payment_id,
            "redirect_url": f"https://mada.sa/pay/{payment_id}",
            "status": "pending",
            "amount": amount,
            "currency": currency,
        }

    async def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify Mada webhook signature"""
        if not self.api_key or self.api_key == "test":
            return True
        
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature)


class STCPayService:
    """STC Pay digital wallet service"""

    def __init__(self):
        self.api_key = settings.STC_PAY_API_KEY
        self.merchant_id = settings.STC_PAY_MERCHANT_ID
        self.endpoint = settings.STC_PAY_ENDPOINT
        self.client = httpx.AsyncClient()

    async def create_payment(
        self,
        amount: float,
        mobile_number: str,
        reference: str = None,
        description: str = None,
    ) -> Dict[str, Any]:
        """Create STC Pay payment transaction"""
        try:
            # Generate unique transaction ID
            transaction_id = str(uuid4())
            
            # Normalize mobile number (remove +966, add 0)
            if mobile_number.startswith("+966"):
                mobile_number = "0" + mobile_number[4:]
            elif mobile_number.startswith("966"):
                mobile_number = "0" + mobile_number[3:]
            elif not mobile_number.startswith("05"):
                mobile_number = "05" + mobile_number[-8:]

            # Prepare payment data
            payment_data = {
                "merchant_id": self.merchant_id,
                "transaction_id": transaction_id,
                "amount": amount,
                "mobile_number": mobile_number,
                "reference": reference,
                "description": description or f"Payment for order {reference}",
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Add signature for security
            payment_data["signature"] = self._generate_signature(payment_data)

            # For development/testing, return mock response
            if not self.api_key or self.api_key == "test":
                return self._mock_stc_response(transaction_id, amount, mobile_number)

            # Make API call to STC Pay
            response = await self.client.post(
                f"{self.endpoint}/v1/payment/request",
                json=payment_data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                logger.error(f"STC Pay API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=400, detail="STC Pay payment creation failed"
                )

            result = response.json()
            return {
                "transaction_id": result.get("transaction_id", transaction_id),
                "payment_url": result.get("payment_url"),
                "status": result.get("status", "pending"),
                "mobile_number": mobile_number,
                "reference": reference,
            }

        except httpx.RequestError as e:
            logger.error(f"STC Pay payment request failed: {e}")
            raise HTTPException(status_code=500, detail="STC Pay service unavailable")

    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Generate HMAC signature for STC Pay API"""
        if not self.api_key:
            return "test_signature"
        
        # Create signature string from sorted data
        signature_string = "&".join(
            f"{k}={v}" for k, v in sorted(data.items()) if k != "signature"
        )
        
        return hmac.new(
            self.api_key.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()

    def _mock_stc_response(self, transaction_id: str, amount: float, mobile_number: str) -> Dict[str, Any]:
        """Generate mock response for testing"""
        return {
            "transaction_id": transaction_id,
            "payment_url": f"https://stcpay.com.sa/pay/{transaction_id}",
            "status": "pending",
            "amount": amount,
            "mobile_number": mobile_number,
        }

    async def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify STC Pay webhook signature"""
        if not self.api_key or self.api_key == "test":
            return True
        
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature)

    def validate_mobile_number(self, mobile_number: str) -> bool:
        """Validate Saudi mobile number format"""
        # Remove spaces and special characters
        clean_number = "".join(filter(str.isdigit, mobile_number))
        
        # Check if it's a valid Saudi number
        if len(clean_number) == 10 and clean_number.startswith("05"):
            return True
        elif len(clean_number) == 12 and clean_number.startswith("966"):
            return True
        elif len(clean_number) == 13 and clean_number.startswith("+966"):
            return True
        
        return False