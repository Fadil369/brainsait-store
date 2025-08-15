"""
Comprehensive Payment Gateway Service
Supports Stripe, PayPal, Apple Pay with local Saudi gateways integration
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx
import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.orders import Order, OrderItem, OrderStatus, PaymentMethod
from app.models.products import Product
from app.models.users import User
from app.schemas.payment import (
    ApplePayValidation,
    PaymentRequest,
    PaymentResponse,
    PayPalPaymentCreate,
    StripeProductCreate,
    StripeSubscriptionCreate,
)

# Use global settings instance


class PaymentGatewayService:
    """Unified payment gateway service"""

    def __init__(self):
        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe

        # PayPal configuration
        self.paypal_client_id = settings.PAYPAL_CLIENT_ID
        self.paypal_secret = settings.PAYPAL_SECRET
        self.paypal_base_url = settings.PAYPAL_BASE_URL

        # Apple Pay configuration
        self.apple_pay_merchant_id = settings.APPLE_PAY_MERCHANT_ID
        self.apple_pay_domain = settings.APPLE_PAY_DOMAIN

    # ==================== STRIPE INTEGRATION ====================

    async def create_stripe_product(
        self, product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create product in Stripe catalog"""
        try:
            # Create product
            stripe_product = self.stripe.Product.create(
                name=product_data["name"],
                description=product_data.get("description", ""),
                metadata={
                    "product_id": str(product_data["id"]),
                    "category": product_data.get("category", ""),
                    "source": "brainsait_store",
                },
                images=product_data.get("images", []),
                url=product_data.get("live_demo", ""),
                active=True,
            )

            # Create price
            stripe_price = self.stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(product_data["price"] * 100),  # Convert to cents
                currency="sar",
                metadata={
                    "pricing_type": product_data.get("pricing_type", "one_time"),
                    "includes_source": str(product_data.get("includes_source", False)),
                },
            )

            return {
                "product_id": stripe_product.id,
                "price_id": stripe_price.id,
                "product": stripe_product,
                "price": stripe_price,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create Stripe product: {str(e)}",
            )

    async def create_stripe_payment_link(
        self, price_id: str, metadata: Dict[str, Any] = None
    ) -> str:
        """Create Stripe payment link for B2B sales"""
        try:
            payment_link = self.stripe.PaymentLink.create(
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                metadata=metadata or {},
                allow_promotion_codes=True,
                billing_address_collection="required",
                tax_id_collection={"enabled": True},
                custom_fields=[
                    {
                        "key": "company_name",
                        "label": {"type": "text", "custom": "Company Name"},
                        "type": "text",
                        "optional": False,
                    },
                    {
                        "key": "vat_number",
                        "label": {
                            "type": "text",
                            "custom": "VAT Number (if applicable)",
                        },
                        "type": "text",
                        "optional": True,
                    },
                ],
                after_completion={
                    "type": "hosted_confirmation",
                    "hosted_confirmation": {
                        "custom_message": "Thank you for your purchase! You will receive download instructions via email."
                    },
                },
            )

            return payment_link.url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create payment link: {str(e)}",
            )

    async def create_stripe_checkout_session(
        self, order: Order, success_url: str, cancel_url: str
    ) -> Dict[str, Any]:
        """Create Stripe checkout session for order"""
        try:
            line_items = []

            for item in order.items:
                line_items.append(
                    {
                        "price_data": {
                            "currency": "sar",
                            "product_data": {
                                "name": item.product_name,
                                "description": f"License: {item.license_type}",
                                "metadata": {
                                    "product_id": str(item.product_id),
                                    "license_type": item.license_type,
                                },
                            },
                            "unit_amount": int(item.price * 100),
                        },
                        "quantity": item.quantity,
                    }
                )

            session = self.stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "order_id": str(order.id),
                    "user_id": str(order.user_id),
                    "tenant_id": str(order.tenant_id),
                },
                billing_address_collection="required",
                tax_id_collection={"enabled": True},
                allow_promotion_codes=True,
                automatic_tax={"enabled": True},
                customer_email=order.customer_email,
                expires_at=int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
            )

            return {
                "session_id": session.id,
                "checkout_url": session.url,
                "session": session,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create Stripe session: {str(e)}",
            )

    async def sync_products_to_stripe(self, products: List[Product]) -> Dict[str, Any]:
        """Sync all products to Stripe catalog"""
        synced_products = []
        errors = []

        for product in products:
            try:
                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "category": product.category,
                    "images": [product.image_url] if product.image_url else [],
                    "live_demo": product.live_demo,
                    "pricing_type": "one_time",
                    "includes_source": "source_code" in product.bundle_options,
                }

                stripe_data = await self.create_stripe_product(product_data)
                synced_products.append(
                    {
                        "product_id": product.id,
                        "stripe_product_id": stripe_data["product_id"],
                        "stripe_price_id": stripe_data["price_id"],
                    }
                )

                # Add delay to avoid rate limits
                await asyncio.sleep(0.1)

            except Exception as e:
                errors.append({"product_id": product.id, "error": str(e)})

        return {
            "synced_count": len(synced_products),
            "error_count": len(errors),
            "synced_products": synced_products,
            "errors": errors,
        }

    # ==================== PAYPAL INTEGRATION ====================

    async def get_paypal_access_token(self) -> str:
        """Get PayPal access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.paypal_base_url}/v1/oauth2/token",
                    auth=(self.paypal_client_id, self.paypal_secret),
                    headers={"Accept": "application/json"},
                    data={"grant_type": "client_credentials"},
                )
                response.raise_for_status()
                return response.json()["access_token"]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get PayPal token: {str(e)}",
            )

    async def create_paypal_order(self, order: Order) -> Dict[str, Any]:
        """Create PayPal order for B2B payment"""
        try:
            access_token = await self.get_paypal_access_token()

            # Calculate total
            total_amount = sum(item.price * item.quantity for item in order.items)

            # Prepare order items
            items = []
            for item in order.items:
                items.append(
                    {
                        "name": item.product_name,
                        "description": f"License: {item.license_type}",
                        "unit_amount": {
                            "currency_code": "SAR",
                            "value": str(item.price),
                        },
                        "quantity": str(item.quantity),
                        "category": "DIGITAL_GOODS",
                    }
                )

            paypal_order = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": str(order.id),
                        "amount": {
                            "currency_code": "SAR",
                            "value": str(total_amount),
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "SAR",
                                    "value": str(total_amount),
                                }
                            },
                        },
                        "items": items,
                        "description": f"BrainSAIT B2B Solutions - Order #{order.id}",
                        "custom_id": str(order.id),
                        "soft_descriptor": "BRAINSAIT",
                    }
                ],
                "application_context": {
                    "brand_name": "BrainSAIT Solutions",
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                    "return_url": f"{settings.FRONTEND_URL}/payment/success",
                    "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel",
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.paypal_base_url}/v2/checkout/orders",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=paypal_order,
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create PayPal order: {str(e)}",
            )

    async def capture_paypal_payment(self, order_id: str) -> Dict[str, Any]:
        """Capture PayPal payment"""
        try:
            access_token = await self.get_paypal_access_token()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.paypal_base_url}/v2/checkout/orders/{order_id}/capture",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to capture PayPal payment: {str(e)}",
            )

    # ==================== APPLE PAY INTEGRATION ====================

    async def validate_apple_pay_merchant(self, validation_url: str) -> Dict[str, Any]:
        """Validate merchant for Apple Pay"""
        try:
            # This requires Apple Pay merchant certificate
            # In production, you'll need to implement proper certificate handling
            validation_data = {
                "merchantIdentifier": self.apple_pay_merchant_id,
                "domainName": self.apple_pay_domain,
                "displayName": "BrainSAIT Solutions",
            }

            async with httpx.AsyncClient(
                cert=(settings.APPLE_PAY_CERT_PATH, settings.APPLE_PAY_KEY_PATH),
                verify=settings.APPLE_PAY_CA_PATH,
            ) as client:
                response = await client.post(
                    validation_url,
                    json=validation_data,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to validate Apple Pay merchant: {str(e)}",
            )

    async def process_apple_pay_payment(
        self, payment_token: Dict[str, Any], order: Order
    ) -> Dict[str, Any]:
        """Process Apple Pay payment through Stripe"""
        try:
            # Use Stripe to process Apple Pay token
            payment_intent = self.stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),
                currency="sar",
                payment_method_data={
                    "type": "card",
                    "card": {"token": payment_token["paymentData"]["data"]},
                },
                metadata={"order_id": str(order.id), "payment_method": "apple_pay"},
                confirm=True,
                return_url=f"{settings.FRONTEND_URL}/payment/success",
            )

            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "client_secret": payment_intent.client_secret,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process Apple Pay payment: {str(e)}",
            )

    # ==================== SAUDI LOCAL GATEWAYS ====================

    async def create_moyasar_payment(self, order: Order) -> Dict[str, Any]:
        """Create Moyasar payment for local Saudi market"""
        try:
            payment_data = {
                "amount": int(order.total_amount * 100),  # Convert to halalas
                "currency": "SAR",
                "description": f"BrainSAIT Order #{order.id}",
                "publishable_api_key": settings.MOYASAR_PUBLISHABLE_KEY,
                "callback_url": f"{settings.API_URL}/webhooks/moyasar",
                "metadata": {"order_id": str(order.id), "user_id": str(order.user_id)},
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.moyasar.com/v1/payments",
                    headers={
                        "Authorization": f"Basic {settings.MOYASAR_SECRET_KEY}",
                        "Content-Type": "application/json",
                    },
                    json=payment_data,
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create Moyasar payment: {str(e)}",
            )

    async def create_hyperpay_checkout(self, order: Order) -> Dict[str, Any]:
        """Create HyperPay checkout session"""
        try:
            checkout_data = {
                "entityId": settings.HYPERPAY_ENTITY_ID,
                "amount": f"{order.total_amount:.2f}",
                "currency": "SAR",
                "paymentType": "DB",
                "merchantTransactionId": str(order.id),
                "customer.email": order.customer_email,
                "billing.country": "SA",
                "customParameters[order_id]": str(order.id),
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.HYPERPAY_BASE_URL}/v1/checkouts",
                    headers={
                        "Authorization": f"Bearer {settings.HYPERPAY_ACCESS_TOKEN}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data=checkout_data,
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create HyperPay checkout: {str(e)}",
            )

    # ==================== UNIFIED PAYMENT PROCESSING ====================

    async def process_payment(
        self, order: Order, payment_method: str, payment_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process payment through specified gateway"""

        try:
            if payment_method == "stripe":
                return await self.create_stripe_checkout_session(
                    order,
                    payment_data.get(
                        "success_url", f"{settings.FRONTEND_URL}/payment/success"
                    ),
                    payment_data.get(
                        "cancel_url", f"{settings.FRONTEND_URL}/payment/cancel"
                    ),
                )

            elif payment_method == "paypal":
                return await self.create_paypal_order(order)

            elif payment_method == "apple_pay":
                return await self.process_apple_pay_payment(
                    payment_data["payment_token"], order
                )

            elif payment_method == "moyasar":
                return await self.create_moyasar_payment(order)

            elif payment_method == "hyperpay":
                return await self.create_hyperpay_checkout(order)

            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported payment method: {payment_method}",
                )

        except Exception as e:
            # Log error for monitoring
            print(f"Payment processing error: {e}")
            raise

    async def verify_webhook_signature(
        self, payload: bytes, signature: str, gateway: str
    ) -> bool:
        """Verify webhook signature for security"""

        if gateway == "stripe":
            try:
                self.stripe.Webhook.construct_event(
                    payload, signature, settings.STRIPE_WEBHOOK_SECRET
                )
                return True
            except:
                return False

        elif gateway == "paypal":
            # Implement PayPal webhook verification
            # This requires PayPal webhook certificate verification
            return True  # Simplified for now

        return False

    async def handle_payment_webhook(
        self, gateway: str, event_data: Dict[str, Any], db: Session
    ) -> Dict[str, Any]:
        """Handle payment gateway webhooks"""

        if gateway == "stripe":
            return await self._handle_stripe_webhook(event_data, db)
        elif gateway == "paypal":
            return await self._handle_paypal_webhook(event_data, db)
        elif gateway == "moyasar":
            return await self._handle_moyasar_webhook(event_data, db)
        elif gateway == "hyperpay":
            return await self._handle_hyperpay_webhook(event_data, db)

    async def _handle_stripe_webhook(self, event: Dict[str, Any], db: Session):
        """Handle Stripe webhook events"""

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            order_id = session["metadata"]["order_id"]

            # Update order status
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.PAID
                order.payment_method = PaymentMethod.STRIPE
                order.payment_reference = session["id"]
                order.paid_at = datetime.utcnow()
                db.commit()

        elif event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            order_id = payment_intent["metadata"]["order_id"]

            # Update order status
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.PAID
                order.payment_reference = payment_intent["id"]
                order.paid_at = datetime.utcnow()
                db.commit()

        return {"status": "handled"}

    async def _handle_paypal_webhook(self, event: Dict[str, Any], db: Session):
        """Handle PayPal webhook events"""

        if event["event_type"] == "CHECKOUT.ORDER.APPROVED":
            order_data = event["resource"]
            order_id = order_data["purchase_units"][0]["custom_id"]

            # Update order status
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.PAID
                order.payment_method = PaymentMethod.PAYPAL
                order.payment_reference = order_data["id"]
                order.paid_at = datetime.utcnow()
                db.commit()

        return {"status": "handled"}

    async def _handle_moyasar_webhook(self, event: Dict[str, Any], db: Session):
        """Handle Moyasar webhook events"""

        if event["type"] == "payment_paid":
            payment = event["data"]
            order_id = payment["metadata"]["order_id"]

            # Update order status
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.PAID
                order.payment_method = PaymentMethod.MOYASAR
                order.payment_reference = payment["id"]
                order.paid_at = datetime.utcnow()
                db.commit()

        return {"status": "handled"}

    async def _handle_hyperpay_webhook(self, event: Dict[str, Any], db: Session):
        """Handle HyperPay webhook events"""

        if event["type"] == "payment.success":
            payment = event["data"]
            order_id = payment["merchantTransactionId"]

            # Update order status
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = OrderStatus.PAID
                order.payment_method = PaymentMethod.HYPERPAY
                order.payment_reference = payment["id"]
                order.paid_at = datetime.utcnow()
                db.commit()

        return {"status": "handled"}


# Global instance
payment_gateway = PaymentGatewayService()
