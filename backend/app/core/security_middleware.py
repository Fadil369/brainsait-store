"""
Security middleware for input validation, audit logging, and protection
"""

import json
import time
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis

from .config import settings
from .security import (
    validate_input_security,
    validate_sql_input,
    create_audit_entry,
    check_rate_limit_violations,
    validate_ip_address
)

# Redis client for tracking
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware that handles:
    - Input validation and sanitization
    - Rate limiting
    - Audit logging
    - IP validation
    - Request/response security headers
    """
    
    def __init__(self, app, enable_audit_logging: bool = True):
        super().__init__(app)
        self.enable_audit_logging = enable_audit_logging
        
        # Paths that require special security attention
        self.sensitive_paths = {
            "/api/v1/auth/login",
            "/api/v1/auth/register", 
            "/api/v1/auth/reset-password",
            "/api/v1/users",
            "/api/v1/payments",
            "/api/v1/billing"
        }
        
        # Paths that don't need full validation (health checks, etc.)
        self.exempt_paths = {
            "/health",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json"
        }

    async def dispatch(self, request: Request, call_next):
        # Generate request ID for tracking
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            # Skip validation for exempt paths
            if request.url.path in self.exempt_paths:
                response = await call_next(request)
                return self._add_security_headers(response, request_id)
            
            # Validate IP address
            client_ip = self._get_client_ip(request)
            if not validate_ip_address(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied from this IP address"
                )
            
            # Check for rate limiting violations
            rate_limit_violations = await self._check_rate_limiting(request, client_ip)
            if rate_limit_violations:
                await self._log_security_event(
                    request, "rate_limit_exceeded", rate_limit_violations
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Validate request body for security threats
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_request_body(request)
            
            # Validate query parameters
            await self._validate_query_parameters(request)
            
            # Process the request
            response = await call_next(request)
            
            # Log successful requests if audit logging is enabled
            if self.enable_audit_logging:
                await self._create_audit_log(request, response, start_time)
            
            return self._add_security_headers(response, request_id)
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log unexpected errors
            await self._log_security_event(
                request, "security_error", {"error": str(e)}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security validation failed"
            )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"

    async def _check_rate_limiting(self, request: Request, client_ip: str) -> Optional[Dict[str, Any]]:
        """Check for rate limiting violations"""
        try:
            # Different rate limits for different endpoints
            if request.url.path in self.sensitive_paths:
                limit = 10  # 10 requests per minute for sensitive endpoints
                window = 60
            else:
                limit = settings.RATE_LIMIT_REQUESTS
                window = settings.RATE_LIMIT_WINDOW
            
            # Use user ID if authenticated, otherwise use IP
            identifier = getattr(request.state, "user_id", client_ip)
            key = f"rate_limit:{identifier}:{request.url.path}"
            
            current = await redis_client.get(key)
            if current and int(current) >= limit:
                return {
                    "identifier": identifier,
                    "path": request.url.path,
                    "limit": limit,
                    "window": window,
                    "current_count": int(current)
                }
            
            # Increment counter
            pipeline = redis_client.pipeline()
            pipeline.incr(key)
            pipeline.expire(key, window)
            await pipeline.execute()
            
            return None
            
        except Exception:
            # If Redis is down, allow the request but log the issue
            return None

    async def _validate_request_body(self, request: Request):
        """Validate request body for security threats"""
        try:
            # Read body if present
            if hasattr(request, "_body"):
                body = request._body
            else:
                body = await request.body()
                request._body = body
            
            if not body:
                return
            
            # Try to parse as JSON and validate
            try:
                data = json.loads(body.decode('utf-8'))
                await self._validate_json_data(data, request.url.path)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON, treat as form data or other format
                body_str = body.decode('utf-8', errors='ignore')
                if len(body_str) > 10000:  # Limit body size for validation
                    body_str = body_str[:10000]
                validate_input_security(body_str, "request_body")
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request body"
            )

    async def _validate_json_data(self, data: Any, path: str):
        """Recursively validate JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Special validation for sensitive fields
                    if key.lower() in ['password', 'token', 'secret', 'key']:
                        continue  # Skip validation for actual password fields
                    
                    # Validate for XSS and injection
                    validate_input_security(value, key)
                    
                    # SQL injection validation for certain fields
                    if key.lower() in ['search', 'query', 'filter', 'name', 'description']:
                        validate_sql_input(value)
                        
                elif isinstance(value, (dict, list)):
                    await self._validate_json_data(value, path)
                    
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    await self._validate_json_data(item, path)
                elif isinstance(item, str):
                    validate_input_security(item, "list_item")

    async def _validate_query_parameters(self, request: Request):
        """Validate query parameters for security threats"""
        for key, value in request.query_params.items():
            if isinstance(value, str):
                validate_input_security(value, f"query_param_{key}")
                
                # Additional SQL injection validation for search parameters
                if key.lower() in ['search', 'q', 'query', 'filter']:
                    validate_sql_input(value)

    async def _create_audit_log(self, request: Request, response: Response, start_time: float):
        """Create audit log entry"""
        try:
            processing_time = time.time() - start_time
            
            # Extract user information if available
            user_id = getattr(request.state, "user_id", None)
            tenant_id = getattr(request.state, "tenant_id", None)
            
            audit_entry = create_audit_entry(
                user_id=user_id,
                action=f"{request.method} {request.url.path}",
                resource_type="api_request",
                resource_id=request.state.request_id,
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "status_code": response.status_code,
                    "processing_time": round(processing_time, 3),
                    "content_length": response.headers.get("content-length"),
                },
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                tenant_id=tenant_id
            )
            
            # Store in Redis for immediate access and processing
            await redis_client.lpush(
                "audit_logs",
                json.dumps(audit_entry)
            )
            
            # Keep only last 10000 entries in Redis
            await redis_client.ltrim("audit_logs", 0, 9999)
            
        except Exception:
            # Don't fail the request if audit logging fails
            pass

    async def _log_security_event(self, request: Request, event_type: str, details: Dict[str, Any]):
        """Log security events for monitoring"""
        try:
            security_event = {
                "event_type": event_type,
                "timestamp": time.time(),
                "request_id": getattr(request.state, "request_id", None),
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
                "path": request.url.path,
                "method": request.method,
                "details": details
            }
            
            # Store security events in a separate Redis list
            await redis_client.lpush(
                "security_events",
                json.dumps(security_event)
            )
            
            # Keep only last 1000 security events
            await redis_client.ltrim("security_events", 0, 999)
            
        except Exception:
            # Don't fail the request if logging fails
            pass

    def _add_security_headers(self, response: Response, request_id: str) -> Response:
        """Add security headers to response"""
        # Request tracking
        response.headers["X-Request-ID"] = request_id
        
        # Security headers (additional to what's in main.py)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        
        # API-specific headers
        response.headers["X-API-Version"] = settings.APP_VERSION
        response.headers["X-Rate-Limit-Remaining"] = "available"
        
        return response


class FileUploadSecurityMiddleware(BaseHTTPMiddleware):
    """
    Specialized middleware for file upload security
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.upload_paths = {"/api/v1/upload", "/api/v1/media"}

    async def dispatch(self, request: Request, call_next):
        # Only process file upload requests
        if (request.method == "POST" and 
            any(path in request.url.path for path in self.upload_paths)):
            
            await self._validate_file_upload_request(request)
        
        return await call_next(request)

    async def _validate_file_upload_request(self, request: Request):
        """Validate file upload requests"""
        content_type = request.headers.get("content-type", "")
        
        # Check content type
        if not content_type.startswith("multipart/form-data"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type for file upload"
            )
        
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)
            max_size = getattr(settings, 'MAX_FILE_SIZE', 10 * 1024 * 1024)
            if size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size is {max_size / 1024 / 1024}MB"
                )