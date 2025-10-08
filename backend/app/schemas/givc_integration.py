"""
Shared data models for GIVC integration
Compliant with FHIR R4 and NPHIES standards
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, validator


# ==================== ENUMS ====================

class ProviderType(str, Enum):
    """Healthcare provider type enumeration"""
    PHYSICIAN = "physician"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    DENTIST = "dentist"
    THERAPIST = "therapist"
    TECHNICIAN = "technician"
    ADMINISTRATOR = "administrator"
    OTHER = "other"


class ServiceType(str, Enum):
    """Healthcare service type enumeration"""
    GIVC_API = "givc_api"
    HEALTHLINC_EHR = "healthlinc_ehr"
    HEALTHLINC_RCM = "healthlinc_rcm"
    MCP_SERVERLINC = "mcp_serverlinc"
    HEALTHLINC_LOGS = "healthlinc_logs"
    CUSTOM_INTEGRATION = "custom_integration"


class ProvisioningStatus(str, Enum):
    """Service provisioning status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ClaimStatus(str, Enum):
    """NPHIES claim status"""
    DRAFT = "draft"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"


# ==================== HEALTHCARE PROVIDER MODELS ====================

class HealthcareProviderProfile(BaseModel):
    """
    Shared healthcare provider profile across BrainSAIT and GIVC systems
    Aligned with FHIR Practitioner resource
    """
    
    # Identity (FHIR: Practitioner.identifier)
    id: str = Field(..., description="Unique provider identifier (UUID)")
    tenant_id: str = Field(..., description="Multi-tenant context")
    email: EmailStr = Field(..., description="Provider email")
    
    # Personal Information (FHIR: Practitioner.name)
    given_name: str = Field(..., description="First name", min_length=1, max_length=100)
    family_name: str = Field(..., description="Last name", min_length=1, max_length=100)
    given_name_ar: Optional[str] = Field(None, description="Arabic first name")
    family_name_ar: Optional[str] = Field(None, description="Arabic last name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    
    # Professional Information (FHIR: Practitioner.qualification)
    license_number: str = Field(..., description="Medical license number")
    license_type: ProviderType = Field(..., description="License type")
    specialization: Optional[str] = Field(None, description="Medical specialization")
    sub_specialization: Optional[str] = Field(None, description="Sub-specialization")
    
    # OID Mapping (FHIR: Practitioner.identifier with OID system)
    provider_oid: str = Field(
        ..., 
        description="Healthcare provider OID (1.3.6.1.4.1.61026.1.2.1.*)",
        regex=r"^1\.3\.6\.1\.4\.1\.61026\.1\.2\.1\.\d+$"
    )
    organization_oid: Optional[str] = Field(
        None, 
        description="Organization OID",
        regex=r"^1\.3\.6\.1\.4\.1\.61026\.\d+(\.\d+)*$"
    )
    
    # NPHIES Integration (FHIR: Practitioner.identifier)
    nphies_provider_id: Optional[str] = Field(None, description="NPHIES provider identifier")
    nphies_license_number: Optional[str] = Field(None, description="NPHIES license")
    nphies_enabled: bool = Field(default=False, description="NPHIES integration enabled")
    
    # Contact Information (FHIR: Practitioner.telecom)
    phone: Optional[str] = Field(None, description="Phone number")
    mobile: Optional[str] = Field(None, description="Mobile number")
    
    # Status (FHIR: Practitioner.active)
    is_active: bool = Field(default=True, description="Provider active status")
    verified: bool = Field(default=False, description="Identity verification status")
    verification_date: Optional[datetime] = Field(None, description="Date of verification")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created the record")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "provider_uuid_123",
                "tenant_id": "clinic_uuid_456",
                "email": "dr.ahmed@clinic.sa",
                "given_name": "Ahmed",
                "family_name": "Al-Sayed",
                "given_name_ar": "أحمد",
                "family_name_ar": "السيد",
                "license_number": "MED-SA-12345",
                "license_type": "physician",
                "specialization": "Cardiology",
                "provider_oid": "1.3.6.1.4.1.61026.1.2.1.100",
                "organization_oid": "1.3.6.1.4.1.61026.1.2.2.200",
                "nphies_provider_id": "NPHIES-PROV-123",
                "nphies_license_number": "LICENSE-12345",
                "nphies_enabled": True,
                "phone": "+966112345678",
                "mobile": "+966501234567",
                "is_active": True,
                "verified": True,
                "verification_date": "2025-01-01T00:00:00Z"
            }
        }


# ==================== HEALTHCARE SERVICE MODELS ====================

