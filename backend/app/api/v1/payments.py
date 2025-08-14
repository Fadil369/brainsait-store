"""
BrainSAIT Payment Processing API
Supporting Stripe, PayPal, Apple Pay, Mada (Saudi debit), and STC Pay
ZATCA compliant invoicing with B2B focus
"""

import hashlib
import hmac
import json
import logging
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_tenant, get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.products import Product
from app.models.store import Invoice, Order, Payment
from app.schemas.payments import (
    ApplePayPaymentCreate,
    InvoiceResponse,
    MadaPaymentCreate,
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentLinkCreate,
    PaymentMethodResponse,
    PaymentWebhook,
    PayPalPaymentCreate,
    STCPaymentCreate,
    StripeProductCreate,
)
from app.services.notifications import NotificationService
from app.services.payment_providers import MadaService, STCPayService, StripeService
from app.services.zatca_service import ZATCAService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize payment services
stripe_service = StripeService()
mada_service = MadaService()
stc_service = STCPayService()
zatca_service = ZATCAService()
notification_service = NotificationService()


@router.get("/methods", response_model=Dict[str, PaymentMethodResponse])
async def get_payment_methods(
    request: Request, tenant_id: UUID = Depends(get_current_tenant)
):
    """Get available payment methods for tenant"""

    methods = {
        "stripe": PaymentMethodResponse(
            id="stripe",
            name="Credit/Debit Cards",
            name_ar="البطاقات الائتمانية/المدينة",
            description="Visa, Mastercard, American Express, Apple Pay",
            description_ar="فيزا، ماستركارد، أمريكان إكسبريس، أبل باي",
            supported_currencies=["SAR", "USD", "EUR"],
            fees={"percentage": 2.9, "fixed": 0},
            enabled=True,
            logo_url="/payment-logos/stripe.svg",
        ),
        "paypal": PaymentMethodResponse(
            id="paypal",
            name="PayPal",
            name_ar="باي بال",
            description="PayPal, Credit Cards, Bank Transfer",
            description_ar="باي بال، البطاقات الائتمانية، تحويل بنكي",
            supported_currencies=["SAR", "USD", "EUR"],
            fees={"percentage": 3.4, "fixed": 0},
            enabled=True,
            logo_url="/payment-logos/paypal.svg",
        ),
        "apple_pay": PaymentMethodResponse(
            id="apple_pay",
            name="Apple Pay",
            name_ar="أبل باي",
            description="Touch ID, Face ID, Apple Watch",
            description_ar="بصمة الإصبع، التعرف على الوجه، ساعة أبل",
            supported_currencies=["SAR", "USD", "EUR"],
            fees={"percentage": 2.9, "fixed": 0},
            enabled=True,
            logo_url="/payment-logos/apple-pay.svg",
        ),
        "mada": PaymentMethodResponse(
            id="mada",
            name="Mada Cards",
            name_ar="بطاقات مدى",
            description="Saudi domestic debit cards",
            description_ar="البطاقات المدينة السعودية المحلية",
            supported_currencies=["SAR"],
            fees={"percentage": 1.5, "fixed": 0},
            enabled=True,
            logo_url="/payment-logos/mada.svg",
        ),
        "stc_pay": PaymentMethodResponse(
            id="stc_pay",
            name="STC Pay",
            name_ar="STC Pay",
            description="Mobile wallet payment",
            description_ar="دفع عبر المحفظة الرقمية",
            supported_currencies=["SAR"],
            fees={"percentage": 1.0, "fixed": 0},
            enabled=True,
            logo_url="/payment-logos/stc-pay.svg",
        ),
    }

    return methods


