"""
Store-related Pydantic schemas for API validation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, validator


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    description: str = Field(..., min_length=10, max_length=2000)
    description_ar: Optional[str] = Field(None, max_length=2000)
    price_sar: Decimal = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="active", pattern="^(active|inactive|draft)$")
    features: List[str] = Field(default_factory=list)
    features_ar: Optional[List[str]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    description_ar: Optional[str] = Field(None, max_length=2000)
    price_sar: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(None, pattern="^(active|inactive|draft)$")
    features: Optional[List[str]] = None
    features_ar: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductResponse(ProductBase):
    """Schema for product API responses"""
    id: int
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductSearchResponse(BaseModel):
    """Schema for paginated product search results"""
    products: List[ProductResponse]
    pagination: Dict[str, Any]
    filters: Dict[str, Any]


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    name_ar: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    description_ar: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryResponse(CategoryBase):
    """Schema for category API responses"""
    id: int
    tenant_id: UUID
    product_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Cart Schemas
class CartItemBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)


class CartItemCreate(CartItemBase):
    """Schema for adding items to cart"""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart items"""
    quantity: int = Field(..., gt=0, le=100)


class CartItemResponse(CartItemBase):
    """Schema for cart item responses"""
    id: int
    unit_price: Decimal
    total_price: Decimal
    product_name: str
    product_name_ar: Optional[str]

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema for cart responses"""
    id: int
    user_id: UUID
    tenant_id: UUID
    items: List[CartItemResponse]
    total_amount: Decimal
    item_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order Schemas
class CustomerInfo(BaseModel):
    """Customer information for orders"""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str = Field(..., pattern=r'^\+966[5][0-9]{8}$')
    company: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, pattern=r'^[3][0-9]{14}$')


class Address(BaseModel):
    """Address information"""
    street: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="SA", pattern="^[A-Z]{2}$")


class OrderBase(BaseModel):
    customer_info: CustomerInfo
    shipping_address: Address
    billing_address: Optional[Address] = None
    payment_method: str = Field(..., pattern="^(stripe|mada|stc_pay|paypal|apple_pay)$")
    notes: Optional[str] = Field(None, max_length=500)
    preferred_language: str = Field(default="en", pattern="^(en|ar)$")

    @validator('billing_address', always=True)
    def set_billing_address(cls, v, values):
        return v or values.get('shipping_address')


class OrderCreate(OrderBase):
    """Schema for creating new orders"""
    pass


class OrderItemResponse(BaseModel):
    """Schema for order item responses"""
    id: int
    product_id: int
    product_name: str
    product_name_ar: Optional[str]
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True


class OrderResponse(OrderBase):
    """Schema for order responses"""
    id: int
    order_number: str
    tenant_id: UUID
    user_id: UUID
    status: str
    items: List[OrderItemResponse]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str = "SAR"
    payment_status: str
    payment_id: Optional[str]
    zatca_invoice_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Search and Filter Schemas
class ProductFilter(BaseModel):
    """Schema for product filtering parameters"""
    category: Optional[str] = None
    search: Optional[str] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    status: str = Field(default="active")
    tags: Optional[List[str]] = None

    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and values.get('min_price') is not None:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit