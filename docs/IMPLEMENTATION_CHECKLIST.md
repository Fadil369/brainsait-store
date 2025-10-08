# GIVC Integration - Implementation Checklist

## Overview
This checklist guides the implementation of the GIVC Healthcare Platform integration with BrainSAIT Store based on the completed architecture documentation.

**Status**: Ready for Implementation  
**Last Updated**: 2025-01-09

---

## Phase 1: Pre-Implementation ✅ COMPLETE

### Documentation & Architecture ✅
- [x] Service inventory completed
- [x] Architecture diagrams created
- [x] Data flows documented
- [x] Shared models defined (FHIR-compliant)
- [x] Authentication flow designed
- [x] Secrets management documented
- [x] Configuration audit completed
- [x] CI/CD integration documented

### Code Artifacts ✅
- [x] Shared data models created (`backend/app/schemas/givc_integration.py`)
- [x] Integration tests written (21 tests, including smoke tests)
- [x] Configuration keys added to `config.py`
- [x] Environment variable templates updated (`.env.example`)
- [x] Architecture documentation updated

---

## Phase 2: Environment Setup

### Development Environment
- [ ] Install required dependencies
  ```bash
  cd backend
  pip install -r requirements.txt
  pip install pytest pytest-asyncio httpx PyJWT
  ```
- [ ] Create `.env` file from `.env.example`
- [ ] Configure development database
  ```bash
  createdb brainsait_store_dev
  ```
- [ ] Configure Redis for sessions
  ```bash
  redis-server --daemonize yes
  ```
- [ ] Set up local test JWT secret
  ```bash
  export JWT_SECRET_KEY="dev_jwt_secret_key_min_32_chars"
  ```

### Staging Environment
- [ ] Provision staging database (PostgreSQL)
- [ ] Provision staging Redis
- [ ] Deploy backend to staging
- [ ] Deploy frontend to staging (Cloudflare Pages)
- [ ] Deploy API Gateway to staging (Cloudflare Workers)
- [ ] Configure staging secrets in Vault
  - [ ] JWT_SECRET_KEY
  - [ ] DATABASE_URL
  - [ ] REDIS_URL
  - [ ] GIVC_API_KEY
  - [ ] NPHIES_CLIENT_SECRET (test environment)

### Production Environment
- [ ] Provision production database with backups
- [ ] Provision production Redis cluster
- [ ] Set up HashiCorp Vault for secrets
- [ ] Configure production secrets
  - [ ] JWT_SECRET_KEY (generate new, 32+ chars)
  - [ ] DATABASE_URL
  - [ ] REDIS_URL
  - [ ] GIVC_API_KEY
  - [ ] NPHIES_CLIENT_ID
  - [ ] NPHIES_CLIENT_SECRET
  - [ ] STRIPE_SECRET_KEY
  - [ ] PAYPAL_SECRET
- [ ] Set up SSL certificates
- [ ] Configure CORS origins
- [ ] Enable audit logging

---

## Phase 3: Code Implementation

### Backend Implementation

#### Authentication Service
- [ ] Implement JWT token generation with healthcare claims
  - [ ] Add `provider_oid` to token payload
  - [ ] Add `nphies_license` to token payload
  - [ ] Add `metadata` object for healthcare info
- [ ] Implement token validation middleware
  - [ ] Validate signature with shared secret
  - [ ] Check expiration
  - [ ] Verify audience includes "givc-api"
  - [ ] Extract healthcare metadata
- [ ] Implement session exchange endpoint
  ```python
  POST /api/v1/auth/session-exchange
  Body: { "brainsait_token": "...", "service": "givc-api" }
  ```

#### GIVC Integration Service
- [ ] Create GIVC integration service class
  ```python
  # backend/app/services/givc_service.py
  class GIVCIntegrationService:
      async def provision_healthcare_service(...)
      async def sync_provider_profile(...)
      async def validate_nphies_credentials(...)
  ```
- [ ] Implement service provisioning endpoint
  ```python
  POST /api/v1/givc/provision
  Body: ServiceProvisioningRequest
  Response: ServiceProvisioningResponse
  ```
