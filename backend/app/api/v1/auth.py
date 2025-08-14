"""
Authentication API endpoints with Enterprise SSO support
Supports OAuth 2.0, SAML 2.0, and Active Directory integration
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import hashlib
import secrets
import xmltodict
import base64
import urllib.parse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from app.core.config import get_settings
from app.core.database import get_db
from app.core.tenant import get_current_tenant
from app.models.users import User, UserRole, LoginSession
from app.models.tenants import Tenant, TenantSSO
from app.schemas.auth import (
    UserLogin, UserRegister, TokenResponse, UserResponse,
    SAMLRequest, SAMLResponse, OAuthAuthorizationRequest,
    OAuthTokenRequest, ActiveDirectoryConfig
)
from app.core.security import create_access_token, verify_password, hash_password
from app.core.dependencies import get_redis_client

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# ==================== BASIC AUTHENTICATION ====================

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    redis = Depends(get_redis_client)
):
    """Standard email/password authentication"""
    
    # Check if user exists in this tenant
    user = db.query(User).filter(
        User.email == user_data.email,
        User.tenant_id == tenant.id,
        User.is_active == True
    ).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Create refresh token
    refresh_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id), "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Log the session
    session = LoginSession(
        user_id=user.id,
        tenant_id=tenant.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        login_method="email_password",
        is_active=True
    )
    db.add(session)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Cache user session in Redis
    await redis.setex(
        f"session:{user.id}:{session.id}",
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        access_token
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """User registration for tenant"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.tenant_id == tenant.id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        tenant_id=tenant.id,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role=UserRole.USER,
        is_active=True,
        email_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)

# ==================== OAUTH 2.0 INTEGRATION ====================

@router.get("/oauth/{provider}/authorize")
async def oauth_authorize(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Initiate OAuth 2.0 authorization flow"""
    
    # Get tenant's OAuth configuration
    sso_config = db.query(TenantSSO).filter(
        TenantSSO.tenant_id == tenant.id,
        TenantSSO.provider == provider,
        TenantSSO.is_active == True
    ).first()
    
    if not sso_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth provider {provider} not configured for this tenant"
        )
    
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in Redis for validation
    redis = await get_redis_client()
    await redis.setex(f"oauth_state:{state}", 600, f"{tenant.id}:{provider}")
    
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": sso_config.client_id,
        "redirect_uri": sso_config.redirect_uri,
        "scope": sso_config.scopes or "openid profile email",
        "state": state
    }
    
    authorization_url = f"{sso_config.authorization_url}?" + urllib.parse.urlencode(auth_params)
    
    return RedirectResponse(url=authorization_url)

@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db),
    redis = Depends(get_redis_client)
):
    """Handle OAuth 2.0 callback"""
    
    # Validate state parameter
    stored_state = await redis.get(f"oauth_state:{state}")
    if not stored_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter"
        )
    
    tenant_id, provider_name = stored_state.decode().split(":")
    if provider_name != provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider mismatch"
        )
    
    # Get tenant and SSO config
    tenant = db.query(Tenant).filter(Tenant.id == int(tenant_id)).first()
    sso_config = db.query(TenantSSO).filter(
        TenantSSO.tenant_id == tenant.id,
        TenantSSO.provider == provider
    ).first()
    
    # Exchange code for tokens
    token_data = await exchange_oauth_code(sso_config, code)
    
    # Get user info from provider
    user_info = await get_oauth_user_info(sso_config, token_data["access_token"])
    
    # Find or create user
    user = await find_or_create_oauth_user(db, tenant, provider, user_info)
    
    # Create session tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Clean up state
    await redis.delete(f"oauth_state:{state}")
    
    # Redirect to frontend with token
    frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
    return RedirectResponse(url=frontend_url)

# ==================== SAML 2.0 INTEGRATION ====================

@router.get("/saml/{provider}/sso")
async def saml_sso_initiate(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Initiate SAML 2.0 SSO"""
    
    # Get tenant's SAML configuration
    sso_config = db.query(TenantSSO).filter(
        TenantSSO.tenant_id == tenant.id,
        TenantSSO.provider == provider,
        TenantSSO.sso_type == "saml",
        TenantSSO.is_active == True
    ).first()
    
    if not sso_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SAML provider {provider} not configured"
        )
    
    # Generate SAML Request
    saml_request = generate_saml_auth_request(sso_config, request)
    
    # Encode and deflate the request
    encoded_request = base64.b64encode(saml_request.encode()).decode()
    
    # Build SSO URL
    sso_params = {
        "SAMLRequest": encoded_request,
        "RelayState": f"{tenant.id}:{provider}"
    }
    
    sso_url = f"{sso_config.sso_url}?" + urllib.parse.urlencode(sso_params)
    
    return RedirectResponse(url=sso_url)

