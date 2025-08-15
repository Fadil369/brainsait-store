"""
Tenants API Router - Multi-tenant Management

Handles tenant configuration, settings, and management for the BrainSAIT Store platform.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_current_admin_user
from app.core.database import get_db
from app.core.tenant import get_tenant_config
from pydantic import BaseModel, Field

router = APIRouter()


# Tenant Schemas
class TenantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    domain: Optional[str] = Field(None, max_length=100)
    language: str = Field(default="en", pattern="^(en|ar)$")
    timezone: str = Field(default="Asia/Riyadh")
    currency: str = Field(default="SAR")
    is_active: bool = Field(default=True)


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    domain: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, pattern="^(en|ar)$")
    timezone: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    id: UUID
    features: Dict[str, Any]
    payment_config: Dict[str, Any]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TenantConfigResponse(BaseModel):
    tenant_id: UUID
    config: Dict[str, Any]
    features: Dict[str, Any]
    payment_methods: List[str]


# Tenant Management Endpoints


@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all tenants (Admin only)
    """
    # In a real implementation, this would query the tenants table
    # For now, return mock data
    return [
        {
            "id": UUID("00000000-0000-0000-0000-000000000001"),
            "name": "brainsait",
            "display_name": "BrainSAIT Store",
            "domain": "brainsait.com",
            "language": "en",
            "timezone": "Asia/Riyadh",
            "currency": "SAR",
            "is_active": True,
            "features": {
                "multi_language": True,
                "zatca_compliance": True,
                "mada_payments": True,
                "stc_pay": True,
                "sms_notifications": True,
            },
            "payment_config": {
                "stripe": {"enabled": True},
                "mada": {"enabled": True},
                "stc_pay": {"enabled": True},
                "paypal": {"enabled": True},
                "apple_pay": {"enabled": True},
            },
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z",
        }
    ]


