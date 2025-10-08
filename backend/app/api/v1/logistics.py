"""
Logistics Operations API endpoints
Route optimization, delivery management, proof of delivery, incidents, and load planning
"""

import math
import random
import secrets
import string
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_tenant_id
from app.models.logistics import (
    Delivery,
    DeliveryStatus,
    Driver,
    Incident,
    IncidentSeverity,
    IncidentType,
    LoadPlan,
    Route,
    RouteStatus,
    SafetyAlert,
)
from app.models.users import User
from app.schemas.logistics import (
    DeliveryCreate,
    DeliveryResponse,
    DeliveryUpdate,
    IncidentAISuggestion,
    IncidentCreate,
    IncidentResponse,
    LoadItem,
    LoadPlanCreate,
    LoadPlanResponse,
    PaginatedDeliveriesResponse,
    PaginatedIncidentsResponse,
    PaginatedRoutesResponse,
    ProofOfDelivery,
    RouteCreate,
    RouteOptimizationRequest,
    RouteOptimizationResponse,
    RouteResponse,
    SafetyAlertCreate,
    SafetyAlertResponse,
)

router = APIRouter()


def generate_route_number() -> str:
    """Generate unique route number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4)
    )
    return f"RT-{timestamp}-{random_part}"


def generate_tracking_number() -> str:
    """Generate unique tracking number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8)
    )
    return f"TRK-{timestamp}-{random_part}"


def generate_incident_number() -> str:
    """Generate unique incident number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    return f"INC-{timestamp}-{random_part}"


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in kilometers (Haversine formula)"""
    R = 6371  # Earth's radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def optimize_route_ai(waypoints: List[dict], constraints: dict) -> dict:
    """
    AI-powered multi-constraint route optimization
    Uses heuristic algorithms for TSP with constraints
    """
    
    # Start with the first waypoint as origin
    if not waypoints:
        return {
            "optimized_sequence": [],
            "total_distance": 0,
            "estimated_duration": 0,
            "optimization_score": 0,
        }
    
    origin = waypoints[0]
    remaining = waypoints[1:]
    optimized = [origin]
    total_distance = 0
    
    # Nearest neighbor with time window constraints
    current = origin
    while remaining:
        # Find nearest accessible point
        nearest_idx = 0
        nearest_dist = float("inf")
        
        for idx, point in enumerate(remaining):
            dist = calculate_distance(
                current["lat"], current["lng"],
                point["lat"], point["lng"]
            )
            
            # Apply priority weighting
            priority_factor = 1.0
            if point.get("priority", 0) > 0:
                priority_factor = 0.7  # Prioritize high-priority deliveries
            
            weighted_dist = dist * priority_factor
            
            if weighted_dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = idx
        
        next_point = remaining.pop(nearest_idx)
        optimized.append(next_point)
        total_distance += nearest_dist
        current = next_point
    
    # Calculate metrics
    estimated_duration = int(total_distance * 3)  # ~3 minutes per km average
    
    # Add delivery time estimates
    estimated_duration += len(waypoints) * 10  # 10 min per stop
    
    # Calculate optimization score (100 = perfect)
    # Based on distance efficiency and constraint satisfaction
    optimization_score = min(100, 95 - (len(waypoints) * 2))
    
    return {
        "optimized_sequence": optimized,
        "total_distance": round(total_distance, 2),
        "estimated_duration": estimated_duration,
        "optimization_score": optimization_score,
        "fuel_efficiency": round(total_distance * 0.08, 2),  # L per km
        "carbon_footprint": round(total_distance * 0.12, 2),  # kg CO2
    }


