"""
Configuration settings for BrainSAIT Store API
Handles environment variables and application settings
"""

import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "BrainSAIT Store API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://user:password@localhost:5432/brainsait_store"
    )
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3001",
        "https://*.brainsait.com",
        "https://brainsait.com",
    ]

    # Multi-language support
    SUPPORTED_LANGUAGES: List[str] = ["en", "ar"]
    DEFAULT_LANGUAGE: str = "en"

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # Payment Gateways
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # PayPal Configuration
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_SECRET: Optional[str] = None
    PAYPAL_BASE_URL: str = "https://api.paypal.com"
    PAYPAL_WEBHOOK_ID: Optional[str] = None
    PAYPAL_ENVIRONMENT: str = "live"

    # Apple Pay Configuration
    APPLE_PAY_MERCHANT_ID: Optional[str] = None
    APPLE_PAY_DOMAIN: Optional[str] = None
    APPLE_PAY_CERT_PATH: Optional[str] = None
    APPLE_PAY_KEY_PATH: Optional[str] = None
    APPLE_PAY_CA_PATH: Optional[str] = None

    # App Store Connect API Configuration
    APP_STORE_CONNECT_KEY_ID: Optional[str] = None
    APP_STORE_CONNECT_ISSUER_ID: Optional[str] = None
    APP_STORE_CONNECT_PRIVATE_KEY_PATH: Optional[str] = None
    APP_STORE_SHARED_SECRET: Optional[str] = None

    # Mada Payment (Saudi Arabia)
    MADA_MERCHANT_ID: Optional[str] = None
    MADA_API_KEY: Optional[str] = None
    MADA_ENDPOINT: str = "https://api.mada.sa"

    # STC Pay (Saudi Arabia)
    STC_PAY_MERCHANT_ID: Optional[str] = None
    STC_PAY_API_KEY: Optional[str] = None
    STC_PAY_ENDPOINT: str = "https://api.stcpay.com.sa"

    # ZATCA (Saudi Tax Authority)
    ZATCA_ENABLED: bool = False
    ZATCA_VAT_NUMBER: Optional[str] = None
    ZATCA_CR_NUMBER: Optional[str] = None
    ZATCA_SELLER_NAME: Optional[str] = None
    ZATCA_SELLER_NAME_AR: Optional[str] = None

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@brainsait.com"
    FROM_NAME: str = "BrainSAIT Store"
    FROM_NAME_AR: str = "متجر برين سايت"

    # SMS Configuration (Saudi Arabia)
    SMS_PROVIDER: str = "unifonic"  # or "taqnyat"
    UNIFONIC_APP_SID: Optional[str] = None
    UNIFONIC_SENDER_ID: Optional[str] = None
    TAQNYAT_API_KEY: Optional[str] = None
    TAQNYAT_SENDER: Optional[str] = None

    # WebSocket
    WEBSOCKET_URL: str = "ws://localhost:8000"

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Caching
    CACHE_TTL: int = 300  # 5 minutes default
    PRODUCT_CACHE_TTL: int = 3600  # 1 hour for products

    # Multi-tenant
    TENANT_HEADER: str = "X-Tenant-ID"
    DEFAULT_TENANT: str = "brainsait"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