- [ ] Implement webhook receiver for GIVC events
  ```python
  POST /webhooks/givc/claim-status
  POST /webhooks/givc/authorization
  ```
- [ ] Add HMAC signature validation for webhooks

#### OID Management Service
- [ ] Implement OID registration endpoint
  ```python
  POST /api/v1/oid/register
  Body: { "provider_id": "...", "organization_id": "..." }
  Response: { "provider_oid": "1.3.6.1.4.1.61026.1.2.1.xxx" }
  ```
- [ ] Implement OID tree query endpoint
  ```python
  GET /api/v1/oid/tree
  Response: OID tree structure
  ```
- [ ] Implement OID to provider lookup
  ```python
  GET /api/v1/oid/providers/{oid}
  Response: HealthcareProviderProfile
  ```

#### Database Migrations
- [ ] Create migration for healthcare provider table
  ```sql
  CREATE TABLE healthcare_providers (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    email VARCHAR(255) NOT NULL,
    given_name VARCHAR(100) NOT NULL,
    family_name VARCHAR(100) NOT NULL,
    given_name_ar VARCHAR(100),
    family_name_ar VARCHAR(100),
    license_number VARCHAR(50) NOT NULL,
    provider_oid VARCHAR(100) NOT NULL UNIQUE,
    nphies_provider_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  ```
- [ ] Create migration for healthcare service products
- [ ] Create migration for service provisioning records
- [ ] Create migration for audit logs table (if not exists)

#### API Endpoints
- [ ] Healthcare provider CRUD
  ```python
  GET    /api/v1/healthcare/providers
  POST   /api/v1/healthcare/providers
  GET    /api/v1/healthcare/providers/{id}
  PUT    /api/v1/healthcare/providers/{id}
  DELETE /api/v1/healthcare/providers/{id}
  ```
- [ ] Healthcare service products
  ```python
  GET /api/v1/healthcare/products
  GET /api/v1/healthcare/products/{id}
  ```
- [ ] Service provisioning
  ```python
  POST /api/v1/healthcare/provision
  GET  /api/v1/healthcare/provision/{order_id}
  ```

### Frontend Implementation

#### UI Components
- [ ] Create healthcare provider profile component
- [ ] Create GIVC service selection component
- [ ] Create NPHIES credential input form
- [ ] Add OID display in provider dashboard

#### API Integration
- [ ] Add GIVC API client
  ```typescript
  // frontend/src/lib/api/givc-client.ts
  export class GIVCApiClient {
    async getHealthcareProviders(): Promise<HealthcareProvider[]>
    async provisionService(request: ProvisionRequest): Promise<ProvisionResponse>
    async exchangeSession(token: string): Promise<SessionResponse>
  }
  ```
- [ ] Update authentication flow for healthcare claims
- [ ] Add session exchange on GIVC resource access

### GIVC API Implementation (Cross-Repo)

#### Token Validation
- [ ] Implement JWT validation with shared secret
  ```javascript
  // givc-healthcare-api/src/auth.js
  import jwt from 'jsonwebtoken';
  
  export async function validateBrainsaitToken(token, env) {
    const secret = env.JWT_SECRET_KEY;
    const payload = jwt.verify(token, secret, {
      algorithms: ['HS256'],
      audience: 'givc-api'
    });
    return payload;
  }
  ```
- [ ] Extract healthcare metadata from token
- [ ] Create GIVC internal session

#### Provisioning Endpoint
- [ ] Implement service provisioning handler
  ```javascript
  POST /api/v1/provision
  Handler: createHealthcareAccount(request, env)
  ```
- [ ] Generate GIVC account credentials
- [ ] Configure NPHIES integration for account
- [ ] Send webhook back to BrainSAIT Store
  ```javascript
  POST {brainsait_webhook_url}/webhooks/givc/provision-complete
  ```

#### Webhook Sender
- [ ] Implement webhook sender for claim events
  ```javascript
  async function sendWebhook(event, data, env) {
    const signature = generateHMAC(data, env.WEBHOOK_SECRET);
    await fetch(env.BRAINSAIT_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-GIVC-Signature': signature,
        'X-GIVC-Event': event
      },
      body: JSON.stringify(data)
    });
  }
  ```

---

## Phase 4: Testing

