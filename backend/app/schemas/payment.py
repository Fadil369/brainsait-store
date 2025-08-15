"""
Payment schemas for all supported gateways
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, validator


class PaymentMethod(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    MOYASAR = "moyasar"
    HYPERPAY = "hyperpay"
    MADA = "mada"
    STC_PAY = "stc_pay"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class LicenseType(str, Enum):
    APP_ONLY = "app_only"
    APP_WITH_SOURCE = "app_with_source"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


# ==================== BASIC PAYMENT SCHEMAS ====================


class PaymentRequest(BaseModel):
    payment_method: PaymentMethod
    amount: Decimal = Field(..., gt=0, description="Payment amount in SAR")
    currency: str = Field(default="SAR", description="Payment currency")
    order_id: Optional[str] = None
    customer_email: EmailStr
    customer_name: str
    items: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class PaymentResponse(BaseModel):
    payment_id: str
    status: PaymentStatus
    payment_method: PaymentMethod
    amount: Decimal
    currency: str
    checkout_url: Optional[str] = None
    redirect_url: Optional[str] = None
    client_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


# ==================== STRIPE SCHEMAS ====================


class StripeProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, str]] = None
    url: Optional[str] = None
    active: bool = True


class StripePriceCreate(BaseModel):
    product_id: str
    unit_amount: int = Field(..., gt=0, description="Amount in halalas (cents)")
    currency: str = Field(default="sar")
    recurring: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, str]] = None


class StripeCheckoutRequest(BaseModel):
    price_id: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    mode: str = Field(default="payment", pattern="^(payment|subscription|setup)$")
    success_url: str
    cancel_url: str
    customer_email: Optional[EmailStr] = None
    allow_promotion_codes: bool = True
    billing_address_collection: str = Field(default="required")
    tax_id_collection: Dict[str, bool] = Field(default={"enabled": True})
    metadata: Optional[Dict[str, str]] = None


class StripeSubscriptionCreate(BaseModel):
    customer_id: str
    price_id: str
    trial_period_days: Optional[int] = None
    metadata: Optional[Dict[str, str]] = None


class StripeWebhookEvent(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]
    created: int
    api_version: str


# ==================== PAYPAL SCHEMAS ====================


class PayPalAmount(BaseModel):
    currency_code: str = "SAR"
    value: str


class PayPalItem(BaseModel):
    name: str
    description: Optional[str] = None
    unit_amount: PayPalAmount
    quantity: str = "1"
    category: str = "DIGITAL_GOODS"


class PayPalPurchaseUnit(BaseModel):
    reference_id: str
    amount: PayPalAmount
    description: Optional[str] = None
    custom_id: Optional[str] = None
    items: Optional[List[PayPalItem]] = None


class PayPalPaymentCreate(BaseModel):
    intent: str = "CAPTURE"
    purchase_units: List[PayPalPurchaseUnit]
    application_context: Optional[Dict[str, Any]] = None


class PayPalWebhookEvent(BaseModel):
    id: str
    event_type: str
    resource: Dict[str, Any]
    create_time: str
    event_version: str


# ==================== APPLE PAY SCHEMAS ====================


class ApplePayValidation(BaseModel):
    validation_url: str
    domain_name: str


class ApplePayPaymentData(BaseModel):
    version: str
    data: str
    signature: str
    header: Dict[str, Any]


class ApplePayPaymentToken(BaseModel):
    payment_data: ApplePayPaymentData
    payment_method: Dict[str, Any]
    transaction_identifier: str


class ApplePayPaymentRequest(BaseModel):
    payment_token: ApplePayPaymentToken
    order_id: str
    amount: Decimal
    currency: str = "SAR"


# ==================== SAUDI LOCAL GATEWAY SCHEMAS ====================


class MoyasarPaymentCreate(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in halalas")
    currency: str = "SAR"
    description: str
    source: Optional[Dict[str, Any]] = None
    callback_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MoyasarWebhookEvent(BaseModel):
    type: str
    data: Dict[str, Any]
    created_at: str


class HyperPayCheckoutCreate(BaseModel):
    entity_id: str
    amount: str
    currency: str = "SAR"
    payment_type: str = "DB"
    merchant_transaction_id: str
    customer_email: Optional[EmailStr] = None
    billing_country: str = "SA"


class HyperPayWebhookEvent(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: str


class STCPayRequest(BaseModel):
    amount: Decimal
    currency: str = "SAR"
    mobile_number: str = Field(..., pattern="^(\\+966|966|0)?5[0-9]{8}$")
    reference_id: str
    description: str


class MadaPaymentRequest(BaseModel):
    amount: Decimal
    currency: str = "SAR"
    card_number: str = Field(..., min_length=16, max_length=19)
    expiry_month: str = Field(..., pattern="^(0[1-9]|1[0-2])$")
    expiry_year: str = Field(..., pattern="^20[2-9][0-9]$")
    cvv: str = Field(..., min_length=3, max_length=4)
    cardholder_name: str


# ==================== ORDER AND INVOICE SCHEMAS ====================


class OrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    license_type: LicenseType
    quantity: int = Field(default=1, ge=1)
    price: Decimal = Field(..., gt=0)
    includes_source_code: bool = False
    support_months: int = Field(default=12, ge=0, le=60)


class OrderCreate(BaseModel):
    customer_email: EmailStr
    customer_name: str
    company_name: Optional[str] = None
    vat_number: Optional[str] = None
    billing_address: Optional[Dict[str, str]] = None
    items: List[OrderItemCreate] = Field(..., min_items=1)
    discount_code: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    payment_method: Optional[PaymentMethod] = None
    customer_email: EmailStr
    customer_name: str
    company_name: Optional[str] = None
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    items: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvoiceGenerate(BaseModel):
    order_id: int
    include_vat: bool = True
    language: str = Field(default="en", pattern="^(en|ar)$")
    template: str = Field(default="standard")


class PaymentLinkCreate(BaseModel):
    product_ids: List[int] = Field(..., min_items=1)
    customer_email: Optional[EmailStr] = None
    expires_at: Optional[datetime] = None
    allow_promotion_codes: bool = True
    collect_billing_address: bool = True
    collect_tax_id: bool = True
    custom_fields: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, str]] = None


class PaymentLinkResponse(BaseModel):
    id: str
    url: str
    product_count: int
    total_amount: Decimal
    currency: str
    active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime


# ==================== WEBHOOK SCHEMAS ====================


class WebhookEvent(BaseModel):
    id: str
    type: str
    gateway: PaymentMethod
    data: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None
    verified: bool = False


class WebhookResponse(BaseModel):
    status: str
    message: Optional[str] = None
    order_id: Optional[str] = None
    payment_id: Optional[str] = None


# ==================== ANALYTICS SCHEMAS ====================


class PaymentAnalytics(BaseModel):
    total_revenue: Decimal
    payment_count: int
    average_order_value: Decimal
    conversion_rate: float
    gateway_breakdown: Dict[str, Dict[str, Union[int, Decimal]]]
    period_start: datetime
    period_end: datetime


class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[Decimal] = None
    reason: str
    metadata: Optional[Dict[str, str]] = None


class RefundResponse(BaseModel):
    refund_id: str
    status: str
    amount: Decimal
    currency: str
    reason: str
    created_at: datetime