class HealthcareServiceProduct(BaseModel):
    """
    Product model for healthcare services sold in BrainSAIT Store
    Aligned with FHIR HealthcareService resource
    """
    
    # Product Identity (FHIR: HealthcareService.identifier)
    product_id: str = Field(..., description="Store product ID (UUID)")
    sku: str = Field(..., description="Stock keeping unit", regex=r"^[A-Z0-9-]+$")
    
    # Product Information (FHIR: HealthcareService.name, category)
    name: str = Field(..., description="Product name (English)", min_length=1, max_length=200)
    name_ar: str = Field(..., description="Product name (Arabic)", min_length=1, max_length=200)
    description: str = Field(..., description="Product description")
    description_ar: Optional[str] = Field(None, description="Product description (Arabic)")
    category: str = Field(..., description="Product category")
    
    # Healthcare Metadata
    service_type: ServiceType = Field(..., description="Healthcare service type")
    oid_mapping: Optional[str] = Field(None, description="Related OID node")
    fhir_resource_type: Optional[str] = Field(
        None, 
        description="Related FHIR resource type",
        regex=r"^[A-Z][a-zA-Z]+$"  # e.g., "Patient", "Claim", "HealthcareService"
    )
    
    # Pricing (FHIR: extension for pricing)
    price_sar: float = Field(..., description="Price in Saudi Riyals", gt=0)
    vat_rate: float = Field(default=0.15, description="VAT rate (15% in Saudi)", ge=0, le=1)
    currency: str = Field(default="SAR", description="Currency code")
    
    # NPHIES Integration
    nphies_service_code: Optional[str] = Field(None, description="NPHIES service code")
    requires_authorization: bool = Field(default=False, description="Requires prior authorization")
    
    # Features & Capabilities (FHIR: HealthcareService.characteristic)
    features: List[str] = Field(default_factory=list, description="Service features")
    includes_support: bool = Field(default=True, description="Includes customer support")
    support_duration_months: int = Field(default=12, description="Support duration", ge=0, le=60)
    
    # Provisioning
    auto_provision: bool = Field(default=True, description="Automatic provisioning on purchase")
    provisioning_endpoint: Optional[str] = Field(None, description="GIVC provisioning API endpoint")
    
    # Metadata
    is_active: bool = Field(default=True, description="Product active status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('price_sar')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return round(v, 2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_givc_healthcare_api",
                "sku": "GIVC-API-PRO",
                "name": "GIVC Healthcare API - Professional",
                "name_ar": "واجهة GIVC للرعاية الصحية - احترافي",
                "description": "AI-powered healthcare API with NPHIES integration",
                "description_ar": "واجهة برمجية للرعاية الصحية مدعومة بالذكاء الاصطناعي مع تكامل نفيس",
                "category": "healthcare",
                "service_type": "givc_api",
                "oid_mapping": "1.3.6.1.4.1.61026.1.2.1",
                "fhir_resource_type": "HealthcareService",
                "price_sar": 3499.0,
                "vat_rate": 0.15,
                "currency": "SAR",
                "nphies_service_code": "NPHIES-SVC-001",
                "requires_authorization": False,
                "features": [
                    "AI Medical Processing",
                    "NPHIES Integration",
                    "FHIR R4 Support",
                    "Real-time Claims Processing"
                ],
                "includes_support": True,
                "support_duration_months": 12,
                "auto_provision": True,
                "provisioning_endpoint": "https://givc-healthcare-api.fadil.workers.dev/api/v1/provision"
            }
        }


# ==================== PROVISIONING MODELS ====================

class ServiceProvisioningRequest(BaseModel):
    """Request model for provisioning GIVC healthcare services"""
    
    order_id: str = Field(..., description="BrainSAIT Store order ID")
    product_sku: str = Field(..., description="Product SKU to provision")
    
    # Customer Information
    customer_user_id: str = Field(..., description="User ID from BrainSAIT Store")
    customer_tenant_id: str = Field(..., description="Tenant ID from BrainSAIT Store")
    customer_email: EmailStr = Field(..., description="Customer email")
    provider_oid: Optional[str] = Field(None, description="Healthcare provider OID")
    
    # Subscription Details
    subscription_start_date: datetime = Field(..., description="Subscription start date")
    subscription_duration_months: int = Field(..., description="Duration in months", ge=1, le=60)
    
    # Additional Configuration
    configuration: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Service-specific configuration"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "order_uuid_123",
                "product_sku": "GIVC-API-PRO",
                "customer_user_id": "user_uuid_456",
                "customer_tenant_id": "tenant_uuid_789",
                "customer_email": "provider@clinic.sa",
                "provider_oid": "1.3.6.1.4.1.61026.1.2.1.100",
                "subscription_start_date": "2025-01-01T00:00:00Z",
                "subscription_duration_months": 12,
                "configuration": {
                    "enable_nphies": True,
                    "enable_ai_processing": True,
                    "max_claims_per_month": 1000
                }
            }
        }


