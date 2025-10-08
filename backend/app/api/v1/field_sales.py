"""
Field Sales API endpoints
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.field_sales import (
    SalesRepCreate,
    SalesRepUpdate,
    SalesRepResponse,
    SalesRepDashboard,
    OutletCheckInCreate,
    OutletCheckInUpdate,
    OutletCheckInResponse,
    VoiceOrderCreate,
    VoiceOrderResponse,
    CreditRequestCreate,
    CreditRequestUpdate,
    CreditRequestResponse,
    LeaderboardResponse,
    LeaderboardEntry,
    AchievementResponse,
    OfflineSyncData,
    OfflineSyncResponse,
)
from app.services.field_sales import FieldSalesService

router = APIRouter(prefix="/field-sales", tags=["Field Sales"])


# Sales Rep Endpoints
@router.post("/reps", response_model=SalesRepResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_rep(
    rep_data: SalesRepCreate,
    tenant_id: str = "default",  # TODO: Get from auth
    db: Session = Depends(get_db),
):
    """Create a new sales representative"""
    service = FieldSalesService(db)
    
    # Check if rep code already exists
    existing = service.get_sales_rep_by_code(rep_data.rep_code, tenant_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sales rep code already exists",
        )
    
    sales_rep = service.create_sales_rep(rep_data.dict(), tenant_id)
    return sales_rep


@router.get("/reps/{rep_id}", response_model=SalesRepResponse)
async def get_sales_rep(
    rep_id: UUID,
    db: Session = Depends(get_db),
):
    """Get sales rep by ID"""
    service = FieldSalesService(db)
    sales_rep = service.get_sales_rep(rep_id)
    
    if not sales_rep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found",
        )
    
    return sales_rep


@router.get("/reps/user/{user_id}", response_model=SalesRepResponse)
async def get_sales_rep_by_user(
    user_id: UUID,
    tenant_id: str = "default",  # TODO: Get from auth
    db: Session = Depends(get_db),
):
    """Get sales rep by user ID"""
    service = FieldSalesService(db)
    sales_rep = service.get_sales_rep_by_user_id(user_id, tenant_id)
    
    if not sales_rep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found for this user",
        )
    
    return sales_rep


@router.patch("/reps/{rep_id}", response_model=SalesRepResponse)
async def update_sales_rep(
    rep_id: UUID,
    update_data: SalesRepUpdate,
    db: Session = Depends(get_db),
):
    """Update sales rep information"""
    service = FieldSalesService(db)
    sales_rep = service.update_sales_rep(rep_id, update_data.dict(exclude_unset=True))
    
    if not sales_rep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found",
        )
    
    return sales_rep


# Dashboard Endpoint
@router.get("/dashboard/{rep_id}", response_model=SalesRepDashboard)
async def get_rep_dashboard(
    rep_id: UUID,
    db: Session = Depends(get_db),
):
    """Get comprehensive dashboard for sales rep"""
    service = FieldSalesService(db)
    dashboard = service.get_dashboard_data(rep_id)
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found",
        )
    
    return dashboard


# Check-in Endpoints
@router.post("/check-ins", response_model=OutletCheckInResponse, status_code=status.HTTP_201_CREATED)
async def create_check_in(
    check_in_data: OutletCheckInCreate,
    rep_id: UUID = Query(..., description="Sales rep ID"),
    tenant_id: str = "default",  # TODO: Get from auth
    db: Session = Depends(get_db),
):
    """Create outlet check-in with geofencing and photo"""
    service = FieldSalesService(db)
    
    # Verify sales rep exists
    sales_rep = service.get_sales_rep(rep_id)
    if not sales_rep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found",
        )
    
    check_in = service.create_check_in(rep_id, check_in_data.dict(), tenant_id)
    
    # Update gamification
    service.update_gamification(rep_id, "check_in")
    
    return check_in


@router.patch("/check-ins/{check_in_id}", response_model=OutletCheckInResponse)
async def update_check_in(
    check_in_id: UUID,
    update_data: OutletCheckInUpdate,
    db: Session = Depends(get_db),
):
    """Update check-in (e.g., check-out)"""
    service = FieldSalesService(db)
    check_in = service.update_check_in(check_in_id, update_data.dict(exclude_unset=True))
    
    if not check_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found",
        )
    
    # Update gamification if checking out
    if update_data.check_out_time:
        service.update_gamification(check_in.sales_rep_id, "check_out")
    
    return check_in


@router.get("/check-ins", response_model=List[OutletCheckInResponse])
async def get_check_ins(
    rep_id: UUID = Query(..., description="Sales rep ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get check-ins for a sales rep"""
    service = FieldSalesService(db)
    check_ins = service.get_rep_check_ins(rep_id, start_date, end_date, limit)
    return check_ins


