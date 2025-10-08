"""
Customer Portal API endpoints for SSDP outlet owners
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_language,
    get_tenant_id,
    verify_rate_limit,
)
from app.models.orders import Order, OrderItem
from app.models.products import Product
from app.models.users import User
from app.schemas.customer_portal import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate,
    DashboardStats,
    InventoryItem,
    InventoryInsights,
    NotificationResponse,
    PaymentSummary,
    PromotionResponse,
    RecommendationResponse,
    TransactionResponse,
)

router = APIRouter()


# Dashboard Overview
@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    language: str = Depends(get_language),
):
    """Get dashboard statistics for customer portal"""
    
    # Get total orders
    total_orders_query = select(func.count(Order.id)).where(
        and_(
            Order.user_id == current_user.id,
            Order.tenant_id == tenant_id
        )
    )
    total_orders_result = await db.execute(total_orders_query)
    total_orders = total_orders_result.scalar() or 0
    
    # Get orders in transit
    in_transit_query = select(func.count(Order.id)).where(
        and_(
            Order.user_id == current_user.id,
            Order.tenant_id == tenant_id,
            Order.status.in_(['processing', 'shipped'])
        )
    )
    in_transit_result = await db.execute(in_transit_query)
    in_transit = in_transit_result.scalar() or 0
    
    # Get current balance (mock for now)
    current_balance = 45890.00
    available_credit = 54110.00
    
    return DashboardStats(
        total_orders=total_orders,
        available_products=432,  # Mock value
        current_balance=current_balance,
        available_credit=available_credit,
        orders_in_transit=in_transit,
        low_stock_items=3,  # Mock value
        change_percentage=12.5
    )


# Inventory Insights
@router.get("/inventory", response_model=InventoryInsights)
async def get_inventory_insights(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get inventory insights including low stock and expiring items"""
    
    # In a real implementation, this would query the inventory database
    # For now, return mock data
    items = [
        InventoryItem(
            id="P001",
            name="Product A",
            name_ar="منتج أ",
            category="Electronics",
            stock=45,
            reorder_level=50,
            expiry_date="2025-06-15",
            velocity="fast",
            last_restocked="2025-01-10"
        ),
        InventoryItem(
            id="P002",
            name="Product B",
            name_ar="منتج ب",
            category="Food",
            stock=15,
            reorder_level=30,
            expiry_date="2025-02-28",
            velocity="medium",
            last_restocked="2025-01-12"
        ),
    ]
    
    return InventoryInsights(
        items=items,
        low_stock_count=2,
        expiring_soon_count=1,
        fast_moving_count=1
    )


# Payment Management
@router.get("/payment-summary", response_model=PaymentSummary)
async def get_payment_summary(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get payment summary including credit info and transactions"""
    
    return PaymentSummary(
        current_balance=45890.00,
        credit_limit=100000.00,
        available_credit=54110.00,
        due_date="2025-02-15",
        minimum_payment=5000.00,
        credit_utilization=45.89
    )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    period: str = Query("month", pattern="^(week|month|year)$"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get transaction history"""
    
    # Mock transactions
    transactions = [
        TransactionResponse(
            id="TXN-001",
            date="2025-01-15",
            type="payment",
            amount=-15000.00,
            balance=45890.00,
            description="Order payment"
        ),
        TransactionResponse(
            id="TXN-002",
            date="2025-01-10",
            type="credit",
            amount=20000.00,
            balance=60890.00,
            description="Credit adjustment"
        ),
    ]
    
    return transactions


# Promotions and Notifications
@router.get("/promotions", response_model=List[PromotionResponse])
async def get_active_promotions(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    language: str = Depends(get_language),
):
    """Get active promotions"""
    
    promotions = [
        PromotionResponse(
            id="PROMO-001",
            title="New Year Special",
            title_ar="عرض رأس السنة الخاص",
            discount="20%",
            valid_until="2025-01-31",
            description="Get 20% off on all electronics",
            description_ar="احصل على خصم 20٪ على جميع الإلكترونيات",
            code="NEWYEAR2025",
            status="active"
        ),
    ]
    
    return promotions


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get user notifications"""
    
    notifications = [
        NotificationResponse(
            id="NOTIF-001",
            type="order",
            title="Order Shipped",
            title_ar="تم شحن الطلب",
            message="Your order ORD-12345 has been shipped",
            message_ar="تم شحن طلبك ORD-12345",
            timestamp="2 hours ago",
            read=False
        ),
    ]
    
    if unread_only:
        notifications = [n for n in notifications if not n.read]
    
    return notifications


# AI Recommendations
@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_ai_recommendations(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    language: str = Depends(get_language),
):
    """Get AI-powered recommendations for ordering and inventory"""
    
    recommendations = [
        RecommendationResponse(
            id="REC-001",
            type="reorder",
            title="Reorder Suggestion",
            title_ar="اقتراح إعادة الطلب",
            description="Based on your ordering patterns, you may run out of Product A in 5 days",
            description_ar="بناءً على أنماط الطلب الخاصة بك، قد تنفد من المنتج أ في 5 أيام",
            action="Order Now",
            action_ar="اطلب الآن",
            priority="high",
            products=["Product A", "Product B"],
            estimated_savings=450.00
        ),
    ]
    
    return recommendations


# Complaint Management
@router.post("/complaints", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Submit a new complaint"""
    
    # In a real implementation, this would create a complaint in the database
    # For now, return a mock response
    return ComplaintResponse(
        id="CMP-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        title=complaint.title,
        title_ar=complaint.title,
        category=complaint.category,
        category_ar=complaint.category,
        description=complaint.description,
        description_ar=complaint.description,
        status="open",
        priority=complaint.priority,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        assigned_to="Pending Assignment",
        messages=0
    )


@router.get("/complaints", response_model=List[ComplaintResponse])
async def get_complaints(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get user complaints"""
    
    complaints = [
        ComplaintResponse(
            id="CMP-001",
            title="Damaged Product Received",
            title_ar="تم استلام منتج تالف",
            category="Quality",
            category_ar="الجودة",
            description="Product A arrived with packaging damage",
            description_ar="وصل المنتج أ مع تلف في التغليف",
            status="in-progress",
            priority="high",
            created_at="2025-01-14",
            updated_at="2025-01-15",
            assigned_to="Support Team",
            messages=3
        ),
    ]
    
    if status_filter:
        complaints = [c for c in complaints if c.status == status_filter]
    
    return complaints


@router.patch("/complaints/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: str,
    complaint_update: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update a complaint"""
    
    # In a real implementation, this would update the complaint in the database
    # For now, return a mock response
    return ComplaintResponse(
        id=complaint_id,
        title="Updated Complaint",
        title_ar="شكوى محدثة",
        category="Quality",
        category_ar="الجودة",
        description="Updated description",
        description_ar="وصف محدث",
        status=complaint_update.status or "open",
        priority="medium",
        created_at="2025-01-14",
        updated_at=datetime.now().isoformat(),
        assigned_to="Support Team",
        messages=3
    )


# Analytics and Feedback
@router.post("/feedback")
async def submit_feedback(
    rating: int = Query(..., ge=1, le=5),
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Submit feedback for the customer portal"""
    
    # In a real implementation, this would store feedback in the database
    return {"message": "Feedback received successfully", "rating": rating}


@router.get("/usage-analytics")
async def get_usage_analytics(
    period: str = Query("month", pattern="^(week|month|year)$"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get usage analytics for the customer portal"""
    
    return {
        "total_logins": 45,
        "orders_placed": 12,
        "average_session_duration": "8m 23s",
        "most_used_feature": "ordering",
        "period": period
    }
