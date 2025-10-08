# Service Inventory and Data Flows

## Overview
This document provides a comprehensive inventory of all services in the BrainSAIT ecosystem with their data flows, focusing on the integration between BrainSAIT Store and GIVC Healthcare Platform.

---

## System Architecture

### Core Services Inventory

#### 1. BrainSAIT Store Platform
**Service Name**: BrainSAIT Store  
**Type**: E-commerce Platform  
**Technology**: Next.js 14 (Frontend) + FastAPI (Backend)  
**Status**: ✅ Production Ready  
**URL**: https://store.brainsait.io  
**Repository**: https://github.com/Fadil369/brainsait-store

**Components**:
- Frontend (Next.js 14 with TypeScript)
- Backend API (FastAPI with Python 3.11+)
- PostgreSQL Database
- Redis Cache
- Cloudflare Workers (API Gateway)

**Responsibilities**:
- Product catalog management
- Shopping cart and checkout
- Payment processing (Stripe, PayPal, Mada, STC Pay)
- Order management
- Multi-tenant B2B features
- Arabic/English bilingual support
- Analytics and reporting

#### 2. GIVC Healthcare API
**Service Name**: GIVC Healthcare API  
**Type**: Healthcare Processing Service  
**Technology**: Cloudflare Workers + AI Models  
**Status**: ✅ Live  
**URL**: https://givc-healthcare-api.fadil.workers.dev  
**Repository**: Cross-referenced in GIVC system

**Components**:
- AI Medical Data Processing
- NPHIES Integration Layer
- FHIR Resource Management
- Healthcare Provider Directory
- Medical Records Processing

**Responsibilities**:
- Medical data processing with AI
- NPHIES (Saudi Healthcare) integration
- FHIR-compliant data transformation
- Healthcare provider management
- Medical terminology standardization
- Secure PHI (Protected Health Information) handling

#### 3. BrainSAIT API Gateway
**Service Name**: BrainSAIT API Gateway  
**Type**: API Gateway & Router  
**Technology**: Cloudflare Workers  
**Status**: ✅ Live  
**URL**: https://brainsait-api-gateway.fadil.workers.dev  
**Deployment**: Cloudflare Workers Global Network

**Components**:
- Request routing and load balancing
- Rate limiting (KV Storage)
- CORS management
- Health monitoring
- Multi-tenant routing

**Responsibilities**:
- Route requests to appropriate backend services
- Enforce rate limits (120 req/min default)
- Handle CORS for cross-origin requests
- Monitor service health
- Tenant context management
- Request/response transformation

#### 4. HealthLinc EHR/RCM System
**Service Name**: HealthLinc  
**Type**: Electronic Health Records & Revenue Cycle Management  
**Technology**: Python/FastAPI  
**Status**: ✅ Production Ready  
**Repository**: https://github.com/Fadil369/HealthLinc

**Components**:
- Patient records management
- Appointment scheduling
- Billing and claims processing
- Clinical documentation
- Revenue cycle management

**Responsibilities**:
- Manage patient health records
- Schedule and track appointments
- Process insurance claims
- Generate medical documentation
- Track revenue cycle metrics
- Integrate with NPHIES for claims submission

#### 5. HealthLinc Logs Monitoring
**Service Name**: HealthLinc Logs  
**Type**: Logging and Monitoring Service  
**Technology**: Cloudflare Workers  
**Status**: ✅ Live  
**URL**: https://healthlinc-logs.fadil.workers.dev

**Responsibilities**:
- Real-time log aggregation
- Smart alerting and notifications
- Performance monitoring
- Error tracking
- Audit trail management
- Compliance logging

#### 6. MCP ServerLinc
**Service Name**: MCP ServerLinc  
**Type**: Model Context Protocol Server  
**Technology**: Cloudflare Workers  
**Status**: ✅ Live  
**URL**: https://mcp-serverlinc.fadil.workers.dev

**Responsibilities**:
- AI model context management
- Protocol translation
- Model versioning
- Context synchronization
- Integration orchestration

