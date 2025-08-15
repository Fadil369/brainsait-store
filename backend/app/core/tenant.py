"""
Multi-tenant middleware and utilities
"""

import logging
from typing import Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to handle multi-tenant context"""

    async def dispatch(self, request: Request, call_next):
        # Extract tenant ID from header or subdomain
        tenant_id = self._extract_tenant_id(request)

        # Validate tenant
        if not await self._validate_tenant(tenant_id):
            tenant_id = settings.DEFAULT_TENANT

        # Set tenant context
        request.state.tenant_id = tenant_id

        # Add tenant to response headers
        response = await call_next(request)
        response.headers["X-Tenant-ID"] = tenant_id

        return response

    def _extract_tenant_id(self, request: Request) -> str:
        """Extract tenant ID from request"""

        # 1. Check custom header
        tenant_id = request.headers.get(settings.TENANT_HEADER)
        if tenant_id:
            return tenant_id.lower().strip()

        # 2. Check subdomain
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0].lower()
            if subdomain and subdomain != "www" and subdomain != "api":
                return subdomain

        # 3. Check path prefix (e.g., /tenant/api/v1/...)
        path = request.url.path
        if path.startswith("/") and len(path.split("/")) > 1:
            potential_tenant = path.split("/")[1]
            if potential_tenant not in ["api", "docs", "redoc", "health", "metrics"]:
                return potential_tenant.lower()

        # 4. Default tenant
        return settings.DEFAULT_TENANT

    async def _validate_tenant(self, tenant_id: str) -> bool:
        """Validate if tenant exists and is active"""

        # For now, allow all tenants
        # In production, you would check against a database
        if not tenant_id or len(tenant_id) < 2 or len(tenant_id) > 50:
            return False

        # Check if tenant contains only valid characters
        if not tenant_id.replace("-", "").replace("_", "").isalnum():
            return False

        return True


def get_tenant_from_request(request: Request) -> str:
    """Get tenant ID from request state"""
    return getattr(request.state, "tenant_id", settings.DEFAULT_TENANT)


def get_tenant_database_url(tenant_id: str) -> str:
    """Get database URL for specific tenant"""
    # For multi-database setup, you would modify the database name
    # For single database with tenant isolation, return the same URL
    return settings.DATABASE_URL


def get_tenant_config(tenant_id: str) -> dict:
    """Get tenant-specific configuration"""
    # In production, this would come from a database
    tenant_configs = {
        "brainsait": {
            "name": "BrainSAIT",
            "name_ar": "برين سايت",
            "logo": "/assets/logos/brainsait.png",
            "primary_color": "#2563eb",
            "currency": "SAR",
            "country": "SA",
            "language": "ar",
            "timezone": "Asia/Riyadh",
            "features": {
                "multi_language": True,
                "zatca_compliance": True,
                "mada_payments": True,
                "stc_pay": True,
                "sms_notifications": True,
            },
        },
        "demo": {
            "name": "Demo Store",
            "name_ar": "متجر تجريبي",
            "logo": "/assets/logos/demo.png",
            "primary_color": "#059669",
            "currency": "USD",
            "country": "US",
            "language": "en",
            "timezone": "UTC",
            "features": {
                "multi_language": False,
                "zatca_compliance": False,
                "mada_payments": False,
                "stc_pay": False,
                "sms_notifications": False,
            },
        },
    }

    return tenant_configs.get(tenant_id, tenant_configs["brainsait"])


from fastapi import Depends, Request
from uuid import UUID


def get_current_tenant(request: Request) -> UUID:
    """Get current tenant from request"""
    tenant_id = get_tenant_from_request(request)
    # For now, return a default UUID - in production this would lookup the actual tenant
    # This is a simplified implementation for the payment services to work
    from uuid import uuid5, NAMESPACE_DNS
    return uuid5(NAMESPACE_DNS, tenant_id)
