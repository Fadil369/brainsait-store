"""
DISTRIBUTIONLINC Agent Models
AI-powered intelligence layer for SSDP (Saudi Smart Distribution Platform)
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
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


class DemandForecast(Base):
    """Demand forecasting predictions for products/regions"""

    __tablename__ = "demand_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Product & Location
    product_id = Column(String(100), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    product_name_ar = Column(String(255), nullable=True)
    region = Column(String(100), nullable=False, index=True)
    region_ar = Column(String(100), nullable=True)

    # Forecast Period
    forecast_date = Column(DateTime(timezone=True), nullable=False, index=True)
    forecast_horizon_days = Column(Integer, nullable=False, default=30)

    # Predicted Demand
    predicted_quantity = Column(Numeric(15, 2), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    lower_bound = Column(Numeric(15, 2), nullable=False)
    upper_bound = Column(Numeric(15, 2), nullable=False)

    # Influencing Factors
    seasonal_factor = Column(Float, nullable=True)
    weather_impact = Column(Float, nullable=True)
    holiday_impact = Column(Float, nullable=True)
    trend_factor = Column(Float, nullable=True)

    # Model Metadata
    model_version = Column(String(50), nullable=False)
    features_used = Column(JSON, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index(
            "idx_demand_forecast_product_region_date",
            "tenant_id",
            "product_id",
            "region",
            "forecast_date",
        ),
    )


class DynamicPricing(Base):
    """Dynamic pricing recommendations"""

    __tablename__ = "dynamic_pricing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Product Information
    product_id = Column(String(100), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    product_name_ar = Column(String(255), nullable=True)

    # Current State
    current_price = Column(Numeric(15, 2), nullable=False)
    base_price = Column(Numeric(15, 2), nullable=False)

    # Recommended Price
    recommended_price = Column(Numeric(15, 2), nullable=False)
    min_price = Column(Numeric(15, 2), nullable=False)
    max_price = Column(Numeric(15, 2), nullable=False)
    confidence_score = Column(Float, nullable=False)

    # Pricing Factors
    inventory_level = Column(Integer, nullable=True)
    competitor_avg_price = Column(Numeric(15, 2), nullable=True)
    demand_level = Column(String(20), nullable=True)  # high, medium, low
    elasticity_score = Column(Float, nullable=True)

    # Revenue Impact
    estimated_revenue_impact = Column(Numeric(15, 2), nullable=True)
    estimated_volume_change = Column(Float, nullable=True)

    # Status
    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, approved, rejected, applied
    applied_at = Column(DateTime(timezone=True), nullable=True)

    # Valid Period
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)

    # Model Metadata
    model_version = Column(String(50), nullable=False)
    reasoning = Column(JSON, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index(
            "idx_dynamic_pricing_product_date",
            "tenant_id",
            "product_id",
            "valid_from",
        ),
    )


class RouteOptimization(Base):
    """Route optimization recommendations"""

    __tablename__ = "route_optimizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Route Information
    route_name = Column(String(255), nullable=False)
    route_name_ar = Column(String(255), nullable=True)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)

    # Optimization Results
    optimal_path = Column(JSON, nullable=False)  # Array of waypoints
    estimated_duration_minutes = Column(Integer, nullable=False)
    estimated_distance_km = Column(Numeric(10, 2), nullable=False)
    estimated_cost = Column(Numeric(15, 2), nullable=False)

    # Traffic Intelligence
    traffic_level = Column(String(20), nullable=True)  # low, medium, high
    traffic_delay_minutes = Column(Integer, nullable=True)
    best_departure_time = Column(DateTime(timezone=True), nullable=True)

    # Vehicle & Driver
    vehicle_type = Column(String(50), nullable=True)
    vehicle_capacity_kg = Column(Numeric(10, 2), nullable=True)
    assigned_driver_id = Column(String(100), nullable=True)
    driver_performance_score = Column(Float, nullable=True)

    # Delivery Windows
    delivery_windows = Column(JSON, nullable=True)  # Array of time windows
    stops_count = Column(Integer, nullable=False, default=0)
    total_cargo_kg = Column(Numeric(10, 2), nullable=True)

    # Status
    status = Column(
        String(20), nullable=False, default="recommended"
    )  # recommended, in_progress, completed, cancelled
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Model Metadata
    optimization_algorithm = Column(String(50), nullable=False)
    factors_considered = Column(JSON, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index(
            "idx_route_optimization_tenant_status",
            "tenant_id",
            "status",
            "created_at",
        ),
    )


class InventoryPrediction(Base):
    """Inventory prediction and restocking recommendations"""

    __tablename__ = "inventory_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Product Information
    product_id = Column(String(100), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    product_name_ar = Column(String(255), nullable=True)
    warehouse_id = Column(String(100), nullable=False, index=True)
    warehouse_name = Column(String(255), nullable=False)

    # Current State
    current_stock = Column(Numeric(15, 2), nullable=False)
    reorder_point = Column(Numeric(15, 2), nullable=False)
    safety_stock = Column(Numeric(15, 2), nullable=False)

    # Predictions
    predicted_depletion_date = Column(DateTime(timezone=True), nullable=True)
    days_until_stockout = Column(Integer, nullable=True)
    recommended_reorder_quantity = Column(Numeric(15, 2), nullable=False)
    recommended_reorder_date = Column(DateTime(timezone=True), nullable=False)

    # Cost Analysis
    holding_cost = Column(Numeric(15, 2), nullable=True)
    ordering_cost = Column(Numeric(15, 2), nullable=True)
    stockout_risk_cost = Column(Numeric(15, 2), nullable=True)
    optimal_order_quantity = Column(Numeric(15, 2), nullable=True)

    # Demand Factors
    average_daily_demand = Column(Numeric(15, 2), nullable=False)
    demand_volatility = Column(Float, nullable=True)
    lead_time_days = Column(Integer, nullable=False)

    # PO Suggestion
    po_suggested = Column(Boolean, nullable=False, default=False)
    po_generated = Column(Boolean, nullable=False, default=False)
    po_id = Column(String(100), nullable=True)

    # Risk Level
    risk_level = Column(
        String(20), nullable=False, default="low"
    )  # low, medium, high, critical
    confidence_score = Column(Float, nullable=False)

    # Model Metadata
    model_version = Column(String(50), nullable=False)
    prediction_factors = Column(JSON, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index(
            "idx_inventory_prediction_product_warehouse",
            "tenant_id",
            "product_id",
            "warehouse_id",
        ),
    )


class CustomerChurnPrediction(Base):
    """Customer churn prediction and retention recommendations"""

    __tablename__ = "customer_churn_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Customer Information
    customer_id = Column(String(100), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_type = Column(String(50), nullable=True)  # outlet, distributor, etc.

    # Churn Prediction
    churn_probability = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_level = Column(
        String(20), nullable=False, default="low"
    )  # low, medium, high, critical
    predicted_churn_date = Column(DateTime(timezone=True), nullable=True)
    days_until_churn = Column(Integer, nullable=True)

    # Risk Factors
    recency_days = Column(Integer, nullable=True)  # Days since last order
    frequency_decline = Column(Float, nullable=True)  # % decline in order frequency
    monetary_decline = Column(Float, nullable=True)  # % decline in order value
    complaint_count = Column(Integer, nullable=False, default=0)
    payment_delay_days = Column(Integer, nullable=False, default=0)

    # Customer Metrics
    lifetime_value = Column(Numeric(15, 2), nullable=True)
    average_order_value = Column(Numeric(15, 2), nullable=True)
    total_orders = Column(Integer, nullable=False, default=0)
    engagement_score = Column(Float, nullable=True)

    # Retention Recommendations
    retention_strategy = Column(JSON, nullable=True)  # Array of recommended actions
    recommended_discount = Column(Numeric(5, 2), nullable=True)  # Percentage
    recommended_contact_method = Column(String(50), nullable=True)
    priority_level = Column(Integer, nullable=False, default=1)  # 1-5

    # Action Tracking
    action_taken = Column(Boolean, nullable=False, default=False)
    action_type = Column(String(100), nullable=True)
    action_date = Column(DateTime(timezone=True), nullable=True)
    action_outcome = Column(String(20), nullable=True)  # retained, churned, pending

    # Model Metadata
    model_version = Column(String(50), nullable=False)
    features_importance = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=False)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    reviewed_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index(
            "idx_customer_churn_risk",
            "tenant_id",
            "risk_level",
            "churn_probability",
        ),
    )


class DistributionLincAuditLog(Base):
    """Audit log for all DISTRIBUTIONLINC operations"""

    __tablename__ = "distributionlinc_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Action Details
    action_type = Column(
        String(50), nullable=False, index=True
    )  # forecast, pricing, route, inventory, churn
    action = Column(String(100), nullable=False)  # create, update, approve, reject, etc.
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)

    # User Information
    user_id = Column(String(100), nullable=False)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)

    # Request Details
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_ip = Column(String(50), nullable=True)
    request_params = Column(JSON, nullable=True)

    # Response Details
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)

    # Changes
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)

    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index(
            "idx_audit_log_tenant_action_time",
            "tenant_id",
            "action_type",
            "timestamp",
        ),
    )
