"""
Users API Router - User Management

Handles user registration, profile management, and user-related operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_current_admin_user, get_current_tenant
from app.core.database import get_db
from pydantic import BaseModel, Field, EmailStr

router = APIRouter()


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+966[5][0-9]{8}$')
    company: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="user", pattern="^(user|admin|manager)$")
    is_active: bool = Field(default=True)
    preferred_language: str = Field(default="en", pattern="^(en|ar)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+966[5][0-9]{8}$')
    company: Optional[str] = Field(None, max_length=100)
    preferred_language: Optional[str] = Field(None, pattern="^(en|ar)$")
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str]
    company: Optional[str]
    role: str
    is_active: bool
    preferred_language: str
    tenant_id: UUID
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+966[5][0-9]{8}$')
    company: Optional[str] = Field(None, max_length=100)
    preferred_language: Optional[str] = Field(None, pattern="^(en|ar)$")


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserActivity(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# User Management Endpoints


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    List users in current tenant (Admin only)
    """
    # Mock user data for the current implementation
    mock_users = [
        {
            "id": UUID("22222222-2222-2222-2222-222222222222"),
            "email": "admin@brainsait.com",
            "name": "Admin User",
            "phone": "+966501234567",
            "company": "BrainSAIT",
            "role": "admin",
            "is_active": True,
            "preferred_language": "en",
            "tenant_id": tenant_id,
            "last_login": datetime.now(),
            "created_at": datetime(2023, 1, 1),
            "updated_at": datetime.now(),
        },
        {
            "id": UUID("33333333-3333-3333-3333-333333333333"),
            "email": "user@brainsait.com",
            "name": "Test User",
            "phone": "+966509876543",
            "company": "Test Company",
            "role": "user",
            "is_active": True,
            "preferred_language": "ar",
            "tenant_id": tenant_id,
            "last_login": datetime.now(),
            "created_at": datetime(2023, 6, 1),
            "updated_at": datetime.now(),
        },
    ]
    
    # Apply filters
    filtered_users = mock_users
    
    if search:
        filtered_users = [
            user for user in filtered_users
            if search.lower() in user["name"].lower() or search.lower() in user["email"].lower()
        ]
    
    if role:
        filtered_users = [user for user in filtered_users if user["role"] == role]
    
    if is_active is not None:
        filtered_users = [user for user in filtered_users if user["is_active"] == is_active]
    
    # Apply pagination
    return filtered_users[skip:skip + limit]


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user's profile
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "phone": "+966501234567",
        "company": "BrainSAIT",
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "preferred_language": "en",
        "tenant_id": current_user["tenant_id"],
        "last_login": datetime.now(),
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime.now(),
    }


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile
    """
    # In a real implementation, this would update the user in the database
    updated_user = {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": profile_data.name or current_user["name"],
        "phone": profile_data.phone or "+966501234567",
        "company": profile_data.company or "BrainSAIT",
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "preferred_language": profile_data.preferred_language or "en",
        "tenant_id": current_user["tenant_id"],
        "last_login": datetime.now(),
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime.now(),
    }
    
    return updated_user


@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change current user's password
    """
    # In a real implementation, this would:
    # 1. Verify the current password
    # 2. Hash the new password
    # 3. Update the database
    # 4. Invalidate existing sessions
    
    # Mock password validation
    if len(password_data.current_password) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is required"
        )
    
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    return {"message": "Password changed successfully"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get specific user by ID (Admin only)
    """
    # Mock user data
    if str(user_id) == "22222222-2222-2222-2222-222222222222":
        return {
            "id": user_id,
            "email": "admin@brainsait.com",
            "name": "Admin User",
            "phone": "+966501234567",
            "company": "BrainSAIT",
            "role": "admin",
            "is_active": True,
            "preferred_language": "en",
            "tenant_id": tenant_id,
            "last_login": datetime.now(),
            "created_at": datetime(2023, 1, 1),
            "updated_at": datetime.now(),
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new user (Admin only)
    """
    # In a real implementation, this would:
    # 1. Check if email already exists
    # 2. Hash the password
    # 3. Create user in database
    # 4. Send welcome email
    
    new_user_id = UUID("44444444-4444-4444-4444-444444444444")
    
    return {
        "id": new_user_id,
        "email": user_data.email,
        "name": user_data.name,
        "phone": user_data.phone,
        "company": user_data.company,
        "role": user_data.role,
        "is_active": user_data.is_active,
        "preferred_language": user_data.preferred_language,
        "tenant_id": tenant_id,
        "last_login": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user (Admin only)
    """
    # In a real implementation, this would update the user in the database
    if str(user_id) != "22222222-2222-2222-2222-222222222222":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user_id,
        "email": "admin@brainsait.com",
        "name": user_data.name or "Admin User",
        "phone": user_data.phone or "+966501234567",
        "company": user_data.company or "BrainSAIT",
        "role": "admin",
        "is_active": user_data.is_active if user_data.is_active is not None else True,
        "preferred_language": user_data.preferred_language or "en",
        "tenant_id": tenant_id,
        "last_login": datetime.now(),
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime.now(),
    }


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate user (Admin only)
    
    Note: We don't actually delete users to preserve data integrity.
    Instead, we mark them as inactive.
    """
    if str(user_id) == str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # In a real implementation, this would mark the user as inactive
    return {"message": "User deactivated successfully"}


# User Activity and Analytics


@router.get("/{user_id}/activity", response_model=List[UserActivity])
async def get_user_activity(
    user_id: UUID,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user activity log
    Users can only view their own activity, admins can view any user's activity
    """
    if str(user_id) != str(current_user["id"]) and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock activity data
    activities = [
        {
            "id": UUID("55555555-5555-5555-5555-555555555555"),
            "user_id": user_id,
            "action": "login",
            "details": {"method": "email", "success": True},
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "timestamp": datetime.now(),
        },
        {
            "id": UUID("66666666-6666-6666-6666-666666666666"),
            "user_id": user_id,
            "action": "purchase",
            "details": {"order_id": "ORD-2023-001", "amount": 1499.99, "currency": "SAR"},
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "timestamp": datetime.now(),
        },
    ]
    
    return activities[:limit]


@router.get("/me/analytics")
async def get_user_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user's analytics and usage statistics
    """
    return {
        "user_id": current_user["id"],
        "period_days": days,
        "metrics": {
            "total_orders": 12,
            "total_spent": 18567.89,
            "products_purchased": 23,
            "login_count": 45,
            "last_login": datetime.now().isoformat(),
            "account_age_days": 120,
        },
        "favorite_categories": [
            {"category": "ai", "purchases": 8, "spent": 12000.00},
            {"category": "courses", "purchases": 3, "spent": 4500.00},
            {"category": "templates", "purchases": 2, "spent": 2067.89},
        ],
        "payment_methods_used": {
            "mada": {"count": 8, "amount": 12456.78},
            "stc_pay": {"count": 3, "amount": 4567.89},
            "stripe": {"count": 1, "amount": 1543.22},
        },
        "monthly_activity": {
            "2023-10": {"orders": 3, "spent": 4567.89},
            "2023-11": {"orders": 5, "spent": 7890.12},
            "2023-12": {"orders": 4, "spent": 6109.88},
        },
    }


# User Role Management


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    new_role: str = Field(..., pattern="^(user|admin|manager)$"),
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user role (Admin only)
    """
    if str(user_id) == str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    # In a real implementation, this would update the user's role in the database
    return {"message": f"User role updated to {new_role}", "user_id": user_id, "new_role": new_role}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate user account (Admin only)
    """
    # In a real implementation, this would activate the user in the database
    return {"message": "User activated successfully", "user_id": user_id}