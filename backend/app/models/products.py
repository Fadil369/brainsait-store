"""
Product models for e-commerce functionality
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"


class StockStatus(str, enum.Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    BACKORDER = "backorder"


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Basic Information
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)

    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=0)

    # Media
    image_url = Column(String(500), nullable=True)
    icon = Column(String(100), nullable=True)

    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_title_ar = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_description_ar = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
    products = relationship("Product", back_populates="category")

    # Indexes
    __table_args__ = (
        Index("idx_categories_tenant_slug", "tenant_id", "slug", unique=True),
        Index("idx_categories_parent", "parent_id"),
        Index("idx_categories_status", "is_active"),
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Brand(Base):
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Basic Information
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)

    # Media
    logo_url = Column(String(500), nullable=True)

    # Contact Information
    website = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="brand")

    # Indexes
    __table_args__ = (
        Index("idx_brands_tenant_slug", "tenant_id", "slug", unique=True),
        Index("idx_brands_status", "is_active"),
    )

    def __repr__(self):
        return f"<Brand {self.name}>"


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Basic Information
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    slug = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=False, index=True)
    barcode = Column(String(100), nullable=True, index=True)

    # Description
    short_description = Column(Text, nullable=True)
    short_description_ar = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    specifications = Column(JSON, nullable=True)  # Key-value pairs
    specifications_ar = Column(JSON, nullable=True)  # Key-value pairs in Arabic

    # Categorization
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    tags_ar = Column(ARRAY(String), nullable=True)

    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    compare_price = Column(
        Numeric(10, 2), nullable=True
    )  # Original price for discount display
    cost_price = Column(Numeric(10, 2), nullable=True)  # Cost for margin calculation

    # Tax
    tax_rate = Column(
        Numeric(5, 2), nullable=False, default=15.00
    )  # 15% VAT for Saudi Arabia
    is_tax_exempt = Column(Boolean, nullable=False, default=False)

    # Inventory
    track_inventory = Column(Boolean, nullable=False, default=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=5)
    stock_status = Column(
        Enum(StockStatus), nullable=False, default=StockStatus.IN_STOCK
    )

    # Shipping
    weight = Column(Numeric(8, 2), nullable=True)  # in kg
    length = Column(Numeric(8, 2), nullable=True)  # in cm
    width = Column(Numeric(8, 2), nullable=True)  # in cm
    height = Column(Numeric(8, 2), nullable=True)  # in cm
    requires_shipping = Column(Boolean, nullable=False, default=True)

    # Media
    images = Column(JSON, nullable=True)  # Array of image URLs
    video_url = Column(String(500), nullable=True)

    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_title_ar = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_description_ar = Column(Text, nullable=True)

    # Status and Visibility
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.DRAFT)
    is_active = Column(Boolean, nullable=False, default=False)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_digital = Column(Boolean, nullable=False, default=False)

    # Analytics
    view_count = Column(Integer, nullable=False, default=0)
    purchase_count = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

    # Indexes
    __table_args__ = (
        Index("idx_products_tenant_slug", "tenant_id", "slug", unique=True),
        Index("idx_products_tenant_sku", "tenant_id", "sku", unique=True),
        Index("idx_products_category", "category_id"),
        Index("idx_products_brand", "brand_id"),
        Index("idx_products_status", "status"),
        Index("idx_products_featured", "is_featured"),
        Index("idx_products_barcode", "barcode"),
    )

    @property
    def final_price(self) -> float:
        """Calculate final price including tax"""
        if self.is_tax_exempt:
            return float(self.price)
        return float(self.price) * (1 + float(self.tax_rate) / 100)

    @property
    def is_on_sale(self) -> bool:
        """Check if product is on sale"""
        return self.compare_price and self.compare_price > self.price

    @property
    def discount_percentage(self) -> Optional[float]:
        """Calculate discount percentage"""
        if not self.is_on_sale:
            return None
        return (
            (float(self.compare_price) - float(self.price)) / float(self.compare_price)
        ) * 100

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Variant Information
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    sku = Column(String(100), nullable=False, index=True)
    barcode = Column(String(100), nullable=True, index=True)

    # Variant Options (e.g., size, color)
    options = Column(JSON, nullable=True)  # {"size": "L", "color": "Red"}
    options_ar = Column(JSON, nullable=True)  # {"size": "كبير", "color": "أحمر"}

    # Pricing
    price = Column(Numeric(10, 2), nullable=True)  # If null, use product price
    compare_price = Column(Numeric(10, 2), nullable=True)
    cost_price = Column(Numeric(10, 2), nullable=True)

    # Inventory
    stock_quantity = Column(Integer, nullable=False, default=0)

    # Media
    image_url = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="variants")

    # Indexes
    __table_args__ = (
        Index("idx_product_variants_tenant_sku", "tenant_id", "sku", unique=True),
        Index("idx_product_variants_product", "product_id"),
        Index("idx_product_variants_barcode", "barcode"),
    )

    def __repr__(self):
        return f"<ProductVariant {self.name}>"


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Review Content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)

    # Review Images
    images = Column(JSON, nullable=True)  # Array of image URLs

    # Status
    is_approved = Column(Boolean, nullable=False, default=False)
    is_verified_purchase = Column(Boolean, nullable=False, default=False)

    # Helpfulness
    helpful_count = Column(Integer, nullable=False, default=0)
    not_helpful_count = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    # Indexes
    __table_args__ = (
        Index("idx_product_reviews_product", "product_id"),
        Index("idx_product_reviews_user", "user_id"),
        Index("idx_product_reviews_tenant", "tenant_id"),
        Index("idx_product_reviews_approved", "is_approved"),
    )

    def __repr__(self):
        return f"<ProductReview {self.rating} stars>"
