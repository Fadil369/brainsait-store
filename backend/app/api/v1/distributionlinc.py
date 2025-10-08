"""
DISTRIBUTIONLINC Agent API Endpoints
AI-powered intelligence layer for SSDP
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.models.users import User
from app.schemas.distributionlinc import (
    BatchChurnAnalysisRequest,
    BatchDemandForecastRequest,
    BatchInventoryCheckRequest,
    ChurnActionRequest,
    CustomerChurnPredictionRequest,
    CustomerChurnPredictionResponse,
    DemandForecastRequest,
    DemandForecastResponse,
    DistributionAnalyticsRequest,
    DistributionAnalyticsResponse,
    DynamicPricingRequest,
    DynamicPricingResponse,
    InventoryPredictionRequest,
    InventoryPredictionResponse,
    PaginatedResponse,
    PricingApprovalRequest,
    RetentionStrategy,
    RouteOptimizationRequest,
    RouteOptimizationResponse,
    SuccessResponse,
)
from app.services.distributionlinc import DistributionLincService

router = APIRouter()


def _get_language(request: Request) -> str:
    """Extract language from request headers"""
    accept_lang = request.headers.get("Accept-Language", "en")
    return "ar" if "ar" in accept_lang else "en"


def _translate_message(message_en: str, message_ar: str, lang: str) -> str:
    """Return appropriate message based on language"""
    return message_ar if lang == "ar" else message_en


# =============== Demand Forecasting Endpoints ===============


@router.post("/forecast/demand", response_model=DemandForecastResponse, status_code=status.HTTP_201_CREATED)
async def generate_demand_forecast(
    request: Request,
    forecast_request: DemandForecastRequest,
    current_user: User = Depends(require_role(["admin", "analyst", "user"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate demand forecast for a product in a region
    
    **Supports:** English & Arabic (عربي)
    
    **Factors considered:**
    - Historical demand data
    - Seasonal patterns (Saudi market specific)
    - Weather impact
    - Holiday effects (Ramadan, Eid, National Day)
    - Trend analysis
    """
    lang = _get_language(request)
    
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        # Generate product name in Arabic (in production, fetch from product service)
        product_name = f"Product {forecast_request.product_id}"
        product_name_ar = f"منتج {forecast_request.product_id}"
        region_ar = forecast_request.region  # In production, translate region name

        forecast = await service.generate_demand_forecast(
            product_id=forecast_request.product_id,
            product_name=product_name,
            region=forecast_request.region,
            forecast_horizon_days=forecast_request.forecast_horizon_days,
            product_name_ar=product_name_ar,
            region_ar=region_ar,
        )

        await db.commit()

        # Convert to response
        response_data = DemandForecastResponse(
            id=str(forecast.id),
            product_id=forecast.product_id,
            product_name=forecast.product_name,
            product_name_ar=forecast.product_name_ar,
            region=forecast.region,
            region_ar=forecast.region_ar,
            forecast_date=forecast.forecast_date,
            forecast_horizon_days=forecast.forecast_horizon_days,
            predicted_quantity=float(forecast.predicted_quantity),
            confidence_score=forecast.confidence_score,
            lower_bound=float(forecast.lower_bound),
            upper_bound=float(forecast.upper_bound),
            factors={
                "seasonal_factor": forecast.seasonal_factor,
                "weather_impact": forecast.weather_impact,
                "holiday_impact": forecast.holiday_impact,
                "trend_factor": forecast.trend_factor,
            } if forecast_request.include_factors else None,
            model_version=forecast.model_version,
            created_at=forecast.created_at,
        )

        return response_data

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_translate_message(
                f"Failed to generate demand forecast: {str(e)}",
                f"فشل في إنشاء توقع الطلب: {str(e)}",
                lang,
            ),
        )


