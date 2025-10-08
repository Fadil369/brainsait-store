"""
Field Sales API schemas for validation and serialization
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.field_sales import (
    SalesRepStatus,
    CheckInStatus,
    CreditStatus,
    BadgeType,
)


# Enums for API
class SalesRepStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"


class CheckInStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CreditStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class BadgeTypeEnum(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


# Sales Rep Schemas
class SalesRepBase(BaseModel):
    rep_code: str = Field(..., min_length=3, max_length=20)
    territory: Optional[str] = Field(None, max_length=100)
    monthly_target: Decimal = Field(default=0, ge=0)
    commission_rate: float = Field(default=0.05, ge=0, le=1)


class SalesRepCreate(SalesRepBase):
    user_id: UUID
    manager_id: Optional[UUID] = None


class SalesRepUpdate(BaseModel):
    territory: Optional[str] = None
    monthly_target: Optional[Decimal] = None
    commission_rate: Optional[float] = None
    status: Optional[SalesRepStatusEnum] = None


class SalesRepResponse(SalesRepBase):
    id: UUID
    user_id: UUID
    tenant_id: str
    status: SalesRepStatusEnum
    current_month_sales: Decimal
    total_sales: Decimal
    total_commission: Decimal
    points: int
    level: int
    badges: Optional[List[str]] = None
    csat_score: Optional[float] = None
    total_visits: int
    successful_visits: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Outlet Check-in Schemas
class CheckInLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None


class OutletCheckInCreate(BaseModel):
    outlet_name: str = Field(..., min_length=1, max_length=255)
    outlet_id: Optional[str] = Field(None, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    photo_base64: Optional[str] = None  # Base64 encoded photo
    visit_notes: Optional[str] = None
    products_discussed: Optional[List[str]] = None


class OutletCheckInUpdate(BaseModel):
    check_out_time: Optional[datetime] = None
    visit_notes: Optional[str] = None
    products_discussed: Optional[List[str]] = None
    orders_placed: Optional[List[str]] = None
    status: Optional[CheckInStatusEnum] = None


class OutletCheckInResponse(BaseModel):
    id: UUID
    sales_rep_id: UUID
    outlet_name: str
    outlet_id: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    geofence_verified: bool
    distance_from_outlet: Optional[float] = None
    photo_url: Optional[str] = None
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: CheckInStatusEnum
    visit_notes: Optional[str] = None
    products_discussed: Optional[List[str]] = None
    orders_placed: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Voice Order Schemas
class VoiceOrderCreate(BaseModel):
    audio_base64: str  # Base64 encoded audio
    language: str = Field(default="ar", pattern="^(ar|en)$")
    audio_duration_seconds: Optional[int] = None


class VoiceOrderResponse(BaseModel):
    id: UUID
    sales_rep_id: UUID
    language: str
    audio_duration_seconds: Optional[int] = None
    raw_transcription: Optional[str] = None
    processed_text: Optional[str] = None
    confidence_score: Optional[float] = None
    extracted_products: Optional[List[Dict[str, Any]]] = None
    extracted_customer: Optional[Dict[str, Any]] = None
    order_id: Optional[UUID] = None
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Credit Request Schemas
class CreditRequestCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: Optional[str] = Field(None, max_length=255)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    customer_business: Optional[str] = Field(None, max_length=255)
    requested_amount: Decimal = Field(..., gt=0)
    credit_term_days: int = Field(default=30, gt=0, le=365)
    purpose: Optional[str] = None


class CreditRequestUpdate(BaseModel):
    status: Optional[CreditStatusEnum] = None
    approved_amount: Optional[Decimal] = None
    approved_term_days: Optional[int] = None
    decision_notes: Optional[str] = None


class CreditRequestResponse(BaseModel):
    id: UUID
    sales_rep_id: UUID
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: str
    customer_business: Optional[str] = None
    requested_amount: Decimal
    credit_term_days: int
    purpose: Optional[str] = None
    ai_score: Optional[float] = None
    ai_recommendation: Optional[str] = None
    risk_factors: Optional[List[str]] = None
    status: CreditStatusEnum
    approved_amount: Optional[Decimal] = None
    approved_term_days: Optional[int] = None
    decision_notes: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Dashboard Schemas
class SalesRepDashboard(BaseModel):
    rep_info: SalesRepResponse
    target_progress: Dict[str, Any]
    recent_check_ins: List[OutletCheckInResponse]
    pending_credits: List[CreditRequestResponse]
    leaderboard_position: Dict[str, Any]
    achievements: List[Dict[str, Any]]
    route_summary: Dict[str, Any]


class TargetProgress(BaseModel):
    monthly_target: Decimal
    current_sales: Decimal
    progress_percentage: float
    days_remaining: int
    daily_average_required: Decimal


class LeaderboardEntry(BaseModel):
    rank: int
    sales_rep_id: UUID
    rep_name: str
    total_sales: Decimal
    total_orders: int
    points_earned: int
    territory: Optional[str] = None


class LeaderboardResponse(BaseModel):
    period_type: str
    period_start: datetime
    period_end: datetime
    entries: List[LeaderboardEntry]
    my_position: Optional[LeaderboardEntry] = None


class AchievementResponse(BaseModel):
    id: UUID
    code: str
    name: str
    name_ar: str
    description: Optional[str] = None
    description_ar: Optional[str] = None
    badge_type: BadgeTypeEnum
    badge_icon: Optional[str] = None
    requirement_type: str
    requirement_value: int
    points_reward: int
    is_earned: bool = False
    earned_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Offline Sync Schemas
class OfflineSyncData(BaseModel):
    check_ins: Optional[List[OutletCheckInCreate]] = None
    voice_orders: Optional[List[VoiceOrderCreate]] = None
    credit_requests: Optional[List[CreditRequestCreate]] = None
    last_sync_at: Optional[datetime] = None


class OfflineSyncResponse(BaseModel):
    synced_check_ins: int
    synced_voice_orders: int
    synced_credit_requests: int
    failed_items: List[Dict[str, Any]]
    sync_completed_at: datetime