#### 7. OID Integration Service
**Service Name**: OID System Bridge  
**Type**: Healthcare Identifier Management  
**Technology**: FastAPI (Embedded in BrainSAIT Store)  
**Status**: ✅ Operational  
**API Endpoint**: /api/v1/oid/*

**Components**:
- OID tree management
- Healthcare provider linking
- Product-OID mapping
- NPHIES integration support

**Responsibilities**:
- Manage OID tree structure (1.3.6.1.4.1.61026.*)
- Link healthcare providers to OID nodes
- Map products to healthcare services via OIDs
- Support NPHIES integration with proper identifiers
- Maintain OID hierarchy and metadata

---

## Data Flow Diagrams

### 1. User Purchase Flow (E-commerce)

```
User (Browser)
    │
    ├─→ Frontend (Next.js) → View Products, Add to Cart
    │
    └─→ API Gateway (Cloudflare Workers)
         │
         ├─→ Rate Limiting Check (KV Storage)
         ├─→ CORS Validation
         └─→ Route to Backend
              │
              └─→ FastAPI Backend
                   │
                   ├─→ Product Service → PostgreSQL (Read Products)
                   ├─→ Cart Service → Redis (Cart State)
                   ├─→ Payment Service → Stripe/PayPal/Mada API
                   ├─→ Order Service → PostgreSQL (Create Order)
                   └─→ Notification Service → Email/SMS
                        │
                        └─→ Response → Gateway → Frontend → User
```

### 2. Healthcare Service Integration Flow (GIVC)

```
Healthcare Provider/User
    │
    └─→ BrainSAIT Store
         │
         └─→ Purchase Healthcare Product (GIVC API, HealthLinc)
              │
              ├─→ API Gateway → FastAPI Backend
              │    │
              │    ├─→ Validate Tenant & Healthcare Credentials
              │    ├─→ Check OID Mapping
              │    └─→ Create Order with Healthcare Metadata
              │
              └─→ Provision Healthcare Service
                   │
                   ├─→ GIVC Healthcare API
                   │    ├─→ Create Healthcare Account
                   │    ├─→ Assign NPHIES Credentials
                   │    └─→ Initialize AI Medical Processing
                   │
                   ├─→ HealthLinc EHR
                   │    ├─→ Create Provider Account
                   │    ├─→ Setup Practice Configuration
                   │    └─→ Initialize Revenue Cycle Management
                   │
                   └─→ OID Integration Service
                        ├─→ Register Provider OID
                        ├─→ Link to NPHIES System
                        └─→ Update Healthcare Provider Directory
```

### 3. Authentication & Session Exchange Flow

```
User Authentication Request
    │
    ├─→ BrainSAIT Store Frontend
    │    └─→ POST /api/v1/auth/login
    │
    └─→ API Gateway
         │
         └─→ FastAPI Backend (Auth Service)
              │
              ├─→ Validate Credentials (PostgreSQL)
              ├─→ Check Tenant Context
              ├─→ Generate JWT Tokens (Access + Refresh)
              ├─→ Store Session (Redis)
              └─→ Return Tokens + User Profile
                   │
                   └─→ Frontend stores tokens
                        │
                        └─→ Subsequent Requests Include:
                             ├─→ Authorization: Bearer {access_token}
                             └─→ X-Tenant-ID: {tenant_id}

Cross-Service Session Exchange (BrainSAIT ↔ GIVC):
    │
    ├─→ User Authenticated in BrainSAIT
    │    └─→ Access Token Generated with Claims:
    │         ├─→ user_id
    │         ├─→ tenant_id
    │         ├─→ email
    │         ├─→ roles
    │         └─→ permissions
    │
    └─→ Request to GIVC Service
         │
         ├─→ Forward BrainSAIT Token in Header
         ├─→ GIVC Validates Token (Shared Secret/Public Key)
         ├─→ GIVC Creates Internal Session
         └─→ GIVC Returns GIVC-Specific Token (if needed)
              │
              └─→ User Can Access Both Systems with Single Sign-On
```

### 4. NPHIES Integration Data Flow (Saudi Healthcare)

```
Healthcare Transaction (Claim/Authorization)
    │
    ├─→ HealthLinc EHR (Provider enters claim data)
    │    │
    │    └─→ Validate Clinical Data
    │         ├─→ Patient demographics
    │         ├─→ Diagnosis codes (ICD-10)
    │         ├─→ Procedure codes (CPT/HCPCS)
    │         └─→ Provider information
    │
    └─→ GIVC Healthcare API
         │
         ├─→ Transform to FHIR Format
         │    ├─→ Patient Resource
         │    ├─→ Claim Resource
         │    ├─→ Coverage Resource
         │    └─→ Organization Resource
         │
         ├─→ Enrich with OID Data
         │    ├─→ Provider OID (1.3.6.1.4.1.61026.1.2.1.xxx)
         │    ├─→ Organization OID
         │    └─→ Facility OID
         │
         └─→ Submit to NPHIES
              │
              ├─→ Authorization Request → NPHIES API
              ├─→ Claim Submission → NPHIES API
              └─→ Response Processing
                   │
                   ├─→ Success → Update HealthLinc Status
                   ├─→ Pending → Queue for Follow-up
                   └─→ Rejection → Log Error, Notify Provider
                        │
                        └─→ Audit Log to HealthLinc Logs
```

### 5. Analytics & Monitoring Data Flow

```
System Events (All Services)
    │
    ├─→ Application Logs
    │    ├─→ BrainSAIT Store Backend
    │    ├─→ GIVC Healthcare API
    │    ├─→ HealthLinc EHR
    │    └─→ API Gateway
    │         │
    │         └─→ HealthLinc Logs Service
    │              ├─→ Aggregate Logs
    │              ├─→ Parse and Index
    │              ├─→ Detect Anomalies
    │              └─→ Generate Alerts
    │
    ├─→ Performance Metrics
    │    ├─→ Response Times
    │    ├─→ Error Rates
    │    ├─→ Request Volumes
    │    └─→ Resource Utilization
    │         │
    │         └─→ Analytics Service
    │              ├─→ Real-time Dashboard
    │              ├─→ Historical Trends
    │              └─→ Predictive Insights
    │
    └─→ Business Metrics
         ├─→ Sales Data (BrainSAIT Store)
         ├─→ Healthcare Transactions (GIVC)
         ├─→ Claims Processing (HealthLinc)
         └─→ Revenue Metrics
              │
              └─→ PostgreSQL Analytics Tables
                   └─→ BI Tools & Reports
```

---

## Service Dependencies

### Dependency Matrix

| Service | Depends On | Provides To |
|---------|-----------|-------------|
| BrainSAIT Store Frontend | API Gateway, CDN | User Interface |
| BrainSAIT Store Backend | PostgreSQL, Redis, Payment APIs | API Gateway, Frontend |
| API Gateway | KV Storage | All Frontend Apps, External Integrations |
| GIVC Healthcare API | NPHIES API, AI Models | HealthLinc, Store Backend |
| HealthLinc EHR | GIVC API, OID Service | Healthcare Providers |
| HealthLinc Logs | All Services | Monitoring Dashboard |
| OID Integration Service | PostgreSQL | GIVC, HealthLinc, NPHIES |
| MCP ServerLinc | AI Models | GIVC, Store Backend |

### Critical Paths

1. **E-commerce Critical Path**:
   Frontend → API Gateway → Backend → PostgreSQL/Redis → Payment Gateway → Order Fulfillment

2. **Healthcare Critical Path**:
   HealthLinc → GIVC API → OID Service → NPHIES → Payer Response

3. **Authentication Critical Path**:
   Frontend → API Gateway → Auth Service → Redis (Session) → PostgreSQL (User Data)

---

## Integration Points

### 1. BrainSAIT Store ↔ GIVC Healthcare API

**Integration Type**: REST API  
**Authentication**: JWT Token (Shared Secret Validation)  
**Data Format**: JSON with FHIR resources

**Endpoints**:
- `POST /api/v1/givc/healthcare/account` - Create healthcare account
- `GET /api/v1/givc/healthcare/providers` - List providers
- `POST /api/v1/givc/healthcare/claims` - Submit claims
- `GET /api/v1/givc/healthcare/claims/{id}` - Get claim status

**Shared Data Models**:
- Healthcare Provider Profile
- Patient Demographics
- Medical Claims
- Authorization Requests

### 2. BrainSAIT Store ↔ HealthLinc EHR

**Integration Type**: REST API + Webhooks  
**Authentication**: API Keys + OAuth 2.0  
**Data Format**: JSON

**Endpoints**:
- `POST /api/v1/healthlinc/providers` - Create provider account
- `GET /api/v1/healthlinc/appointments` - List appointments
- `POST /api/v1/healthlinc/claims` - Submit claims
- `GET /api/v1/healthlinc/revenue` - Get revenue metrics

**Webhooks**:
- `webhook/healthlinc/claim-status` - Claim status updates
- `webhook/healthlinc/payment-received` - Payment notifications

### 3. GIVC ↔ NPHIES (Saudi Healthcare)

**Integration Type**: SOAP/REST API (FHIR-based)  
**Authentication**: X.509 Certificates + OAuth  
**Data Format**: FHIR R4 Resources

**Key Resources**:
- Patient (demographics)
- Claim (billing)
- Coverage (insurance)
- Organization (provider/payer)
- Practitioner (healthcare professional)

### 4. Cross-Service Authentication

**Method**: JWT Token Validation with Shared Secret  
**Token Claims**:
```json
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "email": "user@example.com",
  "name": "User Name",
  "roles": ["admin", "healthcare_provider"],
  "permissions": ["read:products", "write:claims"],
  "iss": "brainsait-store",
  "aud": ["givc-api", "healthlinc-api"],
  "exp": 1234567890,
  "iat": 1234567890
}
```

---

## Data Consistency & Synchronization

### 1. Product Catalog Sync
- **Frequency**: Real-time on changes
- **Method**: Event-driven updates via Redis Pub/Sub
- **Fallback**: Scheduled sync every 5 minutes

### 2. Healthcare Provider Directory
- **Frequency**: Daily full sync + real-time updates
- **Method**: API polling + webhooks
- **Reconciliation**: Weekly full reconciliation

### 3. Order & Transaction Sync
- **Frequency**: Real-time
- **Method**: Webhook notifications
- **Retry Logic**: Exponential backoff (up to 5 attempts)

### 4. Session State Sync
- **Frequency**: Real-time
- **Storage**: Redis with 30-minute TTL
- **Replication**: Cross-region for high availability

---

## Service Level Agreements (SLAs)

| Service | Uptime | Response Time | Error Rate |
|---------|--------|---------------|------------|
| BrainSAIT Store Frontend | 99.9% | <500ms (p95) | <0.1% |
| BrainSAIT Store Backend | 99.95% | <200ms (p95) | <0.1% |
| API Gateway | 99.99% | <50ms (p95) | <0.01% |
| GIVC Healthcare API | 99.9% | <300ms (p95) | <0.1% |
| HealthLinc EHR | 99.95% | <400ms (p95) | <0.1% |
| NPHIES Integration | 99.5% | <2000ms (p95) | <1% |

---

## Disaster Recovery & Failover

### Backup Services
1. **Primary**: Cloudflare global network
2. **Failover**: Regional VMs on standby
3. **Data Backup**: PostgreSQL daily snapshots + PITR
4. **Cache Failover**: Redis cluster with automatic failover

### Recovery Time Objectives (RTO)
- Critical Services (Store, API Gateway): 5 minutes
- Healthcare Services (GIVC, HealthLinc): 15 minutes
- Analytics & Reporting: 1 hour

### Recovery Point Objectives (RPO)
- Transaction Data: 0 (real-time replication)
- Healthcare Records: 5 minutes (backup frequency)
- Analytics Data: 1 hour (acceptable data loss)

---

## Compliance & Security

### Data Classification
1. **Highly Sensitive**: PHI (Protected Health Information)
2. **Sensitive**: User credentials, payment information
3. **Internal**: Business metrics, logs
4. **Public**: Product catalog, marketing content

### Security Controls
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Access control (RBAC + ABAC)
- Audit logging (all data access)
- Data masking (PHI in non-production)

### Compliance Standards
- **HIPAA**: Healthcare data handling
- **NPHIES**: Saudi healthcare integration
- **ZATCA**: Saudi tax authority e-invoicing
- **PCI DSS**: Payment card data security
- **GDPR**: European data protection (if applicable)

---

## Service Contact Information

| Service | Team Contact | On-Call | Documentation |
|---------|-------------|---------|---------------|
| BrainSAIT Store | store-team@brainsait.com | +966-xxx-xxx-xxxx | /docs/store/ |
| GIVC Healthcare API | givc-team@brainsait.com | +966-xxx-xxx-xxxx | /docs/givc/ |
| HealthLinc EHR | healthlinc@brainsait.com | +966-xxx-xxx-xxxx | /docs/healthlinc/ |
| API Gateway | infrastructure@brainsait.com | +966-xxx-xxx-xxxx | /docs/infrastructure/ |
| DevOps | devops@brainsait.com | +966-xxx-xxx-xxxx | /docs/devops/ |

---

**Last Updated**: 2025-01-09  
**Document Owner**: DevOps Team  
**Review Frequency**: Monthly
