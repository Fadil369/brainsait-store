"""
Authentication and SSO Pydantic schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class SSOType(str, Enum):
    oauth = "oauth"
    saml = "saml"
    ldap = "ldap"
    oidc = "oidc"


class SSOProvider(str, Enum):
    azure_ad = "azure_ad"
    google = "google"
    okta = "okta"
    active_directory = "active_directory"
    onelogin = "onelogin"
    ping_identity = "ping_identity"
    custom = "custom"


# ==================== BASIC AUTH SCHEMAS ====================


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
    tenant_subdomain: Optional[str] = None


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    company: Optional[str] = None
    phone: Optional[str] = None
    terms_accepted: bool = True

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    email_verified: bool
    sso_provider: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# ==================== OAUTH 2.0 SCHEMAS ====================


class OAuthAuthorizationRequest(BaseModel):
    provider: SSOProvider
    redirect_uri: Optional[str] = None
    scopes: Optional[List[str]] = None
    state: Optional[str] = None


class OAuthTokenRequest(BaseModel):
    provider: SSOProvider
    code: str
    state: str
    redirect_uri: Optional[str] = None


class OAuthUserInfo(BaseModel):
    external_id: str
    email: EmailStr
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


# ==================== SAML 2.0 SCHEMAS ====================


class SAMLRequest(BaseModel):
    provider: SSOProvider
    relay_state: Optional[str] = None
    force_auth: bool = False
    is_passive: bool = False


class SAMLResponse(BaseModel):
    saml_response: str
    relay_state: Optional[str] = None
    signature: Optional[str] = None


class SAMLUserAttributes(BaseModel):
    name_id: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    groups: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None


# ==================== ACTIVE DIRECTORY SCHEMAS ====================


class ActiveDirectoryConfig(BaseModel):
    server: str
    domain: str
    base_dn: str
    bind_user: Optional[str] = None
    bind_password: Optional[str] = None
    user_search_filter: str = "(userPrincipalName={username})"
    group_search_filter: str = "(member={user_dn})"
    use_ssl: bool = True
    use_tls: bool = False


class LDAPUserInfo(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    groups: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None


# ==================== SSO CONFIGURATION SCHEMAS ====================


class TenantSSOCreate(BaseModel):
    provider: SSOProvider
    sso_type: SSOType
    display_name: str
    description: Optional[str] = None

    # OAuth Configuration
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    user_info_url: Optional[str] = None
    scopes: Optional[str] = None
    redirect_uri: Optional[str] = None

    # SAML Configuration
    entity_id: Optional[str] = None
    sso_url: Optional[str] = None
    acs_url: Optional[str] = None
    x509_certificate: Optional[str] = None
    private_key: Optional[str] = None
    metadata_url: Optional[str] = None

    # LDAP Configuration
    ldap_server: Optional[str] = None
    base_dn: Optional[str] = None
    domain: Optional[str] = None
    bind_user: Optional[str] = None
    bind_password: Optional[str] = None
    user_search_filter: Optional[str] = None
    group_search_filter: Optional[str] = None

    # Attribute Mapping
    attribute_mapping: Optional[Dict[str, str]] = None

    # Settings
    auto_create_users: bool = True
    enforce_sso: bool = False
    require_group_membership: bool = False
    allowed_groups: Optional[List[str]] = None


class TenantSSOUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    client_secret: Optional[str] = None
    x509_certificate: Optional[str] = None
    private_key: Optional[str] = None
    bind_password: Optional[str] = None
    attribute_mapping: Optional[Dict[str, str]] = None
    auto_create_users: Optional[bool] = None
    enforce_sso: Optional[bool] = None
    require_group_membership: Optional[bool] = None
    allowed_groups: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TenantSSOResponse(BaseModel):
    id: int
    provider: SSOProvider
    sso_type: SSOType
    display_name: str
    description: Optional[str] = None
    is_active: bool
    auto_create_users: bool
    enforce_sso: bool
    require_group_membership: bool
    allowed_groups: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None

    # Public configuration (no secrets)
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    user_info_url: Optional[str] = None
    scopes: Optional[str] = None
    redirect_uri: Optional[str] = None
    entity_id: Optional[str] = None
    sso_url: Optional[str] = None
    acs_url: Optional[str] = None
    metadata_url: Optional[str] = None
    ldap_server: Optional[str] = None
    domain: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== SSO SESSION SCHEMAS ====================


class SSOSessionCreate(BaseModel):
    sso_config_id: int
    external_session_id: Optional[str] = None
    state_parameter: Optional[str] = None
    provider_user_id: Optional[str] = None
    provider_email: Optional[EmailStr] = None
    provider_attributes: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SSOSessionResponse(BaseModel):
    id: str
    user_id: int
    sso_config_id: int
    session_id: str
    external_session_id: Optional[str] = None
    provider_user_id: Optional[str] = None
    provider_email: Optional[str] = None
    initiated_at: datetime
    authenticated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


# ==================== GROUP MAPPING SCHEMAS ====================


class SSOGroupMappingCreate(BaseModel):
    external_group_name: str
    external_group_id: Optional[str] = None
    internal_role: str
    permissions: Optional[Dict[str, Any]] = None
    auto_assign: bool = True


class SSOGroupMappingResponse(BaseModel):
    id: int
    external_group_name: str
    external_group_id: Optional[str] = None
    internal_role: str
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool
    auto_assign: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== AUDIT SCHEMAS ====================


class SSOAuditLogResponse(BaseModel):
    id: int
    event_type: str
    event_description: Optional[str] = None
    provider: Optional[str] = None
    user_id: Optional[int] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ==================== PROVIDER TEMPLATES ====================


class SSOProviderTemplate(BaseModel):
    provider: SSOProvider
    sso_type: SSOType
    display_name: str
    description: str
    configuration_template: Dict[str, Any]
    required_fields: List[str]
    optional_fields: List[str]
    documentation_url: Optional[str] = None


# ==================== ERROR SCHEMAS ====================


class SSOError(BaseModel):
    error: str
    error_description: Optional[str] = None
    error_uri: Optional[str] = None
    state: Optional[str] = None


class AuthenticationError(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retry_after: Optional[int] = None
