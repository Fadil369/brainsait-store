"""
BrainSAIT B2B Platform - Main FastAPI Application
Multi-tenant SaaS with Arabic/English support
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import auth, tenants, users, workflows, billing, integrations, store, payments, app_store, analytics
from app.api.v1 import integrations_linkedin as linkedin
from app.core.tenant import TenantMiddleware
from app.core.localization import LocalizationMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting BrainSAIT B2B Platform...")
    await init_db()
    logger.info("✅ Database connected")

    yield

    # Shutdown
    logger.info("🔄 Shutting down...")
    await close_db()
    logger.info("👋 Goodbye!")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-tenant B2B SaaS Platform with Arabic/English Support",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware with security restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Tenant-ID",
        "X-Request-ID",
        "X-Forwarded-For",
        "User-Agent"
    ],
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining"],
)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        
        # Content Security Policy
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:;"
            )
        
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Add Trusted Host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*.brainsait.com", "localhost"]
)

# Add Tenant Context middleware
app.add_middleware(TenantMiddleware)

# Add Localization middleware
app.add_middleware(LocalizationMiddleware)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)

app.include_router(
    tenants.router,
    prefix=f"{settings.API_V1_PREFIX}/tenants",
    tags=["Tenants"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Users"]
)

app.include_router(
    workflows.router,
    prefix=f"{settings.API_V1_PREFIX}/workflows",
    tags=["Workflows"]
)

app.include_router(
    billing.router,
    prefix=f"{settings.API_V1_PREFIX}/billing",
    tags=["Billing"]
)

app.include_router(
    integrations.router,
    prefix=f"{settings.API_V1_PREFIX}/integrations",
    tags=["Integrations"]
)

app.include_router(
    linkedin.router,
    prefix=f"{settings.API_V1_PREFIX}/integrations/linkedin",
    tags=["LinkedIn"]
)

app.include_router(
    store.router,
    prefix=f"{settings.API_V1_PREFIX}/store",
    tags=["Store"]
)

app.include_router(
    payments.router,
    prefix=f"{settings.API_V1_PREFIX}/payments",
    tags=["Payments"]
)

app.include_router(
    app_store.router,
    prefix=f"{settings.API_V1_PREFIX}/app-store",
    tags=["App Store Connect"]
)

app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["Analytics"]
)

@app.get("/")
async def root(request: Request):
    """Root endpoint with language support"""
    lang = request.headers.get("Accept-Language", "en")

    if "ar" in lang:
        return {
            "message": "مرحباً بك في منصة BrainSAIT B2B",
            "version": settings.APP_VERSION,
            "docs": "/api/docs",
            "language": "ar"
        }
    else:
        return {
            "message": "Welcome to BrainSAIT B2B Platform",
            "version": settings.APP_VERSION,
            "docs": "/api/docs",
            "language": "en"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/api/v1/info")
async def api_info(request: Request):
    """API information endpoint"""
    tenant_id = getattr(request.state, "tenant_id", None)

    return {
        "api_version": "v1",
        "tenant_id": tenant_id,
        "features": {
            "multi_tenant": True,
            "bilingual": True,
            "languages": settings.SUPPORTED_LANGUAGES,
            "automation": True,
            "integrations": ["zapier", "n8n", "calendly", "stripe", "mada"]
        },
        "contact": {
            "support": "support@brainsait.com",
            "sales": "sales@brainsait.com",
            "website": "https://brainsait.com"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)

    lang = request.headers.get("Accept-Language", "en")

    if "ar" in lang:
        message = "حدث خطأ في النظام. يرجى المحاولة مرة أخرى."
    else:
        message = "A system error occurred. Please try again."

    return JSONResponse(
        status_code=500,
        content={"detail": message}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
