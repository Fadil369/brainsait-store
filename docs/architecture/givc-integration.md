# GIVC Integration Architecture

## Overview
This document describes the unified architecture between BrainSAIT Store and GIVC Healthcare Platform, detailing integration patterns, data flows, and shared models.

---

## Architecture Overview

### Unified System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          User Interface Layer                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  BrainSAIT Store Frontend              GIVC Healthcare Portal               │
│  (Next.js 14)                          (Healthcare Provider UI)             │
│  ├── Product Catalog                   ├── Patient Management               │
│  ├── Shopping Cart                     ├── Claims Processing                │
│  ├── Checkout Flow                     ├── Authorization Requests           │
│  └── Order Management                  └── Revenue Cycle Dashboard          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Unified API Gateway Layer                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  BrainSAIT API Gateway (Cloudflare Workers)                                │
│  ├── Cross-Service Routing                                                 │
│  ├── Unified Authentication (JWT)                                          │
│  ├── Rate Limiting & Throttling                                            │
│  ├── Request/Response Transformation                                       │
│  └── Health Monitoring & Circuit Breaker                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    ▼                                ▼
┌─────────────────────────────────┐  ┌────────────────────────────────────────┐
│   BrainSAIT Store Services      │  │   GIVC Healthcare Services             │
├─────────────────────────────────┤  ├────────────────────────────────────────┤
│  FastAPI Backend                │  │  GIVC Healthcare API                   │
│  ├── Product Service            │  │  (Cloudflare Workers + AI)             │
│  ├── Order Service              │  │  ├── FHIR Resource Management          │
│  ├── Payment Service            │  │  ├── NPHIES Integration                │
│  ├── User Service               │  │  ├── AI Medical Processing             │
│  ├── Tenant Service             │  │  ├── Healthcare Provider Directory     │
│  └── OID Integration Service    │◄─┼─►└── Medical Terminology Service      │
│                                 │  │                                        │
│  Supporting Services:           │  │  Supporting Services:                  │
│  ├── Analytics Service          │  │  ├── HealthLinc EHR/RCM                │
│  ├── Notification Service       │  │  ├── HealthLinc Logs (Monitoring)      │
│  ├── Integration Service        │  │  ├── MCP ServerLinc (AI Context)       │
│  └── Audit Service              │  │  └── Claims Processing Engine          │
└─────────────────────────────────┘  └────────────────────────────────────────┘
                    │                                │
                    └───────────────┬────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Shared Data Layer                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database (Multi-tenant)        Redis Cache (Distributed)        │
│  ├── Users & Authentication                ├── Session Store                │
│  ├── Tenants & Organizations               ├── Cache Layer                  │
│  ├── Products & Healthcare Services        ├── Rate Limiting                │
│  ├── Orders & Transactions                 └── Real-time Data               │
│  ├── Healthcare Providers (OID-mapped)                                      │
│  ├── Medical Claims & Authorizations                                        │
│  └── Audit Logs & Compliance Records                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       External Integration Layer                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── NPHIES (Saudi Healthcare)                                              │
│  ├── Payment Gateways (Stripe, PayPal, Mada, STC Pay)                      │
│  ├── ZATCA E-Invoicing                                                      │
│  ├── LinkedIn API (Lead Generation)                                         │
│  ├── Email/SMS Services                                                     │
│  └── Cloud Storage (S3/R2)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Repo Integration Architecture

### Repository Structure

```
BrainSAIT Ecosystem
│
├── brainsait-store (Main E-commerce Platform)
│   ├── frontend/ (Next.js 14)
│   ├── backend/ (FastAPI)
│   ├── infrastructure/ (Cloudflare Workers)
│   └── docs/ (Architecture & Integration Docs)
│
├── GIVC Healthcare System (Healthcare Services)
│   ├── givc-api/ (Healthcare API - Cloudflare Workers)
│   ├── healthlinc/ (EHR/RCM System)
│   ├── healthlinc-logs/ (Monitoring Service)
│   └── mcp-serverlinc/ (AI Context Protocol)
│
└── Shared Resources
    ├── OID Tree (/Users/fadil369/02_BRAINSAIT_ECOSYSTEM/...)
    ├── Shared Models (FHIR, Healthcare Domain)
    ├── Authentication Service (JWT with cross-service validation)
    └── Configuration Management (Secrets, Environment)
```

