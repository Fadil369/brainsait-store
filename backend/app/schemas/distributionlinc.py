"""
DISTRIBUTIONLINC Agent Schemas
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, confloat, conint, validator


# =============== Demand Forecasting Schemas ===============


class DemandForecastRequest(BaseModel):
    """Request schema for demand forecasting"""

    product_id: str = Field(..., description="Product identifier")
    region: str = Field(..., description="Region name")
    forecast_horizon_days: int = Field(
        default=30, ge=1, le=365, description="Forecast period in days"
    )
    include_factors: bool = Field(
        default=True, description="Include influencing factors in response"
    )


class DemandForecastFactors(BaseModel):
    """Influencing factors for demand forecast"""

    seasonal_factor: Optional[float] = None
    weather_impact: Optional[float] = None
    holiday_impact: Optional[float] = None
    trend_factor: Optional[float] = None


class DemandForecastResponse(BaseModel):
    """Response schema for demand forecasting"""

    id: str
    product_id: str
    product_name: str
    product_name_ar: Optional[str] = None
    region: str
    region_ar: Optional[str] = None
    forecast_date: datetime
    forecast_horizon_days: int
    predicted_quantity: float
    confidence_score: float
    lower_bound: float
    upper_bound: float
    factors: Optional[DemandForecastFactors] = None
    model_version: str
    created_at: datetime

    class Config:
        from_attributes = True


class BatchDemandForecastRequest(BaseModel):
    """Batch request for multiple forecasts"""

    products: List[str] = Field(..., description="List of product IDs")
    regions: List[str] = Field(..., description="List of regions")
    forecast_horizon_days: int = Field(default=30, ge=1, le=365)


# =============== Dynamic Pricing Schemas ===============


class DynamicPricingRequest(BaseModel):
    """Request schema for dynamic pricing"""

    product_id: str = Field(..., description="Product identifier")
    consider_competitors: bool = Field(default=True)
    consider_inventory: bool = Field(default=True)
    consider_demand: bool = Field(default=True)
    min_margin_percent: Optional[float] = Field(
        default=None, ge=0, le=100, description="Minimum profit margin percentage"
    )


class DynamicPricingFactors(BaseModel):
    """Pricing factors analysis"""

    inventory_level: Optional[int] = None
    competitor_avg_price: Optional[float] = None
    demand_level: Optional[str] = None
    elasticity_score: Optional[float] = None


class DynamicPricingResponse(BaseModel):
    """Response schema for dynamic pricing"""

    id: str
    product_id: str
    product_name: str
    product_name_ar: Optional[str] = None
    current_price: float
    base_price: float
    recommended_price: float
    min_price: float
    max_price: float
    confidence_score: float
    factors: Optional[DynamicPricingFactors] = None
    estimated_revenue_impact: Optional[float] = None
    estimated_volume_change: Optional[float] = None
    reasoning: Optional[Dict[str, Any]] = None
    valid_from: datetime
    valid_until: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PricingApprovalRequest(BaseModel):
    """Request to approve/reject pricing recommendation"""

    pricing_id: str
    action: str = Field(..., pattern="^(approve|reject)$")
    notes: Optional[str] = None


# =============== Route Optimization Schemas ===============


class RouteOptimizationRequest(BaseModel):
    """Request schema for route optimization"""

    route_name: str = Field(..., description="Route name")
    route_name_ar: Optional[str] = None
    origin: str = Field(..., description="Starting point")
    destination: str = Field(..., description="End point")
    waypoints: Optional[List[str]] = Field(
        default=None, description="Optional intermediate stops"
    )
    vehicle_type: Optional[str] = None
    vehicle_capacity_kg: Optional[float] = None
    cargo_weight_kg: Optional[float] = None
    consider_traffic: bool = Field(default=True)
    preferred_departure_time: Optional[datetime] = None
    delivery_windows: Optional[List[Dict[str, Any]]] = None


class RouteOptimizationResponse(BaseModel):
    """Response schema for route optimization"""

    id: str
    route_name: str
    route_name_ar: Optional[str] = None
    origin: str
    destination: str
    optimal_path: List[Dict[str, Any]]
    estimated_duration_minutes: int
    estimated_distance_km: float
    estimated_cost: float
    traffic_level: Optional[str] = None
    traffic_delay_minutes: Optional[int] = None
    best_departure_time: Optional[datetime] = None
    stops_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# =============== Inventory Prediction Schemas ===============


class InventoryPredictionRequest(BaseModel):
    """Request schema for inventory prediction"""

    product_id: str
    warehouse_id: str
    current_stock: float = Field(..., ge=0)
    lead_time_days: int = Field(..., ge=1)
    include_po_suggestion: bool = Field(default=True)


class InventoryPredictionResponse(BaseModel):
    """Response schema for inventory prediction"""

    id: str
    product_id: str
    product_name: str
    product_name_ar: Optional[str] = None
    warehouse_id: str
    warehouse_name: str
    current_stock: float
    reorder_point: float
    safety_stock: float
    predicted_depletion_date: Optional[datetime] = None
    days_until_stockout: Optional[int] = None
    recommended_reorder_quantity: float
    recommended_reorder_date: datetime
    average_daily_demand: float
    demand_volatility: Optional[float] = None
    risk_level: str
    confidence_score: float
    po_suggested: bool
    po_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BatchInventoryCheckRequest(BaseModel):
    """Batch request for inventory predictions"""

    warehouse_id: str
    products: Optional[List[str]] = Field(
        default=None, description="Specific products to check, or all if None"
    )
    risk_level_filter: Optional[str] = Field(
        default=None, pattern="^(low|medium|high|critical)$"
    )


# =============== Customer Churn Schemas ===============


class CustomerChurnPredictionRequest(BaseModel):
    """Request schema for churn prediction"""

    customer_id: str
    include_recommendations: bool = Field(default=True)


class RetentionStrategy(BaseModel):
    """Retention strategy recommendation"""

    strategy_type: str
    description: str
    description_ar: Optional[str] = None
    priority: int
    estimated_cost: Optional[float] = None
    estimated_success_rate: Optional[float] = None


class CustomerChurnPredictionResponse(BaseModel):
    """Response schema for churn prediction"""

    id: str
    customer_id: str
    customer_name: str
    customer_type: Optional[str] = None
    churn_probability: float
    risk_level: str
    predicted_churn_date: Optional[datetime] = None
    days_until_churn: Optional[int] = None
    recency_days: Optional[int] = None
    frequency_decline: Optional[float] = None
    monetary_decline: Optional[float] = None
    complaint_count: int
    lifetime_value: Optional[float] = None
    average_order_value: Optional[float] = None
    total_orders: int
    retention_strategies: Optional[List[RetentionStrategy]] = None
    recommended_discount: Optional[float] = None
    recommended_contact_method: Optional[str] = None
    priority_level: int
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class ChurnActionRequest(BaseModel):
    """Request to log retention action"""

    churn_prediction_id: str
    action_type: str = Field(..., description="Type of action taken")
    notes: Optional[str] = None


class BatchChurnAnalysisRequest(BaseModel):
    """Batch request for churn analysis"""

    risk_level_filter: Optional[str] = Field(
        default=None, pattern="^(low|medium|high|critical)$"
    )
    min_churn_probability: Optional[float] = Field(default=None, ge=0, le=1)
    limit: int = Field(default=100, ge=1, le=1000)


# =============== Analytics & Reporting Schemas ===============


class DistributionAnalyticsRequest(BaseModel):
    """Request for distribution analytics"""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    region: Optional[str] = None
    include_forecasts: bool = Field(default=True)
    include_pricing: bool = Field(default=True)
    include_routes: bool = Field(default=True)
    include_inventory: bool = Field(default=True)
    include_churn: bool = Field(default=True)


class DistributionAnalyticsResponse(BaseModel):
    """Response for distribution analytics"""

    period_start: datetime
    period_end: datetime
    region: Optional[str] = None
    forecasts_generated: int
    pricing_recommendations: int
    routes_optimized: int
    inventory_alerts: int
    churn_predictions: int
    total_cost_savings: Optional[float] = None
    total_revenue_impact: Optional[float] = None
    accuracy_metrics: Optional[Dict[str, float]] = None


# =============== Model Performance Schemas ===============


class ModelPerformanceRequest(BaseModel):
    """Request for model performance metrics"""

    model_type: str = Field(
        ...,
        pattern="^(demand|pricing|route|inventory|churn)$",
        description="Type of model",
    )
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ModelPerformanceResponse(BaseModel):
    """Response for model performance metrics"""

    model_type: str
    model_version: str
    period_start: datetime
    period_end: datetime
    predictions_count: int
    average_confidence: float
    accuracy_metrics: Dict[str, float]
    error_metrics: Dict[str, float]
    last_retrained: Optional[datetime] = None


# =============== Common Response Schemas ===============


class SuccessResponse(BaseModel):
    """Generic success response"""

    success: bool = True
    message: str
    message_ar: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Generic error response"""

    success: bool = False
    error: str
    error_ar: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""

    success: bool = True
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
