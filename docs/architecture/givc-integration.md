# GIVC Healthcare Platform Integration Architecture

## Overview

This document details the architecture for integrating the GIVC Healthcare Platform with the BrainsAIT Store ecosystem, creating a unified B2B healthcare solution.

**Integration ID**: `givc-brainsait-integration-v1`  
**Status**: 🔄 In Progress  
**Last Updated**: October 2024

---

## 🏥 GIVC Healthcare Platform

### Platform Description
GIVC is a comprehensive healthcare platform providing:
- AI-powered medical data processing
- NPHIES integration for Saudi healthcare system
- Real-time healthcare analytics
- HIPAA-compliant data handling
- Healthcare provider management

### Live Endpoints
- **Production API**: `https://givc-healthcare-api.fadil.workers.dev`
- **Healthcare Portal**: GIVC web application
- **Admin Interface**: Healthcare provider management

---

## 🏗️ Integration Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     BrainsAIT Store Frontend                    │
│                    (Next.js 14 / TypeScript)                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Product Catalog │  │  Healthcare      │  │  Analytics   │  │
│  │  (GIVC Products) │  │  Dashboard       │  │  Dashboard   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BrainsAIT API Gateway                          │
│                  (Cloudflare Workers)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  Request     │  │  Multi-Tenant│  │  Healthcare API    │    │
│  │  Routing     │  │  Isolation   │  │  Routing           │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
└──────────┬──────────────────────────────────────┬───────────────┘
           │                                      │
           ▼                                      ▼
┌──────────────────────────┐      ┌─────────────────────────────┐
│  BrainsAIT Backend       │      │  GIVC Healthcare API        │
│  (FastAPI / Python)      │      │  (Cloudflare Workers)       │
├──────────────────────────┤      ├─────────────────────────────┤
│  • Store Services        │      │  • AI Processing            │
│  • Payment Processing    │      │  • NPHIES Integration       │
│  • User Management       │      │  • Medical Data Processing  │
│  • Order Management      │      │  • Healthcare Analytics     │
│  • Analytics             │      │  • Provider Management      │
└──────────┬───────────────┘      └────────────┬────────────────┘
           │                                   │
           ▼                                   ▼
┌──────────────────────────┐      ┌─────────────────────────────┐
│  PostgreSQL Database     │      │  GIVC Data Store            │
│  • Users & Tenants       │      │  • Medical Records          │
│  • Products & Orders     │      │  • Healthcare Providers     │
│  • Payments & Invoices   │      │  • NPHIES Data              │
│  • Analytics Events      │      │  • AI Processing Results    │
└──────────────────────────┘      └─────────────────────────────┘
```

---

## 🔗 Integration Points

### 1. Product Catalog Integration

**Purpose**: Integrate GIVC healthcare products into BrainsAIT Store

**Implementation**:
```typescript
// Frontend: frontend/src/data/products.ts
{
  id: 5,
  category: "websites",
  title: "Givc",
  arabicTitle: "موقع Givc",
  description: "GIVC Healthcare Platform | Complete B2B solution",
  price: 14999,
  features: [
    "🏥 Healthcare Integration",
    "📊 Real-time Analytics",
    "🔐 HIPAA Compliant",
    "🇸🇦 NPHIES Compatible"
  ]
}
```

**Data Flow**:
1. Product data stored in BrainsAIT product catalog
2. GIVC-specific metadata (healthcare features, compliance)
3. Pricing tiers for different healthcare provider sizes
4. Live demo links to GIVC platform

### 2. Healthcare API Integration

**Purpose**: Enable healthcare-specific functionality through GIVC API

**Endpoints**:
```
GIVC Healthcare API:
├── GET  /health                    # Health check
├── POST /api/v1/medical/process    # AI medical data processing
├── POST /api/v1/nphies/submit      # NPHIES submission
├── GET  /api/v1/providers          # Healthcare provider list
├── GET  /api/v1/analytics          # Healthcare analytics
└── POST /api/v1/claims             # Insurance claims processing
```

**Integration Pattern**:
```typescript
// API Gateway routes GIVC requests
if (request.url.includes('/healthcare')) {
  return fetch('https://givc-healthcare-api.fadil.workers.dev' + path, {
    headers: {
      'X-Tenant-ID': tenantId,
      'Authorization': `Bearer ${token}`
    }
  });
}
```

### 3. Multi-Tenant Healthcare Data

**Purpose**: Isolate healthcare provider data by tenant

**Implementation**:
- Tenant ID passed in all GIVC API requests
- Healthcare data scoped to tenant
- Provider-specific configurations
- Compliance settings per tenant

**Security**:
- HIPAA-compliant data handling
- Encrypted data at rest and in transit
- Audit logging for all medical data access
- Role-based access control (RBAC)

### 4. Analytics & Reporting

**Purpose**: Unified analytics across BrainsAIT and GIVC

**Metrics Integrated**:
- Healthcare product usage
- NPHIES submission statistics
- Provider performance metrics
- Revenue from healthcare products
- Customer healthcare journey tracking

**Dashboard Integration**:
```
Admin Dashboard:
├── Healthcare Product Sales
├── GIVC API Usage Metrics
├── Provider Onboarding Stats
├── NPHIES Integration Health
└── Compliance & Audit Reports
```

### 5. Authentication & Authorization

**Purpose**: Unified authentication across platforms

**Flow**:
```
User Login (BrainsAIT)
    │
    ▼