### Unit Tests
- [ ] Run existing unit tests
  ```bash
  pytest backend/tests/ -v --cov
  ```
- [ ] Ensure coverage > 80%

### Integration Tests
- [ ] Run GIVC authentication tests
  ```bash
  pytest backend/tests/integration/test_givc_auth.py -v
  ```
- [ ] Run smoke tests
  ```bash
  pytest backend/tests/integration/test_givc_auth.py -v -m smoke
  ```
- [ ] Add provisioning integration tests
- [ ] Add webhook integration tests

### End-to-End Tests
- [ ] Test complete purchase flow
  1. User logs in
  2. Browses healthcare products
  3. Adds GIVC API to cart
  4. Completes checkout
  5. Service automatically provisioned
  6. User receives credentials
- [ ] Test cross-service authentication
  1. User logs into BrainSAIT
  2. Accesses GIVC resource
  3. Token validated by GIVC
  4. Resource returned
- [ ] Test webhook delivery
  1. GIVC submits test claim
  2. Webhook sent to BrainSAIT
  3. BrainSAIT processes webhook
  4. Status updated in database

### Performance Tests
- [ ] Load test authentication endpoint (1000 req/s)
- [ ] Load test token validation (5000 req/s)
- [ ] Measure provisioning time (target: < 2 minutes)
- [ ] Test webhook reliability (99.9% delivery)

### Security Tests
- [ ] Test token tampering detection
- [ ] Test expired token rejection
- [ ] Test wrong audience rejection
- [ ] Test cross-tenant access prevention
- [ ] Test HMAC signature validation
- [ ] Penetration testing (optional, recommended)

---

## Phase 5: Deployment

### Staging Deployment
- [ ] Deploy backend to staging
  ```bash
  cd backend
  docker build -t brainsait-store-backend:staging .
  docker push registry.brainsait.com/store-backend:staging
  kubectl apply -f k8s/staging/
  ```
- [ ] Deploy frontend to staging
  ```bash
  cd frontend
  npm run build
  wrangler pages deploy out --env staging
  ```
- [ ] Deploy API Gateway to staging
  ```bash
  cd infrastructure/cloudflare/workers
  wrangler deploy --env staging
  ```
- [ ] Sync secrets to staging
  ```bash
  ./scripts/sync_shared_secrets.sh staging
  ```
- [ ] Run database migrations
  ```bash
  alembic upgrade head
  ```

### Staging Validation
- [ ] Verify all services healthy
  ```bash
  ./scripts/verify_all_integrations.sh staging
  ```
- [ ] Run integration tests against staging
- [ ] Manual testing of critical flows
- [ ] Performance testing
- [ ] Security scanning

### Production Deployment
- [ ] Create deployment checklist review
- [ ] Obtain approval from stakeholders
- [ ] Schedule maintenance window (if needed)
- [ ] Deploy to production (blue-green)
  ```bash
  ./scripts/deploy_production.sh --blue-green
  ```
- [ ] Sync production secrets
  ```bash
  ./scripts/sync_shared_secrets.sh production
  ```
- [ ] Run production smoke tests
- [ ] Monitor for 1 hour post-deployment
- [ ] Gradual traffic shift (10% → 50% → 100%)

### Rollback Plan
- [ ] Document rollback procedure
- [ ] Test rollback in staging
- [ ] Keep previous version available
- [ ] Set rollback trigger criteria
  - Error rate > 1%
  - Response time > 2s p95
  - Critical functionality broken

---

## Phase 6: Monitoring & Operations

### Monitoring Setup
- [ ] Configure health check alerts
  - [ ] API Gateway health
  - [ ] Backend health
  - [ ] GIVC API health
  - [ ] Database connectivity
  - [ ] Redis connectivity
- [ ] Configure performance alerts
  - [ ] Response time > 500ms p95
  - [ ] Error rate > 0.5%
  - [ ] Request rate anomalies
- [ ] Configure security alerts
  - [ ] Failed authentication attempts > 10/min
  - [ ] Invalid token attempts > 5/min
  - [ ] Webhook signature failures > 5/min

### Logging
- [ ] Ensure structured logging enabled
- [ ] Verify audit logging for PHI access
- [ ] Configure log shipping to HealthLinc Logs
- [ ] Set up log retention (7 years for HIPAA)