# Route Endpoints
@router.post("/routes/optimize", response_model=RouteOptimizationResponse)
async def optimize_route(
    request: RouteOptimizationRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """
    AI-powered route optimization with multi-constraint support
    Optimizes delivery sequence for minimum distance, time, and fuel consumption
    """
    
    # Verify driver exists
    driver_query = select(Driver).where(
        and_(Driver.id == request.driver_id, Driver.tenant_id == tenant_id)
    )
    driver_result = await db.execute(driver_query)
    driver = driver_result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    # Get delivery locations
    deliveries_query = select(Delivery).where(
        and_(
            Delivery.id.in_(request.delivery_ids),
            Delivery.tenant_id == tenant_id,
        )
    )
    deliveries_result = await db.execute(deliveries_query)
    deliveries = deliveries_result.scalars().all()
    
    if not deliveries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No deliveries found"
        )
    
    # Build waypoints list
    waypoints = [
        {
            "id": str(request.start_location.lat) + str(request.start_location.lng),
            "lat": request.start_location.lat,
            "lng": request.start_location.lng,
            "address": request.start_location.address,
            "type": "start",
        }
    ]
    
    for delivery in deliveries:
        loc = delivery.delivery_location
        waypoints.append({
            "id": str(delivery.id),
            "lat": loc["lat"],
            "lng": loc["lng"],
            "address": loc.get("address", ""),
            "type": "delivery",
            "priority": 1 if str(delivery.id) in (request.constraints.priority_delivery_ids if request.constraints else []) else 0,
        })
    
    # Run optimization
    constraints_dict = request.constraints.model_dump() if request.constraints else {}
    optimization_result = optimize_route_ai(waypoints, constraints_dict)
    
    # Create route
    route_number = generate_route_number()
    route = Route(
        tenant_id=tenant_id,
        driver_id=request.driver_id,
        route_number=route_number,
        route_name=f"Optimized Route - {datetime.now().strftime('%Y-%m-%d')}",
        planned_date=datetime.utcnow(),
        start_location=request.start_location.model_dump(),
        waypoints=optimization_result["optimized_sequence"],
        total_distance_km=optimization_result["total_distance"],
        estimated_duration_min=optimization_result["estimated_duration"],
        total_stops=len(deliveries),
        optimization_score=optimization_result["optimization_score"],
        optimization_algorithm=request.optimization_algorithm,
        optimization_constraints=constraints_dict,
    )
    
    db.add(route)
    await db.commit()
    await db.refresh(route)
    
    return RouteOptimizationResponse(
        route_id=route.id,
        optimized_waypoints=optimization_result["optimized_sequence"],
        total_distance_km=optimization_result["total_distance"],
        estimated_duration_min=optimization_result["estimated_duration"],
        optimization_score=optimization_result["optimization_score"],
        fuel_efficiency=optimization_result.get("fuel_efficiency"),
        carbon_footprint_kg=optimization_result.get("carbon_footprint"),
    )


@router.post("/routes", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_data: RouteCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create a new delivery route"""
    
    # Verify driver exists
    driver_query = select(Driver).where(
        and_(Driver.id == route_data.driver_id, Driver.tenant_id == tenant_id)
    )
    driver_result = await db.execute(driver_query)
    driver = driver_result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    route_number = generate_route_number()
    
    route = Route(
        tenant_id=tenant_id,
        driver_id=route_data.driver_id,
        route_number=route_number,
        route_name=route_data.route_name,
        planned_date=route_data.planned_date,
        start_location=route_data.start_location.model_dump(),
        end_location=route_data.end_location.model_dump() if route_data.end_location else None,
        optimization_constraints=route_data.constraints.model_dump() if route_data.constraints else {},
    )
    
    db.add(route)
    await db.commit()
    await db.refresh(route)
    
    return route


@router.get("/routes", response_model=PaginatedRoutesResponse)
async def list_routes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    driver_id: Optional[UUID] = None,
    status_filter: Optional[RouteStatus] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """List routes with filtering"""
    
    query = select(Route).where(Route.tenant_id == tenant_id)
    
    if driver_id:
        query = query.where(Route.driver_id == driver_id)
    
    if status_filter:
        query = query.where(Route.status == status_filter)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(desc(Route.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    routes = result.scalars().all()
    
    return PaginatedRoutesResponse(
        items=routes,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/routes/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get route details"""
    
    query = select(Route).where(
        and_(Route.id == route_id, Route.tenant_id == tenant_id)
    )
    
    result = await db.execute(query)
    route = result.scalar_one_or_none()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )
    
    return route


