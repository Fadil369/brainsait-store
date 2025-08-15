"""
Order and cart API schemas for validation and serialization
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.orders import OrderStatus, PaymentStatus, ShippingStatus


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    RETURNED = "returned"


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class ShippingStatusEnum(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


# Address Schemas
class AddressBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company: Optional[str] = Field(None, max_length=100)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=2, max_length=2)  # ISO country code
    phone: Optional[str] = Field(None, max_length=20)


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    pass


# Cart Item Schemas
class CartItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: int = Field(..., gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: int
    unit_price: float
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Product information
    product_name: str
    product_name_ar: Optional[str] = None
    product_sku: str
    product_image: Optional[str] = None
    product_slug: str

    # Variant information (if applicable)
    variant_name: Optional[str] = None
    variant_options: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    items: List[CartItemResponse]
    subtotal: float
    tax_amount: float
    total_amount: float
    item_count: int
    currency: str = "SAR"


# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    variant_id: Optional[UUID] = None
    product_name: str
    product_name_ar: Optional[str] = None
    product_sku: str
    variant_name: Optional[str] = None
    variant_options: Optional[Dict[str, str]] = None
    quantity: int
    unit_price: float
    total_price: float
    tax_rate: float
    tax_amount: float
    product_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Order Schemas
class OrderBase(BaseModel):
    customer_email: str = Field(..., max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_name: str = Field(..., max_length=255)
    billing_address: AddressCreate
    shipping_address: AddressCreate
    shipping_method: Optional[str] = Field(None, max_length=100)
    customer_notes: Optional[str] = None
    coupon_code: Optional[str] = Field(None, max_length=50)


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    payment_status: Optional[PaymentStatusEnum] = None
    shipping_status: Optional[ShippingStatusEnum] = None
    shipping_method: Optional[str] = Field(None, max_length=100)
    tracking_number: Optional[str] = Field(None, max_length=255)
    tracking_url: Optional[str] = Field(None, max_length=500)
    admin_notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    status: OrderStatusEnum
    payment_status: PaymentStatusEnum
    shipping_status: ShippingStatusEnum
    customer_email: str
    customer_phone: Optional[str] = None
    customer_name: str
    billing_address: Dict[str, Any]
    shipping_address: Dict[str, Any]
    shipping_method: Optional[str] = None
    shipping_cost: float
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    currency: str
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    coupon_code: Optional[str] = None
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # Related data
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: UUID
    order_number: str
    status: OrderStatusEnum
    payment_status: PaymentStatusEnum
    shipping_status: ShippingStatusEnum
    customer_name: str
    total_amount: float
    currency: str
    item_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Order Status History
class OrderStatusHistoryResponse(BaseModel):
    id: UUID
    from_status: Optional[str] = None
    to_status: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Coupon Schemas
class CouponBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    discount_type: str = Field(..., pattern="^(percentage|fixed|free_shipping)$")
    discount_value: float = Field(..., gt=0)
    minimum_amount: Optional[float] = Field(None, gt=0)
    maximum_discount: Optional[float] = Field(None, gt=0)
    usage_limit: Optional[int] = Field(None, gt=0)
    usage_limit_per_user: Optional[int] = Field(None, gt=0)
    valid_from: datetime
    valid_until: Optional[datetime] = None
    applicable_products: Optional[List[UUID]] = None
    applicable_categories: Optional[List[UUID]] = None
    is_active: bool = Field(default=True)


class CouponCreate(CouponBase):
    pass


class CouponUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    discount_value: Optional[float] = Field(None, gt=0)
    minimum_amount: Optional[float] = Field(None, gt=0)
    maximum_discount: Optional[float] = Field(None, gt=0)
    usage_limit: Optional[int] = Field(None, gt=0)
    usage_limit_per_user: Optional[int] = Field(None, gt=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    applicable_products: Optional[List[UUID]] = None
    applicable_categories: Optional[List[UUID]] = None
    is_active: Optional[bool] = None


class CouponResponse(CouponBase):
    id: UUID
    tenant_id: str
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponValidationRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    subtotal: float = Field(..., gt=0)
    items: List[UUID] = []  # Product IDs in cart


class CouponValidationResponse(BaseModel):
    valid: bool
    discount_amount: float = 0
    message: str
    message_ar: Optional[str] = None


# Checkout Schemas
class CheckoutRequest(BaseModel):
    billing_address: AddressCreate
    shipping_address: AddressCreate
    shipping_method: Optional[str] = Field(None, max_length=100)
    payment_method: str = Field(..., max_length=50)
    customer_notes: Optional[str] = None
    coupon_code: Optional[str] = Field(None, max_length=50)
    save_payment_method: bool = Field(default=False)


class CheckoutResponse(BaseModel):
    order_id: UUID
    order_number: str
    total_amount: float
    currency: str
    payment_required: bool
    payment_intent_id: Optional[str] = None  # For Stripe
    payment_url: Optional[str] = None  # For other gateways
    client_secret: Optional[str] = None  # For Stripe

    class Config:
        from_attributes = True


# Pagination
class PaginatedOrdersResponse(BaseModel):
    items: List[OrderListResponse]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool
