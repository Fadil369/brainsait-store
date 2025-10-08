"""
Payment Provider Services for Saudi Market
Implements Mada, STC Pay, and Stripe payment processing
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import httpx
import stripe
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class StripeService:
    """Stripe payment processing service"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe
        
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "SAR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create Stripe payment intent"""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "status": intent.status,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment intent creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
            
    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm Stripe payment status"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,
                "currency": intent.currency.upper(),
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment confirmation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))


class MadaService:
    """Mada card payment service for Saudi Arabia"""
    
    def __init__(self):
        self.merchant_id = settings.MADA_MERCHANT_ID
        self.api_key = settings.MADA_API_KEY
        self.endpoint = settings.MADA_ENDPOINT
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def create_payment_intent(
        self,
        amount: float,
        order_id: UUID,
        customer_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create Mada payment intent
        
        Args:
            amount: Payment amount in SAR
            order_id: Order UUID
            customer_info: Customer details (name, email, phone)
            metadata: Additional metadata
            
        Returns:
            Payment intent details with redirect URL
        """
        try:
            payload = {
                "merchant_id": self.merchant_id,
                "amount": f"{amount:.2f}",
                "currency": "SAR",
                "order_reference": str(order_id),
                "customer": {
                    "name": customer_info.get("name", ""),
                    "email": customer_info.get("email", ""),
                    "phone": customer_info.get("phone", ""),
                },
                "callback_url": f"{settings.API_BASE_URL}/api/v1/payments/mada/callback",
                "metadata": metadata or {},
            }
            
            # Sign the request
            signature = self._generate_signature(payload)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Signature": signature,
                "Content-Type": "application/json",
            }
            
            response = await self.client.post(
                f"{self.endpoint}/v1/payments/create",
                json=payload,
                headers=headers,
            )
            
            if response.status_code != 200:
                logger.error(f"Mada payment creation failed: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Mada payment failed: {response.text}"
                )
                
            data = response.json()
            return {
                "payment_id": data.get("payment_id"),
                "redirect_url": data.get("redirect_url"),
                "status": data.get("status", "pending"),
                "expires_at": data.get("expires_at"),
            }
            
        except httpx.RequestError as e:
            logger.error(f"Mada API request failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Mada payment service unavailable"
            )
            
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Verify Mada payment status
        
        Args:
            payment_id: Mada payment ID
            
        Returns:
            Payment status and details
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            response = await self.client.get(
                f"{self.endpoint}/v1/payments/{payment_id}",
                headers=headers,
            )
            
            if response.status_code != 200:
                logger.error(f"Mada payment verification failed: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Payment verification failed: {response.text}"
                )
                
            data = response.json()
            return {
                "payment_id": data.get("payment_id"),
                "status": data.get("status"),
                "amount": float(data.get("amount", 0)),
                "currency": data.get("currency", "SAR"),
                "paid_at": data.get("paid_at"),
                "card_last4": data.get("card", {}).get("last4"),
                "card_brand": "mada",
            }
            
        except httpx.RequestError as e:
            logger.error(f"Mada verification request failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Mada payment service unavailable"
            )
            
    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate HMAC signature for Mada requests"""
        # Sort keys and create string representation
        sorted_data = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            self.api_key.encode(),
            sorted_data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    def verify_webhook_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify Mada webhook signature"""
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature)


class STCPayService:
    """STC Pay digital wallet service for Saudi Arabia"""
    
    def __init__(self):
        self.merchant_id = settings.STC_PAY_MERCHANT_ID
        self.api_key = settings.STC_PAY_API_KEY
        self.endpoint = settings.STC_PAY_ENDPOINT
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def create_payment_intent(
        self,
        amount: float,
        order_id: UUID,
        customer_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create STC Pay payment intent with QR code
        
        Args:
            amount: Payment amount in SAR
            order_id: Order UUID
            customer_info: Customer details (name, phone)
            metadata: Additional metadata
            
        Returns:
            Payment intent with QR code data
        """
        try:
            payload = {
                "merchant_id": self.merchant_id,
                "amount": f"{amount:.2f}",
                "currency": "SAR",
                "reference_id": str(order_id),
                "customer_mobile": customer_info.get("phone", ""),
                "description": f"Order {order_id}",
                "callback_url": f"{settings.API_BASE_URL}/api/v1/payments/stc-pay/callback",
                "metadata": metadata or {},
            }
            
            # Generate signature
            signature = self._generate_signature(payload)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Signature": signature,
                "Content-Type": "application/json",
            }
            
            response = await self.client.post(
                f"{self.endpoint}/v2/directpayment/request",
                json=payload,
                headers=headers,
            )
            
            if response.status_code != 200:
                logger.error(f"STC Pay payment creation failed: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"STC Pay payment failed: {response.text}"
                )
                
            data = response.json()
            return {
                "transaction_id": data.get("transaction_id"),
                "qr_code": data.get("qr_code"),
                "payment_url": data.get("payment_url"),
                "status": data.get("status", "pending"),
                "expires_at": data.get("expires_at"),
            }
            
        except httpx.RequestError as e:
            logger.error(f"STC Pay API request failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="STC Pay service unavailable"
            )
            
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verify STC Pay transaction status
        
        Args:
            transaction_id: STC Pay transaction ID
            
        Returns:
            Transaction status and details
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            response = await self.client.get(
                f"{self.endpoint}/v2/directpayment/status/{transaction_id}",
                headers=headers,
            )
            
            if response.status_code != 200:
                logger.error(f"STC Pay verification failed: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Transaction verification failed: {response.text}"
                )
                
            data = response.json()
            return {
                "transaction_id": data.get("transaction_id"),
                "status": data.get("status"),
                "amount": float(data.get("amount", 0)),
                "currency": data.get("currency", "SAR"),
                "paid_at": data.get("payment_time"),
                "reference_id": data.get("reference_id"),
            }
            
        except httpx.RequestError as e:
            logger.error(f"STC Pay verification request failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="STC Pay service unavailable"
            )
            
    async def generate_qr_code(
        self,
        amount: float,
        order_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate QR code for STC Pay payment
        
        Args:
            amount: Payment amount in SAR
            order_id: Order UUID
            
        Returns:
            QR code data and payment URL
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": f"{amount:.2f}",
            "currency": "SAR",
            "reference_id": str(order_id),
        }
        
        signature = self._generate_signature(payload)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Signature": signature,
            "Content-Type": "application/json",
        }
        
        try:
            response = await self.client.post(
                f"{self.endpoint}/v2/qrcode/generate",
                json=payload,
                headers=headers,
            )
            
            if response.status_code != 200:
                logger.error(f"STC Pay QR generation failed: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"QR code generation failed: {response.text}"
                )
                
            data = response.json()
            return {
                "qr_code": data.get("qr_code"),
                "qr_code_url": data.get("qr_code_url"),
                "expires_at": data.get("expires_at"),
            }
            
        except httpx.RequestError as e:
            logger.error(f"STC Pay QR generation request failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="STC Pay service unavailable"
            )
            
    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate HMAC signature for STC Pay requests"""
        # Create signature string according to STC Pay specs
        sorted_data = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            self.api_key.encode(),
            sorted_data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    def verify_webhook_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify STC Pay webhook signature"""
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature)
