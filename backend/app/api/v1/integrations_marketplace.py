"""
Integration Marketplace API endpoints
Manages third-party integrations and marketplace functionality
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_tenant_id, verify_rate_limit
from app.models.users import User
from app.services.integration_marketplace import IntegrationMarketplace

router = APIRouter()


class IntegrationInstallRequest(BaseModel):
    """Request model for installing integrations"""
    configuration: Dict


class WebhookTestRequest(BaseModel):
    """Request model for webhook testing"""
    event_type: Optional[str] = "test"


class IntegrationResponse(BaseModel):
    """Response model for integrations"""
    id: str
    name: str
    description: str
    category: str
    vendor: str
    icon: str
    pricing: str
    features: List[str]
    supported_events: List[str]
    setup_complexity: str
    status: str
    rating: float
    installs: int
    documentation_url: str
    webhook_url: str
    oauth_required: bool


class InstalledIntegrationResponse(BaseModel):
    """Response model for installed integrations"""
    id: str
    name: str
    status: str
    installed_at: str
    last_sync: Optional[str]
    sync_count: int
    health_status: str


@router.get("/marketplace", response_model=List[IntegrationResponse])
async def get_marketplace_integrations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search integrations"),
    pricing: Optional[str] = Query(None, description="Filter by pricing model"),
    complexity: Optional[str] = Query(None, description="Filter by setup complexity"),
):
    """Get all available integrations in the marketplace"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        integrations = await marketplace.get_available_integrations()
        
        # Apply filters
        if category:
            integrations = [i for i in integrations if i['category'].lower() == category.lower()]
        
        if pricing:
            integrations = [i for i in integrations if i['pricing'].lower() == pricing.lower()]
            
        if complexity:
            integrations = [i for i in integrations if i['setup_complexity'].lower() == complexity.lower()]
        
        if search:
            search_lower = search.lower()
            integrations = [
                i for i in integrations 
                if search_lower in i['name'].lower() 
                or search_lower in i['description'].lower()
                or search_lower in i['vendor'].lower()
            ]
        
        # Sort by rating and installs
        integrations.sort(key=lambda x: (x['rating'], x['installs']), reverse=True)
        
        return [
            IntegrationResponse(
                id=integration['id'],
                name=integration['name'],
                description=integration['description'],
                category=integration['category'],
                vendor=integration['vendor'],
                icon=integration['icon'],
                pricing=integration['pricing'],
                features=integration['features'],
                supported_events=integration['supported_events'],
                setup_complexity=integration['setup_complexity'],
                status=integration['status'],
                rating=integration['rating'],
                installs=integration['installs'],
                documentation_url=integration['documentation_url'],
                webhook_url=integration['webhook_url'],
                oauth_required=integration['oauth_required']
            )
            for integration in integrations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch marketplace integrations: {str(e)}"
        )


@router.get("/installed", response_model=List[InstalledIntegrationResponse])
async def get_installed_integrations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get integrations installed by the current tenant"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        installed = await marketplace.get_installed_integrations(current_user.id)
        
        return [
            InstalledIntegrationResponse(
                id=integration['id'],
                name=integration['name'],
                status=integration['status'],
                installed_at=integration['installed_at'],
                last_sync=integration.get('last_sync'),
                sync_count=integration['sync_count'],
                health_status=integration['health_status']
            )
            for integration in installed
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch installed integrations: {str(e)}"
        )


@router.post("/install/{integration_id}")
async def install_integration(
    integration_id: str,
    install_request: IntegrationInstallRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Install a new integration"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        result = await marketplace.install_integration(
            integration_id=integration_id,
            configuration=install_request.configuration,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Integration {integration_id} installed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to install integration: {str(e)}"
        )


@router.delete("/uninstall/{integration_id}")
async def uninstall_integration(
    integration_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Uninstall an integration"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        result = await marketplace.uninstall_integration(
            integration_id=integration_id,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Integration {integration_id} uninstalled successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to uninstall integration: {str(e)}"
        )


@router.get("/health/{integration_id}")
async def get_integration_health(
    integration_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get health status of an installed integration"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        health = await marketplace.get_integration_health(integration_id)
        
        return {
            "success": True,
            "data": health,
            "message": "Integration health status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration health: {str(e)}"
        )


@router.get("/analytics/{integration_id}")
async def get_integration_analytics(
    integration_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
):
    """Get analytics for an installed integration"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        analytics = await marketplace.get_integration_analytics(integration_id, days)
        
        return {
            "success": True,
            "data": analytics,
            "message": "Integration analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration analytics: {str(e)}"
        )


@router.post("/test-webhook/{integration_id}")
async def test_integration_webhook(
    integration_id: str,
    test_request: WebhookTestRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Send a test webhook to verify integration setup"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        result = await marketplace.trigger_webhook_test(
            integration_id=integration_id,
            event_type=test_request.event_type
        )
        
        # Remove internal error details from response
        response = {
            "success": result['success'],
            "message": result.get('message', 'Webhook test completed')
        }
        if result['success']:
            response["data"] = result
        else:
            # Only include generic error message
            response["error"] = result.get("error", "Internal error")
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test webhook: {str(e)}"
        )


@router.get("/categories")
async def get_integration_categories(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get all available integration categories"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        integrations = await marketplace.get_available_integrations()
        
        # Extract unique categories with counts
        categories = {}
        for integration in integrations:
            category = integration['category']
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'count': 0,
                    'description': {
                        'marketing': 'Email marketing, lead generation, and campaign automation',
                        'automation': 'Workflow automation and process optimization',
                        'crm': 'Customer relationship management and sales tools',
                        'payments': 'Payment processing and financial management',
                        'analytics': 'Data analysis and business intelligence',
                        'communication': 'Messaging, video conferencing, and team collaboration'
                    }.get(category, f'{category.title()} integrations')
                }
            categories[category]['count'] += 1
        
        return {
            "success": True,
            "data": list(categories.values()),
            "message": "Integration categories retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration categories: {str(e)}"
        )


@router.get("/stats")
async def get_marketplace_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get marketplace statistics"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        marketplace = IntegrationMarketplace(db, tenant_id)
        
        # Get all integrations and installed integrations
        all_integrations = await marketplace.get_available_integrations()
        installed_integrations = await marketplace.get_installed_integrations(current_user.id)
        
        stats = {
            "total_integrations": len(all_integrations),
            "installed_integrations": len(installed_integrations),
            "categories": len(set(i['category'] for i in all_integrations)),
            "popular_integrations": sorted(
                all_integrations, 
                key=lambda x: x['installs'], 
                reverse=True
            )[:5],
            "recent_installs": sorted(
                installed_integrations,
                key=lambda x: x['installed_at'],
                reverse=True
            )[:3],
            "health_summary": {
                "healthy": len([i for i in installed_integrations if i['health_status'] == 'healthy']),
                "warning": len([i for i in installed_integrations if i['health_status'] == 'warning']),
                "error": len([i for i in installed_integrations if i['health_status'] == 'error'])
            }
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "Marketplace statistics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get marketplace stats: {str(e)}"
        )