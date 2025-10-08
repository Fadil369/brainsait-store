"""
Driver Management API endpoints
Handles driver profiles, registration, and status management
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_tenant_id,
    verify_rate_limit,
)
from app.models.logistics import Driver, DriverEarnings, DriverStatus, Incident, Route
from app.models.users import User
from app.schemas.logistics import (
    DriverCreate,
    DriverResponse,
    DriverStatsResponse,
    DriverUpdate,
    EarningsSummary,
    FatigueAnalysis,
    PaginatedDriversResponse,
)

router = APIRouter()


def generate_driver_code() -> str:
    """Generate unique driver code"""
    timestamp = datetime.now().strftime("%y%m")
    random_part = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    return f"DRV-{timestamp}-{random_part}"


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def register_driver(
    driver_data: DriverCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Register a new driver"""
    
    # Generate unique driver code
    driver_code = generate_driver_code()
    
    # Create driver
    driver = Driver(
        tenant_id=tenant_id,
        user_id=current_user.id,
        driver_code=driver_code,
        full_name=driver_data.full_name,
        phone=driver_data.phone,
        email=driver_data.email,
        national_id=driver_data.national_id,
        license_number=driver_data.license_number,
        license_type=driver_data.license_type,
        license_expiry=driver_data.license_expiry,
        vehicle_type=driver_data.vehicle_type,
        vehicle_make=driver_data.vehicle_make,
        vehicle_model=driver_data.vehicle_model,
        vehicle_year=driver_data.vehicle_year,
        vehicle_plate=driver_data.vehicle_plate,
        vehicle_capacity_kg=driver_data.vehicle_capacity_kg,
        vehicle_capacity_m3=driver_data.vehicle_capacity_m3,
        hourly_rate=driver_data.hourly_rate,
        per_delivery_rate=driver_data.per_delivery_rate,
        emergency_contact=driver_data.emergency_contact,
    )
    
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    
    return driver