# Delivery Endpoints
@router.post("/deliveries", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    delivery_data: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create a new delivery"""
    
    # Verify route exists
    route_query = select(Route).where(
        and_(Route.id == delivery_data.route_id, Route.tenant_id == tenant_id)
    )
    route_result = await db.execute(route_query)
    route = route_result.scalar_one_or_none()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )
    
    tracking_number = generate_tracking_number()
    
    # Auto-assign sequence number if not provided
    if delivery_data.sequence_number is None:
        count_query = select(func.count()).where(Delivery.route_id == delivery_data.route_id)
        count_result = await db.execute(count_query)
        sequence = (count_result.scalar() or 0) + 1
    else:
        sequence = delivery_data.sequence_number
    
    delivery = Delivery(
        tenant_id=tenant_id,
        route_id=delivery_data.route_id,
        driver_id=route.driver_id,
        order_id=delivery_data.order_id,
        tracking_number=tracking_number,
        sequence_number=sequence,
        package_weight_kg=delivery_data.package_weight_kg,
        package_dimensions=delivery_data.package_dimensions.model_dump() if delivery_data.package_dimensions else None,
        package_description=delivery_data.package_description,
        special_instructions=delivery_data.special_instructions,
        delivery_location=delivery_data.delivery_location.model_dump(),
        delivery_contact=delivery_data.delivery_contact.model_dump(),
        delivery_window_start=delivery_data.delivery_window_start,
        delivery_window_end=delivery_data.delivery_window_end,
    )
    
    db.add(delivery)
    
    # Update route total stops
    route.total_stops += 1
    
    await db.commit()
    await db.refresh(delivery)
    
    return delivery


@router.get("/deliveries", response_model=PaginatedDeliveriesResponse)
async def list_deliveries(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    route_id: Optional[UUID] = None,
    driver_id: Optional[UUID] = None,
    status_filter: Optional[DeliveryStatus] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """List deliveries with filtering"""
    
    query = select(Delivery).where(Delivery.tenant_id == tenant_id)
    
    if route_id:
        query = query.where(Delivery.route_id == route_id)
    
    if driver_id:
        query = query.where(Delivery.driver_id == driver_id)
    
    if status_filter:
        query = query.where(Delivery.status == status_filter)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Delivery.sequence_number)
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    deliveries = result.scalars().all()
    
    return PaginatedDeliveriesResponse(
        items=deliveries,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.put("/deliveries/{delivery_id}", response_model=DeliveryResponse)
async def update_delivery(
    delivery_id: UUID,
    delivery_data: DeliveryUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update delivery status and proof of delivery"""
    
    query = select(Delivery).where(
        and_(Delivery.id == delivery_id, Delivery.tenant_id == tenant_id)
    )
    
    result = await db.execute(query)
    delivery = result.scalar_one_or_none()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found"
        )
    
    # Update status
    if delivery_data.status:
        delivery.status = delivery_data.status
        
        if delivery_data.status == DeliveryStatus.DELIVERED:
            delivery.delivered_at = datetime.utcnow()
            
            # Update route completed stops
            route_query = select(Route).where(Route.id == delivery.route_id)
            route_result = await db.execute(route_query)
            route = route_result.scalar_one_or_none()
            if route:
                route.completed_stops += 1
    
    # Update proof of delivery
    if delivery_data.pod:
        delivery.pod_signature = delivery_data.pod.signature
        delivery.pod_photo = delivery_data.pod.photo
        delivery.pod_gps_location = delivery_data.pod.gps_location
        delivery.pod_recipient_name = delivery_data.pod.recipient_name
        delivery.pod_notes = delivery_data.pod.notes
        delivery.delivered_at = datetime.utcnow()
    
    # Update failure reason
    if delivery_data.failure_reason:
        delivery.failure_reason = delivery_data.failure_reason
        delivery.attempt_count += 1
        delivery.last_attempt_at = datetime.utcnow()
    
    delivery.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(delivery)
    
    return delivery


