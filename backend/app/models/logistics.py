"""
Logistics and Driver Management Models for SSDP
Supports driver profiles, routes, deliveries, incidents, and safety features
"""

from datetime import datetime, time
from enum import Enum as PyEnum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class DriverStatus(str, PyEnum):
    """Driver availability status"""
    AVAILABLE = "available"
    ON_ROUTE = "on_route"
    ON_BREAK = "on_break"
    OFFLINE = "offline"
    SUSPENDED = "suspended"


class VehicleType(str, PyEnum):
    """Vehicle type classification"""
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    TRUCK_SMALL = "truck_small"
    TRUCK_MEDIUM = "truck_medium"
    TRUCK_LARGE = "truck_large"


class RouteStatus(str, PyEnum):
    """Route execution status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DeliveryStatus(str, PyEnum):
    """Individual delivery status"""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class IncidentType(str, PyEnum):
    """Incident classification"""
    ACCIDENT = "accident"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    TRAFFIC_DELAY = "traffic_delay"
    WEATHER_DELAY = "weather_delay"
    CUSTOMER_UNAVAILABLE = "customer_unavailable"
    PACKAGE_DAMAGE = "package_damage"
    SECURITY_ISSUE = "security_issue"
    OTHER = "other"


class IncidentSeverity(str, PyEnum):
    """Incident severity level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Driver(Base):
    """Driver profile and credentials"""
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Personal Information
    driver_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    national_id = Column(String(50), nullable=True)
    
    # License Information
    license_number = Column(String(100), nullable=False)
    license_type = Column(String(50), nullable=False)
    license_expiry = Column(DateTime, nullable=False)
    
    # Vehicle Information
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    vehicle_make = Column(String(100), nullable=True)
    vehicle_model = Column(String(100), nullable=True)
    vehicle_year = Column(Integer, nullable=True)
    vehicle_plate = Column(String(50), nullable=False)
    vehicle_capacity_kg = Column(Float, nullable=True)
    vehicle_capacity_m3 = Column(Float, nullable=True)
    
    # Status and Performance
    status = Column(Enum(DriverStatus), default=DriverStatus.AVAILABLE, nullable=False)
    rating = Column(Float, default=5.0)
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    
    # Safety and Compliance
    last_safety_training = Column(DateTime, nullable=True)
    last_health_check = Column(DateTime, nullable=True)
    fatigue_alert_count = Column(Integer, default=0)
    
    # Financial
    hourly_rate = Column(Float, nullable=True)
    per_delivery_rate = Column(Float, nullable=True)
    total_earnings = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Additional data
    preferences = Column(JSON, default=dict)
    emergency_contact = Column(JSON, nullable=True)
    
    # Relationships
    routes = relationship("Route", back_populates="driver", cascade="all, delete-orphan")
    deliveries = relationship("Delivery", back_populates="driver", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="driver", cascade="all, delete-orphan")
    earnings_records = relationship("DriverEarnings", back_populates="driver", cascade="all, delete-orphan")


