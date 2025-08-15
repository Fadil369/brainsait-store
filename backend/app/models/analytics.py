"""
Analytics models for tracking user behavior and business metrics
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class EventType(str, enum.Enum):
    """Analytics event types"""
    PAGE_VIEW = "page_view"
    PRODUCT_VIEW = "product_view"
    PRODUCT_SEARCH = "product_search"
    CART_ADD = "cart_add"
    CART_REMOVE = "cart_remove"
    CHECKOUT_START = "checkout_start"
    CHECKOUT_COMPLETE = "checkout_complete"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    USER_REGISTER = "user_register"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    CUSTOM = "custom"


class AnalyticsEvent(Base):
    """Store individual analytics events"""
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)

    # Event Information
    event_type = Column(Enum(EventType), nullable=False, index=True)
    event_name = Column(String(255), nullable=False, index=True)
    event_data = Column(JSON, nullable=True)  # Flexible data storage

    # Context Information
    page_url = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    country = Column(String(2), nullable=True)  # ISO country code
    city = Column(String(100), nullable=True)

    # Device Information
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # Business Metrics
    revenue = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), nullable=True, default="SAR")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", backref="analytics_events")

    # Indexes
    __table_args__ = (
        Index("idx_analytics_tenant_type", "tenant_id", "event_type"),
        Index("idx_analytics_tenant_date", "tenant_id", "created_at"),
        Index("idx_analytics_user_date", "user_id", "created_at"),
        Index("idx_analytics_session", "session_id"),
        Index("idx_analytics_revenue", "revenue"),
    )

    def __repr__(self):
        return f"<AnalyticsEvent {self.event_name}>"


class ProductAnalytics(Base):
    """Aggregated product analytics"""
    __tablename__ = "product_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)

    # Date for aggregation
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Metrics
    views = Column(Integer, nullable=False, default=0)
    cart_adds = Column(Integer, nullable=False, default=0)
    purchases = Column(Integer, nullable=False, default=0)
    revenue = Column(Numeric(10, 2), nullable=False, default=0)
    search_impressions = Column(Integer, nullable=False, default=0)
    search_clicks = Column(Integer, nullable=False, default=0)

    # Conversion rates (calculated)
    view_to_cart_rate = Column(Numeric(5, 4), nullable=True)  # cart_adds / views
    cart_to_purchase_rate = Column(Numeric(5, 4), nullable=True)  # purchases / cart_adds
    search_ctr = Column(Numeric(5, 4), nullable=True)  # search_clicks / search_impressions

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", backref="analytics")

    # Indexes
    __table_args__ = (
        Index("idx_product_analytics_tenant_date", "tenant_id", "date"),
        Index("idx_product_analytics_product_date", "product_id", "date"),
        Index("idx_product_analytics_revenue", "revenue"),
        Index("idx_product_analytics_views", "views"),
        # Unique constraint on product and date
        Index("idx_product_analytics_unique", "product_id", "date", unique=True),
    )

    def __repr__(self):
        return f"<ProductAnalytics {self.product_id} {self.date}>"


class UserBehaviorAnalytics(Base):
    """User behavior analytics and segmentation"""
    __tablename__ = "user_behavior_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Date for aggregation
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Session metrics
    sessions = Column(Integer, nullable=False, default=0)
    total_session_duration = Column(Integer, nullable=False, default=0)  # in seconds
    avg_session_duration = Column(Integer, nullable=False, default=0)  # in seconds
    page_views = Column(Integer, nullable=False, default=0)
    bounce_rate = Column(Numeric(5, 4), nullable=True)

    # E-commerce metrics
    cart_items_added = Column(Integer, nullable=False, default=0)
    orders_placed = Column(Integer, nullable=False, default=0)
    total_spent = Column(Numeric(10, 2), nullable=False, default=0)
    products_viewed = Column(Integer, nullable=False, default=0)
    categories_explored = Column(Integer, nullable=False, default=0)

    # Engagement metrics
    searches_performed = Column(Integer, nullable=False, default=0)
    reviews_written = Column(Integer, nullable=False, default=0)
    social_shares = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="behavior_analytics")

    # Indexes
    __table_args__ = (
        Index("idx_user_behavior_tenant_date", "tenant_id", "date"),
        Index("idx_user_behavior_user_date", "user_id", "date"),
        Index("idx_user_behavior_spent", "total_spent"),
        # Unique constraint on user and date
        Index("idx_user_behavior_unique", "user_id", "date", unique=True),
    )

    def __repr__(self):
        return f"<UserBehaviorAnalytics {self.user_id} {self.date}>"


class BusinessMetrics(Base):
    """Daily business metrics aggregation"""
    __tablename__ = "business_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Date for aggregation
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Revenue metrics
    total_revenue = Column(Numeric(10, 2), nullable=False, default=0)
    total_orders = Column(Integer, nullable=False, default=0)
    avg_order_value = Column(Numeric(10, 2), nullable=False, default=0)
    total_customers = Column(Integer, nullable=False, default=0)
    new_customers = Column(Integer, nullable=False, default=0)

    # Traffic metrics
    total_visitors = Column(Integer, nullable=False, default=0)
    unique_visitors = Column(Integer, nullable=False, default=0)
    page_views = Column(Integer, nullable=False, default=0)
    bounce_rate = Column(Numeric(5, 4), nullable=True)

    # Conversion metrics
    conversion_rate = Column(Numeric(5, 4), nullable=True)  # orders / visitors
    cart_abandonment_rate = Column(Numeric(5, 4), nullable=True)

    # Product metrics
    products_sold = Column(Integer, nullable=False, default=0)
    top_selling_category = Column(String(255), nullable=True)
    inventory_turnover = Column(Numeric(10, 2), nullable=True)

    # Customer metrics
    customer_lifetime_value = Column(Numeric(10, 2), nullable=True)
    customer_acquisition_cost = Column(Numeric(10, 2), nullable=True)
    repeat_purchase_rate = Column(Numeric(5, 4), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_business_metrics_tenant_date", "tenant_id", "date"),
        Index("idx_business_metrics_revenue", "total_revenue"),
        # Unique constraint on tenant and date
        Index("idx_business_metrics_unique", "tenant_id", "date", unique=True),
    )

    def __repr__(self):
        return f"<BusinessMetrics {self.tenant_id} {self.date}>"


class RetentionAnalytics(Base):
    """Customer retention analytics"""
    __tablename__ = "retention_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Cohort information
    cohort_month = Column(DateTime(timezone=True), nullable=False, index=True)  # When users first made purchase
    period_number = Column(Integer, nullable=False)  # Months since first purchase (0, 1, 2, etc.)

    # Metrics
    total_customers = Column(Integer, nullable=False, default=0)
    returning_customers = Column(Integer, nullable=False, default=0)
    retention_rate = Column(Numeric(5, 4), nullable=False, default=0)
    revenue = Column(Numeric(10, 2), nullable=False, default=0)
    avg_order_value = Column(Numeric(10, 2), nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_retention_tenant_cohort", "tenant_id", "cohort_month"),
        Index("idx_retention_period", "period_number"),
        Index("idx_retention_rate", "retention_rate"),
        # Unique constraint
        Index("idx_retention_unique", "tenant_id", "cohort_month", "period_number", unique=True),
    )

    def __repr__(self):
        return f"<RetentionAnalytics {self.cohort_month} P{self.period_number}>"