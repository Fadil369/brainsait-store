"""
Schemas for Customer Portal API
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Dashboard
class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_orders: int
    available_products: int
    current_balance: float
    available_credit: float
    orders_in_transit: int
    low_stock_items: int
    change_percentage: float


# Inventory
class InventoryItem(BaseModel):
    """Inventory item details"""
    id: str
    name: str
    name_ar: str
    category: str
    stock: int
    reorder_level: int
    expiry_date: Optional[str] = None
    velocity: str  # fast, medium, slow
    last_restocked: str


class InventoryInsights(BaseModel):
    """Inventory insights summary"""
    items: List[InventoryItem]
    low_stock_count: int
    expiring_soon_count: int
    fast_moving_count: int


# Payment
class PaymentSummary(BaseModel):
    """Payment summary"""
    current_balance: float
    credit_limit: float
    available_credit: float
    due_date: str
    minimum_payment: float
    credit_utilization: float


class TransactionResponse(BaseModel):
    """Transaction details"""
    id: str
    date: str
    type: str  # payment, credit, refund
    amount: float
    balance: float
    description: str


# Promotions and Notifications
class PromotionResponse(BaseModel):
    """Promotion details"""
    id: str
    title: str
    title_ar: str
    discount: str
    valid_until: str
    description: str
    description_ar: str
    code: str
    status: str


class NotificationResponse(BaseModel):
    """Notification details"""
    id: str
    type: str  # order, promotion, payment, inventory
    title: str
    title_ar: str
    message: str
    message_ar: str
    timestamp: str
    read: bool


# AI Recommendations
class RecommendationResponse(BaseModel):
    """AI recommendation"""
    id: str
    type: str  # reorder, bundle, timing, seasonal
    title: str
    title_ar: str
    description: str
    description_ar: str
    action: str
    action_ar: str
    priority: str  # high, medium, low
    products: List[str]
    estimated_savings: float


# Complaints
class ComplaintCreate(BaseModel):
    """Create complaint request"""
    title: str
    category: str
    description: str
    priority: str = Field(default="medium", regex="^(low|medium|high)$")


class ComplaintUpdate(BaseModel):
    """Update complaint request"""
    status: Optional[str] = Field(None, regex="^(open|in-progress|resolved)$")
    description: Optional[str] = None


class ComplaintResponse(BaseModel):
    """Complaint details"""
    id: str
    title: str
    title_ar: str
    category: str
    category_ar: str
    description: str
    description_ar: str
    status: str
    priority: str
    created_at: str
    updated_at: str
    assigned_to: str
    messages: int


# Feedback
class FeedbackCreate(BaseModel):
    """Submit feedback"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    feature: Optional[str] = None


# Usage Analytics
class UsageAnalytics(BaseModel):
    """Usage analytics"""
    total_logins: int
    orders_placed: int
    average_session_duration: str
    most_used_feature: str
    period: str