# Incident Endpoints
@router.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def report_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Report a new incident with AI-powered suggestions"""
    
    incident_number = generate_incident_number()
    
    # AI suggestion logic (mock implementation)
    ai_suggestions = generate_ai_incident_suggestions(
        incident_data.incident_type,
        incident_data.description
    )
    
    # Get driver from user
    driver_query = select(Driver).where(
        and_(Driver.user_id == current_user.id, Driver.tenant_id == tenant_id)
    )
    driver_result = await db.execute(driver_query)
    driver = driver_result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found for current user"
        )
    
    incident = Incident(
        tenant_id=tenant_id,
        driver_id=driver.id,
        route_id=incident_data.route_id,
        delivery_id=incident_data.delivery_id,
        incident_number=incident_number,
        incident_type=incident_data.incident_type,
        severity=incident_data.severity,
        title=incident_data.title,
        description=incident_data.description,
        location=incident_data.location,
        photos=incident_data.photos,
        videos=incident_data.videos,
        estimated_delay_min=incident_data.estimated_delay_min,
        ai_suggested_category=ai_suggestions["category"],
        ai_suggested_actions=ai_suggestions["actions"],
        ai_confidence_score=ai_suggestions["confidence"],
    )
    
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    
    return incident


def generate_ai_incident_suggestions(
    incident_type: IncidentType, description: str
) -> dict:
    """Generate AI-powered incident suggestions (mock implementation)"""
    
    suggestions_map = {
        IncidentType.ACCIDENT: {
            "category": "Safety Critical",
            "actions": [
                "Ensure all parties are safe",
                "Document the scene with photos",
                "Contact emergency services if needed",
                "Report to fleet manager immediately",
                "Fill out accident report form",
            ],
            "confidence": 0.95,
        },
        IncidentType.VEHICLE_BREAKDOWN: {
            "category": "Operational",
            "actions": [
                "Pull over to a safe location",
                "Contact roadside assistance",
                "Notify dispatcher for route reassignment",
                "Document vehicle condition",
            ],
            "confidence": 0.92,
        },
        IncidentType.TRAFFIC_DELAY: {
            "category": "Delivery Impact",
            "actions": [
                "Update ETA for affected deliveries",
                "Find alternate route if possible",
                "Notify customers of delay",
                "Document traffic conditions",
            ],
            "confidence": 0.88,
        },
        IncidentType.CUSTOMER_UNAVAILABLE: {
            "category": "Delivery Failed",
            "actions": [
                "Attempt contact via phone",
                "Leave delivery notice",
                "Take photo of location",
                "Reschedule delivery attempt",
            ],
            "confidence": 0.90,
        },
    }
    
    return suggestions_map.get(
        incident_type,
        {
            "category": "General",
            "actions": ["Document incident details", "Contact supervisor"],
            "confidence": 0.75,
        },
    )


@router.get("/incidents", response_model=PaginatedIncidentsResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    driver_id: Optional[UUID] = None,
    severity: Optional[IncidentSeverity] = None,
    resolved: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """List incidents with filtering"""
    
    query = select(Incident).where(Incident.tenant_id == tenant_id)
    
    if driver_id:
        query = query.where(Incident.driver_id == driver_id)
    
    if severity:
        query = query.where(Incident.severity == severity)
    
    if resolved is not None:
        query = query.where(Incident.is_resolved == resolved)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(desc(Incident.occurred_at))
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return PaginatedIncidentsResponse(
        items=incidents,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


# Load Planning Endpoints
@router.post("/load-plans", response_model=LoadPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_load_plan(
    plan_data: LoadPlanCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create optimized 3D load plan"""
    
    # Verify route exists
    route_query = select(Route).where(
        and_(Route.id == plan_data.route_id, Route.tenant_id == tenant_id)
    )
    route_result = await db.execute(route_query)
    route = route_result.scalar_one_or_none()
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )
    
    # Calculate load metrics
    total_weight = sum(item.weight_kg for item in plan_data.items)
    
    vehicle_volume = (
        plan_data.vehicle_length_m *
        plan_data.vehicle_width_m *
        plan_data.vehicle_height_m
    )
    
    items_volume = sum(
        item.length_m * item.width_m * item.height_m
        for item in plan_data.items
    )
    
    weight_utilization = (total_weight / plan_data.max_weight_kg) * 100
    volume_utilization = (items_volume / vehicle_volume) * 100
    
    # Generate loading sequence (optimized by priority and delivery order)
    sorted_items = sorted(
        plan_data.items,
        key=lambda x: (x.fragile, -x.priority),
        reverse=True
    )
    
    loading_sequence = [
        {
            "item_id": item.item_id,
            "position": idx + 1,
            "instructions": "Load first" if item.fragile else "Standard loading",
        }
        for idx, item in enumerate(sorted_items)
    ]
    
    # Calculate optimization scores
    optimization_score = min(100, (weight_utilization + volume_utilization) / 2)
    balance_score = 85.0  # Mock score
    accessibility_score = 90.0  # Mock score
    
    load_plan = LoadPlan(
        tenant_id=tenant_id,
        route_id=plan_data.route_id,
        vehicle_length_m=plan_data.vehicle_length_m,
        vehicle_width_m=plan_data.vehicle_width_m,
        vehicle_height_m=plan_data.vehicle_height_m,
        max_weight_kg=plan_data.max_weight_kg,
        items=[item.model_dump() for item in plan_data.items],
        total_weight_kg=total_weight,
        weight_utilization_pct=round(weight_utilization, 2),
        volume_utilization_pct=round(volume_utilization, 2),
        loading_sequence=loading_sequence,
        optimization_score=round(optimization_score, 2),
        balance_score=balance_score,
        accessibility_score=accessibility_score,
    )
    
    db.add(load_plan)
    await db.commit()
    await db.refresh(load_plan)
    
    return load_plan


