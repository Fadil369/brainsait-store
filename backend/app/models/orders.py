"""
Order and cart models for e-commerce functionality
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Enum, 
    Numeric, ForeignKey, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    RETURNED = "returned"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class ShippingStatus(str, enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.id'), nullable=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Cart Details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Price at time of adding to cart
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("ProductVariant")
    
    # Indexes
    __table_args__ = (
        Index('idx_cart_items_user', 'user_id'),
        Index('idx_cart_items_product', 'product_id'),
        Index('idx_cart_items_tenant', 'tenant_id'),
    )
    
    @property
    def total_price(self) -> float:
        return float(self.unit_price) * self.quantity
    
    def __repr__(self):
        return f"<CartItem {self.quantity} x {self.product.name}>"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Order Status
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    shipping_status = Column(Enum(ShippingStatus), nullable=False, default=ShippingStatus.PENDING)
    
    # Customer Information
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    customer_name = Column(String(255), nullable=False)
    
    # Billing Address
    billing_address = Column(JSON, nullable=False)
    
    # Shipping Address
    shipping_address = Column(JSON, nullable=False)
    shipping_method = Column(String(100), nullable=True)
    shipping_cost = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Pricing
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Currency
    currency = Column(String(3), nullable=False, default="SAR")
    
    # Payment
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    
    # Coupon/Discount
    coupon_code = Column(String(50), nullable=True)
    
    # Notes
    customer_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Tracking
    tracking_number = Column(String(255), nullable=True)
    tracking_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")
    invoices = relationship("Invoice", back_populates="order")
    status_history = relationship("OrderStatusHistory", back_populates="order")
    
    # Indexes
    __table_args__ = (
        Index('idx_orders_user', 'user_id'),
        Index('idx_orders_tenant', 'tenant_id'),
        Index('idx_orders_status', 'status'),
        Index('idx_orders_payment_status', 'payment_status'),
        Index('idx_orders_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.id'), nullable=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Product Information (snapshot at time of order)
    product_name = Column(String(255), nullable=False)
    product_name_ar = Column(String(255), nullable=True)
    product_sku = Column(String(100), nullable=False)
    variant_name = Column(String(255), nullable=True)
    variant_options = Column(JSON, nullable=True)
    
    # Pricing
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False)
    
    # Product Image (for invoice/receipt)
    product_image = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant")
    
    # Indexes
    __table_args__ = (
        Index('idx_order_items_order', 'order_id'),
        Index('idx_order_items_product', 'product_id'),
        Index('idx_order_items_tenant', 'tenant_id'),
    )
    
    def __repr__(self):
        return f"<OrderItem {self.quantity} x {self.product_name}>"


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Status Information
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    comment = Column(Text, nullable=True)
    
    # User who made the change
    changed_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="status_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_order_status_history_order', 'order_id'),
        Index('idx_order_status_history_tenant', 'tenant_id'),
    )
    
    def __repr__(self):
        return f"<OrderStatusHistory {self.from_status} -> {self.to_status}>"


class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Coupon Information
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Discount Configuration
    discount_type = Column(String(20), nullable=False)  # percentage, fixed, free_shipping
    discount_value = Column(Numeric(10, 2), nullable=False)
    minimum_amount = Column(Numeric(10, 2), nullable=True)
    maximum_discount = Column(Numeric(10, 2), nullable=True)
    
    # Usage Limits
    usage_limit = Column(Integer, nullable=True)  # Total usage limit
    usage_limit_per_user = Column(Integer, nullable=True)  # Per user limit
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Conditions
    applicable_products = Column(JSON, nullable=True)  # Product IDs
    applicable_categories = Column(JSON, nullable=True)  # Category IDs
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_coupons_tenant_code', 'tenant_id', 'code', unique=True),
        Index('idx_coupons_active', 'is_active'),
        Index('idx_coupons_validity', 'valid_from', 'valid_until'),
    )
    
    def __repr__(self):
        return f"<Coupon {self.code}>"