"""
Pydantic schemas for logistics and driver management
"""

from datetime import datetime, time
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.logistics import (
    DeliveryStatus,
    DriverStatus,
    IncidentSeverity,
    IncidentType,
    RouteStatus,
    VehicleType,
)


# Driver Schemas
class DriverBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    license_number: str
    license_type: str
    license_expiry: datetime
    vehicle_type: VehicleType
    vehicle_plate: str
    vehicle_capacity_kg: Optional[float] = None
    vehicle_capacity_m3: Optional[float] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None


class DriverCreate(DriverBase):
    national_id: Optional[str] = None
    hourly_rate: Optional[float] = None
    per_delivery_rate: Optional[float] = None
    emergency_contact: Optional[Dict] = None


class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[DriverStatus] = None
    vehicle_plate: Optional[str] = None
    vehicle_capacity_kg: Optional[float] = None
    vehicle_capacity_m3: Optional[float] = None
    hourly_rate: Optional[float] = None
    per_delivery_rate: Optional[float] = None
    emergency_contact: Optional[Dict] = None
    preferences: Optional[Dict] = None


class DriverResponse(DriverBase):
    id: UUID
    driver_code: str
    tenant_id: str
    status: DriverStatus
    rating: float
    total_deliveries: int
    successful_deliveries: int
    total_earnings: float
    fatigue_alert_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DriverStatsResponse(BaseModel):
    driver_id: UUID
    today_deliveries: int
    week_deliveries: int
    month_deliveries: int
    today_earnings: float
    week_earnings: float
    month_earnings: float
    current_rating: float
    active_routes: int
    completion_rate: float


# Route Schemas
class LocationData(BaseModel):
    lat: float
    lng: float
    address: str


class RouteConstraints(BaseModel):
    max_weight_kg: Optional[float] = None
    max_volume_m3: Optional[float] = None
    time_window_start: Optional[time] = None
    time_window_end: Optional[time] = None
    priority_delivery_ids: Optional[List[UUID]] = Field(default_factory=list)
    avoid_tolls: bool = False
    avoid_highways: bool = False


class RouteCreate(BaseModel):
    driver_id: UUID
    route_name: Optional[str] = None
    planned_date: datetime
    start_location: LocationData
    end_location: Optional[LocationData] = None
    constraints: Optional[RouteConstraints] = None


class RouteOptimizationRequest(BaseModel):
    driver_id: UUID
    delivery_ids: List[UUID]
    start_location: LocationData
    constraints: Optional[RouteConstraints] = None
    optimization_algorithm: str = "ai_multi_constraint"


class RouteOptimizationResponse(BaseModel):
    route_id: UUID
    optimized_waypoints: List[Dict]
    total_distance_km: float
    estimated_duration_min: int
    optimization_score: float
    fuel_efficiency: Optional[float] = None
    carbon_footprint_kg: Optional[float] = None


class RouteResponse(BaseModel):
    id: UUID
    tenant_id: str
    driver_id: UUID
    route_number: str
    route_name: Optional[str]
    planned_date: datetime
    start_location: Dict
    end_location: Optional[Dict]
    waypoints: List[Dict]
    total_distance_km: Optional[float]
    estimated_duration_min: Optional[int]
    actual_duration_min: Optional[int]
    total_stops: int
    completed_stops: int
    status: RouteStatus
    optimization_score: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Delivery Schemas
class PackageDimensions(BaseModel):
    length_cm: float
    width_cm: float
    height_cm: float


class DeliveryContact(BaseModel):
    name: str
    phone: str
    alternate_phone: Optional[str] = None


class DeliveryCreate(BaseModel):
    route_id: UUID
    order_id: Optional[UUID] = None
    package_weight_kg: Optional[float] = None
    package_dimensions: Optional[PackageDimensions] = None
    package_description: Optional[str] = None
    special_instructions: Optional[str] = None
    delivery_location: LocationData
    delivery_contact: DeliveryContact
    delivery_window_start: Optional[time] = None
    delivery_window_end: Optional[time] = None
    sequence_number: Optional[int] = None


class ProofOfDelivery(BaseModel):
    signature: Optional[str] = None  # Base64 image or signature data
    photo: Optional[str] = None  # URL or base64
    gps_location: Dict  # {lat, lng, accuracy}
    recipient_name: str
    notes: Optional[str] = None


class DeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    pod: Optional[ProofOfDelivery] = None
    failure_reason: Optional[str] = None