### Integration Strategy

#### 1. Authentication & Session Management

**Single Sign-On (SSO) Implementation**:

```
User Login Flow:
┌─────────┐                     ┌──────────────┐                ┌──────────┐
│  User   │                     │   BrainSAIT  │                │   GIVC   │
│ (Browser)│                    │     Store    │                │   API    │
└────┬────┘                     └──────┬───────┘                └────┬─────┘
     │                                 │                             │
     │  1. Login Request               │                             │
     ├────────────────────────────────►│                             │
     │                                 │                             │
     │  2. Validate Credentials        │                             │
     │     (Check PostgreSQL)          │                             │
     │◄────────────────────────────────┤                             │
     │                                 │                             │
     │  3. Generate JWT Token          │                             │
     │     Claims:                     │                             │
     │     - user_id                   │                             │
     │     - tenant_id                 │                             │
     │     - roles                     │                             │
     │     - permissions               │                             │
     │     - iss: "brainsait"          │                             │
     │     - aud: ["store", "givc"]    │                             │
     │◄────────────────────────────────┤                             │
     │                                 │                             │
     │  4. Store Session in Redis      │                             │
     │     (30 min TTL)                │                             │
     │                                 │                             │
     │  5. Request GIVC Resource       │                             │
     │     (with JWT token)            │                             │
     ├─────────────────────────────────┼────────────────────────────►│
     │                                 │                             │
     │                                 │  6. Validate JWT Token      │
     │                                 │     (Shared Secret/         │
     │                                 │      Public Key)            │
     │                                 │◄────────────────────────────┤
     │                                 │                             │
     │                                 │  7. Check Permissions       │
     │                                 │     & Create GIVC Session   │
     │                                 │                             │
     │  8. Return GIVC Resource        │                             │
     │◄────────────────────────────────┼─────────────────────────────┤
     │                                 │                             │
```

**Token Structure**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid_123",
    "tenant_id": "tenant_uuid_456",
    "email": "provider@example.com",
    "name": "Dr. Ahmed Al-Sayed",
    "roles": ["healthcare_provider", "admin"],
    "permissions": [
      "read:products",
      "write:claims",
      "read:patients",
      "write:authorizations"
    ],
    "metadata": {
      "provider_oid": "1.3.6.1.4.1.61026.1.2.1.xxx",
      "nphies_license": "LICENSE-12345",
      "organization_id": "org_uuid_789"
    },
    "iss": "brainsait-store",
    "aud": ["brainsait-store", "givc-api", "healthlinc"],
    "exp": 1704844800,
    "iat": 1704843000
  }
}
```

#### 2. Shared Data Models

**Healthcare Provider Profile** (Shared between BrainSAIT Store & GIVC):

```python
# backend/app/schemas/givc_integration.py
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class HealthcareProviderProfile(BaseModel):
    """Shared healthcare provider profile across BrainSAIT and GIVC systems"""
    
    # Identity
    id: str = Field(..., description="Unique provider identifier")
    tenant_id: str = Field(..., description="Multi-tenant context")
    email: str = Field(..., description="Provider email")
    
    # Personal Information (FHIR Practitioner alignment)
    given_name: str = Field(..., description="First name")
    family_name: str = Field(..., description="Last name")
    given_name_ar: Optional[str] = Field(None, description="Arabic first name")
    family_name_ar: Optional[str] = Field(None, description="Arabic last name")
    
    # Professional Information
    license_number: str = Field(..., description="Medical license number")
    license_type: str = Field(..., description="License type (e.g., Physician, Nurse)")
    specialization: Optional[str] = Field(None, description="Medical specialization")
    
    # OID Mapping
    provider_oid: str = Field(..., description="Healthcare provider OID (1.3.6.1.4.1.61026.1.2.1.*)")
    organization_oid: Optional[str] = Field(None, description="Organization OID")
    
    # NPHIES Integration
    nphies_provider_id: Optional[str] = Field(None, description="NPHIES provider identifier")
    nphies_license_number: Optional[str] = Field(None, description="NPHIES license")
    
    # Status
    is_active: bool = Field(default=True, description="Provider active status")
    verified: bool = Field(default=False, description="Identity verification status")
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
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
                "license_type": "Physician",
                "specialization": "Cardiology",
                "provider_oid": "1.3.6.1.4.1.61026.1.2.1.100",
                "nphies_provider_id": "NPHIES-PROV-123",
                "is_active": True,
                "verified": True
            }
        }