@router.get("/", response_model=PaginatedDriversResponse)
async def list_drivers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[DriverStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """List all drivers with pagination and filtering"""
    
    # Build query
    query = select(Driver).where(
        and_(Driver.tenant_id == tenant_id, Driver.is_active == True)
    )
    
    # Apply filters
    if status_filter:
        query = query.where(Driver.status == status_filter)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Driver.full_name.ilike(search_term),
                Driver.driver_code.ilike(search_term),
                Driver.phone.ilike(search_term),
                Driver.vehicle_plate.ilike(search_term),
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(desc(Driver.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    drivers = result.scalars().all()
    
    return PaginatedDriversResponse(
        items=drivers,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get driver details"""
    
    query = select(Driver).where(
        and_(
            Driver.id == driver_id,
            Driver.tenant_id == tenant_id,
            Driver.is_active == True,
        )
    )
    
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    return driver


@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: UUID,
    driver_data: DriverUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update driver information"""
    
    query = select(Driver).where(
        and_(
            Driver.id == driver_id,
            Driver.tenant_id == tenant_id,
            Driver.is_active == True,
        )
    )
    
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    # Update fields
    update_data = driver_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(driver, field, value)
    
    driver.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(driver)
    
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_driver(
    driver_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Deactivate a driver (soft delete)"""
    
    query = select(Driver).where(
        and_(Driver.id == driver_id, Driver.tenant_id == tenant_id)
    )
    
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    driver.is_active = False
    driver.status = DriverStatus.OFFLINE
    driver.updated_at = datetime.utcnow()
    
    await db.commit()


@router.get("/{driver_id}/stats", response_model=DriverStatsResponse)
async def get_driver_stats(
    driver_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get driver performance statistics"""
    
    # Verify driver exists
    driver_query = select(Driver).where(
        and_(Driver.id == driver_id, Driver.tenant_id == tenant_id)
    )
    driver_result = await db.execute(driver_query)
    driver = driver_result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    # Calculate date ranges
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get today's stats
    today_earnings_query = select(func.coalesce(func.sum(DriverEarnings.total_amount), 0)).where(
        and_(
            DriverEarnings.driver_id == driver_id,
            DriverEarnings.date >= today_start,
        )
    )
    today_earnings_result = await db.execute(today_earnings_query)
    today_earnings = float(today_earnings_result.scalar() or 0)
    
    # Get week's stats
    week_earnings_query = select(func.coalesce(func.sum(DriverEarnings.total_amount), 0)).where(
        and_(
            DriverEarnings.driver_id == driver_id,
            DriverEarnings.date >= week_start,
        )
    )
    week_earnings_result = await db.execute(week_earnings_query)
    week_earnings = float(week_earnings_result.scalar() or 0)
    
    # Get month's stats
    month_earnings_query = select(func.coalesce(func.sum(DriverEarnings.total_amount), 0)).where(
        and_(
            DriverEarnings.driver_id == driver_id,
            DriverEarnings.date >= month_start,
        )
    )
    month_earnings_result = await db.execute(month_earnings_query)
    month_earnings = float(month_earnings_result.scalar() or 0)
    
    # Get active routes count
    active_routes_query = select(func.count()).where(
        and_(
            Route.driver_id == driver_id,
            Route.status.in_(["planned", "in_progress"]),
        )
    )
    active_routes_result = await db.execute(active_routes_query)
    active_routes = active_routes_result.scalar() or 0
    
    # Calculate completion rate
    completion_rate = 0.0
    if driver.total_deliveries > 0:
        completion_rate = (driver.successful_deliveries / driver.total_deliveries) * 100
    
    return DriverStatsResponse(
        driver_id=driver_id,
        today_deliveries=0,  # TODO: Implement delivery count
        week_deliveries=0,
        month_deliveries=driver.total_deliveries,
        today_earnings=today_earnings,
        week_earnings=week_earnings,
        month_earnings=month_earnings,
        current_rating=driver.rating,
        active_routes=active_routes,
        completion_rate=round(completion_rate, 2),
    )


@router.get("/{driver_id}/earnings", response_model=EarningsSummary)
async def get_driver_earnings(
    driver_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get driver earnings for a period"""
    
    # Verify driver exists
    driver_query = select(Driver).where(
        and_(Driver.id == driver_id, Driver.tenant_id == tenant_id)
    )
    driver_result = await db.execute(driver_query)
    driver = driver_result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    # Set default date range (current month)
    if not start_date:
        now = datetime.utcnow()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get earnings records
    query = select(DriverEarnings).where(
        and_(
            DriverEarnings.driver_id == driver_id,
            DriverEarnings.date >= start_date,
            DriverEarnings.date <= end_date,
        )
    ).order_by(DriverEarnings.date)
    
    result = await db.execute(query)
    earnings_records = result.scalars().all()
    
    # Calculate totals
    total_earnings = sum(e.total_amount for e in earnings_records)
    total_bonuses = sum(e.bonus_amount for e in earnings_records)
    total_deductions = sum(e.deduction_amount for e in earnings_records)
    net_earnings = total_earnings - total_deductions
    total_deliveries = sum(e.deliveries_completed for e in earnings_records)
    total_hours = sum(e.hours_worked or 0 for e in earnings_records)
    
    # Build breakdown
    breakdown = [
        {
            "date": e.date,
            "base_amount": e.base_amount,
            "bonus_amount": e.bonus_amount,
            "deduction_amount": e.deduction_amount,
            "total_amount": e.total_amount,
            "hours_worked": e.hours_worked,
            "deliveries_completed": e.deliveries_completed,
            "distance_traveled_km": e.distance_traveled_km,
            "on_time_bonus": e.on_time_bonus,
            "rating_bonus": e.rating_bonus,
            "efficiency_bonus": e.efficiency_bonus,
        }
        for e in earnings_records
    ]
    
    return EarningsSummary(
        driver_id=driver_id,
        period_start=start_date,
        period_end=end_date,
        total_earnings=total_earnings,
        total_bonuses=total_bonuses,
        total_deductions=total_deductions,
        net_earnings=net_earnings,
        deliveries_completed=total_deliveries,
        hours_worked=total_hours,
        average_rating=driver.rating,
        breakdown=breakdown,
    )


@router.get("/{driver_id}/fatigue-analysis", response_model=FatigueAnalysis)
async def analyze_driver_fatigue(
    driver_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Analyze driver fatigue and provide recommendations"""
    
    # Verify driver exists
    driver_query = select(Driver).where(
        and_(Driver.id == driver_id, Driver.tenant_id == tenant_id)
    )
    driver_result = await db.execute(driver_query)
    driver = driver_result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    # TODO: Implement actual fatigue analysis based on route data
    # For now, return mock data with safety recommendations
    
    hours_driven = 6.5
    continuous_drive = 180  # minutes
    
    # Simple fatigue scoring algorithm
    fatigue_score = min(100, (hours_driven / 8) * 50 + (continuous_drive / 240) * 50)
    
    recommendation = "Driver is within safe driving limits"
    break_required = False
    break_time = 0
    
    if fatigue_score > 70:
        recommendation = "CRITICAL: Driver must take immediate rest break"
        break_required = True
        break_time = 30
    elif fatigue_score > 50:
        recommendation = "WARNING: Driver should plan for a break soon"
        break_required = True
        break_time = 15
    elif continuous_drive > 180:
        recommendation = "Recommend 15-minute break after next delivery"
        break_required = True
        break_time = 15
    
    return FatigueAnalysis(
        driver_id=driver_id,
        hours_driven_today=hours_driven,
        continuous_drive_time_min=continuous_drive,
        fatigue_score=round(fatigue_score, 2),
        recommendation=recommendation,
        break_required=break_required,
        estimated_break_time_min=break_time,
    )


@router.post("/{driver_id}/status")
async def update_driver_status(
    driver_id: UUID,
    new_status: DriverStatus,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update driver availability status"""
    
    query = select(Driver).where(
        and_(Driver.id == driver_id, Driver.tenant_id == tenant_id)
    )
    
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found"
        )
    
    driver.status = new_status
    driver.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Driver status updated successfully", "status": new_status}