@router.post("/saml/{provider}/acs")
async def saml_assertion_consumer(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """SAML 2.0 Assertion Consumer Service"""
    
    form_data = await request.form()
    saml_response = form_data.get("SAMLResponse")
    relay_state = form_data.get("RelayState")
    
    if not saml_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing SAML response"
        )
    
    # Parse relay state
    tenant_id, provider_name = relay_state.split(":")
    tenant = db.query(Tenant).filter(Tenant.id == int(tenant_id)).first()
    
    # Get SAML configuration
    sso_config = db.query(TenantSSO).filter(
        TenantSSO.tenant_id == tenant.id,
        TenantSSO.provider == provider
    ).first()
    
    # Decode and validate SAML response
    decoded_response = base64.b64decode(saml_response).decode()
    user_attributes = validate_saml_response(decoded_response, sso_config)
    
    # Find or create user
    user = await find_or_create_saml_user(db, tenant, provider, user_attributes)
    
    # Create session tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Redirect to frontend
    frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
    return RedirectResponse(url=frontend_url)

# ==================== ACTIVE DIRECTORY INTEGRATION ====================

@router.post("/ad/authenticate")
async def authenticate_active_directory(
    credentials: Dict[str, str],
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Authenticate against Active Directory via LDAP"""
    
    # Get tenant's AD configuration
    ad_config = db.query(TenantSSO).filter(
        TenantSSO.tenant_id == tenant.id,
        TenantSSO.provider == "active_directory",
        TenantSSO.is_active == True
    ).first()
    
    if not ad_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active Directory not configured"
        )
    
    # Authenticate with AD
    user_info = await authenticate_ldap(
        ad_config,
        credentials["username"],
        credentials["password"]
    )
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Active Directory credentials"
        )
    
    # Find or create user
    user = await find_or_create_ad_user(db, tenant, user_info)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )

# ==================== SSO CONFIGURATION MANAGEMENT ====================

@router.get("/sso/providers")
async def get_sso_providers(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Get available SSO providers for tenant"""
    
    providers = db.query(TenantSSO).filter(
        TenantSSO.tenant_id == tenant.id,
        TenantSSO.is_active == True
    ).all()
    
    return [
        {
            "provider": p.provider,
            "sso_type": p.sso_type,
            "display_name": p.display_name,
            "login_url": f"/auth/{p.sso_type}/{p.provider}/authorize" if p.sso_type == "oauth" else f"/auth/saml/{p.provider}/sso"
        }
        for p in providers
    ]

@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    redis = Depends(get_redis_client)
):
    """Logout user and invalidate session"""
    
    try:
        # Decode token to get user info
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        
        # Invalidate all user sessions
        sessions = db.query(LoginSession).filter(
            LoginSession.user_id == user_id,
            LoginSession.is_active == True
        ).all()
        
        for session in sessions:
            session.is_active = False
            session.logout_time = datetime.utcnow()
            # Remove from Redis
            await redis.delete(f"session:{user_id}:{session.id}")
        
        db.commit()
        
        return {"message": "Successfully logged out"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

# ==================== HELPER FUNCTIONS ====================

async def exchange_oauth_code(sso_config: TenantSSO, code: str) -> Dict[str, Any]:
    """Exchange OAuth authorization code for access token"""
    import httpx
    
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": sso_config.redirect_uri,
        "client_id": sso_config.client_id,
        "client_secret": sso_config.client_secret
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(sso_config.token_url, data=token_data)
        response.raise_for_status()
        return response.json()

async def get_oauth_user_info(sso_config: TenantSSO, access_token: str) -> Dict[str, Any]:
    """Get user information from OAuth provider"""
    import httpx
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(sso_config.user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()

def generate_saml_auth_request(sso_config: TenantSSO, request: Request) -> str:
    """Generate SAML Authentication Request"""
    
    request_id = f"_{secrets.token_hex(16)}"
    issue_instant = datetime.utcnow().isoformat() + "Z"
    
    saml_request = f"""
    <samlp:AuthnRequest 
        xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
        ID="{request_id}"
        Version="2.0"
        IssueInstant="{issue_instant}"
        Destination="{sso_config.sso_url}"
        AssertionConsumerServiceURL="{sso_config.acs_url}">
        <saml:Issuer>{sso_config.entity_id}</saml:Issuer>
    </samlp:AuthnRequest>
    """
    
    return saml_request.strip()

def validate_saml_response(saml_response: str, sso_config: TenantSSO) -> Dict[str, Any]:
    """Validate SAML response and extract user attributes"""
    
    try:
        # Parse XML response
        response_dict = xmltodict.parse(saml_response)
        
        # Extract user attributes
        assertion = response_dict.get("samlp:Response", {}).get("saml:Assertion", {})
        attribute_statement = assertion.get("saml:AttributeStatement", {})
        attributes = attribute_statement.get("saml:Attribute", [])
        
        user_attributes = {}
        if isinstance(attributes, list):
            for attr in attributes:
                name = attr.get("@Name", "")
                value = attr.get("saml:AttributeValue", "")
                user_attributes[name] = value
        
        return user_attributes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid SAML response: {str(e)}"
        )

async def authenticate_ldap(ad_config: TenantSSO, username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user against Active Directory via LDAP"""
    
    try:
        import ldap3
        
        # Create LDAP connection
        server = ldap3.Server(ad_config.ldap_server, get_info=ldap3.ALL)
        
        # Bind with user credentials
        user_dn = f"{username}@{ad_config.domain}" if "@" not in username else username
        
        with ldap3.Connection(server, user=user_dn, password=password, auto_bind=True) as conn:
            # Search for user attributes
            search_filter = f"(userPrincipalName={user_dn})"
            conn.search(
                ad_config.base_dn,
                search_filter,
                attributes=["displayName", "mail", "department", "title"]
            )
            
            if conn.entries:
                entry = conn.entries[0]
                return {
                    "username": username,
                    "email": str(entry.mail),
                    "full_name": str(entry.displayName),
                    "department": str(entry.department),
                    "title": str(entry.title)
                }
        
        return None
        
    except Exception as e:
        print(f"LDAP authentication error: {e}")
        return None

async def find_or_create_oauth_user(db: Session, tenant: Tenant, provider: str, user_info: Dict[str, Any]) -> User:
    """Find or create user from OAuth provider data"""
    
    email = user_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by OAuth provider"
        )
    
    # Find existing user
    user = db.query(User).filter(
        User.email == email,
        User.tenant_id == tenant.id
    ).first()
    
    if not user:
        # Create new user
        user = User(
            tenant_id=tenant.id,
            email=email,
            full_name=user_info.get("name", ""),
            sso_provider=provider,
            sso_id=user_info.get("sub") or user_info.get("id"),
            role=UserRole.USER,
            is_active=True,
            email_verified=True  # Assume verified by OAuth provider
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

async def find_or_create_saml_user(db: Session, tenant: Tenant, provider: str, attributes: Dict[str, Any]) -> User:
    """Find or create user from SAML attributes"""
    
    email = attributes.get("email") or attributes.get("emailaddress")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided in SAML assertion"
        )
    
    # Find existing user
    user = db.query(User).filter(
        User.email == email,
        User.tenant_id == tenant.id
    ).first()
    
    if not user:
        # Create new user
        user = User(
            tenant_id=tenant.id,
            email=email,
            full_name=attributes.get("displayname", ""),
            sso_provider=provider,
            role=UserRole.USER,
            is_active=True,
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

async def find_or_create_ad_user(db: Session, tenant: Tenant, user_info: Dict[str, Any]) -> User:
    """Find or create user from Active Directory data"""
    
    email = user_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in Active Directory"
        )
    
    # Find existing user
    user = db.query(User).filter(
        User.email == email,
        User.tenant_id == tenant.id
    ).first()
    
    if not user:
        # Create new user
        user = User(
            tenant_id=tenant.id,
            email=email,
            full_name=user_info.get("full_name", ""),
            sso_provider="active_directory",
            sso_id=user_info.get("username"),
            role=UserRole.USER,
            is_active=True,
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user