```

**Healthcare Service Product** (Maps Store Products to GIVC Services):

```python
class HealthcareServiceProduct(BaseModel):
    """Product model for healthcare services sold in BrainSAIT Store"""
    
    # Product Identity
    product_id: str = Field(..., description="Store product ID")
    sku: str = Field(..., description="Stock keeping unit")
    
    # Product Information
    name: str = Field(..., description="Product name (English)")
    name_ar: str = Field(..., description="Product name (Arabic)")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    
    # Healthcare Metadata
    service_type: str = Field(..., description="Healthcare service type (GIVC API, HealthLinc, etc.)")
    oid_mapping: Optional[str] = Field(None, description="Related OID node")
    fhir_resource_type: Optional[str] = Field(None, description="Related FHIR resource type")
    
    # Pricing
    price_sar: float = Field(..., description="Price in Saudi Riyals")
    vat_rate: float = Field(default=0.15, description="VAT rate (15% in Saudi)")
    
    # NPHIES Integration
    nphies_service_code: Optional[str] = Field(None, description="NPHIES service code")
    requires_authorization: bool = Field(default=False, description="Requires prior authorization")
    
    # Features & Capabilities
    features: List[str] = Field(default_factory=list, description="Service features")
    includes_support: bool = Field(default=True, description="Includes customer support")
    support_duration_months: int = Field(default=12, description="Support duration")
    
    # Provisioning
    auto_provision: bool = Field(default=True, description="Automatic provisioning on purchase")
    provisioning_endpoint: Optional[str] = Field(None, description="GIVC provisioning API endpoint")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_givc_healthcare_api",
                "sku": "GIVC-API-PRO",
                "name": "GIVC Healthcare API - Professional",
                "name_ar": "واجهة GIVC للرعاية الصحية - احترافي",
                "description": "AI-powered healthcare API with NPHIES integration",
                "category": "healthcare",
                "service_type": "givc_api",
                "oid_mapping": "1.3.6.1.4.1.61026.1.2.1",
                "fhir_resource_type": "HealthcareService",
                "price_sar": 3499.0,
                "vat_rate": 0.15,
                "nphies_service_code": "NPHIES-SVC-001",
                "requires_authorization": False,
                "features": [
                    "AI Medical Processing",
                    "NPHIES Integration",
                    "FHIR R4 Support",
                    "Real-time Claims"
                ],
                "auto_provision": True,
                "provisioning_endpoint": "https://givc-healthcare-api.fadil.workers.dev/provision"
            }
        }