# Voice Order Endpoints
@router.post("/voice-orders", response_model=VoiceOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_voice_order(
    voice_data: VoiceOrderCreate,
    rep_id: UUID = Query(..., description="Sales rep ID"),
    tenant_id: str = "default",  # TODO: Get from auth
    db: Session = Depends(get_db),
):
    """
    Create voice order for speech-to-text processing
    
    Supports Arabic and English voice input for order creation.
    The audio will be processed asynchronously.
    """
    service = FieldSalesService(db)
    
    # Verify sales rep exists
    sales_rep = service.get_sales_rep(rep_id)
    if not sales_rep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found",
        )
    
    voice_order = service.create_voice_order(rep_id, voice_data.dict(), tenant_id)
    return voice_order


@router.get("/voice-orders/{order_id}", response_model=VoiceOrderResponse)
async def get_voice_order(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    """Get voice order by ID"""
    from app.models.field_sales import VoiceOrder
    
    voice_order = db.query(VoiceOrder).filter(VoiceOrder.id == order_id).first()
    
    if not voice_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice order not found",
        )
    
    return voice_order


# Credit Request Endpoints
@router.post("/credit-requests", response_model=CreditRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_credit_request(
    credit_data: CreditRequestCreate,
    rep_id: UUID = Query(..., description="Sales rep ID"),
    tenant_id: str = "default",  # TODO: Get from auth
    db: Session = Depends(get_db),
):
    """
    Create credit request with AI-based assessment
    
    The system will automatically assess credit risk and provide recommendations.
    """
    service = FieldSalesService(db)
    
    # Verify sales rep exists
    sales_rep = service.get_sales_rep(rep_id)
    if not sales_rep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found",
        )
    
    credit_request = service.create_credit_request(rep_id, credit_data.dict(), tenant_id)
    return credit_request


@router.patch("/credit-requests/{credit_id}", response_model=CreditRequestResponse)
async def update_credit_request(
    credit_id: UUID,
    update_data: CreditRequestUpdate,
    decided_by: Optional[UUID] = Query(None, description="User ID making the decision"),
    db: Session = Depends(get_db),
):
    """Update credit request (approve/reject)"""
    service = FieldSalesService(db)
    credit_request = service.update_credit_request(
        credit_id, update_data.dict(exclude_unset=True), decided_by
    )
    
    if not credit_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit request not found",
        )
    
    # Update gamification if approved
    if update_data.status == "approved":
        service.update_gamification(credit_request.sales_rep_id, "credit_approved")
    
    return credit_request