@router.get("/current", response_model=TenantConfigResponse)
async def get_current_tenant_config(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Get current tenant configuration
    """
    tenant_id = current_user["tenant_id"]
    
    # Get tenant configuration
    config = get_tenant_config(str(tenant_id))
    
    # Extract available payment methods
    payment_methods = []
    if config.get("features", {}).get("mada_payments"):
        payment_methods.append("mada")
    if config.get("features", {}).get("stc_pay"):
        payment_methods.append("stc_pay")
    if config.get("payment_config", {}).get("stripe", {}).get("enabled"):
        payment_methods.append("stripe")
    if config.get("payment_config", {}).get("paypal", {}).get("enabled"):
        payment_methods.append("paypal")
    if config.get("payment_config", {}).get("apple_pay", {}).get("enabled"):
        payment_methods.append("apple_pay")
    
    return {
        "tenant_id": tenant_id,
        "config": config,
        "features": config.get("features", {}),
        "payment_methods": payment_methods,
    }


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get specific tenant by ID (Admin only)
    """
    # In a real implementation, this would query the database
    if str(tenant_id) == "00000000-0000-0000-0000-000000000001":
        return {
            "id": tenant_id,
            "name": "brainsait",
            "display_name": "BrainSAIT Store",
            "domain": "brainsait.com",
            "language": "en",
            "timezone": "Asia/Riyadh",
            "currency": "SAR",
            "is_active": True,
            "features": {
                "multi_language": True,
                "zatca_compliance": True,
                "mada_payments": True,
                "stc_pay": True,
                "sms_notifications": True,
            },
            "payment_config": {
                "stripe": {"enabled": True},
                "mada": {"enabled": True},
                "stc_pay": {"enabled": True},
            },
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z",
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Tenant not found"
    )


@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new tenant (Admin only)
    """
    # In a real implementation, this would create a new tenant in the database
    # For now, return mock response
    new_tenant_id = UUID("11111111-1111-1111-1111-111111111111")
    
    return {
        "id": new_tenant_id,
        "name": tenant_data.name,
        "display_name": tenant_data.display_name or tenant_data.name,
        "domain": tenant_data.domain,
        "language": tenant_data.language,
        "timezone": tenant_data.timezone,
        "currency": tenant_data.currency,
        "is_active": tenant_data.is_active,
        "features": {
            "multi_language": True,
            "zatca_compliance": True,
            "mada_payments": True,
            "stc_pay": True,
            "sms_notifications": True,
        },
        "payment_config": {
            "stripe": {"enabled": False},
            "mada": {"enabled": True},
            "stc_pay": {"enabled": True},
        },
        "created_at": "2023-12-01T10:00:00Z",
        "updated_at": "2023-12-01T10:00:00Z",
    }


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update tenant (Admin only)
    """
    # In a real implementation, this would update the tenant in the database
    # For now, return mock response
    if str(tenant_id) != "00000000-0000-0000-0000-000000000001":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return {
        "id": tenant_id,
        "name": tenant_data.name or "brainsait",
        "display_name": tenant_data.display_name or "BrainSAIT Store",
        "domain": tenant_data.domain or "brainsait.com",
        "language": tenant_data.language or "en",
        "timezone": tenant_data.timezone or "Asia/Riyadh",
        "currency": tenant_data.currency or "SAR",
        "is_active": tenant_data.is_active if tenant_data.is_active is not None else True,
        "features": {
            "multi_language": True,
            "zatca_compliance": True,
            "mada_payments": True,
            "stc_pay": True,
            "sms_notifications": True,
        },
        "payment_config": {
            "stripe": {"enabled": True},
            "mada": {"enabled": True},
            "stc_pay": {"enabled": True},
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-12-01T10:00:00Z",
    }


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate tenant (Admin only)
    
    Note: We don't actually delete tenants to preserve data integrity.
    Instead, we mark them as inactive.
    """
    if str(tenant_id) == "00000000-0000-0000-0000-000000000001":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate the default tenant"
        )
    
    # In a real implementation, this would mark the tenant as inactive
    return {"message": "Tenant deactivated successfully"}


# Tenant Features Management


@router.get("/{tenant_id}/features")
async def get_tenant_features(
    tenant_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    """
    Get tenant-specific features
    """
    # Ensure user has access to this tenant
    if current_user["tenant_id"] != tenant_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    config = get_tenant_config(str(tenant_id))
    return config.get("features", {})


@router.put("/{tenant_id}/features")
async def update_tenant_features(
    tenant_id: UUID,
    features: Dict[str, Any],
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update tenant features (Admin only)
    """
    # In a real implementation, this would update the tenant features in database
    valid_features = {
        "multi_language",
        "zatca_compliance", 
        "mada_payments",
        "stc_pay",
        "sms_notifications",
        "advanced_analytics",
        "api_access",
        "white_label",
    }
    
    # Validate feature keys
    invalid_features = set(features.keys()) - valid_features
    if invalid_features:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid features: {', '.join(invalid_features)}"
        )
    
    return {"message": "Tenant features updated successfully", "features": features}


# Tenant Analytics


@router.get("/{tenant_id}/analytics")
async def get_tenant_analytics(
    tenant_id: UUID,
    days: int = 30,
    current_user: dict = Depends(get_current_user),
):
    """
    Get tenant analytics and usage statistics
    """
    # Ensure user has access to this tenant
    if current_user["tenant_id"] != tenant_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mock analytics data
    return {
        "tenant_id": tenant_id,
        "period_days": days,
        "metrics": {
            "total_orders": 156,
            "total_revenue": 234567.89,
            "active_users": 45,
            "products_sold": 289,
            "conversion_rate": 3.2,
            "average_order_value": 1504.15,
        },
        "payment_methods": {
            "mada": {"count": 89, "revenue": 134567.12},
            "stc_pay": {"count": 34, "revenue": 56789.34},
            "stripe": {"count": 23, "revenue": 34567.89},
            "paypal": {"count": 10, "revenue": 8643.54},
        },
        "top_products": [
            {"name": "AI Business Assistant", "sales": 45, "revenue": 67425.55},
            {"name": "Digital Marketing Course", "sales": 32, "revenue": 95936.80},
            {"name": "E-commerce Template", "sales": 28, "revenue": 42140.00},
        ],
        "geographic_distribution": {
            "riyadh": {"orders": 67, "revenue": 101234.56},
            "jeddah": {"orders": 34, "revenue": 52341.78},
            "dammam": {"orders": 23, "revenue": 35678.90},
            "other": {"orders": 32, "revenue": 45312.65},
        },
    }