@router.get("/forecast/demand", response_model=List[DemandForecastResponse])
async def list_demand_forecasts(
    request: Request,
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    region: Optional[str] = Query(None, description="Filter by region"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    current_user: User = Depends(require_role(["admin", "analyst", "user"])),
    db: AsyncSession = Depends(get_db),
):
    """
    List demand forecasts with optional filters
    
    **Bilingual Support:** English & Arabic (عربي)
    """
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        forecasts = await service.get_demand_forecasts(
            product_id=product_id, region=region, limit=limit
        )

        return [
            DemandForecastResponse(
                id=str(f.id),
                product_id=f.product_id,
                product_name=f.product_name,
                product_name_ar=f.product_name_ar,
                region=f.region,
                region_ar=f.region_ar,
                forecast_date=f.forecast_date,
                forecast_horizon_days=f.forecast_horizon_days,
                predicted_quantity=float(f.predicted_quantity),
                confidence_score=f.confidence_score,
                lower_bound=float(f.lower_bound),
                upper_bound=float(f.upper_bound),
                model_version=f.model_version,
                created_at=f.created_at,
            )
            for f in forecasts
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve forecasts: {str(e)}",
        )


# =============== Dynamic Pricing Endpoints ===============


@router.post("/pricing/optimize", response_model=DynamicPricingResponse, status_code=status.HTTP_201_CREATED)
async def generate_pricing_recommendation(
    request: Request,
    pricing_request: DynamicPricingRequest,
    current_user: User = Depends(require_role(["admin", "pricing_manager"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate dynamic pricing recommendation
    
    **Supports:** English & Arabic (عربي)
    
    **Factors considered:**
    - Current inventory levels
    - Competitor pricing
    - Demand elasticity
    - Market trends
    
    **Role required:** admin or pricing_manager
    """
    lang = _get_language(request)
    
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        # In production, fetch actual product data
        product_name = f"Product {pricing_request.product_id}"
        product_name_ar = f"منتج {pricing_request.product_id}"
        current_price = 100.0  # Fetch from product service
        base_price = 90.0  # Fetch from product service
        inventory_level = 500 if pricing_request.consider_inventory else None

        pricing = await service.generate_pricing_recommendation(
            product_id=pricing_request.product_id,
            product_name=product_name,
            current_price=current_price,
            base_price=base_price,
            inventory_level=inventory_level,
            product_name_ar=product_name_ar,
        )

        await db.commit()

        return DynamicPricingResponse(
            id=str(pricing.id),
            product_id=pricing.product_id,
            product_name=pricing.product_name,
            product_name_ar=pricing.product_name_ar,
            current_price=float(pricing.current_price),
            base_price=float(pricing.base_price),
            recommended_price=float(pricing.recommended_price),
            min_price=float(pricing.min_price),
            max_price=float(pricing.max_price),
            confidence_score=pricing.confidence_score,
            factors={
                "inventory_level": pricing.inventory_level,
                "competitor_avg_price": float(pricing.competitor_avg_price) if pricing.competitor_avg_price else None,
                "demand_level": pricing.demand_level,
                "elasticity_score": pricing.elasticity_score,
            },
            estimated_revenue_impact=float(pricing.estimated_revenue_impact) if pricing.estimated_revenue_impact else None,
            estimated_volume_change=pricing.estimated_volume_change,
            reasoning=pricing.reasoning,
            valid_from=pricing.valid_from,
            valid_until=pricing.valid_until,
            status=pricing.status,
            created_at=pricing.created_at,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_translate_message(
                f"Failed to generate pricing recommendation: {str(e)}",
                f"فشل في إنشاء توصية التسعير: {str(e)}",
                lang,
            ),
        )


@router.post("/pricing/approve", response_model=SuccessResponse)
async def approve_pricing_recommendation(
    request: Request,
    approval_request: PricingApprovalRequest,
    current_user: User = Depends(require_role(["admin", "pricing_manager"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve or reject pricing recommendation
    
    **Role required:** admin or pricing_manager
    """
    lang = _get_language(request)
    
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        if approval_request.action == "approve":
            pricing = await service.approve_pricing(
                pricing_id=approval_request.pricing_id,
                approved_by=current_user.email,
            )
            if not pricing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=_translate_message(
                        "Pricing recommendation not found",
                        "لم يتم العثور على توصية التسعير",
                        lang,
                    ),
                )
            await db.commit()
            message_en = "Pricing recommendation approved successfully"
            message_ar = "تمت الموافقة على توصية التسعير بنجاح"
        else:
            # Reject logic (update status to rejected)
            message_en = "Pricing recommendation rejected"
            message_ar = "تم رفض توصية التسعير"

        return SuccessResponse(
            success=True,
            message=_translate_message(message_en, message_ar, lang),
            message_ar=message_ar if lang == "en" else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}",
        )


@router.get("/pricing/recommendations", response_model=List[DynamicPricingResponse])
async def list_pricing_recommendations(
    request: Request,
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["admin", "pricing_manager", "analyst"])),
    db: AsyncSession = Depends(get_db),
):
    """List pricing recommendations with optional filters"""
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        recommendations = await service.get_pricing_recommendations(
            product_id=product_id, status=status_filter, limit=limit
        )

        return [
            DynamicPricingResponse(
                id=str(p.id),
                product_id=p.product_id,
                product_name=p.product_name,
                product_name_ar=p.product_name_ar,
                current_price=float(p.current_price),
                base_price=float(p.base_price),
                recommended_price=float(p.recommended_price),
                min_price=float(p.min_price),
                max_price=float(p.max_price),
                confidence_score=p.confidence_score,
                estimated_revenue_impact=float(p.estimated_revenue_impact) if p.estimated_revenue_impact else None,
                estimated_volume_change=p.estimated_volume_change,
                valid_from=p.valid_from,
                valid_until=p.valid_until,
                status=p.status,
                created_at=p.created_at,
            )
            for p in recommendations
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pricing recommendations: {str(e)}",
        )


# =============== Route Optimization Endpoints ===============


@router.post("/route/optimize", response_model=RouteOptimizationResponse, status_code=status.HTTP_201_CREATED)
async def optimize_delivery_route(
    request: Request,
    route_request: RouteOptimizationRequest,
    current_user: User = Depends(require_role(["admin", "logistics_manager", "user"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Optimize delivery route using AI
    
    **Supports:** English & Arabic (عربي)
    
    **Factors considered:**
    - Real-time traffic conditions
    - Delivery time windows
    - Vehicle capacity constraints
    - Driver performance metrics
    - Distance and cost optimization
    """
    lang = _get_language(request)
    
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        route = await service.optimize_route(
            route_name=route_request.route_name,
            origin=route_request.origin,
            destination=route_request.destination,
            waypoints=route_request.waypoints,
            vehicle_capacity_kg=route_request.vehicle_capacity_kg,
            cargo_weight_kg=route_request.cargo_weight_kg,
            route_name_ar=route_request.route_name_ar,
        )

        await db.commit()

        return RouteOptimizationResponse(
            id=str(route.id),
            route_name=route.route_name,
            route_name_ar=route.route_name_ar,
            origin=route.origin,
            destination=route.destination,
            optimal_path=route.optimal_path,
            estimated_duration_minutes=route.estimated_duration_minutes,
            estimated_distance_km=float(route.estimated_distance_km),
            estimated_cost=float(route.estimated_cost),
            traffic_level=route.traffic_level,
            traffic_delay_minutes=route.traffic_delay_minutes,
            best_departure_time=route.best_departure_time,
            stops_count=route.stops_count,
            status=route.status,
            created_at=route.created_at,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_translate_message(
                f"Failed to optimize route: {str(e)}",
                f"فشل في تحسين المسار: {str(e)}",
                lang,
            ),
        )


@router.get("/route/optimizations", response_model=List[RouteOptimizationResponse])
async def list_route_optimizations(
    request: Request,
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["admin", "logistics_manager", "analyst"])),
    db: AsyncSession = Depends(get_db),
):
    """List route optimizations with optional filters"""
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        routes = await service.get_route_optimizations(status=status_filter, limit=limit)

        return [
            RouteOptimizationResponse(
                id=str(r.id),
                route_name=r.route_name,
                route_name_ar=r.route_name_ar,
                origin=r.origin,
                destination=r.destination,
                optimal_path=r.optimal_path,
                estimated_duration_minutes=r.estimated_duration_minutes,
                estimated_distance_km=float(r.estimated_distance_km),
                estimated_cost=float(r.estimated_cost),
                traffic_level=r.traffic_level,
                traffic_delay_minutes=r.traffic_delay_minutes,
                best_departure_time=r.best_departure_time,
                stops_count=r.stops_count,
                status=r.status,
                created_at=r.created_at,
            )
            for r in routes
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve route optimizations: {str(e)}",
        )


# =============== Inventory Prediction Endpoints ===============


@router.post("/inventory/predict", response_model=InventoryPredictionResponse, status_code=status.HTTP_201_CREATED)
async def predict_inventory_needs(
    request: Request,
    inventory_request: InventoryPredictionRequest,
    current_user: User = Depends(require_role(["admin", "inventory_manager", "user"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Predict inventory needs and generate PO suggestions
    
    **Supports:** English & Arabic (عربي)
    
    **Features:**
    - Predictive restocking recommendations
    - Safety stock calculations
    - Economic Order Quantity (EOQ)
    - Purchase Order suggestions
    - Risk level assessment
    """
    lang = _get_language(request)
    
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        # In production, fetch actual product/warehouse data
        product_name = f"Product {inventory_request.product_id}"
        product_name_ar = f"منتج {inventory_request.product_id}"
        warehouse_name = f"Warehouse {inventory_request.warehouse_id}"

        prediction = await service.predict_inventory_needs(
            product_id=inventory_request.product_id,
            product_name=product_name,
            warehouse_id=inventory_request.warehouse_id,
            warehouse_name=warehouse_name,
            current_stock=inventory_request.current_stock,
            lead_time_days=inventory_request.lead_time_days,
            product_name_ar=product_name_ar,
        )

        await db.commit()

        return InventoryPredictionResponse(
            id=str(prediction.id),
            product_id=prediction.product_id,
            product_name=prediction.product_name,
            product_name_ar=prediction.product_name_ar,
            warehouse_id=prediction.warehouse_id,
            warehouse_name=prediction.warehouse_name,
            current_stock=float(prediction.current_stock),
            reorder_point=float(prediction.reorder_point),
            safety_stock=float(prediction.safety_stock),
            predicted_depletion_date=prediction.predicted_depletion_date,
            days_until_stockout=prediction.days_until_stockout,
            recommended_reorder_quantity=float(prediction.recommended_reorder_quantity),
            recommended_reorder_date=prediction.recommended_reorder_date,
            average_daily_demand=float(prediction.average_daily_demand),
            demand_volatility=prediction.demand_volatility,
            risk_level=prediction.risk_level,
            confidence_score=prediction.confidence_score,
            po_suggested=prediction.po_suggested,
            po_id=prediction.po_id,
            created_at=prediction.created_at,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_translate_message(
                f"Failed to predict inventory needs: {str(e)}",
                f"فشل في توقع احتياجات المخزون: {str(e)}",
                lang,
            ),
        )


@router.get("/inventory/predictions", response_model=List[InventoryPredictionResponse])
async def list_inventory_predictions(
    request: Request,
    warehouse_id: Optional[str] = Query(None, description="Filter by warehouse ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["admin", "inventory_manager", "analyst"])),
    db: AsyncSession = Depends(get_db),
):
    """List inventory predictions with optional filters"""
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        predictions = await service.get_inventory_predictions(
            warehouse_id=warehouse_id, risk_level=risk_level, limit=limit
        )

        return [
            InventoryPredictionResponse(
                id=str(p.id),
                product_id=p.product_id,
                product_name=p.product_name,
                product_name_ar=p.product_name_ar,
                warehouse_id=p.warehouse_id,
                warehouse_name=p.warehouse_name,
                current_stock=float(p.current_stock),
                reorder_point=float(p.reorder_point),
                safety_stock=float(p.safety_stock),
                predicted_depletion_date=p.predicted_depletion_date,
                days_until_stockout=p.days_until_stockout,
                recommended_reorder_quantity=float(p.recommended_reorder_quantity),
                recommended_reorder_date=p.recommended_reorder_date,
                average_daily_demand=float(p.average_daily_demand),
                demand_volatility=p.demand_volatility,
                risk_level=p.risk_level,
                confidence_score=p.confidence_score,
                po_suggested=p.po_suggested,
                po_id=p.po_id,
                created_at=p.created_at,
            )
            for p in predictions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve inventory predictions: {str(e)}",
        )


# =============== Customer Churn Endpoints ===============


@router.post("/churn/predict", response_model=CustomerChurnPredictionResponse, status_code=status.HTTP_201_CREATED)
async def predict_customer_churn(
    request: Request,
    churn_request: CustomerChurnPredictionRequest,
    current_user: User = Depends(require_role(["admin", "sales_manager", "analyst"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Predict customer churn probability and generate retention strategies
    
    **Supports:** English & Arabic (عربي)
    
    **Features:**
    - At-risk customer identification
    - Churn probability calculation
    - Personalized retention strategies
    - Priority-based action recommendations
    """
    lang = _get_language(request)
    
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        # In production, fetch actual customer data
        customer_name = f"Customer {churn_request.customer_id}"
        recency_days = 45  # Days since last order
        total_orders = 15
        lifetime_value = 12500.0

        prediction = await service.predict_customer_churn(
            customer_id=churn_request.customer_id,
            customer_name=customer_name,
            customer_type="outlet",
            recency_days=recency_days,
            total_orders=total_orders,
            lifetime_value=lifetime_value,
        )

        await db.commit()

        # Convert retention strategies
        retention_strategies = None
        if churn_request.include_recommendations and prediction.retention_strategy:
            retention_strategies = [
                RetentionStrategy(**strategy) for strategy in prediction.retention_strategy
            ]

        return CustomerChurnPredictionResponse(
            id=str(prediction.id),
            customer_id=prediction.customer_id,
            customer_name=prediction.customer_name,
            customer_type=prediction.customer_type,
            churn_probability=prediction.churn_probability,
            risk_level=prediction.risk_level,
            predicted_churn_date=prediction.predicted_churn_date,
            days_until_churn=prediction.days_until_churn,
            recency_days=prediction.recency_days,
            frequency_decline=prediction.frequency_decline,
            monetary_decline=prediction.monetary_decline,
            complaint_count=prediction.complaint_count,
            lifetime_value=float(prediction.lifetime_value) if prediction.lifetime_value else None,
            average_order_value=float(prediction.average_order_value) if prediction.average_order_value else None,
            total_orders=prediction.total_orders,
            retention_strategies=retention_strategies,
            recommended_discount=float(prediction.recommended_discount) if prediction.recommended_discount else None,
            recommended_contact_method=prediction.recommended_contact_method,
            priority_level=prediction.priority_level,
            confidence_score=prediction.confidence_score,
            created_at=prediction.created_at,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_translate_message(
                f"Failed to predict customer churn: {str(e)}",
                f"فشل في توقع تسرب العملاء: {str(e)}",
                lang,
            ),
        )


@router.post("/churn/action", response_model=SuccessResponse)
async def log_retention_action(
    request: Request,
    action_request: ChurnActionRequest,
    current_user: User = Depends(require_role(["admin", "sales_manager"])),
    db: AsyncSession = Depends(get_db),
):
    """Log retention action taken for at-risk customer"""
    lang = _get_language(request)
    
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        prediction = await service.log_churn_action(
            prediction_id=action_request.churn_prediction_id,
            action_type=action_request.action_type,
        )

        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_translate_message(
                    "Churn prediction not found",
                    "لم يتم العثور على توقع التسرب",
                    lang,
                ),
            )

        await db.commit()

        return SuccessResponse(
            success=True,
            message=_translate_message(
                "Retention action logged successfully",
                "تم تسجيل إجراء الاحتفاظ بنجاح",
                lang,
            ),
            message_ar="تم تسجيل إجراء الاحتفاظ بنجاح" if lang == "en" else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log action: {str(e)}",
        )


@router.get("/churn/predictions", response_model=List[CustomerChurnPredictionResponse])
async def list_churn_predictions(
    request: Request,
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    min_churn_probability: Optional[float] = Query(None, ge=0, le=1),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["admin", "sales_manager", "analyst"])),
    db: AsyncSession = Depends(get_db),
):
    """List customer churn predictions with optional filters"""
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        predictions = await service.get_churn_predictions(
            risk_level=risk_level,
            min_churn_probability=min_churn_probability,
            limit=limit,
        )

        return [
            CustomerChurnPredictionResponse(
                id=str(p.id),
                customer_id=p.customer_id,
                customer_name=p.customer_name,
                customer_type=p.customer_type,
                churn_probability=p.churn_probability,
                risk_level=p.risk_level,
                predicted_churn_date=p.predicted_churn_date,
                days_until_churn=p.days_until_churn,
                recency_days=p.recency_days,
                frequency_decline=p.frequency_decline,
                monetary_decline=p.monetary_decline,
                complaint_count=p.complaint_count,
                lifetime_value=float(p.lifetime_value) if p.lifetime_value else None,
                average_order_value=float(p.average_order_value) if p.average_order_value else None,
                total_orders=p.total_orders,
                recommended_discount=float(p.recommended_discount) if p.recommended_discount else None,
                recommended_contact_method=p.recommended_contact_method,
                priority_level=p.priority_level,
                confidence_score=p.confidence_score,
                created_at=p.created_at,
            )
            for p in predictions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve churn predictions: {str(e)}",
        )


# =============== Analytics Endpoints ===============


@router.get("/analytics/distribution", response_model=DistributionAnalyticsResponse)
async def get_distribution_analytics(
    request: Request,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_role(["admin", "analyst"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive distribution analytics
    
    **Bilingual Support:** English & Arabic (عربي)
    
    **Includes:**
    - Forecast metrics
    - Pricing optimization results
    - Route efficiency
    - Inventory management performance
    - Customer retention metrics
    """
    service = DistributionLincService(
        db=db, tenant_id=current_user.tenant_id, user_id=current_user.email
    )

    try:
        analytics = await service.get_distribution_analytics(
            start_date=start_date, end_date=end_date
        )

        return DistributionAnalyticsResponse(**analytics)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}",
        )