JWT Token Issued
    │
    ├─→ BrainsAIT Store Access
    │
    └─→ GIVC Healthcare Access
        (Token validated by GIVC API)
```

**Token Claims**:
```json
{
  "user_id": "uuid",
  "tenant_id": "tenant-uuid",
  "roles": ["healthcare_provider", "admin"],
  "givc_access": true,
  "healthcare_permissions": [
    "read_medical_data",
    "submit_nphies",
    "access_analytics"
  ]
}
```

---

## 🔐 Security Architecture

### Data Protection

**Encryption**:
- TLS 1.3 for data in transit
- AES-256 encryption for data at rest
- Field-level encryption for sensitive medical data

**Access Control**:
- Multi-factor authentication (MFA) for healthcare providers
- Role-based access control (RBAC)
- Attribute-based access control (ABAC) for medical data
- Session management with secure JWT tokens

**Compliance**:
- HIPAA compliance for US healthcare data
- ZATCA compliance for Saudi Arabia
- NPHIES integration compliance
- Regular security audits

### API Security

**Authentication**:
```http
Authorization: Bearer <jwt-token>
X-Tenant-ID: <tenant-id>
X-API-Key: <api-key>
```

**Rate Limiting**:
- Standard users: 60 requests/minute
- Healthcare providers: 120 requests/minute
- Enterprise: 240 requests/minute

**Input Validation**:
- Schema validation for all requests
- Sanitization of medical data inputs
- SQL injection prevention
- XSS protection

---

## 🔄 Data Synchronization

### Product Synchronization

**Schedule**: Real-time updates with eventual consistency

**Process**:
1. GIVC product updates trigger webhook
2. BrainsAIT receives webhook notification
3. Product catalog updated in database
4. Cache invalidated
5. Frontend receives updated product data

**Fallback**: Manual sync every 24 hours

### Healthcare Provider Data

**Synchronization Points**:
- Provider registration
- Provider profile updates
- License verification updates
- Compliance status changes

**Implementation**:
```python
# Backend synchronization service
async def sync_givc_provider_data(tenant_id: str):
    """Sync healthcare provider data from GIVC"""
    givc_data = await givc_api.get_provider(tenant_id)
    
    # Update local cache
    await cache.set(f"provider:{tenant_id}", givc_data, ttl=3600)
    
    # Update database
    await db.update_provider_data(tenant_id, givc_data)
    
    # Trigger analytics update
    await analytics.track_provider_sync(tenant_id)