```

#### 3. API Endpoint Mapping

**BrainSAIT Store → GIVC Integration Endpoints**:

| BrainSAIT Store Endpoint | GIVC Endpoint | Purpose |
|--------------------------|---------------|---------|
| `POST /api/v1/orders` (healthcare products) | `POST /api/v1/givc/provision` | Provision GIVC service on purchase |
| `GET /api/v1/oid/providers` | `GET /api/v1/givc/providers` | Sync provider directory |
| `POST /api/v1/oid/register` | `POST /api/v1/givc/providers/register` | Register new healthcare provider |
| `GET /api/v1/products?category=healthcare` | `GET /api/v1/givc/services` | List available healthcare services |
| `POST /api/v1/auth/login` | `POST /api/v1/givc/auth/validate` | Validate SSO token for GIVC |

**Webhook Integration**:

| Source | Webhook Event | Target Endpoint | Purpose |
|--------|---------------|-----------------|---------|
| GIVC | `claim.submitted` | `/webhooks/givc/claim-status` | Notify BrainSAIT of claim submission |
| GIVC | `authorization.approved` | `/webhooks/givc/authorization` | Update authorization status |
| HealthLinc | `payment.received` | `/webhooks/healthlinc/payment` | Record payment in BrainSAIT |
| BrainSAIT | `order.completed` | `/webhooks/brainsait/order` | Trigger GIVC provisioning |
| BrainSAIT | `provider.created` | `/webhooks/brainsait/provider` | Sync provider to GIVC |

#### 4. FHIR Resource Naming Standards

**Naming Convention**: Follow FHIR R4 standards with Saudi healthcare extensions

**Common FHIR Resources Used**:

1. **Patient** (NPHIES-Patient-Profile)
   - Identifier: Saudi national ID (iqama/national ID)
   - Extension: Saudi-specific demographics
   - Naming: `Patient/{patient-id}`

2. **Practitioner** (NPHIES-Practitioner-Profile)
   - Identifier: Medical license number
   - Extension: Specialization, credentials
   - Naming: `Practitioner/{practitioner-id}`

3. **Organization** (NPHIES-Organization-Profile)
   - Identifier: Commercial registration, OID
   - Extension: Saudi healthcare facility type
   - Naming: `Organization/{organization-id}`

4. **Claim** (NPHIES-Claim-Profile)
   - Identifier: Claim reference number
   - Extension: Saudi-specific claim details
   - Naming: `Claim/{claim-id}`

5. **Coverage** (NPHIES-Coverage-Profile)
   - Identifier: Insurance policy number
   - Extension: Saudi payer information
   - Naming: `Coverage/{coverage-id}`

**OID to FHIR Mapping**:
```
1.3.6.1.4.1.61026 (BrainSAIT Root)
├── 1.3.6.1.4.1.61026.1.2.1 (NPHIES Integration)
│   ├── .100-199 (Practitioner OIDs) → FHIR Practitioner
│   ├── .200-299 (Organization OIDs) → FHIR Organization
│   └── .300-399 (Facility OIDs) → FHIR Location
├── 1.3.6.1.4.1.61026.2.1 (AI Ecosystem)
│   └── .100 (GIVC AI Services) → HealthcareService
└── 1.3.6.1.4.1.61026.3 (Security & Compliance)
    └── .100 (Audit Logs) → AuditEvent
```

---

## Data Flow Patterns

### Pattern 1: Healthcare Product Purchase Flow

```
1. User browses BrainSAIT Store
2. User adds healthcare product (e.g., GIVC API subscription) to cart
3. User proceeds to checkout
4. Payment processed via Stripe/Mada
5. Order created in BrainSAIT Store database
   ├─→ Order status: "payment_completed"
   └─→ Trigger: provisioning webhook

6. BrainSAIT Store calls GIVC provisioning API:
   POST https://givc-healthcare-api.fadil.workers.dev/api/v1/provision
   Body: {
     "order_id": "order_uuid_123",
     "product_sku": "GIVC-API-PRO",
     "customer": {
       "user_id": "user_uuid_456",
       "tenant_id": "tenant_uuid_789",
       "email": "provider@clinic.sa",
       "provider_oid": "1.3.6.1.4.1.61026.1.2.1.100"
     },
     "subscription": {
       "start_date": "2025-01-01",
       "duration_months": 12
     }
   }

7. GIVC API provisions resources:
   ├─→ Create GIVC account
   ├─→ Assign API credentials
   ├─→ Configure NPHIES integration
   ├─→ Setup healthcare provider profile
   └─→ Initialize AI medical processing

8. GIVC returns provisioning details:
   Response: {
     "status": "success",
     "account_id": "givc_account_uuid",
     "api_key": "givc_api_key_***",
     "nphies_credentials": {
       "client_id": "nphies_client_***",
       "endpoints": {
         "authorization": "https://nphies.sa/auth",
         "claim": "https://nphies.sa/claim"
       }
     },
     "access_url": "https://portal.givc.brainsait.com/account/..."
   }

9. BrainSAIT Store updates order:
   ├─→ Order status: "fulfilled"
   ├─→ Store provisioning details
   └─→ Send confirmation email with access instructions

