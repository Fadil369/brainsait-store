"""
Payment API schemas for validation and serialization
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.payments import PaymentMethod, PaymentStatus, RefundStatus


class PaymentMethodEnum(str, Enum):
    STRIPE = "stripe"
    MADA = "mada"
    STC_PAY = "stc_pay"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"
    WALLET = "wallet"


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class RefundStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSED = "processed"
    REJECTED = "rejected"


# Payment Intent Schemas
class PaymentIntentCreate(BaseModel):
    order_id: UUID
    payment_method: PaymentMethodEnum
    return_url: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class PaymentIntentResponse(BaseModel):
    id: str
    client_secret: Optional[str] = None
    payment_url: Optional[str] = None
    status: str
    amount: float
    currency: str
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Stripe Payment Schemas
class StripePaymentMethodCreate(BaseModel):
    payment_method_id: str = Field(..., min_length=1)
    save_payment_method: bool = Field(default=False)


class StripePaymentConfirm(BaseModel):
    payment_intent_id: str = Field(..., min_length=1)
    payment_method_id: Optional[str] = None


class StripeWebhookPayload(BaseModel):
    id: str
    object: str
    type: str
    data: Dict[str, Any]
    created: int
    livemode: bool


# Mada Payment Schemas
class MadaPaymentCreate(BaseModel):
    card_number: str = Field(..., pattern=r"^\d{16}$")
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2023)
    cvv: str = Field(..., pattern=r"^\d{3,4}$")
    cardholder_name: str = Field(..., min_length=1, max_length=100)


class MadaPaymentResponse(BaseModel):
    transaction_id: str
    reference_number: str
    status: str
    auth_code: Optional[str] = None
    response_code: str
    response_message: str


# STC Pay Schemas
class STCPaymentCreate(BaseModel):
    phone_number: str = Field(..., pattern=r"^(05|5)\d{8}$")  # Saudi mobile format
    otp: Optional[str] = Field(None, pattern=r"^\d{4,6}$")


class STCPaymentResponse(BaseModel):
    transaction_id: str
    reference: str
    status: str
    approval_code: Optional[str] = None
    payment_url: Optional[str] = None


# Bank Transfer Schemas
class BankTransferCreate(BaseModel):
    bank_name: str = Field(..., min_length=1, max_length=100)
    account_holder_name: str = Field(..., min_length=1, max_length=100)
    reference_number: str = Field(..., min_length=1, max_length=255)
    transfer_date: datetime
    notes: Optional[str] = Field(None, max_length=500)


# Payment Response Schemas
class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="SAR", max_length=3)
    payment_method: PaymentMethodEnum
    metadata: Optional[Dict[str, Any]] = None


class PaymentCreate(PaymentBase):
    order_id: UUID


class PaymentResponse(PaymentBase):
    id: UUID
    order_id: UUID
    status: PaymentStatusEnum
    gateway_transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Payment Refund Schemas
class PaymentRefundCreate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)  # If None, refund full amount
    reason: str = Field(..., min_length=1, max_length=500)


class PaymentRefundResponse(BaseModel):
    id: UUID
    payment_id: UUID
    amount: float
    reason: str
    status: RefundStatusEnum
    gateway_refund_id: Optional[str] = None
    processed_by_user_id: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# User Payment Method Schemas
class UserPaymentMethodBase(BaseModel):
    payment_method: PaymentMethodEnum
    is_default: bool = Field(default=False)


class UserPaymentMethodCreate(UserPaymentMethodBase):
    # Stripe
    stripe_payment_method_id: Optional[str] = None

    # Card info (for display)
    card_last4: Optional[str] = Field(None, pattern=r"^\d{4}$")
    card_brand: Optional[str] = Field(None, max_length=20)
    card_exp_month: Optional[int] = Field(None, ge=1, le=12)
    card_exp_year: Optional[int] = Field(None, ge=2023)

    # STC Pay
    stc_pay_phone: Optional[str] = Field(None, pattern=r"^(05|5)\d{8}$")

    # Bank Transfer
    bank_account_info: Optional[Dict[str, Any]] = None


class UserPaymentMethodResponse(UserPaymentMethodBase):
    id: UUID
    user_id: UUID
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    stc_pay_phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Payment Webhook Schemas
class PaymentWebhookCreate(BaseModel):
    provider: str = Field(..., max_length=50)
    event_type: str = Field(..., max_length=100)
    webhook_id: Optional[str] = Field(None, max_length=255)
    payload: Dict[str, Any]
    headers: Optional[Dict[str, str]] = None


class PaymentWebhookResponse(BaseModel):
    id: UUID
    provider: str
    event_type: str
    webhook_id: Optional[str] = None
    processed: bool
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Summary Schemas
class PaymentMethodInfo(BaseModel):
    method: PaymentMethodEnum
    name: str
    name_ar: str
    description: str
    description_ar: str
    is_available: bool
    fees: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None


class PaymentMethodsResponse(BaseModel):
    methods: List[PaymentMethodInfo]
    default_currency: str = "SAR"
    supported_currencies: List[str] = ["SAR", "USD"]


# Transaction Schemas
class TransactionSummary(BaseModel):
    total_amount: float
    successful_payments: int
    failed_payments: int
    pending_payments: int
    refunded_amount: float
    currency: str = "SAR"


class PaymentAnalytics(BaseModel):
    period: str  # "daily", "weekly", "monthly"
    transactions: List[Dict[str, Any]]
    summary: TransactionSummary


# Additional schemas needed by the payments API
class ApplePayPaymentCreate(BaseModel):
    order_id: UUID
    payment_method_id: str
    return_url: Optional[str] = None


class PayPalPaymentCreate(BaseModel):
    order_id: UUID
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None


class PaymentLinkCreate(BaseModel):
    product_ids: List[int]
    metadata: Optional[Dict[str, Any]] = None
    return_url: Optional[str] = None


class PaymentMethodResponse(BaseModel):
    id: str
    name: str
    name_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
    enabled: bool
    logo_url: Optional[str] = None
    supported_currencies: List[str]
    fees: Dict[str, float]


class InvoiceResponse(BaseModel):
    id: UUID
    order_id: UUID
    invoice_number: str
    zatca_uuid: Optional[str] = None
    qr_code: Optional[str] = None
    total_amount: float
    tax_amount: float
    status: str
    pdf_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentWebhook(BaseModel):
    provider: str
    event_type: str
    data: Dict[str, Any]
    signature: Optional[str] = None


class StripeProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "SAR"
    metadata: Optional[Dict[str, Any]] = None