class DeliveryResponse(BaseModel):
    id: UUID
    tenant_id: str
    route_id: UUID
    driver_id: UUID
    tracking_number: str
    sequence_number: int
    package_weight_kg: Optional[float]
    package_dimensions: Optional[Dict]
    delivery_location: Dict
    delivery_contact: Dict
    status: DeliveryStatus
    estimated_arrival: Optional[datetime]
    actual_arrival: Optional[datetime]
    delivered_at: Optional[datetime]
    attempt_count: int
    pod_signature: Optional[str]
    pod_photo: Optional[str]
    pod_gps_location: Optional[Dict]
    pod_recipient_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Incident Schemas
class IncidentCreate(BaseModel):
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    location: Optional[Dict] = None
    route_id: Optional[UUID] = None
    delivery_id: Optional[UUID] = None
    photos: Optional[List[str]] = Field(default_factory=list)
    videos: Optional[List[str]] = Field(default_factory=list)
    estimated_delay_min: Optional[int] = None


class IncidentAISuggestion(BaseModel):
    suggested_category: str
    suggested_actions: List[str]
    confidence_score: float
    reasoning: str


class IncidentResponse(BaseModel):
    id: UUID
    tenant_id: str
    driver_id: UUID
    incident_number: str
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str
    description: str
    location: Optional[Dict]
    occurred_at: datetime
    photos: List[str]
    ai_suggested_category: Optional[str]
    ai_suggested_actions: Optional[List]
    ai_confidence_score: Optional[float]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    estimated_delay_min: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Earnings Schemas
class EarningsBreakdown(BaseModel):
    date: datetime
    base_amount: float
    bonus_amount: float
    deduction_amount: float
    total_amount: float
    hours_worked: Optional[float]
    deliveries_completed: int
    distance_traveled_km: Optional[float]
    on_time_bonus: float
    rating_bonus: float
    efficiency_bonus: float


class EarningsSummary(BaseModel):
    driver_id: UUID
    period_start: datetime
    period_end: datetime
    total_earnings: float
    total_bonuses: float
    total_deductions: float
    net_earnings: float
    deliveries_completed: int
    hours_worked: float
    average_rating: float
    breakdown: List[EarningsBreakdown]


class EarningsResponse(BaseModel):
    id: UUID
    driver_id: UUID
    date: datetime
    base_amount: float
    bonus_amount: float
    deduction_amount: float
    total_amount: float
    deliveries_completed: int
    is_paid: bool
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


# Load Planning Schemas
class LoadItem(BaseModel):
    item_id: str
    delivery_id: Optional[UUID]
    length_m: float
    width_m: float
    height_m: float
    weight_kg: float
    fragile: bool = False
    stackable: bool = True
    priority: int = 0


class LoadPlanCreate(BaseModel):
    route_id: UUID
    vehicle_length_m: float
    vehicle_width_m: float
    vehicle_height_m: float
    max_weight_kg: float
    items: List[LoadItem]


class LoadPlanResponse(BaseModel):
    id: UUID
    route_id: UUID
    total_weight_kg: float
    weight_utilization_pct: float
    volume_utilization_pct: float
    optimization_score: Optional[float]
    balance_score: Optional[float]
    accessibility_score: Optional[float]
    loading_sequence: List[Dict]
    layout_3d: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True


# Safety Schemas
class SafetyAlertCreate(BaseModel):
    alert_type: str  # fatigue, speeding, harsh_braking, etc.
    severity: str  # low, medium, high, critical
    message: str
    location: Optional[Dict] = None
    metadata: Optional[Dict] = None


class SafetyAlertResponse(BaseModel):
    id: UUID
    driver_id: UUID
    alert_type: str
    severity: str
    message: str
    location: Optional[Dict]
    triggered_at: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    action_taken: Optional[str]

    class Config:
        from_attributes = True


class FatigueAnalysis(BaseModel):
    driver_id: UUID
    hours_driven_today: float
    continuous_drive_time_min: int
    fatigue_score: float  # 0-100, higher = more fatigued
    recommendation: str
    break_required: bool
    estimated_break_time_min: int


# Pagination
class PaginatedDriversResponse(BaseModel):
    items: List[DriverResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PaginatedRoutesResponse(BaseModel):
    items: List[RouteResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PaginatedDeliveriesResponse(BaseModel):
    items: List[DeliveryResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PaginatedIncidentsResponse(BaseModel):
    items: List[IncidentResponse]
    total: int
    page: int
    per_page: int
    pages: int