10. User receives email with:
    ├─→ GIVC account credentials
    ├─→ Quick start guide
    ├─→ NPHIES integration instructions
    └─→ Support contact information
```

### Pattern 2: Cross-Service Authentication Flow

```
1. User logs into BrainSAIT Store
2. JWT token generated with claims for both Store and GIVC access
3. User navigates to "My Healthcare Services" in Store
4. Frontend makes request to GIVC API with BrainSAIT token:
   GET https://givc-healthcare-api.fadil.workers.dev/api/v1/dashboard
   Headers:
     Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     X-Tenant-ID: tenant_uuid_789

5. GIVC API Gateway validates token:
   ├─→ Verify signature (shared secret with BrainSAIT)
   ├─→ Check expiration
   ├─→ Validate audience includes "givc-api"
   └─→ Extract user_id, tenant_id, permissions

6. If token valid:
   ├─→ Create/refresh GIVC session in Redis
   ├─→ Load user's GIVC profile
   └─→ Return dashboard data

7. If token expired:
   ├─→ Return 401 Unauthorized
   └─→ Frontend refreshes token via BrainSAIT Store
        POST /api/v1/auth/refresh
        Body: { "refresh_token": "..." }
```

---

## Configuration Management

### Environment Variables Parity

**BrainSAIT Store** (`.env`):
```bash
# Shared Authentication
JWT_SECRET_KEY=shared_secret_between_brainsait_and_givc_***
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# GIVC Integration
GIVC_API_URL=https://givc-healthcare-api.fadil.workers.dev
GIVC_API_KEY=givc_integration_key_***
GIVC_WEBHOOK_SECRET=webhook_secret_***

# OID Configuration
OID_ROOT=1.3.6.1.4.1.61026
OID_NPHIES_BRANCH=1.3.6.1.4.1.61026.1.2.1
OID_AI_BRANCH=1.3.6.1.4.1.61026.2.1

# NPHIES Integration (shared with GIVC)
NPHIES_BASE_URL=https://nphies.sa/api
NPHIES_CLIENT_ID=brainsait_nphies_client_***
NPHIES_CLIENT_SECRET=brainsait_nphies_secret_***
NPHIES_SCOPE=openid,profile,claims,authorizations

# Database (shared schema)
DATABASE_URL=postgresql://user:pass@localhost:5432/brainsait_unified
REDIS_URL=redis://localhost:6379/0
```

**GIVC Healthcare API** (Cloudflare Workers Secrets):
```bash
# Shared Authentication (must match BrainSAIT)
JWT_SECRET_KEY=shared_secret_between_brainsait_and_givc_***
JWT_ALGORITHM=HS256

# BrainSAIT Integration
BRAINSAIT_STORE_API_URL=https://api.store.brainsait.io
BRAINSAIT_WEBHOOK_SECRET=webhook_secret_***

# NPHIES Integration (same as BrainSAIT)
NPHIES_BASE_URL=https://nphies.sa/api
NPHIES_CLIENT_ID=brainsait_nphies_client_***
NPHIES_CLIENT_SECRET=brainsait_nphies_secret_***

# AI Models
OPENAI_API_KEY=openai_key_***
AI_MODEL_ENDPOINT=https://ai-models.brainsait.com

