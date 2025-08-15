"""
Authentication and authorization utilities for BrainSAIT Store API
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


async def get_current_tenant(request: Request) -> UUID:
    """
    Extract and validate tenant ID from request
    
    Priority order:
    1. X-Tenant-ID header
    2. Subdomain parsing
    3. Default tenant
    """
    # Check X-Tenant-ID header first
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header:
        try:
            return UUID(tenant_header)
        except ValueError:
            pass
    
    # Try subdomain parsing
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        if subdomain not in ["www", "api", "admin"]:
            # Use subdomain as tenant identifier
            # In production, this would map to actual tenant UUIDs
            return UUID("00000000-0000-0000-0000-000000000001")
    
    # Default tenant for development/testing
    return UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Extract and validate current user from authentication token
    
    For testing and development, returns a mock user.
    In production, this would validate JWT tokens and return actual user data.
    """
    # For development/testing - return mock user
    # In production, validate JWT token and extract user info
    
    if credentials is None:
        # Allow anonymous access for development
        return {
            "id": UUID("11111111-1111-1111-1111-111111111111"),
            "email": "anonymous@brainsait.com",
            "name": "Anonymous User",
            "tenant_id": tenant_id,
            "role": "user",
            "is_active": True,
            "is_anonymous": True,
        }
    
    # Basic token validation (in production, use proper JWT validation)
    token = credentials.credentials
    
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user data for testing
    # In production, decode JWT and fetch user from database
    return {
        "id": UUID("22222222-2222-2222-2222-222222222222"),
        "email": "user@brainsait.com",
        "name": "Test User",
        "tenant_id": tenant_id,
        "role": "user",
        "is_active": True,
        "is_anonymous": False,
    }


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Require admin role for protected endpoints
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_tenant_access(tenant_id: UUID):
    """
    Dependency to ensure user has access to specific tenant
    """
    async def _check_tenant_access(
        current_user: dict = Depends(get_current_user),
        current_tenant: UUID = Depends(get_current_tenant)
    ):
        if current_tenant != tenant_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this tenant"
            )
        return current_user
    
    return _check_tenant_access


# User model for type hints
class User:
    """User model for type hints"""
    def __init__(self, id: UUID, email: str, name: str, tenant_id: UUID, role: str = "user"):
        self.id = id
        self.email = email
        self.name = name
        self.tenant_id = tenant_id
        self.role = role
        self.is_active = True