class ServiceProvisioningResponse(BaseModel):
    """Response model for provisioning GIVC healthcare services"""
    
    status: ProvisioningStatus = Field(..., description="Provisioning status")
    account_id: Optional[str] = Field(None, description="GIVC account ID")
    api_key: Optional[str] = Field(None, description="API key (masked)")
    
    # NPHIES Credentials
    nphies_credentials: Optional[Dict[str, Any]] = Field(
        None, 
        description="NPHIES integration credentials"
    )
    
    # Access Information
    access_url: Optional[str] = Field(None, description="Service access URL")
    dashboard_url: Optional[str] = Field(None, description="Dashboard URL")
    
    # Status Information
    message: str = Field(..., description="Status message")
    provisioned_at: Optional[datetime] = Field(None, description="Provisioning completion time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "account_id": "givc_account_uuid",
                "api_key": "givc_api_key_***",
                "nphies_credentials": {
                    "client_id": "nphies_client_***",
                    "endpoints": {
                        "authorization": "https://nphies.sa/auth",
                        "claim": "https://nphies.sa/claim"
                    }
                },
                "access_url": "https://portal.givc.brainsait.com/account/givc_account_uuid",
                "dashboard_url": "https://dashboard.givc.brainsait.com",
                "message": "Service provisioned successfully",
                "provisioned_at": "2025-01-01T00:15:00Z"
            }
        }


# ==================== AUTHENTICATION & SESSION MODELS ====================

class CrossServiceAuthToken(BaseModel):
    """JWT token model for cross-service authentication"""
    
    # Standard JWT claims
    sub: str = Field(..., description="Subject (user ID)")
    iss: str = Field(..., description="Issuer (brainsait-store)")
    aud: List[str] = Field(..., description="Audience (services that can use this token)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    
    # Custom claims
    tenant_id: str = Field(..., description="Tenant context")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User full name")
    roles: List[str] = Field(..., description="User roles")
    permissions: List[str] = Field(..., description="User permissions")
    
    # Healthcare-specific claims
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata (provider_oid, nphies_license, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "sub": "user_uuid_123",
                "iss": "brainsait-store",
                "aud": ["brainsait-store", "givc-api", "healthlinc"],
                "exp": 1704844800,
                "iat": 1704843000,
                "tenant_id": "tenant_uuid_456",
                "email": "provider@clinic.sa",
                "name": "Dr. Ahmed Al-Sayed",
                "roles": ["healthcare_provider", "admin"],
                "permissions": [
                    "read:products",
                    "write:claims",
                    "read:patients",
                    "write:authorizations"
                ],
                "metadata": {
                    "provider_oid": "1.3.6.1.4.1.61026.1.2.1.100",
                    "nphies_license": "LICENSE-12345",
                    "organization_id": "org_uuid_789"
                }
            }
        }


class SessionExchangeRequest(BaseModel):
    """Request to exchange BrainSAIT session for GIVC session"""
    
    brainsait_token: str = Field(..., description="BrainSAIT JWT access token")
    service: str = Field(..., description="Target service (givc-api, healthlinc, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "brainsait_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "service": "givc-api"
            }
        }


class SessionExchangeResponse(BaseModel):
    """Response with GIVC-specific session token"""
    
    service_token: str = Field(..., description="Service-specific token")
    expires_at: datetime = Field(..., description="Token expiration time")
    service_url: str = Field(..., description="Service base URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_token": "givc_session_token_***",
                "expires_at": "2025-01-01T01:00:00Z",
                "service_url": "https://givc-healthcare-api.fadil.workers.dev"
            }
        }


# ==================== FHIR-ALIGNED MODELS ====================

class FHIRIdentifier(BaseModel):
    """FHIR Identifier datatype"""
    
    system: str = Field(..., description="Identifier system (OID or URL)")
    value: str = Field(..., description="Identifier value")
    use: Optional[str] = Field(None, description="Identifier use (official, temp, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "system": "urn:oid:1.3.6.1.4.1.61026.1.2.1",
                "value": "100",
                "use": "official"
            }
        }


class FHIRReference(BaseModel):
    """FHIR Reference datatype"""
    
    reference: str = Field(..., description="Relative or absolute reference")
    type: Optional[str] = Field(None, description="Resource type")
    display: Optional[str] = Field(None, description="Display text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reference": "Practitioner/provider_uuid_123",
                "type": "Practitioner",
                "display": "Dr. Ahmed Al-Sayed"
            }
        }


class NPHIESClaimItem(BaseModel):
    """NPHIES claim line item (FHIR Claim.item)"""
    
    sequence: int = Field(..., description="Item sequence number", ge=1)
    service_code: str = Field(..., description="Service/procedure code")
    service_display: str = Field(..., description="Service description")
    quantity: int = Field(default=1, description="Quantity", ge=1)
    unit_price: float = Field(..., description="Unit price", gt=0)
    net_amount: float = Field(..., description="Net amount (quantity * unit_price)", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "sequence": 1,
                "service_code": "99213",
                "service_display": "Office visit, established patient",
                "quantity": 1,
                "unit_price": 150.0,
                "net_amount": 150.0
            }
        }


# ==================== WEBHOOK MODELS ====================

class WebhookEvent(BaseModel):
    """Base model for webhook events"""
    
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type (e.g., claim.submitted)")
    source: str = Field(..., description="Source service")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(..., description="Event payload")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "event_uuid_123",
                "event_type": "claim.submitted",
                "source": "givc-api",
                "timestamp": "2025-01-01T12:00:00Z",
                "data": {
                    "claim_id": "claim_uuid_456",
                    "status": "submitted",
                    "provider_id": "provider_uuid_789"
                }
            }
        }