class Route(Base):
    """Optimized delivery route"""
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    
    # Route Information
    route_number = Column(String(50), unique=True, nullable=False, index=True)
    route_name = Column(String(200), nullable=True)
    planned_date = Column(DateTime, nullable=False)
    
    # Route Details
    start_location = Column(JSON, nullable=False)  # {lat, lng, address}
    end_location = Column(JSON, nullable=True)  # {lat, lng, address}
    waypoints = Column(JSON, default=list)  # List of delivery waypoints
    
    # Optimization Constraints
    max_weight_kg = Column(Float, nullable=True)
    max_volume_m3 = Column(Float, nullable=True)
    time_window_start = Column(Time, nullable=True)
    time_window_end = Column(Time, nullable=True)
    priority_deliveries = Column(JSON, default=list)  # IDs of priority deliveries
    
    # Route Metrics
    total_distance_km = Column(Float, nullable=True)
    estimated_duration_min = Column(Integer, nullable=True)
    actual_duration_min = Column(Integer, nullable=True)
    total_stops = Column(Integer, default=0)
    completed_stops = Column(Integer, default=0)
    
    # Status
    status = Column(Enum(RouteStatus), default=RouteStatus.PLANNED, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # AI Optimization
    optimization_score = Column(Float, nullable=True)  # 0-100
    optimization_algorithm = Column(String(100), nullable=True)
    optimization_constraints = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = relationship("Driver", back_populates="routes")
    deliveries = relationship("Delivery", back_populates="route", cascade="all, delete-orphan")


class Delivery(Base):
    """Individual delivery within a route"""
    __tablename__ = "deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    
    # Delivery Information
    tracking_number = Column(String(100), unique=True, nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)  # Order in route
    
    # Package Details
    package_weight_kg = Column(Float, nullable=True)
    package_dimensions = Column(JSON, nullable=True)  # {length, width, height}
    package_description = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # Location
    delivery_location = Column(JSON, nullable=False)  # {lat, lng, address}
    delivery_contact = Column(JSON, nullable=False)  # {name, phone}
    
    # Time Windows
    estimated_arrival = Column(DateTime, nullable=True)
    actual_arrival = Column(DateTime, nullable=True)
    delivery_window_start = Column(Time, nullable=True)
    delivery_window_end = Column(Time, nullable=True)
    
    # Status
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
    
    # Proof of Delivery
    pod_signature = Column(String(500), nullable=True)  # Base64 or URL
    pod_photo = Column(String(500), nullable=True)  # URL
    pod_gps_location = Column(JSON, nullable=True)  # {lat, lng, accuracy}
    pod_recipient_name = Column(String(200), nullable=True)
    pod_notes = Column(Text, nullable=True)
    
    # Delivery Attempt Tracking
    attempt_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    route = relationship("Route", back_populates="deliveries")
    driver = relationship("Driver", back_populates="deliveries")


class Incident(Base):
    """Incident and delay reporting"""
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=True)
    
    # Incident Details
    incident_number = Column(String(50), unique=True, nullable=False, index=True)
    incident_type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Enum(IncidentSeverity), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Location and Time
    location = Column(JSON, nullable=True)  # {lat, lng, address}
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Media
    photos = Column(JSON, default=list)  # List of photo URLs
    videos = Column(JSON, default=list)  # List of video URLs
    
    # AI Analysis
    ai_suggested_category = Column(String(100), nullable=True)
    ai_suggested_actions = Column(JSON, default=list)
    ai_confidence_score = Column(Float, nullable=True)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Impact
    estimated_delay_min = Column(Integer, nullable=True)
    affected_deliveries = Column(JSON, default=list)  # List of delivery IDs
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = relationship("Driver", back_populates="incidents")


class DriverEarnings(Base):
    """Driver earnings tracking"""
    __tablename__ = "driver_earnings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True)
    
    # Earnings Details
    date = Column(DateTime, nullable=False, index=True)
    base_amount = Column(Float, nullable=False)
    bonus_amount = Column(Float, default=0.0)
    deduction_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Breakdown
    hours_worked = Column(Float, nullable=True)
    deliveries_completed = Column(Integer, default=0)
    distance_traveled_km = Column(Float, nullable=True)
    
    # Performance Bonuses
    on_time_bonus = Column(Float, default=0.0)
    rating_bonus = Column(Float, default=0.0)
    efficiency_bonus = Column(Float, default=0.0)
    
    # Payment Status
    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(200), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    driver = relationship("Driver", back_populates="earnings_records")


class LoadPlan(Base):
    """3D load planning for vehicle cargo"""
    __tablename__ = "load_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False)
    
    # Vehicle Capacity
    vehicle_length_m = Column(Float, nullable=False)
    vehicle_width_m = Column(Float, nullable=False)
    vehicle_height_m = Column(Float, nullable=False)
    max_weight_kg = Column(Float, nullable=False)
    
    # Load Details
    items = Column(JSON, nullable=False)  # List of items with dimensions and positions
    total_weight_kg = Column(Float, nullable=False)
    weight_utilization_pct = Column(Float, nullable=False)
    volume_utilization_pct = Column(Float, nullable=False)
    
    # 3D Layout
    layout_3d = Column(JSON, nullable=True)  # 3D positioning data for visualization
    loading_sequence = Column(JSON, nullable=False)  # Ordered list for loading
    
    # Optimization
    optimization_score = Column(Float, nullable=True)
    balance_score = Column(Float, nullable=True)
    accessibility_score = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SafetyAlert(Base):
    """Driver safety and fatigue alerts"""
    __tablename__ = "safety_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    
    # Alert Details
    alert_type = Column(String(100), nullable=False)  # fatigue, speeding, harsh_braking, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    
    # Context
    location = Column(JSON, nullable=True)
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Driver Response
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    action_taken = Column(Text, nullable=True)
    
    # Metadata
    alert_metadata = Column(JSON, default=dict)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