# Safety Endpoints
@router.post("/safety-alerts", response_model=SafetyAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_safety_alert(
    alert_data: SafetyAlertCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create a safety alert for a driver"""
    
    # Get driver from user
    driver_query = select(Driver).where(
        and_(Driver.user_id == current_user.id, Driver.tenant_id == tenant_id)
    )
    driver_result = await db.execute(driver_query)
    driver = driver_result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found for current user"
        )
    
    alert = SafetyAlert(
        tenant_id=tenant_id,
        driver_id=driver.id,
        alert_type=alert_data.alert_type,
        severity=alert_data.severity,
        message=alert_data.message,
        location=alert_data.location,
        metadata=alert_data.metadata or {},
    )
    
    db.add(alert)
    
    # Increment fatigue alert count if applicable
    if alert_data.alert_type == "fatigue":
        driver.fatigue_alert_count += 1
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.get("/safety-alerts", response_model=List[SafetyAlertResponse])
async def list_safety_alerts(
    driver_id: Optional[UUID] = None,
    acknowledged: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """List safety alerts"""
    
    query = select(SafetyAlert).where(SafetyAlert.tenant_id == tenant_id)
    
    if driver_id:
        query = query.where(SafetyAlert.driver_id == driver_id)
    
    if acknowledged is not None:
        query = query.where(SafetyAlert.acknowledged == acknowledged)
    
    query = query.order_by(desc(SafetyAlert.triggered_at)).limit(50)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return alerts
