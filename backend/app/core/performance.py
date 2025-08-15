"""
Performance middleware for response compression, caching headers, and monitoring
"""

import gzip
import time
from typing import Callable
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression"""
    
    def __init__(self, app: ASGIApp, minimum_size: int = 1000):
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return await call_next(request)
        
        response = await call_next(request)
        
        # Don't compress if response is too small or already encoded
        if (
            response.headers.get("content-encoding")
            or response.status_code < 200
            or response.status_code >= 300
            or "content-length" in response.headers
            and int(response.headers["content-length"]) < self.minimum_size
        ):
            return response
        
        # Compress JSON responses
        if response.headers.get("content-type", "").startswith("application/json"):
            if hasattr(response, 'body'):
                body = response.body
                if len(body) >= self.minimum_size:
                    compressed_body = gzip.compress(body)
                    if len(compressed_body) < len(body):
                        response.headers["content-encoding"] = "gzip"
                        response.headers["content-length"] = str(len(compressed_body))
                        
                        # Create new response with compressed body
                        return Response(
                            content=compressed_body,
                            status_code=response.status_code,
                            headers=response.headers,
                            media_type=response.media_type
                        )
        
        return response


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding appropriate cache headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add cache headers based on route
        path = request.url.path
        
        if path.startswith("/api/v1/products") and request.method == "GET":
            # Cache product listings for 5 minutes
            response.headers["Cache-Control"] = "public, max-age=300"
        elif path.startswith("/api/v1/categories") and request.method == "GET":
            # Cache categories for 1 hour
            response.headers["Cache-Control"] = "public, max-age=3600"
        elif path.startswith("/api/v1/analytics") and request.method == "GET":
            # Cache analytics for 5 minutes
            response.headers["Cache-Control"] = "public, max-age=300"
        elif path.startswith("/metrics"):
            # Don't cache metrics
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        else:
            # Default cache control for API responses
            response.headers["Cache-Control"] = "no-cache"
        
        # Add ETag for cacheable responses if not present
        if (
            response.headers.get("Cache-Control", "").startswith("public")
            and "etag" not in response.headers
            and hasattr(response, 'body')
        ):
            import hashlib
            etag = hashlib.sha256(response.body).hexdigest()[:32]
            response.headers["ETag"] = f'"{etag}"'
        
        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API performance"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(round(process_time, 3))
        
        # Log slow requests
        if process_time > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.3f}s"
            )
        
        # Log performance metrics (can be sent to monitoring service)
        if settings.ENVIRONMENT == "production":
            # In production, you'd send this to your monitoring service
            # For now, we'll just log it
            logger.info(
                f"API_PERFORMANCE method={request.method} "
                f"path={request.url.path} "
                f"status={response.status_code} "
                f"time={process_time:.3f}s"
            )
        
        return response