@router.post("/stripe/intent", response_model=PaymentIntentResponse)
async def create_stripe_payment_intent(
    payment_data: PaymentIntentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Create Stripe payment intent"""

    try:
        # Get order details
        order_query = select(Order).where(
            and_(
                Order.id == payment_data.order_id,
                Order.tenant_id == tenant_id,
                Order.user_id == current_user.id,
            )
        )

        order_result = await db.execute(order_query)
        order = order_result.scalar_first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status != "pending":
            raise HTTPException(
                status_code=400, detail="Order is not in pending status"
            )

        # Create Stripe payment intent
        payment_intent = await stripe_service.create_payment_intent(
            amount=int(order.total_amount * 100),  # Convert to halalas
            currency="sar",
            metadata={
                "order_id": str(order.id),
                "tenant_id": str(tenant_id),
                "customer_email": order.customer_email,
            },
            customer_email=order.customer_email,
        )

        # Save payment record
        payment = Payment(
            tenant_id=tenant_id,
            order_id=order.id,
            provider="stripe",
            provider_payment_id=payment_intent["id"],
            amount=order.total_amount,
            currency="SAR",
            status="pending",
            metadata={"client_secret": payment_intent["client_secret"]},
        )

        db.add(payment)
        order.payment_intent_id = payment_intent["id"]
        await db.commit()

        return PaymentIntentResponse(
            payment_intent_id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            amount=order.total_amount,
            currency="SAR",
            status="requires_payment_method",
        )

    except Exception as e:
        logger.error(f"Stripe payment intent creation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment intent creation failed")


@router.post("/mada/intent", response_model=PaymentIntentResponse)
async def create_mada_payment_intent(
    payment_data: MadaPaymentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Create Mada payment intent"""

    try:
        # Get order details
        order_query = select(Order).where(
            and_(
                Order.id == payment_data.order_id,
                Order.tenant_id == tenant_id,
                Order.user_id == current_user.id,
            )
        )

        order_result = await db.execute(order_query)
        order = order_result.scalar_first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Create Mada payment
        mada_payment = await mada_service.create_payment(
            amount=order.total_amount,
            currency="SAR",
            reference=str(order.id),
            return_url=payment_data.return_url,
            customer_info={
                "email": order.customer_email,
                "name": payment_data.customer_name,
                "phone": payment_data.customer_phone,
            },
        )

        # Save payment record
        payment = Payment(
            tenant_id=tenant_id,
            order_id=order.id,
            provider="mada",
            provider_payment_id=mada_payment["payment_id"],
            amount=order.total_amount,
            currency="SAR",
            status="pending",
            metadata={"redirect_url": mada_payment["redirect_url"]},
        )

        db.add(payment)
        await db.commit()

        return PaymentIntentResponse(
            payment_intent_id=mada_payment["payment_id"],
            redirect_url=mada_payment["redirect_url"],
            amount=order.total_amount,
            currency="SAR",
            status="requires_action",
        )

    except Exception as e:
        logger.error(f"Mada payment creation failed: {e}")
        raise HTTPException(status_code=500, detail="Mada payment creation failed")


@router.post("/stc-pay/intent", response_model=PaymentIntentResponse)
async def create_stc_payment_intent(
    payment_data: STCPaymentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Create STC Pay payment intent"""

    try:
        # Get order details
        order_query = select(Order).where(
            and_(
                Order.id == payment_data.order_id,
                Order.tenant_id == tenant_id,
                Order.user_id == current_user.id,
            )
        )

        order_result = await db.execute(order_query)
        order = order_result.scalar_first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Validate Saudi mobile number
        if not payment_data.mobile_number.startswith("+966"):
            raise HTTPException(
                status_code=400,
                detail="Mobile number must be a valid Saudi number (+966)",
            )

        # Create STC Pay payment
        stc_payment = await stc_service.create_payment(
            amount=order.total_amount,
            mobile_number=payment_data.mobile_number,
            reference=str(order.id),
            description=f"BrainSAIT Store Order #{order.id}",
        )

        # Save payment record
        payment = Payment(
            tenant_id=tenant_id,
            order_id=order.id,
            provider="stc_pay",
            provider_payment_id=stc_payment["transaction_id"],
            amount=order.total_amount,
            currency="SAR",
            status="pending",
            metadata={"mobile_number": payment_data.mobile_number},
        )

        db.add(payment)
        await db.commit()

        return PaymentIntentResponse(
            payment_intent_id=stc_payment["transaction_id"],
            amount=order.total_amount,
            currency="SAR",
            status="requires_confirmation",
            mobile_verification=True,
        )

    except Exception as e:
        logger.error(f"STC Pay payment creation failed: {e}")
        raise HTTPException(status_code=500, detail="STC Pay payment creation failed")


# ==================== PAYPAL INTEGRATION ====================


@router.post("/paypal/order", response_model=PaymentIntentResponse)
async def create_paypal_order(
    payment_data: PayPalPaymentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Create PayPal order for B2B payment"""

    try:
        # Get order details
        order_query = select(Order).where(
            and_(
                Order.id == payment_data.order_id,
                Order.tenant_id == tenant_id,
                Order.user_id == current_user.id,
            )
        )

        order_result = await db.execute(order_query)
        order = order_result.scalar_first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Get PayPal access token
        access_token = await get_paypal_access_token()

        # Create PayPal order
        paypal_order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(order.id),
                    "amount": {
                        "currency_code": "SAR",
                        "value": str(order.total_amount),
                    },
                    "description": f"BrainSAIT B2B Solutions - Order #{order.id}",
                    "custom_id": str(order.id),
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
                f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=paypal_order_data,
            )
            response.raise_for_status()
            paypal_response = response.json()

        # Save payment record
        payment = Payment(
            tenant_id=tenant_id,
            order_id=order.id,
            provider="paypal",
            provider_payment_id=paypal_response["id"],
            amount=order.total_amount,
            currency="SAR",
            status="pending",
            metadata={"paypal_order": paypal_response},
        )

        db.add(payment)
        await db.commit()

        # Find approval URL
        approval_url = None
        for link in paypal_response.get("links", []):
            if link["rel"] == "approve":
                approval_url = link["href"]
                break

        return PaymentIntentResponse(
            payment_intent_id=paypal_response["id"],
            redirect_url=approval_url,
            amount=order.total_amount,
            currency="SAR",
            status="requires_action",
        )

    except Exception as e:
        logger.error(f"PayPal order creation failed: {e}")
        raise HTTPException(status_code=500, detail="PayPal order creation failed")


@router.post("/paypal/capture/{order_id}")
async def capture_paypal_payment(order_id: str, db: AsyncSession = Depends(get_db)):
    """Capture PayPal payment"""

    try:
        access_token = await get_paypal_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            capture_response = response.json()

        # Update payment status
        payment_query = select(Payment).where(Payment.provider_payment_id == order_id)
        payment_result = await db.execute(payment_query)
        payment = payment_result.scalar_first()

        if payment and capture_response["status"] == "COMPLETED":
            payment.status = "completed"
            payment.completed_at = datetime.utcnow()

            # Update order
            order_query = select(Order).where(Order.id == payment.order_id)
            order_result = await db.execute(order_query)
            order = order_result.scalar_first()

            if order:
                order.status = "paid"
                order.payment_method = "paypal"

            await db.commit()

        return {"status": "success", "capture_id": capture_response["id"]}

    except Exception as e:
        logger.error(f"PayPal capture failed: {e}")
        raise HTTPException(status_code=500, detail="PayPal capture failed")


# ==================== APPLE PAY INTEGRATION ====================


@router.post("/apple-pay/validate")
async def validate_apple_pay_merchant(validation_url: str, domain_name: str):
    """Validate Apple Pay merchant session"""

    # Validate that the validation_url is an Apple Pay domain
    parsed_url = urllib.parse.urlparse(validation_url)
    hostname = parsed_url.hostname
    scheme = parsed_url.scheme
    allowed_hostnames = {
        "apple-pay-gateway.apple.com",
        "apple-pay-gateway-nc.apple.com",
        "apple-pay-gateway-pr.apple.com",
        "apple-pay-gateway-aus.apple.com",
        "apple-pay-gateway-cert.apple.com",
    }
    if scheme != "https" or not hostname or hostname not in allowed_hostnames:
        raise HTTPException(
            status_code=400,
            detail="Invalid validation_url: must be a valid Apple Pay gateway domain over HTTPS",
        )

    try:
        validation_data = {
            "merchantIdentifier": settings.APPLE_PAY_MERCHANT_ID,
            "domainName": domain_name,
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
        logger.error(f"Apple Pay validation failed: {e}")
        raise HTTPException(status_code=500, detail="Apple Pay validation failed")


@router.post("/apple-pay/payment", response_model=PaymentIntentResponse)
async def process_apple_pay_payment(
    payment_data: ApplePayPaymentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Process Apple Pay payment through Stripe"""

    try:
        # Get order details
        order_query = select(Order).where(
            and_(
                Order.id == payment_data.order_id,
                Order.tenant_id == tenant_id,
                Order.user_id == current_user.id,
            )
        )

        order_result = await db.execute(order_query)
        order = order_result.scalar_first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Process Apple Pay through Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="sar",
            payment_method_data={
                "type": "card",
                "card": {"token": payment_data.payment_token},
            },
            metadata={"order_id": str(order.id), "payment_method": "apple_pay"},
            confirm=True,
            return_url=f"{settings.FRONTEND_URL}/payment/success",
        )

        # Save payment record
        payment = Payment(
            tenant_id=tenant_id,
            order_id=order.id,
            provider="apple_pay",
            provider_payment_id=payment_intent["id"],
            amount=order.total_amount,
            currency="SAR",
            status="pending",
            metadata={
                "apple_pay": True,
                "client_secret": payment_intent["client_secret"],
            },
        )

        db.add(payment)
        await db.commit()

        return PaymentIntentResponse(
            payment_intent_id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            amount=order.total_amount,
            currency="SAR",
            status=payment_intent["status"],
        )

    except Exception as e:
        logger.error(f"Apple Pay payment failed: {e}")
        raise HTTPException(status_code=500, detail="Apple Pay payment failed")


# ==================== STRIPE PRODUCT MANAGEMENT ====================


@router.post("/stripe/products/sync")
async def sync_products_to_stripe(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Sync all products to Stripe catalog for payment links"""

    try:
        # Get all active products
        products_query = select(Product).where(Product.is_active == True)
        products_result = await db.execute(products_query)
        products = products_result.scalars().all()

        synced_products = []
        errors = []

        for product in products:
            try:
                # Create Stripe product
                stripe_product = stripe.Product.create(
                    name=product.name,
                    description=product.description,
                    metadata={
                        "product_id": str(product.id),
                        "category": product.category,
                        "source": "brainsait_store",
                    },
                    images=[product.image_url] if product.image_url else [],
                    url=product.live_demo,
                    active=True,
                )

                # Create price
                stripe_price = stripe.Price.create(
                    product=stripe_product.id,
                    unit_amount=int(product.price * 100),
                    currency="sar",
                    metadata={
                        "pricing_type": "one_time",
                        "includes_source": str(
                            "source_code" in (product.bundle_options or [])
                        ),
                    },
                )

                synced_products.append(
                    {
                        "product_id": product.id,
                        "stripe_product_id": stripe_product.id,
                        "stripe_price_id": stripe_price.id,
                    }
                )

            except Exception as e:
                errors.append({"product_id": product.id, "error": str(e)})

        return {
            "synced_count": len(synced_products),
            "error_count": len(errors),
            "synced_products": synced_products,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Product sync failed: {e}")
        raise HTTPException(status_code=500, detail="Product sync failed")


@router.post("/stripe/payment-link")
async def create_stripe_payment_link(
    link_data: PaymentLinkCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Create Stripe payment link for products"""

    try:
        # Get products
        products_query = select(Product).where(Product.id.in_(link_data.product_ids))
        products_result = await db.execute(products_query)
        products = products_result.scalars().all()

        if not products:
            raise HTTPException(status_code=404, detail="No valid products found")

        # Create line items for each product
        line_items = []
        for product in products:
            # Create or get Stripe price
            stripe_price = stripe.Price.create(
                product_data={
                    "name": product.name,
                    "metadata": {"product_id": str(product.id)},
                },
                unit_amount=int(product.price * 100),
                currency="sar",
            )

            line_items.append({"price": stripe_price.id, "quantity": 1})

        # Create payment link
        payment_link = stripe.PaymentLink.create(
            line_items=line_items,
            metadata=link_data.metadata or {},
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
                    "label": {"type": "text", "custom": "VAT Number (if applicable)"},
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

        return {
            "payment_link_id": payment_link.id,
            "url": payment_link.url,
            "product_count": len(products),
            "total_amount": sum(p.price for p in products),
            "currency": "SAR",
            "active": payment_link.active,
        }

    except Exception as e:
        logger.error(f"Payment link creation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment link creation failed")


async def get_paypal_access_token() -> str:
    """Get PayPal access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token",
                auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
                headers={"Accept": "application/json"},
                data={"grant_type": "client_credentials"},
            )
            response.raise_for_status()
            return response.json()["access_token"]
    except Exception as e:
        logger.error(f"Failed to get PayPal token: {e}")
        raise HTTPException(status_code=500, detail="PayPal authentication failed")


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhooks"""

    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        # Handle payment success
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            await handle_payment_success(
                db,
                background_tasks,
                provider="stripe",
                provider_payment_id=payment_intent["id"],
                metadata=payment_intent["metadata"],
            )

        # Handle payment failure
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            await handle_payment_failure(
                db,
                background_tasks,
                provider="stripe",
                provider_payment_id=payment_intent["id"],
                error=payment_intent.get("last_payment_error", {}),
            )

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Stripe webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@router.post("/webhooks/mada")
async def mada_webhook(
    webhook_data: Dict[str, Any],
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Handle Mada payment webhooks"""

    try:
        # Verify webhook signature (implement Mada-specific verification)
        signature = request.headers.get("x-mada-signature")
        if not verify_mada_signature(webhook_data, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle payment status updates
        if webhook_data["status"] == "completed":
            await handle_payment_success(
                db,
                background_tasks,
                provider="mada",
                provider_payment_id=webhook_data["payment_id"],
                metadata={"reference": webhook_data["reference"]},
            )
        elif webhook_data["status"] == "failed":
            await handle_payment_failure(
                db,
                background_tasks,
                provider="mada",
                provider_payment_id=webhook_data["payment_id"],
                error={"message": webhook_data.get("error_message", "Payment failed")},
            )

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Mada webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@router.post("/webhooks/stc-pay")
async def stc_pay_webhook(
    webhook_data: Dict[str, Any],
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Handle STC Pay webhooks"""

    try:
        # Verify webhook signature
        signature = request.headers.get("x-stc-signature")
        if not verify_stc_signature(webhook_data, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle payment status updates
        if webhook_data["status"] == "paid":
            await handle_payment_success(
                db,
                background_tasks,
                provider="stc_pay",
                provider_payment_id=webhook_data["transaction_id"],
                metadata={"mobile": webhook_data.get("mobile_number")},
            )
        elif webhook_data["status"] == "failed":
            await handle_payment_failure(
                db,
                background_tasks,
                provider="stc_pay",
                provider_payment_id=webhook_data["transaction_id"],
                error={"message": webhook_data.get("failure_reason", "Payment failed")},
            )

        return {"status": "success"}

    except Exception as e:
        logger.error(f"STC Pay webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@router.post("/webhooks/paypal")
async def paypal_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Handle PayPal webhooks"""

    try:
        payload = await request.body()
        webhook_data = json.loads(payload.decode())

        # Verify webhook signature (PayPal specific verification)
        auth_header = request.headers.get("PAYPAL-AUTH-ALGO")
        cert_id = request.headers.get("PAYPAL-CERT-ID")
        signature = request.headers.get("PAYPAL-TRANSMISSION-SIG")
        transmission_id = request.headers.get("PAYPAL-TRANSMISSION-ID")
        timestamp = request.headers.get("PAYPAL-TRANSMISSION-TIME")

        # Handle payment events
        if webhook_data["event_type"] == "CHECKOUT.ORDER.APPROVED":
            order_data = webhook_data["resource"]
            await handle_payment_success(
                db,
                background_tasks,
                provider="paypal",
                provider_payment_id=order_data["id"],
                metadata={"reference": order_data["purchase_units"][0]["custom_id"]},
            )
        elif webhook_data["event_type"] == "PAYMENT.CAPTURE.COMPLETED":
            capture_data = webhook_data["resource"]
            await handle_payment_success(
                db,
                background_tasks,
                provider="paypal",
                provider_payment_id=capture_data["supplementary_data"]["related_ids"][
                    "order_id"
                ],
                metadata={"capture_id": capture_data["id"]},
            )
        elif webhook_data["event_type"] == "PAYMENT.CAPTURE.DENIED":
            capture_data = webhook_data["resource"]
            await handle_payment_failure(
                db,
                background_tasks,
                provider="paypal",
                provider_payment_id=capture_data["supplementary_data"]["related_ids"][
                    "order_id"
                ],
                error={
                    "message": "Payment capture denied",
                    "reason": capture_data.get("status_details", {}),
                },
            )

        return {"status": "success"}

    except Exception as e:
        logger.error(f"PayPal webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")


async def handle_payment_success(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    provider: str,
    provider_payment_id: str,
    metadata: Dict[str, Any],
):
    """Handle successful payment processing"""

    try:
        # Find payment record
        payment_query = select(Payment).where(
            Payment.provider_payment_id == provider_payment_id
        )

        payment_result = await db.execute(payment_query)
        payment = payment_result.scalar_first()

        if not payment:
            logger.error(
                f"Payment not found for {provider} payment {provider_payment_id}"
            )
            return

        # Update payment status
        payment.status = "completed"
        payment.completed_at = datetime.utcnow()

        # Update order status
        order_query = select(Order).where(Order.id == payment.order_id)
        order_result = await db.execute(order_query)
        order = order_result.scalar_first()

        if order:
            order.status = "paid"
            order.payment_method = provider

            # Generate ZATCA compliant invoice
            background_tasks.add_task(generate_zatca_invoice, order.id, payment.id)

            # Send confirmation notifications
            background_tasks.add_task(
                send_payment_confirmation,
                order.customer_email,
                order.id,
                payment.amount,
            )

        await db.commit()
        logger.info(f"Payment {provider_payment_id} completed successfully")

    except Exception as e:
        logger.error(f"Error handling payment success: {e}")
        await db.rollback()


async def handle_payment_failure(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    provider: str,
    provider_payment_id: str,
    error: Dict[str, Any],
):
    """Handle failed payment processing"""

    try:
        # Find payment record
        payment_query = select(Payment).where(
            Payment.provider_payment_id == provider_payment_id
        )

        payment_result = await db.execute(payment_query)
        payment = payment_result.scalar_first()

        if not payment:
            logger.error(
                f"Payment not found for {provider} payment {provider_payment_id}"
            )
            return

        # Update payment status
        payment.status = "failed"
        payment.error_message = json.dumps(error)
        payment.failed_at = datetime.utcnow()

        # Update order status
        order_query = select(Order).where(Order.id == payment.order_id)
        order_result = await db.execute(order_query)
        order = order_result.scalar_first()

        if order:
            order.status = "payment_failed"

            # Send failure notification
            background_tasks.add_task(
                send_payment_failure_notification,
                order.customer_email,
                order.id,
                error.get("message", "Payment failed"),
            )

        await db.commit()
        logger.info(f"Payment {provider_payment_id} marked as failed")

    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")
        await db.rollback()


def verify_mada_signature(payload: Dict[str, Any], signature: str) -> bool:
    """Verify Mada webhook signature"""
    # Implementation depends on Mada's specific signature scheme
    expected_signature = hmac.new(
        settings.MADA_WEBHOOK_SECRET.encode(),
        json.dumps(payload, sort_keys=True).encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


def verify_stc_signature(payload: Dict[str, Any], signature: str) -> bool:
    """Verify STC Pay webhook signature"""
    # Implementation depends on STC Pay's specific signature scheme
    expected_signature = hmac.new(
        settings.STC_PAY_WEBHOOK_SECRET.encode(),
        json.dumps(payload, sort_keys=True).encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


async def generate_zatca_invoice(order_id: UUID, payment_id: UUID):
    """Generate ZATCA compliant invoice"""
    try:
        invoice_data = await zatca_service.generate_invoice(order_id, payment_id)
        logger.info(f"ZATCA invoice generated for order {order_id}")
    except Exception as e:
        logger.error(f"ZATCA invoice generation failed for order {order_id}: {e}")


async def send_payment_confirmation(email: str, order_id: UUID, amount: float):
    """Send payment confirmation email"""
    try:
        await notification_service.send_payment_confirmation(email, order_id, amount)
        logger.info(f"Payment confirmation sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send payment confirmation to {email}: {e}")


async def send_payment_failure_notification(
    email: str, order_id: UUID, error_message: str
):
    """Send payment failure notification"""
    try:
        await notification_service.send_payment_failure(email, order_id, error_message)
        logger.info(f"Payment failure notification sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send payment failure notification to {email}: {e}")


@router.get("/invoices/{order_id}", response_model=InvoiceResponse)
async def get_invoice(
    order_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user=Depends(get_current_user),
):
    """Get ZATCA invoice for order"""

    # Verify order belongs to user
    order_query = select(Order).where(
        and_(
            Order.id == order_id,
            Order.tenant_id == tenant_id,
            Order.user_id == current_user.id,
        )
    )

    order_result = await db.execute(order_query)
    order = order_result.scalar_first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get invoice
    invoice_query = select(Invoice).where(Invoice.order_id == order_id)

    invoice_result = await db.execute(invoice_query)
    invoice = invoice_result.scalar_first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return InvoiceResponse(
        id=invoice.id,
        order_id=order_id,
        invoice_number=invoice.invoice_number,
        zatca_uuid=invoice.zatca_uuid,
        qr_code=invoice.qr_code,
        total_amount=invoice.total_amount,
        tax_amount=invoice.tax_amount,
        status=invoice.status,
        pdf_url=invoice.pdf_url,
        created_at=invoice.created_at,
    )