```

---

## 📊 Monitoring & Observability

### Health Checks

**BrainsAIT Gateway**:
```bash
curl https://brainsait-api-gateway.fadil.workers.dev/health
```

**GIVC Healthcare API**:
```bash
curl https://givc-healthcare-api.fadil.workers.dev/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "gateway": "operational",
    "givc_api": "operational",
    "database": "operational",
    "cache": "operational"
  },
  "integration_status": {
    "givc_healthcare": "connected",
    "nphies": "operational"
  }
}
```

### Metrics to Monitor

**Performance**:
- API response time (p50, p95, p99)
- GIVC API latency
- Database query performance
- Cache hit rate

**Availability**:
- Service uptime (target: 99.9%)
- GIVC API availability
- Database availability
- Payment gateway availability

**Business**:
- Healthcare product sales
- GIVC API usage
- Provider onboarding rate
- NPHIES submission success rate

### Alerting Rules

**Critical Alerts** (Page immediately):
- GIVC API unavailable > 2 minutes
- Medical data access violation
- Payment processing failure rate > 5%
- HIPAA compliance breach detected

**Warning Alerts** (Notify within 15 minutes):
- GIVC API response time > 1 second
- Cache hit rate < 80%
- Provider sync failures > 10%
- Database connection pool exhaustion

---

## 🚀 Deployment Strategy

### Phased Rollout

**Phase 1: Internal Testing** (Week 1-2)
- Deploy to staging environment
- Internal team testing
- Security validation
- Performance testing

**Phase 2: Beta Release** (Week 3-4)
- Limited release to select healthcare providers
- Gather feedback
- Monitor metrics
- Fix issues

**Phase 3: General Availability** (Week 5+)
- Full production rollout
- Marketing launch
- Support team ready
- Continuous monitoring

### Deployment Checklist

- [ ] Infrastructure provisioned
- [ ] SSL certificates configured
- [ ] Database migrations completed
- [ ] Environment variables set
- [ ] API keys configured
- [ ] Rate limiting rules deployed
- [ ] Monitoring dashboards set up
- [ ] Alert rules configured
- [ ] Documentation published
- [ ] Support team trained

---

## 🔧 Configuration

### Environment Variables

**BrainsAIT Backend**:
```bash
GIVC_API_URL=https://givc-healthcare-api.fadil.workers.dev
GIVC_API_KEY=<secret-key>
GIVC_WEBHOOK_SECRET=<webhook-secret>
GIVC_INTEGRATION_ENABLED=true
HIPAA_COMPLIANCE_MODE=true
```

**Frontend**:
```bash
NEXT_PUBLIC_GIVC_API_URL=https://givc-healthcare-api.fadil.workers.dev
NEXT_PUBLIC_GIVC_INTEGRATION=enabled
NEXT_PUBLIC_HEALTHCARE_FEATURES=true
```

**API Gateway (Cloudflare Workers)**:
```toml
[env.production.vars]
GIVC_API_URL = "https://givc-healthcare-api.fadil.workers.dev"
GIVC_RATE_LIMIT = "120"
HEALTHCARE_MODE = "enabled"
```

---

## 📋 Testing Strategy

### Integration Testing

**Test Scenarios**:
1. **Product Catalog Integration**
   - GIVC products display correctly
   - Pricing tiers work
   - Healthcare features shown
   - Demo links functional

2. **Healthcare API Integration**
   - Medical data processing
   - NPHIES submissions
   - Provider management
   - Analytics retrieval

3. **Multi-Tenant Isolation**
   - Data segregation
   - Cross-tenant access prevention
   - Tenant-specific configurations

4. **Authentication & Authorization**
   - JWT token validation
   - Role-based access
   - Healthcare permissions
   - Session management

### Performance Testing

**Load Test Scenarios**:
- 100 concurrent users browsing healthcare products
- 50 concurrent NPHIES submissions
- 1000 analytics queries per minute
- Peak hour traffic simulation

**Success Criteria**:
- API response time < 200ms (p95)
- Zero data corruption
- 100% multi-tenant isolation
- 99.9% uptime

---

## 🐛 Troubleshooting

### Common Issues

**Issue: GIVC API Timeout**
```
Symptom: Requests to GIVC API taking > 30 seconds
Diagnosis: Check GIVC API health endpoint
Resolution: 
  1. Verify network connectivity
  2. Check API gateway logs
  3. Review GIVC API status page
  4. Implement circuit breaker if persistent
```

**Issue: Multi-Tenant Data Leak**
```
Symptom: User sees data from another tenant
Diagnosis: Check tenant isolation in queries
Resolution:
  1. Verify tenant_id in all queries
  2. Review middleware tenant detection
  3. Check JWT token claims
  4. Audit database access logs
```

**Issue: HIPAA Compliance Violation**
```
Symptom: Unencrypted medical data detected
Diagnosis: Review data access logs
Resolution:
  1. Identify affected data
  2. Encrypt data immediately
  3. Notify compliance team
  4. Update audit logs
  5. Implement additional controls
```

---

## 📚 References

### Internal Documentation
- [System Architecture](./README.md)
- [Database Schema](./database.md)
- [API Documentation](../api/README.md)
- [Security Architecture](../security/security-audit.md)

### External Resources
- [GIVC Healthcare API Documentation](https://givc-healthcare-api.fadil.workers.dev/docs)
- [NPHIES Integration Guide](https://nphies.sa/)
- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/)
- [ZATCA E-Invoicing](https://zatca.gov.sa/)

### API Endpoints
- **BrainsAIT Gateway**: https://brainsait-api-gateway.fadil.workers.dev
- **GIVC Healthcare API**: https://givc-healthcare-api.fadil.workers.dev
- **Health Check**: /health
- **API Docs**: /api/docs

---

**Document Owner**: Platform/Infra Team  
**Last Updated**: October 2024  
**Status**: 🔄 In Progress  
**Next Review**: Weekly during integration phase
