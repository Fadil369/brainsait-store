"""
FastAPI Dependencies for authentication, authorization, and common functionality
"""

from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import redis.asyncio as redis
from datetime import datetime, timedelta
import json

from .config import settings
from .database import get_db
from app.models.users import User
from app.models.products import Product


# Security
security = HTTPBearer()

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
) -> User:
    """Get current authenticated user"""
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token")
            
    except JWTError:
        raise AuthenticationError("Invalid token")
    
    # Check if token is blacklisted
    if await redis_client.get(f"blacklist:{credentials.credentials}"):
        raise AuthenticationError("Token has been revoked")
    
    # Get user from database
    result = await db.get(User, user_id)
    if result is None:
        raise AuthenticationError("User not found")
        
    user = result
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    # Add language preference from headers
    if request:
        lang = request.headers.get("Accept-Language", settings.DEFAULT_LANGUAGE)
        user.preferred_language = "ar" if "ar" in lang else "en"
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise AuthorizationError("Admin access required")
    return current_user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None),
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None"""
    
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        # Check if token is blacklisted
        if await redis_client.get(f"blacklist:{token}"):
            return None
        
        # Get user from database
        result = await db.get(User, user_id)
        if result is None or not result.is_active:
            return None
            
        user = result
        # Add language preference from headers
        lang = request.headers.get("Accept-Language", settings.DEFAULT_LANGUAGE)
        user.preferred_language = "ar" if "ar" in lang else "en"
        
        return user
        
    except JWTError:
        return None


async def get_tenant_id(
    request: Request,
    tenant_id: Optional[str] = Header(None, alias=settings.TENANT_HEADER),
) -> str:
    """Get tenant ID from header or use default"""
    
    # Check if tenant_id is in request state (set by middleware)
    if hasattr(request.state, "tenant_id") and request.state.tenant_id:
        return request.state.tenant_id
    
    # Use header value or default
    return tenant_id or settings.DEFAULT_TENANT


async def get_language(
    request: Request,
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
) -> str:
    """Get user's preferred language"""
    
    # Check if language is in request state (set by middleware)
    if hasattr(request.state, "language") and request.state.language:
        return request.state.language
    
    # Parse Accept-Language header
    if accept_language:
        # Simple parsing - take first language that we support
        for lang in accept_language.split(","):
            lang_code = lang.split(";")[0].strip().lower()
            if lang_code.startswith("ar"):
                return "ar"
            elif lang_code.startswith("en"):
                return "en"
    
    return settings.DEFAULT_LANGUAGE


async def get_product_with_permission(
    product_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    """Get product with permission check"""
    
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if product is active or user is admin
    if not product.is_active and (not current_user or not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


async def verify_rate_limit(
    request: Request,
    identifier: str = None,
) -> bool:
    """Verify rate limit for user/IP"""
    
    # Use user ID if available, otherwise use IP
    if not identifier:
        identifier = getattr(request.state, "user_id", None) or request.client.host
    
    key = f"rate_limit:{identifier}"
    
    try:
        # Get current count
        current = await redis_client.get(key)
        if current and int(current) >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Increment counter
        pipeline = redis_client.pipeline()
        pipeline.incr(key)
        pipeline.expire(key, settings.RATE_LIMIT_WINDOW)
        await pipeline.execute()
        
        return True
        
    except Exception as e:
        # If Redis is down, allow the request
        return True


async def get_cache(key: str) -> Optional[Dict[Any, Any]]:
    """Get data from Redis cache"""
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def set_cache(key: str, data: Dict[Any, Any], ttl: int = None) -> bool:
    """Set data in Redis cache"""
    try:
        ttl = ttl or settings.CACHE_TTL
        await redis_client.setex(
            key,
            ttl,
            json.dumps(data, default=str)
        )
        return True
    except Exception:
        return False


async def delete_cache(pattern: str) -> bool:
    """Delete cache keys by pattern"""
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
        return True
    except Exception:
        return False