### Dashboards
- [ ] Create operations dashboard
  - Service health status
  - Request rates
  - Error rates
  - Response times
- [ ] Create business dashboard
  - Healthcare product sales
  - Provisioning success rate
  - Active healthcare providers
  - NPHIES integration metrics

### Alerting
- [ ] Configure PagerDuty/OpsGenie
- [ ] Set up on-call rotation
- [ ] Define escalation policy
- [ ] Create runbooks for common issues

---

## Phase 7: Documentation & Training

### Documentation
- [ ] Update API documentation (OpenAPI/Swagger)
- [ ] Create user guides
  - [ ] Healthcare provider onboarding
  - [ ] GIVC service setup
  - [ ] NPHIES integration guide
- [ ] Create admin guides
  - [ ] Service provisioning
  - [ ] Provider management
  - [ ] Troubleshooting
- [ ] Update architecture diagrams (if changed)

### Training
- [ ] Train support team on new features
- [ ] Train sales team on healthcare offerings
- [ ] Create training videos
- [ ] Conduct Q&A sessions

### Marketing
- [ ] Announce GIVC integration
- [ ] Create marketing materials
- [ ] Update website
- [ ] Blog post / press release

---

## Phase 8: Post-Launch

### Week 1
- [ ] Daily monitoring and incident response
- [ ] Collect user feedback
- [ ] Address critical bugs
- [ ] Performance tuning

### Week 2-4
- [ ] Weekly review meetings
- [ ] Feature refinement based on feedback
- [ ] Documentation updates
- [ ] Security review

### Month 2-3
- [ ] Bi-weekly check-ins
- [ ] Optimization based on usage patterns
- [ ] Plan Phase 2 enhancements
- [ ] Conduct retrospective

---

## Success Metrics

### Technical Metrics
- [ ] Uptime > 99.9%
- [ ] API response time < 200ms p95
- [ ] Error rate < 0.1%
- [ ] Provisioning time < 2 minutes
- [ ] Webhook delivery > 99.9%

### Business Metrics
- [ ] Healthcare product sales
- [ ] Active healthcare providers
- [ ] GIVC service usage
- [ ] Customer satisfaction (NPS)
- [ ] Time to provision service

### Compliance Metrics
- [ ] HIPAA audit passed
- [ ] NPHIES integration certified
- [ ] FHIR compliance verified
- [ ] Security audit passed

---

## Risk Management

### Identified Risks

1. **Mada/STC Pay Not Active**
   - **Impact**: Medium
   - **Mitigation**: Use Stripe as primary, activate before launch
   - **Status**: ⚠️ Pending activation

2. **NPHIES Production Access**
   - **Impact**: High
   - **Mitigation**: Test environment validated, production ready
   - **Status**: ✅ Test environment working

3. **ZATCA Certificate Expiry**
   - **Impact**: High
   - **Mitigation**: Renew before 2025-06-30
   - **Status**: ⚠️ Action required

4. **Secret Synchronization Failure**
   - **Impact**: Critical
   - **Mitigation**: Automated sync script with verification
   - **Status**: ✅ Script ready

5. **Database Migration Issues**
   - **Impact**: High
   - **Mitigation**: Test in staging, backup before migration
   - **Status**: ✅ Procedure documented

---

## Sign-Off

### Development Team
- [ ] Architecture reviewed: _________________ Date: _______
- [ ] Code reviewed: _________________ Date: _______
- [ ] Tests reviewed: _________________ Date: _______

### Operations Team
- [ ] Infrastructure ready: _________________ Date: _______
- [ ] Monitoring configured: _________________ Date: _______
- [ ] Runbooks created: _________________ Date: _______

### Security Team
- [ ] Security review: _________________ Date: _______
- [ ] Secrets audit: _________________ Date: _______
- [ ] Compliance verified: _________________ Date: _______

### Business Stakeholders
- [ ] Requirements met: _________________ Date: _______
- [ ] Approved for production: _________________ Date: _______

---

**Checklist Version**: 1.0  
**Last Updated**: 2025-01-09  
**Owner**: DevOps Team
