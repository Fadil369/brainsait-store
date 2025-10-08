"""
Field Sales models for sales rep empowerment features
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
    Float,
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


class SalesRepStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"


class CheckInStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CreditStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class BadgeType(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class SalesRep(Base):
    """Sales representative model"""
    __tablename__ = "sales_reps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Rep Information
    rep_code = Column(String(20), nullable=False, unique=True, index=True)
    territory = Column(String(100), nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("sales_reps.id"), nullable=True)
    
    # Status
    status = Column(Enum(SalesRepStatus), nullable=False, default=SalesRepStatus.ACTIVE)
    
    # Targets & Performance
    monthly_target = Column(Numeric(12, 2), nullable=False, default=0)
    current_month_sales = Column(Numeric(12, 2), nullable=False, default=0)
    total_sales = Column(Numeric(12, 2), nullable=False, default=0)
    commission_rate = Column(Float, nullable=False, default=0.05)  # 5% default
    total_commission = Column(Numeric(12, 2), nullable=False, default=0)
    
    # Gamification
    points = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    badges = Column(JSON, nullable=True)  # List of earned badges
    achievements = Column(JSON, nullable=True)  # Achievement tracking
    
    # CSAT Score
    csat_score = Column(Float, nullable=True)  # Customer satisfaction score
    total_visits = Column(Integer, nullable=False, default=0)
    successful_visits = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    manager = relationship("SalesRep", remote_side=[id], foreign_keys=[manager_id])
    check_ins = relationship("OutletCheckIn", back_populates="sales_rep")
    credit_requests = relationship("CreditRequest", back_populates="sales_rep")
    voice_orders = relationship("VoiceOrder", back_populates="sales_rep")
    
    __table_args__ = (
        Index("idx_sales_reps_tenant_code", "tenant_id", "rep_code", unique=True),
        Index("idx_sales_reps_status", "status"),
        Index("idx_sales_reps_territory", "territory"),
    )


class OutletCheckIn(Base):
    """Outlet check-in with geofencing and photo"""
    __tablename__ = "outlet_checkins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("sales_reps.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Outlet Information
    outlet_name = Column(String(255), nullable=False)
    outlet_id = Column(String(100), nullable=True, index=True)
    
    # Location Data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    geofence_verified = Column(Boolean, nullable=False, default=False)
    distance_from_outlet = Column(Float, nullable=True)  # meters
    
    # Photo Evidence
    photo_url = Column(String(500), nullable=True)
    photo_metadata = Column(JSON, nullable=True)  # GPS, timestamp from photo
    
    # Visit Details
    check_in_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Visit Outcome
    status = Column(Enum(CheckInStatus), nullable=False, default=CheckInStatus.PENDING)
    visit_notes = Column(Text, nullable=True)
    products_discussed = Column(JSON, nullable=True)  # Product IDs
    orders_placed = Column(JSON, nullable=True)  # Order IDs
    
    # Metadata
    device_info = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sales_rep = relationship("SalesRep", back_populates="check_ins")
    
    __table_args__ = (
        Index("idx_checkins_rep_date", "sales_rep_id", "check_in_time"),
        Index("idx_checkins_outlet", "outlet_id"),
        Index("idx_checkins_status", "status"),
    )


class VoiceOrder(Base):
    """Voice-to-order transcription and processing"""
    __tablename__ = "voice_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("sales_reps.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Audio Data
    audio_url = Column(String(500), nullable=True)
    audio_duration_seconds = Column(Integer, nullable=True)
    language = Column(String(5), nullable=False, default="ar")  # ar or en
    
    # Transcription
    raw_transcription = Column(Text, nullable=True)
    processed_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Order Extraction
    extracted_products = Column(JSON, nullable=True)  # Product IDs and quantities
    extracted_customer = Column(JSON, nullable=True)  # Customer info
    order_id = Column(UUID(as_uuid=True), nullable=True)  # Link to actual order
    
    # Status
    processing_status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sales_rep = relationship("SalesRep", back_populates="voice_orders")
    
    __table_args__ = (
        Index("idx_voice_orders_rep", "sales_rep_id"),
        Index("idx_voice_orders_status", "processing_status"),
    )


class CreditRequest(Base):
    """AI-based credit approval requests"""
    __tablename__ = "credit_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("sales_reps.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Customer Information
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(20), nullable=False)
    customer_business = Column(String(255), nullable=True)
    
    # Credit Request Details
    requested_amount = Column(Numeric(12, 2), nullable=False)
    credit_term_days = Column(Integer, nullable=False, default=30)
    purpose = Column(Text, nullable=True)
    
    # AI Assessment
    ai_score = Column(Float, nullable=True)  # 0-100
    ai_recommendation = Column(String(20), nullable=True)  # approve/reject/review
    risk_factors = Column(JSON, nullable=True)
    ai_analysis = Column(JSON, nullable=True)  # Detailed AI analysis
    
    # Decision
    status = Column(Enum(CreditStatus), nullable=False, default=CreditStatus.PENDING)
    approved_amount = Column(Numeric(12, 2), nullable=True)
    approved_term_days = Column(Integer, nullable=True)
    decision_notes = Column(Text, nullable=True)
    decided_by = Column(UUID(as_uuid=True), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sales_rep = relationship("SalesRep", back_populates="credit_requests")
    
    __table_args__ = (
        Index("idx_credit_requests_rep", "sales_rep_id"),
        Index("idx_credit_requests_status", "status"),
        Index("idx_credit_requests_customer", "customer_phone"),
    )


class Leaderboard(Base):
    """Sales rep leaderboard entries"""
    __tablename__ = "leaderboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("sales_reps.id"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Time Period
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metrics
    total_sales = Column(Numeric(12, 2), nullable=False, default=0)
    total_orders = Column(Integer, nullable=False, default=0)
    total_visits = Column(Integer, nullable=False, default=0)
    points_earned = Column(Integer, nullable=False, default=0)
    
    # Ranking
    rank = Column(Integer, nullable=False)
    territory_rank = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sales_rep = relationship("SalesRep")
    
    __table_args__ = (
        Index("idx_leaderboard_period", "period_type", "period_start", "period_end"),
        Index("idx_leaderboard_rank", "rank"),
    )


class Achievement(Base):
    """Achievement definitions and tracking"""
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Achievement Details
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Badge
    badge_type = Column(Enum(BadgeType), nullable=False, default=BadgeType.BRONZE)
    badge_icon = Column(String(500), nullable=True)
    
    # Requirements
    requirement_type = Column(String(50), nullable=False)  # sales, visits, orders
    requirement_value = Column(Integer, nullable=False)
    points_reward = Column(Integer, nullable=False, default=0)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_achievements_code", "code", unique=True),
        Index("idx_achievements_type", "requirement_type"),
    )