@router.get("/credit-requests", response_model=List[CreditRequestResponse])
async def get_credit_requests(
    rep_id: UUID = Query(..., description="Sales rep ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get credit requests for a sales rep"""
    service = FieldSalesService(db)
    credit_requests = service.get_rep_credit_requests(rep_id, status, limit)
    return credit_requests


# Gamification Endpoints
@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    tenant_id: str = "default",  # TODO: Get from auth
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Get leaderboard for specified period
    
    Shows top performing sales reps based on sales, orders, and points.
    """
    service = FieldSalesService(db)
    leaderboard = service.get_leaderboard(tenant_id, period, limit)
    
    # Calculate period dates
    now = datetime.utcnow()
    if period == "daily":
        from datetime import timedelta
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)
    elif period == "weekly":
        from datetime import timedelta
        period_start = now - timedelta(days=now.weekday())
        period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=7)
    else:  # monthly
        from datetime import timedelta
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            period_end = now.replace(year=now.year + 1, month=1, day=1)
        else:
            period_end = now.replace(month=now.month + 1, day=1)
    
    # Format response
    entries = [
        LeaderboardEntry(
            rank=entry.rank,
            sales_rep_id=entry.sales_rep_id,
            rep_name=entry.sales_rep.user.full_name if entry.sales_rep and entry.sales_rep.user else "Unknown",
            total_sales=entry.total_sales,
            total_orders=entry.total_orders,
            points_earned=entry.points_earned,
            territory=entry.sales_rep.territory if entry.sales_rep else None,
        )
        for entry in leaderboard
    ]
    
    return LeaderboardResponse(
        period_type=period,
        period_start=period_start,
        period_end=period_end,
        entries=entries,
    )


@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    rep_id: Optional[UUID] = Query(None, description="Sales rep ID to include earned status"),
    tenant_id: str = "default",  # TODO: Get from auth
    db: Session = Depends(get_db),
):
    """Get all available achievements"""
    from app.models.field_sales import Achievement
    
    achievements = db.query(Achievement).filter(
        Achievement.tenant_id == tenant_id,
        Achievement.is_active == True,
    ).all()
    
    # Get earned badges if rep_id provided
    earned_badges = []
    if rep_id:
        service = FieldSalesService(db)
        sales_rep = service.get_sales_rep(rep_id)
        if sales_rep and sales_rep.badges:
            earned_badges = sales_rep.badges
    
    return [
        AchievementResponse(
            id=achievement.id,
            code=achievement.code,
            name=achievement.name,
            name_ar=achievement.name_ar,
            description=achievement.description,
            description_ar=achievement.description_ar,
            badge_type=achievement.badge_type,
            badge_icon=achievement.badge_icon,
            requirement_type=achievement.requirement_type,
            requirement_value=achievement.requirement_value,
            points_reward=achievement.points_reward,
            is_earned=achievement.code in earned_badges,
        )
        for achievement in achievements
    ]


# Offline Sync Endpoint
@router.post("/sync", response_model=OfflineSyncResponse)
async def sync_offline_data(
    sync_data: OfflineSyncData,
    rep_id: UUID = Query(..., description="Sales rep ID"),
    tenant_id: str = "default",  # TODO: Get from auth
    db: Session = Depends(get_db),
):
    """
    Sync offline data when connection is restored
    
    Accepts batched check-ins, voice orders, and credit requests.
    """
    service = FieldSalesService(db)
    
    # Verify sales rep exists
    sales_rep = service.get_sales_rep(rep_id)
    if not sales_rep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales rep not found",
        )
    
    synced_check_ins = 0
    synced_voice_orders = 0
    synced_credit_requests = 0
    failed_items = []
    
    # Sync check-ins
    if sync_data.check_ins:
        for check_in_data in sync_data.check_ins:
            try:
                service.create_check_in(rep_id, check_in_data.dict(), tenant_id)
                synced_check_ins += 1
            except Exception as e:
                failed_items.append({"type": "check_in", "error": str(e), "data": check_in_data.dict()})
    
    # Sync voice orders
    if sync_data.voice_orders:
        for voice_data in sync_data.voice_orders:
            try:
                service.create_voice_order(rep_id, voice_data.dict(), tenant_id)
                synced_voice_orders += 1
            except Exception as e:
                failed_items.append({"type": "voice_order", "error": str(e), "data": voice_data.dict()})
    
    # Sync credit requests
    if sync_data.credit_requests:
        for credit_data in sync_data.credit_requests:
            try:
                service.create_credit_request(rep_id, credit_data.dict(), tenant_id)
                synced_credit_requests += 1
            except Exception as e:
                failed_items.append({"type": "credit_request", "error": str(e), "data": credit_data.dict()})
    
    return OfflineSyncResponse(
        synced_check_ins=synced_check_ins,
        synced_voice_orders=synced_voice_orders,
        synced_credit_requests=synced_credit_requests,
        failed_items=failed_items,
        sync_completed_at=datetime.utcnow(),
    )


# AR Catalog Endpoints
@router.get("/ar-catalog/products")
async def get_ar_catalog_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get products with AR metadata for augmented reality visualization
    
    Returns product information optimized for AR preview on mobile devices.
    """
    from app.models.products import Product
    
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.limit(limit).all()
    
    # Add AR metadata
    ar_products = []
    for product in products:
        ar_products.append({
            "id": str(product.id),
            "name": product.name,
            "name_ar": product.name_ar,
            "description": product.description,
            "description_ar": product.description_ar,
            "price": float(product.price),
            "image_url": product.image_url,
            "ar_model_url": f"/ar/models/{product.id}.glb",  # Placeholder
            "ar_scale": 1.0,
            "ar_placement": "floor",  # floor or wall
        })
    
    return {"products": ar_products, "total": len(ar_products)}
