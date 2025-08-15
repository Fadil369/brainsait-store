"""
SSO (Single Sign-On) Models for Enterprise Authentication
Supports OAuth 2.0, SAML 2.0, and Active Directory integration
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SSOType(str, enum.Enum):
    """SSO authentication types"""

    OAUTH = "oauth"
    SAML = "saml"
    LDAP = "ldap"
    OIDC = "oidc"


class SSOProvider(str, enum.Enum):
    """Common SSO providers"""

    AZURE_AD = "azure_ad"
    GOOGLE = "google"
    OKTA = "okta"
    ACTIVE_DIRECTORY = "active_directory"
    ONELOGIN = "onelogin"
    PING_IDENTITY = "ping_identity"
    CUSTOM = "custom"


class TenantSSO(Base):
    """SSO configuration per tenant"""

    __tablename__ = "tenant_sso"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Provider information
    provider = Column(Enum(SSOProvider), nullable=False)
    sso_type = Column(Enum(SSOType), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)

    # OAuth 2.0 Configuration
    client_id = Column(String(255))
    client_secret = Column(Text)  # Encrypted
    authorization_url = Column(Text)
    token_url = Column(Text)
    user_info_url = Column(Text)
    scopes = Column(String(500))
    redirect_uri = Column(Text)

    # SAML 2.0 Configuration
    entity_id = Column(String(255))
    sso_url = Column(Text)
    acs_url = Column(Text)
    x509_certificate = Column(Text)
    private_key = Column(Text)  # Encrypted
    metadata_url = Column(Text)

    # LDAP/Active Directory Configuration
    ldap_server = Column(String(255))
    base_dn = Column(String(500))
    domain = Column(String(100))
    bind_user = Column(String(255))
    bind_password = Column(Text)  # Encrypted
    user_search_filter = Column(String(500))
    group_search_filter = Column(String(500))

    # Attribute mapping
    attribute_mapping = Column(JSON)  # Maps provider attributes to our user fields

    # Settings
    is_active = Column(Boolean, default=True)
    auto_create_users = Column(Boolean, default=True)
    enforce_sso = Column(Boolean, default=False)  # Disable password login when True
    require_group_membership = Column(Boolean, default=False)
    allowed_groups = Column(JSON)  # List of allowed AD/LDAP groups

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime)

    # Relationships
    tenant = relationship("Tenant", back_populates="sso_configs")
    login_sessions = relationship("SSOSession", back_populates="sso_config")


class SSOSession(Base):
    """Track SSO authentication sessions"""

    __tablename__ = "sso_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    sso_config_id = Column(Integer, ForeignKey("tenant_sso.id"), nullable=False)

    # Session data
    session_id = Column(String(255), unique=True, index=True)
    external_session_id = Column(String(255))  # Provider's session ID
    state_parameter = Column(String(255))  # For CSRF protection

    # Authentication details
    provider_user_id = Column(String(255))
    provider_email = Column(String(255))
    provider_attributes = Column(JSON)

    # Session management
    initiated_at = Column(DateTime, default=datetime.utcnow)
    authenticated_at = Column(DateTime)
    expires_at = Column(DateTime)
    terminated_at = Column(DateTime)

    # Security
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sso_sessions")
    tenant = relationship("Tenant")
    sso_config = relationship("TenantSSO", back_populates="login_sessions")


class SSOUserMapping(Base):
    """Maps external SSO users to internal users"""

    __tablename__ = "sso_user_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    sso_config_id = Column(Integer, ForeignKey("tenant_sso.id"), nullable=False)

    # External identity
    external_user_id = Column(String(255), nullable=False)
    external_email = Column(String(255))
    external_username = Column(String(255))

    # Provider attributes
    external_attributes = Column(JSON)
    group_memberships = Column(JSON)  # For LDAP/AD groups

    # Mapping metadata
    first_login = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")
    sso_config = relationship("TenantSSO")


class SAMLRequest(Base):
    """Track SAML authentication requests"""

    __tablename__ = "saml_requests"

    id = Column(String(255), primary_key=True)  # SAML Request ID
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    sso_config_id = Column(Integer, ForeignKey("tenant_sso.id"), nullable=False)

    # Request details
    request_xml = Column(Text)
    relay_state = Column(String(500))
    destination = Column(Text)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    consumed_at = Column(DateTime)

    # Status
    is_consumed = Column(Boolean, default=False)
    response_id = Column(String(255))

    # Relationships
    tenant = relationship("Tenant")
    sso_config = relationship("TenantSSO")


class OAuthState(Base):
    """Track OAuth state parameters for CSRF protection"""

    __tablename__ = "oauth_states"

    state = Column(String(255), primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    sso_config_id = Column(Integer, ForeignKey("tenant_sso.id"), nullable=False)

    # Request context
    original_url = Column(Text)
    user_agent = Column(Text)
    ip_address = Column(String(45))

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    consumed_at = Column(DateTime)

    # Status
    is_consumed = Column(Boolean, default=False)

    # Relationships
    tenant = relationship("Tenant")
    sso_config = relationship("TenantSSO")


class SSOAuditLog(Base):
    """Audit log for SSO operations"""

    __tablename__ = "sso_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    sso_config_id = Column(Integer, ForeignKey("tenant_sso.id"))

    # Event details
    event_type = Column(
        String(50), nullable=False
    )  # login, logout, config_change, etc.
    event_description = Column(Text)
    provider = Column(String(50))

    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(String(255))

    # Outcome
    success = Column(Boolean)
    error_message = Column(Text)

    # Additional data
    audit_metadata = Column(JSON)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")
    sso_config = relationship("TenantSSO")


class SSOGroupMapping(Base):
    """Map external groups to internal roles"""

    __tablename__ = "sso_group_mappings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    sso_config_id = Column(Integer, ForeignKey("tenant_sso.id"), nullable=False)

    # Group information
    external_group_name = Column(String(255), nullable=False)
    external_group_id = Column(String(255))

    # Internal mapping
    internal_role = Column(String(50), nullable=False)  # Maps to UserRole enum
    permissions = Column(JSON)  # Additional permissions

    # Settings
    is_active = Column(Boolean, default=True)
    auto_assign = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    sso_config = relationship("TenantSSO")