# Database Access (shared with BrainSAIT)
DATABASE_CONNECTION_STRING=postgresql://...
REDIS_CONNECTION_STRING=redis://...
```

### Configuration Checklist

- [x] JWT secrets synchronized across services
- [x] NPHIES credentials shared between BrainSAIT and GIVC
- [x] Database connection strings use same unified schema
- [x] Redis configuration matches for session sharing
- [x] OID root and branch identifiers consistent
- [x] Webhook secrets configured for bidirectional communication
- [x] API URLs point to correct production endpoints
- [x] FHIR server endpoints configured (if separate)
- [x] Logging levels and destinations aligned
- [x] Feature flags synchronized

---

## Security & Compliance

### Secrets Management

**Encryption Standard**: AES-256-GCM for data at rest, TLS 1.3 for data in transit

**Secret Storage**:
1. **Production Secrets**: Cloudflare Workers Secrets + HashiCorp Vault
2. **Development Secrets**: `.env` files (git-ignored) + local encrypted storage
3. **Secret Rotation**: Automated 90-day rotation for critical secrets

**Access Control**:
- Secrets accessible only to authorized services
- Role-based access for human operators
- Audit logging for all secret access

### Audit Logging

**Audit Events** (stored in PostgreSQL `audit_logs` table):

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL, -- e.g., "auth.login", "givc.provision"
    actor_id UUID NOT NULL, -- user or service ID
    actor_type VARCHAR(50) NOT NULL, -- "user", "service", "system"
    tenant_id UUID NOT NULL,
    resource_type VARCHAR(100), -- e.g., "HealthcareProvider", "Claim"
    resource_id VARCHAR(255),
    action VARCHAR(50) NOT NULL, -- "create", "read", "update", "delete"
    status VARCHAR(50) NOT NULL, -- "success", "failure", "pending"
    metadata JSONB, -- additional contextual data
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_actor_id ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

**Critical Events to Log**:
- Authentication attempts (success/failure)
- Authorization decisions
- PHI access (healthcare data)
- Data modifications (create/update/delete)
- Service provisioning
- Configuration changes
- API key usage
- Cross-service communications

### Compliance Standards

**HIPAA Compliance** (Healthcare data):
- PHI encrypted at rest and in transit
- Access controls and audit logging
- Data retention policies (7 years)
- Business Associate Agreements (BAAs) with third parties

**NPHIES Compliance** (Saudi healthcare):
- FHIR R4 resource structure
- Saudi-specific extensions and profiles
- OID registration and management
- Real-time claim submission and tracking

**ZATCA Compliance** (Saudi tax):
- E-invoicing for all transactions
- QR code generation with required fields
- VAT calculation (15%)
- Invoice retention (6 years)

---

## Testing Strategy

### Integration Testing

**Smoke Test Suite** (`backend/tests/integration/test_givc_auth.py`):
1. Authentication flow (BrainSAIT → GIVC)
2. Session exchange and validation
3. Provider profile sync
4. Healthcare product provisioning
5. Webhook delivery and processing

**Performance Tests**:
- Token validation latency (<50ms)
- Cross-service API calls (<200ms p95)
- Session state replication (<100ms)
- Database query performance (<100ms)

### Monitoring

**Health Checks**:
- `GET /health` on all services (5-second interval)
- Database connectivity
- Redis connectivity
- External API availability (NPHIES, Payment Gateways)

**Alerts**:
- Service downtime (immediate)
- High error rates (>1%)
- Slow response times (p95 >500ms)
- Failed authentication attempts (>10 in 5 min)
- Webhook delivery failures

---

## Deployment & Rollout

### Deployment Strategy

**Phase 1**: Internal Testing (Week 1)
- Deploy to staging environment
- Run smoke tests
- Validate authentication flow
- Test provider provisioning

**Phase 2**: Pilot (Week 2-3)
- Select 5 pilot healthcare providers
- Enable GIVC integration
- Monitor closely
- Gather feedback

**Phase 3**: General Availability (Week 4+)
- Roll out to all customers
- Enable automated provisioning
- Full monitoring and alerting
- Documentation and support

### Rollback Plan

If critical issues detected:
1. Disable GIVC auto-provisioning
2. Revert to manual provisioning process
3. Investigate and fix issues
4. Re-test in staging
5. Gradual re-rollout

---

## Support & Maintenance

### Runbook

**Common Issues**:

1. **Token Validation Failure**
   - Check JWT secret synchronization
   - Verify token expiration settings
   - Review audience claims

2. **Provisioning Failure**
   - Check GIVC API availability
   - Verify webhook delivery
   - Review provisioning logs

3. **Session Not Syncing**
   - Check Redis connectivity
   - Verify session TTL settings
   - Review session replication logs

### On-Call Escalation

**Tier 1**: DevOps (first response)
**Tier 2**: Backend Engineers (integration issues)
**Tier 3**: Architecture Team (design issues)

---

**Last Updated**: 2025-01-09  
**Document Owner**: Architecture Team  
**Review Frequency**: Bi-weekly during integration, monthly after GA
