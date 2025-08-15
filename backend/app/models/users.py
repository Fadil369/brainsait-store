"""
User models for authentication and customer management
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    STAFF = "staff"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Authentication
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    first_name_ar = Column(String(100), nullable=True)
    last_name_ar = Column(String(100), nullable=True)

    # Profile
    avatar_url = Column(String(500), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)

    # Contact Information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(2), nullable=True, default="SA")  # ISO country code

    # Preferences
    preferred_language = Column(String(5), nullable=False, default="ar")
    preferred_currency = Column(String(3), nullable=False, default="SAR")
    timezone = Column(String(50), nullable=False, default="Asia/Riyadh")

    # Status and Role
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)

    # Marketing
    marketing_consent = Column(Boolean, nullable=False, default=False)
    newsletter_subscribed = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    reviews = relationship("ProductReview", back_populates="user")

    # Indexes
    __table_args__ = (
        Index("idx_users_tenant_email", "tenant_id", "email", unique=True),
        Index("idx_users_tenant_phone", "tenant_id", "phone"),
        Index("idx_users_status", "status"),
        Index("idx_users_role", "role"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name_ar(self) -> str:
        if self.first_name_ar and self.last_name_ar:
            return f"{self.first_name_ar} {self.last_name_ar}"
        return self.full_name

    @property
    def display_name(self) -> str:
        """Get display name based on preferred language"""
        if self.preferred_language == "ar":
            return self.full_name_ar
        return self.full_name

    def __repr__(self):
        return f"<User {self.email}>"


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Session Information
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token = Column(String(255), nullable=True, index=True)
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_user_sessions_user", "user_id"),
        Index("idx_user_sessions_tenant", "tenant_id"),
        Index("idx_user_sessions_token", "session_token"),
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)

    # Preference
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_user_preferences_user_key", "user_id", "key", unique=True),
        Index("idx_user_preferences_tenant", "tenant_id"),
    )
