"""
Integrations API Router - Third-party Integration Management

Handles external service integrations, API connections, and integration health monitoring.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_current_admin_user, get_current_tenant
from app.core.database import get_db
from pydantic import BaseModel, Field

router = APIRouter()


# Integration Schemas
class IntegrationConfig(BaseModel):
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    webhook_url: Optional[str] = None
    settings: Dict[str, Any] = {}


class IntegrationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    provider: str = Field(..., pattern="^(stripe|paypal|mada|stc_pay|zatca|sms|email|analytics)$")
    config: IntegrationConfig
    is_active: bool = Field(default=True)
    auto_sync: bool = Field(default=False)


class IntegrationCreate(IntegrationBase):
    pass


class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    config: Optional[IntegrationConfig] = None
    is_active: Optional[bool] = None
    auto_sync: Optional[bool] = None


class IntegrationResponse(IntegrationBase):
    id: UUID
    tenant_id: UUID
    status: str
    last_sync: Optional[datetime]
    health_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationHealth(BaseModel):
    integration_id: UUID
    provider: str
    status: str
    last_check: datetime
    response_time_ms: Optional[float]
    error_message: Optional[str]
    uptime_percentage: float


class WebhookLog(BaseModel):
    id: UUID
    integration_id: UUID
    event_type: str
    payload: Dict[str, Any]
    response_status: int
    processing_time_ms: float
    created_at: datetime

    class Config:
        from_attributes = True


# Integration Management


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(
    provider: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    List integrations for current tenant
    """
    # Mock integration data
    integrations = [
        {
            "id": UUID("integ111-2222-3333-4444-555555555555"),
            "tenant_id": tenant_id,
            "name": "Stripe Payment Gateway",
            "provider": "stripe",
            "config": {
                "api_key": "pk_test_***",
                "secret_key": "sk_test_***",
                "webhook_url": "https://api.brainsait.com/webhooks/stripe",
                "settings": {"currency": "SAR", "capture_method": "automatic"}
            },
            "is_active": True,
            "auto_sync": True,
            "status": "connected",
            "last_sync": datetime.now(),
            "health_status": "healthy",
            "created_at": datetime(2023, 6, 1),
            "updated_at": datetime.now(),
        },
        {
            "id": UUID("integ222-3333-4444-5555-666666666666"),
            "tenant_id": tenant_id,
            "name": "ZATCA E-Invoicing",
            "provider": "zatca",
            "config": {
                "api_key": "zatca_***",
                "endpoint_url": "https://api.zatca.gov.sa",
                "settings": {"company_id": "300012345600003", "environment": "production"}
            },
            "is_active": True,
            "auto_sync": False,
            "status": "connected",
            "last_sync": datetime.now(),
            "health_status": "healthy",
            "created_at": datetime(2023, 7, 15),
            "updated_at": datetime.now(),
        },
        {
            "id": UUID("integ333-4444-5555-6666-777777777777"),
            "tenant_id": tenant_id,
            "name": "STC Pay Digital Wallet",
            "provider": "stc_pay",
            "config": {
                "api_key": "stc_***",
                "secret_key": "stc_secret_***",
                "endpoint_url": "https://api.stcpay.com.sa",
                "settings": {"merchant_id": "STC123456", "callback_url": "https://brainsait.com/callback"}
            },
            "is_active": True,
            "auto_sync": True,
            "status": "connected",
            "last_sync": datetime.now(),
            "health_status": "warning",
            "created_at": datetime(2023, 8, 1),
            "updated_at": datetime.now(),
        },
    ]
    
    if provider:
        integrations = [i for i in integrations if i["provider"] == provider]
    
    if is_active is not None:
        integrations = [i for i in integrations if i["is_active"] == is_active]
    
    return integrations


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get specific integration
    """
    if str(integration_id) == "integ111-2222-3333-4444-555555555555":
        return {
            "id": integration_id,
            "tenant_id": tenant_id,
            "name": "Stripe Payment Gateway",
            "provider": "stripe",
            "config": {
                "api_key": "pk_test_***",
                "secret_key": "sk_test_***",
                "webhook_url": "https://api.brainsait.com/webhooks/stripe",
                "settings": {"currency": "SAR", "capture_method": "automatic"}
            },
            "is_active": True,
            "auto_sync": True,
            "status": "connected",
            "last_sync": datetime.now(),
            "health_status": "healthy",
            "created_at": datetime(2023, 6, 1),
            "updated_at": datetime.now(),
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Integration not found"
    )


@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    integration_data: IntegrationCreate,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new integration (Admin only)
    """
    # In a real implementation, this would:
    # 1. Validate API credentials
    # 2. Test connection to provider
    # 3. Store encrypted credentials
    # 4. Set up webhooks if needed
    
    new_integration_id = UUID("integ444-5555-6666-7777-888888888888")
    
    return {
        "id": new_integration_id,
        "tenant_id": tenant_id,
        "name": integration_data.name,
        "provider": integration_data.provider,
        "config": integration_data.config,
        "is_active": integration_data.is_active,
        "auto_sync": integration_data.auto_sync,
        "status": "connecting",
        "last_sync": None,
        "health_status": "checking",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    integration_data: IntegrationUpdate,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Update integration (Admin only)
    """
    # Mock update
    return {
        "id": integration_id,
        "tenant_id": tenant_id,
        "name": integration_data.name or "Updated Integration",
        "provider": "stripe",  # Would be fetched from database
        "config": integration_data.config or {"api_key": "***"},
        "is_active": integration_data.is_active if integration_data.is_active is not None else True,
        "auto_sync": integration_data.auto_sync if integration_data.auto_sync is not None else False,
        "status": "connected",
        "last_sync": datetime.now(),
        "health_status": "healthy",
        "created_at": datetime(2023, 6, 1),
        "updated_at": datetime.now(),
    }


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete integration (Admin only)
    """
    # In a real implementation, this would:
    # 1. Disable webhooks
    # 2. Clean up API connections
    # 3. Archive integration data
    
    return {"message": "Integration deleted successfully"}


# Integration Testing and Health


@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Test integration connection (Admin only)
    """
    # Mock connection test
    return {
        "integration_id": integration_id,
        "test_result": "success",
        "response_time_ms": 234.5,
        "status_code": 200,
        "message": "Connection test successful",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/{integration_id}/health", response_model=IntegrationHealth)
async def get_integration_health(
    integration_id: UUID,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get integration health status
    """
    return {
        "integration_id": integration_id,
        "provider": "stripe",
        "status": "healthy",
        "last_check": datetime.now(),
        "response_time_ms": 156.7,
        "error_message": None,
        "uptime_percentage": 99.8,
    }


@router.get("/health/overview")
async def get_integrations_health_overview(
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get health overview for all integrations
    """
    return {
        "tenant_id": tenant_id,
        "total_integrations": 5,
        "healthy": 4,
        "warning": 1,
        "error": 0,
        "overall_health": "good",
        "integrations": [
            {
                "id": "integ111-2222-3333-4444-555555555555",
                "name": "Stripe Payment Gateway",
                "provider": "stripe",
                "status": "healthy",
                "uptime": 99.9,
            },
            {
                "id": "integ222-3333-4444-5555-666666666666",
                "name": "ZATCA E-Invoicing",
                "provider": "zatca",
                "status": "healthy",
                "uptime": 98.5,
            },
            {
                "id": "integ333-4444-5555-6666-777777777777",
                "name": "STC Pay Digital Wallet",
                "provider": "stc_pay",
                "status": "warning",
                "uptime": 95.2,
            },
        ],
    }


# Webhook Management


@router.get("/{integration_id}/webhooks", response_model=List[WebhookLog])
async def get_webhook_logs(
    integration_id: UUID,
    limit: int = 50,
    event_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get webhook logs for integration
    """
    # Mock webhook logs
    logs = [
        {
            "id": UUID("webhook1-1111-2222-3333-444444444444"),
            "integration_id": integration_id,
            "event_type": "payment.succeeded",
            "payload": {
                "id": "pi_test_123",
                "amount": 15000,
                "currency": "sar",
                "status": "succeeded"
            },
            "response_status": 200,
            "processing_time_ms": 145.3,
            "created_at": datetime.now(),
        },
        {
            "id": UUID("webhook2-2222-3333-4444-555555555555"),
            "integration_id": integration_id,
            "event_type": "payment.failed",
            "payload": {
                "id": "pi_test_456",
                "amount": 5000,
                "currency": "sar",
                "status": "failed",
                "error": "card_declined"
            },
            "response_status": 200,
            "processing_time_ms": 89.7,
            "created_at": datetime.now(),
        },
    ]
    
    if event_type:
        logs = [log for log in logs if log["event_type"] == event_type]
    
    return logs[:limit]


@router.post("/{integration_id}/webhooks/retry/{webhook_id}")
async def retry_webhook(
    integration_id: UUID,
    webhook_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Retry failed webhook (Admin only)
    """
    return {
        "webhook_id": webhook_id,
        "integration_id": integration_id,
        "status": "queued",
        "message": "Webhook retry queued successfully",
    }


# Integration Analytics


@router.get("/analytics")
async def get_integrations_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Get integrations analytics and usage statistics
    """
    return {
        "tenant_id": tenant_id,
        "period_days": days,
        "metrics": {
            "total_api_calls": 15647,
            "successful_calls": 15234,
            "failed_calls": 413,
            "success_rate": 97.4,
            "average_response_time": 189.5,
            "total_webhooks": 1205,
            "webhook_success_rate": 99.2,
        },
        "by_provider": {
            "stripe": {
                "api_calls": 8924,
                "success_rate": 98.1,
                "avg_response_time": 145.2,
            },
            "zatca": {
                "api_calls": 456,
                "success_rate": 96.8,
                "avg_response_time": 567.8,
            },
            "stc_pay": {
                "api_calls": 3421,
                "success_rate": 95.5,
                "avg_response_time": 234.1,
            },
        },
        "error_analysis": {
            "most_common_errors": [
                {"error": "Rate limit exceeded", "count": 156},
                {"error": "Authentication failed", "count": 89},
                {"error": "Network timeout", "count": 67},
            ],
        },
        "usage_trends": {
            "daily_calls": [
                {"date": "2023-12-01", "calls": 567, "errors": 12},
                {"date": "2023-12-02", "calls": 634, "errors": 8},
                {"date": "2023-12-03", "calls": 589, "errors": 15},
            ],
        },
    }


# Integration Templates and Providers


@router.get("/providers")
async def get_available_providers():
    """
    Get list of available integration providers
    """
    return [
        {
            "id": "stripe",
            "name": "Stripe",
            "description": "Global payment processing platform",
            "description_ar": "منصة معالجة المدفوعات العالمية",
            "category": "payment",
            "supported_features": ["payments", "subscriptions", "webhooks"],
            "setup_complexity": "easy",
            "documentation_url": "https://stripe.com/docs",
        },
        {
            "id": "zatca",
            "name": "ZATCA E-Invoicing",
            "description": "Saudi Arabia electronic invoicing compliance",
            "description_ar": "امتثال الفاتورة الإلكترونية في المملكة العربية السعودية",
            "category": "compliance",
            "supported_features": ["e_invoicing", "tax_compliance", "qr_codes"],
            "setup_complexity": "medium",
            "documentation_url": "https://zatca.gov.sa/en/E-Invoicing/Introduction/Pages/What-is-e-invoicing.aspx",
        },
        {
            "id": "stc_pay",
            "name": "STC Pay",
            "description": "Saudi digital wallet and payment solution",
            "description_ar": "محفظة رقمية سعودية وحل دفع",
            "category": "payment",
            "supported_features": ["digital_wallet", "qr_payments", "mobile_payments"],
            "setup_complexity": "medium",
            "documentation_url": "https://developer.stcpay.com.sa",
        },
        {
            "id": "mada",
            "name": "Mada",
            "description": "Saudi national payment system",
            "description_ar": "نظام الدفع الوطني السعودي",
            "category": "payment",
            "supported_features": ["card_payments", "local_processing"],
            "setup_complexity": "hard",
            "documentation_url": "https://mada.com.sa",
        },
    ]


@router.get("/templates/{provider}")
async def get_integration_template(
    provider: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get integration template for specific provider
    """
    templates = {
        "stripe": {
            "name": "Stripe Payment Gateway",
            "provider": "stripe",
            "config": {
                "api_key": "pk_test_YOUR_PUBLISHABLE_KEY",
                "secret_key": "sk_test_YOUR_SECRET_KEY",
                "webhook_url": "https://your-domain.com/webhooks/stripe",
                "settings": {
                    "currency": "SAR",
                    "capture_method": "automatic",
                    "payment_methods": ["card", "apple_pay", "google_pay"]
                }
            },
            "required_fields": ["api_key", "secret_key"],
            "setup_instructions": [
                "Create a Stripe account at stripe.com",
                "Get your API keys from the dashboard",
                "Configure webhook endpoint",
                "Test the connection"
            ],
        },
        "zatca": {
            "name": "ZATCA E-Invoicing",
            "provider": "zatca",
            "config": {
                "api_key": "YOUR_ZATCA_API_KEY",
                "endpoint_url": "https://api.zatca.gov.sa",
                "settings": {
                    "company_id": "YOUR_COMPANY_TAX_NUMBER",
                    "environment": "sandbox",
                    "invoice_format": "UBL2.1"
                }
            },
            "required_fields": ["api_key", "company_id"],
            "setup_instructions": [
                "Register with ZATCA e-invoicing platform",
                "Obtain your API credentials",
                "Configure company tax information",
                "Test invoice generation"
            ],
        },
    }
    
    if provider not in templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found for provider: {provider}"
        )
    
    return templates[provider]