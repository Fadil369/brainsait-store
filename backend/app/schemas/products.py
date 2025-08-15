"""
Product API schemas for validation and serialization
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.products import ProductStatus, StockStatus


class ProductStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"


class StockStatusEnum(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    BACKORDER = "backorder"


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: int = Field(default=0)
    image_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_title_ar: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    meta_description_ar: Optional[str] = None
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_title_ar: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    meta_description_ar: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: UUID
    tenant_id: str
    level: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryWithChildren(CategoryResponse):
    children: List["CategoryResponse"] = []


# Brand Schemas
class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(default=True)


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class BrandResponse(BrandBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    short_description: Optional[str] = None
    short_description_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    specifications_ar: Optional[Dict[str, Any]] = None
    category_id: Optional[UUID] = None
    brand_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    tags_ar: Optional[List[str]] = None
    price: float = Field(..., gt=0)
    compare_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    tax_rate: float = Field(default=15.0, ge=0, le=100)
    is_tax_exempt: bool = Field(default=False)
    track_inventory: bool = Field(default=True)
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)
    weight: Optional[float] = Field(None, gt=0)
    length: Optional[float] = Field(None, gt=0)
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    requires_shipping: bool = Field(default=True)
    images: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_title_ar: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    meta_description_ar: Optional[str] = None
    status: ProductStatusEnum = Field(default=ProductStatusEnum.DRAFT)
    is_active: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    is_digital: bool = Field(default=False)

    @validator("compare_price")
    def validate_compare_price(cls, v, values):
        if v is not None and "price" in values and v <= values["price"]:
            raise ValueError("Compare price must be greater than regular price")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    short_description: Optional[str] = None
    short_description_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    specifications_ar: Optional[Dict[str, Any]] = None
    category_id: Optional[UUID] = None
    brand_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    tags_ar: Optional[List[str]] = None
    price: Optional[float] = Field(None, gt=0)
    compare_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    is_tax_exempt: Optional[bool] = None
    track_inventory: Optional[bool] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    weight: Optional[float] = Field(None, gt=0)
    length: Optional[float] = Field(None, gt=0)
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    requires_shipping: Optional[bool] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_title_ar: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    meta_description_ar: Optional[str] = None
    status: Optional[ProductStatusEnum] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_digital: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID
    tenant_id: str
    stock_status: StockStatusEnum
    final_price: float
    is_on_sale: bool
    discount_percentage: Optional[float]
    view_count: int
    purchase_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    # Related objects
    category: Optional[CategoryResponse] = None
    brand: Optional[BrandResponse] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: UUID
    name: str
    name_ar: Optional[str]
    slug: str
    sku: str
    price: float
    compare_price: Optional[float]
    final_price: float
    is_on_sale: bool
    discount_percentage: Optional[float]
    stock_status: StockStatusEnum
    stock_quantity: int
    images: Optional[List[str]]
    is_featured: bool
    status: ProductStatusEnum
    category: Optional[CategoryResponse] = None
    brand: Optional[BrandResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Product Variant Schemas
class ProductVariantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    options: Optional[Dict[str, str]] = None
    options_ar: Optional[Dict[str, str]] = None
    price: Optional[float] = Field(None, gt=0)
    compare_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)


class ProductVariantCreate(ProductVariantBase):
    product_id: UUID


class ProductVariantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    options: Optional[Dict[str, str]] = None
    options_ar: Optional[Dict[str, str]] = None
    price: Optional[float] = Field(None, gt=0)
    compare_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ProductVariantResponse(ProductVariantBase):
    id: UUID
    product_id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product Review Schemas
class ProductReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    images: Optional[List[str]] = None


class ProductReviewCreate(ProductReviewBase):
    product_id: UUID


class ProductReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    images: Optional[List[str]] = None


class ProductReviewResponse(ProductReviewBase):
    id: UUID
    product_id: UUID
    user_id: UUID
    tenant_id: str
    is_approved: bool
    is_verified_purchase: bool
    helpful_count: int
    not_helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    # User information
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None

    class Config:
        from_attributes = True


# Search and Filter Schemas
class ProductFilters(BaseModel):
    category_ids: Optional[List[UUID]] = None
    brand_ids: Optional[List[UUID]] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    in_stock_only: bool = Field(default=False)
    featured_only: bool = Field(default=False)
    status: Optional[ProductStatusEnum] = None
    search: Optional[str] = Field(None, max_length=255)


class ProductSort(str, Enum):
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"
    POPULARITY = "popularity"
    RATING = "rating"


# Pagination
class PaginatedProductsResponse(BaseModel):
    items: List[ProductListResponse]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool
