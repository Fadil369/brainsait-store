"""
Billing API Router - Subscription and Billing Management

Handles subscription management, billing history, and payment method management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_current_admin_user, get_current_tenant
from app.core.database import get_db
from pydantic import BaseModel, Field

router = APIRouter()


# Billing Schemas
class SubscriptionPlan(BaseModel):
    id: str
    name: str
    name_ar: Optional[str]
    description: str
    description_ar: Optional[str]
    price_monthly: Decimal
    price_yearly: Decimal
    currency: str = "SAR"
    features: List[str]
    features_ar: Optional[List[str]]
    max_users: Optional[int]
    max_products: Optional[int]
    is_active: bool = True


class SubscriptionCreate(BaseModel):
    plan_id: str
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    payment_method_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    plan: SubscriptionPlan
    billing_cycle: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: datetime
    amount: Decimal
    currency: str
    trial_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentMethodBase(BaseModel):
    type: str = Field(..., pattern="^(card|bank_account|digital_wallet)$")
    provider: str = Field(..., pattern="^(stripe|mada|stc_pay|paypal)$")
    is_default: bool = False


class PaymentMethodCreate(PaymentMethodBase):
    token: str  # Payment provider token
    metadata: Dict[str, Any] = {}


class PaymentMethodResponse(PaymentMethodBase):
    id: UUID
    user_id: UUID
    last_four: Optional[str]
    brand: Optional[str]
    expiry_month: Optional[int]
    expiry_year: Optional[int]
    is_expired: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceLineItem(BaseModel):
    description: str
    description_ar: Optional[str]
    quantity: int
    unit_price: Decimal
    total: Decimal


class InvoiceResponse(BaseModel):
    id: UUID
    invoice_number: str
    tenant_id: UUID
    subscription_id: UUID
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    due_date: datetime
    paid_at: Optional[datetime]
    line_items: List[InvoiceLineItem]
    pdf_url: Optional[str]
    zatca_qr_code: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BillingAddress(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    tax_number: Optional[str] = Field(None, pattern=r'^[3][0-9]{14}$')
    street: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="SA", pattern="^[A-Z]{2}$")


# Subscription Management


@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """
    Get available subscription plans
    """
    plans = [
        {
            "id": "starter",
            "name": "Starter Plan",
            "name_ar": "خطة البداية",
            "description": "Perfect for small businesses getting started",
            "description_ar": "مثالية للشركات الصغيرة التي تبدأ رحلتها",
            "price_monthly": Decimal("299.00"),
            "price_yearly": Decimal("2990.00"),  # 10 months price for yearly
            "currency": "SAR",
            "features": [
                "Up to 5 users",
                "100 products",
                "Basic analytics",
                "Email support",
                "Mada payments",
                "ZATCA compliance"
            ],
            "features_ar": [
                "حتى 5 مستخدمين",
                "100 منتج",
                "تحليلات أساسية",
                "دعم عبر البريد الإلكتروني",
                "مدفوعات مدى",
                "امتثال زاتكا"
            ],
            "max_users": 5,
            "max_products": 100,
            "is_active": True
        },
        {
            "id": "professional",
            "name": "Professional Plan",
            "name_ar": "الخطة المهنية",
            "description": "Advanced features for growing businesses",
            "description_ar": "ميزات متقدمة للشركات النامية",
            "price_monthly": Decimal("799.00"),
            "price_yearly": Decimal("7990.00"),
            "currency": "SAR",
            "features": [
                "Up to 25 users",
                "1000 products",
                "Advanced analytics",
                "Priority support",
                "All payment methods",
                "API access",
                "Custom branding"
            ],
            "features_ar": [
                "حتى 25 مستخدم",
                "1000 منتج",
                "تحليلات متقدمة",
                "دعم ذو أولوية",
                "جميع طرق الدفع",
                "وصول للـ API",
                "علامة تجارية مخصصة"
            ],
            "max_users": 25,
            "max_products": 1000,
            "is_active": True
        },
        {
            "id": "enterprise",
            "name": "Enterprise Plan",
            "name_ar": "خطة المؤسسات",
            "description": "Complete solution for large organizations",
            "description_ar": "حل متكامل للمؤسسات الكبيرة",
            "price_monthly": Decimal("1999.00"),
            "price_yearly": Decimal("19990.00"),
            "currency": "SAR",
            "features": [
                "Unlimited users",
                "Unlimited products",
                "Real-time analytics",
                "24/7 dedicated support",
                "All payment methods",
                "Full API access",
                "White-label solution",
                "Custom integrations"
            ],
            "features_ar": [
                "مستخدمين غير محدودين",
                "منتجات غير محدودة",
                "تحليلات في الوقت الفعلي",
                "دعم مخصص 24/7",
                "جميع طرق الدفع",
                "وصول كامل للـ API",
                "حل العلامة البيضاء",
                "تكاملات مخصصة"
            ],
            "max_users": None,
            "max_products": None,
            "is_active": True
        }
    ]
    
    return plans


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get current tenant's subscription
    """
    # Mock subscription data
    now = datetime.now()
    
    return {
        "id": UUID("aaaa1111-bbbb-2222-cccc-333333333333"),
        "tenant_id": tenant_id,
        "plan": {
            "id": "professional",
            "name": "Professional Plan",
            "name_ar": "الخطة المهنية",
            "description": "Advanced features for growing businesses",
            "description_ar": "ميزات متقدمة للشركات النامية",
            "price_monthly": Decimal("799.00"),
            "price_yearly": Decimal("7990.00"),
            "currency": "SAR",
            "features": [
                "Up to 25 users",
                "1000 products",
                "Advanced analytics",
                "Priority support",
                "All payment methods",
                "API access",
                "Custom branding"
            ],
            "features_ar": [
                "حتى 25 مستخدم",
                "1000 منتج",
                "تحليلات متقدمة",
                "دعم ذو أولوية",
                "جميع طرق الدفع",
                "وصول للـ API",
                "علامة تجارية مخصصة"
            ],
            "max_users": 25,
            "max_products": 1000,
            "is_active": True
        },
        "billing_cycle": "monthly",
        "status": "active",
        "current_period_start": now.replace(day=1),
        "current_period_end": (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
        "next_billing_date": (now.replace(day=1) + timedelta(days=32)).replace(day=1),
        "amount": Decimal("799.00"),
        "currency": "SAR",
        "trial_end": None,
        "created_at": datetime(2023, 6, 1),
        "updated_at": now,
    }


@router.post("/subscription", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Create or update subscription (Admin only)
    """
    # Validate plan exists
    valid_plans = ["starter", "professional", "enterprise"]
    if subscription_data.plan_id not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan ID. Must be one of: {', '.join(valid_plans)}"
        )
    
    # In a real implementation, this would:
    # 1. Create subscription in payment provider (Stripe, etc.)
    # 2. Save subscription details in database
    # 3. Update tenant features based on plan
    
    now = datetime.now()
    period_end = now + timedelta(days=30 if subscription_data.billing_cycle == "monthly" else 365)
    
    return {
        "id": UUID("bbbb2222-cccc-3333-dddd-444444444444"),
        "tenant_id": tenant_id,
        "plan": {
            "id": subscription_data.plan_id,
            "name": "Professional Plan",
            "name_ar": "الخطة المهنية",
            "description": "Advanced features for growing businesses",
            "description_ar": "ميزات متقدمة للشركات النامية",
            "price_monthly": Decimal("799.00"),
            "price_yearly": Decimal("7990.00"),
            "currency": "SAR",
            "features": ["Up to 25 users", "1000 products", "Advanced analytics"],
            "features_ar": ["حتى 25 مستخدم", "1000 منتج", "تحليلات متقدمة"],
            "max_users": 25,
            "max_products": 1000,
            "is_active": True
        },
        "billing_cycle": subscription_data.billing_cycle,
        "status": "active",
        "current_period_start": now,
        "current_period_end": period_end,
        "next_billing_date": period_end,
        "amount": Decimal("799.00" if subscription_data.billing_cycle == "monthly" else "7990.00"),
        "currency": "SAR",
        "trial_end": None,
        "created_at": now,
        "updated_at": now,
    }


@router.put("/subscription/cancel")
async def cancel_subscription(
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel current subscription (Admin only)
    """
    # In a real implementation, this would:
    # 1. Cancel subscription in payment provider
    # 2. Update subscription status in database
    # 3. Schedule feature downgrade at period end
    
    return {
        "message": "Subscription cancelled successfully",
        "status": "cancelled",
        "access_until": (datetime.now() + timedelta(days=30)).isoformat(),
    }


# Payment Methods Management


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's saved payment methods
    """
    # Mock payment methods
    return [
        {
            "id": UUID("cccc3333-dddd-4444-eeee-555555555555"),
            "user_id": current_user["id"],
            "type": "card",
            "provider": "mada",
            "is_default": True,
            "last_four": "1234",
            "brand": "mada",
            "expiry_month": 12,
            "expiry_year": 2025,
            "is_expired": False,
            "created_at": datetime(2023, 6, 1),
        },
        {
            "id": UUID("dddd4444-eeee-5555-ffff-666666666666"),
            "user_id": current_user["id"],
            "type": "digital_wallet",
            "provider": "stc_pay",
            "is_default": False,
            "last_four": None,
            "brand": "stc_pay",
            "expiry_month": None,
            "expiry_year": None,
            "is_expired": False,
            "created_at": datetime(2023, 7, 15),
        },
    ]


@router.post("/payment-methods", response_model=PaymentMethodResponse)
async def add_payment_method(
    payment_method_data: PaymentMethodCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add new payment method
    """
    # In a real implementation, this would:
    # 1. Validate the payment method with provider
    # 2. Store the payment method securely
    # 3. Update default if specified
    
    return {
        "id": UUID("eeee5555-ffff-6666-aaaa-777777777777"),
        "user_id": current_user["id"],
        "type": payment_method_data.type,
        "provider": payment_method_data.provider,
        "is_default": payment_method_data.is_default,
        "last_four": "5678",
        "brand": payment_method_data.provider,
        "expiry_month": 6,
        "expiry_year": 2026,
        "is_expired": False,
        "created_at": datetime.now(),
    }


@router.delete("/payment-methods/{payment_method_id}")
async def remove_payment_method(
    payment_method_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove payment method
    """
    # In a real implementation, this would:
    # 1. Verify ownership
    # 2. Remove from payment provider
    # 3. Remove from database
    
    return {"message": "Payment method removed successfully"}


# Billing History and Invoices


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = 20,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get billing invoices for current tenant
    """
    # Mock invoice data
    invoices = [
        {
            "id": UUID("ffff6666-aaaa-7777-bbbb-888888888888"),
            "invoice_number": "INV-2023-001",
            "tenant_id": tenant_id,
            "subscription_id": UUID("aaaa1111-bbbb-2222-cccc-333333333333"),
            "status": "paid",
            "subtotal": Decimal("695.65"),
            "tax_amount": Decimal("104.35"),
            "total_amount": Decimal("800.00"),
            "currency": "SAR",
            "due_date": datetime.now() + timedelta(days=30),
            "paid_at": datetime.now() - timedelta(days=5),
            "line_items": [
                {
                    "description": "Professional Plan - Monthly",
                    "description_ar": "الخطة المهنية - شهرية",
                    "quantity": 1,
                    "unit_price": Decimal("695.65"),
                    "total": Decimal("695.65"),
                }
            ],
            "pdf_url": "/api/v1/billing/invoices/ffff6666-aaaa-7777-bbbb-888888888888/pdf",
            "zatca_qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEA...",
            "created_at": datetime.now() - timedelta(days=10),
        }
    ]
    
    if status:
        invoices = [inv for inv in invoices if inv["status"] == status]
    
    return invoices[:limit]


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get specific invoice
    """
    # Mock invoice lookup
    if str(invoice_id) == "ffff6666-aaaa-7777-bbbb-888888888888":
        return {
            "id": invoice_id,
            "invoice_number": "INV-2023-001",
            "tenant_id": tenant_id,
            "subscription_id": UUID("aaaa1111-bbbb-2222-cccc-333333333333"),
            "status": "paid",
            "subtotal": Decimal("695.65"),
            "tax_amount": Decimal("104.35"),
            "total_amount": Decimal("800.00"),
            "currency": "SAR",
            "due_date": datetime.now() + timedelta(days=30),
            "paid_at": datetime.now() - timedelta(days=5),
            "line_items": [
                {
                    "description": "Professional Plan - Monthly",
                    "description_ar": "الخطة المهنية - شهرية",
                    "quantity": 1,
                    "unit_price": Decimal("695.65"),
                    "total": Decimal("695.65"),
                }
            ],
            "pdf_url": f"/api/v1/billing/invoices/{invoice_id}/pdf",
            "zatca_qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEA...",
            "created_at": datetime.now() - timedelta(days=10),
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Invoice not found"
    )


@router.get("/usage")
async def get_usage_statistics(
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get current usage statistics for billing
    """
    return {
        "tenant_id": tenant_id,
        "current_period": {
            "start": datetime.now().replace(day=1).isoformat(),
            "end": (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).isoformat(),
        },
        "usage": {
            "users": {"current": 12, "limit": 25, "percentage": 48.0},
            "products": {"current": 245, "limit": 1000, "percentage": 24.5},
            "api_calls": {"current": 15640, "limit": 50000, "percentage": 31.3},
            "storage_gb": {"current": 2.4, "limit": 10.0, "percentage": 24.0},
        },
        "plan_limits": {
            "name": "Professional Plan",
            "max_users": 25,
            "max_products": 1000,
            "api_calls_monthly": 50000,
            "storage_gb": 10.0,
        },
    }


# Billing Address Management


@router.get("/address", response_model=BillingAddress)
async def get_billing_address(
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get current billing address
    """
    return {
        "company_name": "BrainSAIT Technology Solutions",
        "tax_number": "300012345600003",
        "street": "King Fahd Road, Building 123, Floor 5",
        "city": "Riyadh",
        "state": "Riyadh Province",
        "postal_code": "12345",
        "country": "SA",
    }


@router.put("/address", response_model=BillingAddress)
async def update_billing_address(
    address_data: BillingAddress,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Update billing address (Admin only)
    """
    # In a real implementation, this would update the billing address in database
    return address_data