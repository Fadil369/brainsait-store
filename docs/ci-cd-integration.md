# CI/CD Integration & Links Verification

## Overview
This document verifies all CI/CD workflows, integration points, and external service connections for the BrainSAIT Store and GIVC integration.

---

## GitHub Actions Workflows

### Active Workflows

#### 1. CodeQL Advanced Security Scanning
**File**: `.github/workflows/codeql.yml`  
**Status**: ✅ Active  
**Triggers**:
- Push to `main` branch
- Pull requests to `main`
- Scheduled: Weekly (Wednesday at 18:18 UTC)

**Languages Analyzed**:
- GitHub Actions workflows
- JavaScript/TypeScript (Frontend)
- Python (Backend)

**Purpose**: Automated security vulnerability scanning

**Integration Points**:
- GitHub Security tab
- Code scanning alerts
- Dependabot alerts integration

**Verification**:
```bash
# Check workflow status
gh workflow view "CodeQL Advanced" --repo Fadil369/brainsait-store

# View recent runs
gh run list --workflow=codeql.yml --limit 5
```

#### 2. Validate Wrangler Configuration
**File**: `.github/workflows/validate-wrangler.yml`  
**Status**: ✅ Active  
**Triggers**:
- Push to `main` or `develop` branches (wrangler.toml changes)
- Pull requests (wrangler.toml changes)

**Checks**:
- Root wrangler.toml validation
- Frontend wrangler.toml validation
- Duplicate TOML key detection
- Dry-run deployment test

**Purpose**: Ensure Cloudflare Workers configuration is valid

**Verification**:
```bash
# Check workflow status
gh workflow view "Validate Wrangler Configuration" --repo Fadil369/brainsait-store

# Manually trigger validation
cd frontend && npx wrangler deploy --dry-run
```

### Recommended Additional Workflows

#### 3. Configuration Parity Check (New)
**Proposed File**: `.github/workflows/verify-config.yml`

```yaml
name: Verify Configuration Parity

on:
  push:
    branches: [main, staging]
    paths:
      - 'backend/app/core/config.py'
      - '**/.env.example'
      - 'docs/architecture/config-checklist.md'
  pull_request:
    branches: [main]

jobs:
  verify-config:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check required config keys
        run: |
          required_keys=(
            "JWT_SECRET_KEY"
            "DATABASE_URL"
            "REDIS_URL"
            "GIVC_API_URL"
            "NPHIES_CLIENT_ID"
            "OID_ROOT"
            "AUDIT_LOG_ENABLED"
          )
          
          missing_keys=()
          for key in "${required_keys[@]}"; do
            if grep -q "$key" backend/.env.example; then
              echo "✅ $key present in .env.example"
            else
              echo "❌ $key missing in .env.example"
              missing_keys+=("$key")
            fi
          done
          
          if [ ${#missing_keys[@]} -gt 0 ]; then
            echo "ERROR: Missing configuration keys: ${missing_keys[*]}"
            exit 1
          fi
      
      - name: Verify config.py has GIVC settings
        run: |
          if ! grep -q "GIVC_API_URL" backend/app/core/config.py; then
            echo "❌ GIVC_API_URL not found in config.py"
            exit 1
          fi
          if ! grep -q "NPHIES_CLIENT_ID" backend/app/core/config.py; then
            echo "❌ NPHIES_CLIENT_ID not found in config.py"
            exit 1
          fi
          echo "✅ GIVC configuration present in config.py"
```

**Purpose**: Ensure configuration consistency across environments

#### 4. GIVC Integration Tests (New)
**Proposed File**: `.github/workflows/givc-integration-tests.yml`

```yaml
name: GIVC Integration Tests

on:
  push:
    branches: [main, staging]
    paths:
      - 'backend/app/schemas/givc_integration.py'
      - 'backend/tests/integration/test_givc_auth.py'
      - 'backend/app/core/config.py'
  pull_request:
    branches: [main]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx PyJWT
      
      - name: Run GIVC authentication smoke tests
        run: |
          cd backend
          pytest tests/integration/test_givc_auth.py -v -m smoke
        env:
          JWT_SECRET_KEY: ${{ secrets.TEST_JWT_SECRET_KEY }}
      
      - name: Run full integration test suite
        run: |
          cd backend
          pytest tests/integration/test_givc_auth.py -v
        env:
          JWT_SECRET_KEY: ${{ secrets.TEST_JWT_SECRET_KEY }}
```

**Purpose**: Validate GIVC integration and authentication flow

---

## External Service Integrations

### 1. Cloudflare Services

#### Cloudflare Workers
**Services Deployed**:
- ✅ BrainSAIT API Gateway: https://brainsait-api-gateway.fadil.workers.dev
- ✅ GIVC Healthcare API: https://givc-healthcare-api.fadil.workers.dev
- ✅ HealthLinc Logs: https://healthlinc-logs.fadil.workers.dev
- ✅ MCP ServerLinc: https://mcp-serverlinc.fadil.workers.dev

**Integration Status**:
```bash
# Verify all workers are operational
curl -s https://brainsait-api-gateway.fadil.workers.dev/health | jq .status
curl -s https://givc-healthcare-api.fadil.workers.dev/health | jq .status
curl -s https://healthlinc-logs.fadil.workers.dev/health | jq .status
curl -s https://mcp-serverlinc.fadil.workers.dev/health | jq .status
```

**Expected Response**: `"healthy"` or `"operational"`

**Deployment**:
- Automated via `wrangler deploy` in CI/CD
- Manual: `cd infrastructure/cloudflare/workers && wrangler deploy`

#### Cloudflare Pages
**Frontend Deployment**: https://store.brainsait.io  
**Status**: ✅ Live

**Verification**:
```bash
# Check frontend deployment
curl -s -o /dev/null -w "%{http_code}" https://store.brainsait.io
# Expected: 200
```

**Build Integration**:
- Build command: `npm run build`
- Output directory: `out`
- Branch: `main` (production), `develop` (preview)

### 2. Payment Gateway Integrations

#### Stripe
**Integration**: ✅ Active  
**Environment**: Live  
**Webhook Endpoint**: `https://api.store.brainsait.io/api/v1/payments/stripe/webhook`

**Verification**:
```bash
# Test Stripe API connectivity
curl https://api.stripe.com/v1/balance \
  -u "$STRIPE_SECRET_KEY:"
```

**Events Subscribed**:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.refunded`
- `customer.subscription.created`
- `customer.subscription.deleted`

#### PayPal
**Integration**: ✅ Active  
**Environment**: Live  
**Webhook Endpoint**: `https://api.store.brainsait.io/api/v1/payments/paypal/webhook`

**Verification**:
```bash
# Test PayPal API connectivity
curl -X POST https://api.paypal.com/v1/oauth2/token \
  -H "Accept: application/json" \
  -H "Accept-Language: en_US" \
  -u "$PAYPAL_CLIENT_ID:$PAYPAL_SECRET" \
  -d "grant_type=client_credentials"
```

#### Mada (Saudi)
**Integration**: ⚠️ Configured (Pending activation)  
**Endpoint**: `https://api.mada.sa/v1`  
**Status**: Configuration ready, awaiting merchant approval

#### STC Pay (Saudi)
**Integration**: ⚠️ Configured (Pending activation)  
**Endpoint**: `https://api.stcpay.com.sa/v1`  
**Status**: Configuration ready, awaiting merchant approval

### 3. NPHIES Integration (Saudi Healthcare)

**Integration**: ✅ Configured  
**Environment**: Test (Production ready)  
**Endpoint**: `https://nphies.sa/api`

**Authentication**: OAuth 2.0 with X.509 certificates

**Verification** (Test Environment):
```bash
# Test NPHIES OAuth
curl -X POST https://nphies-test.sa/api/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=$NPHIES_CLIENT_ID" \
  -d "client_secret=$NPHIES_CLIENT_SECRET" \
  -d "scope=openid,profile,claims,authorizations"
```

**Expected Response**: Access token with 3600s expiry

**API Endpoints Integrated**:
- Authorization requests
- Claim submissions
- Eligibility checks
- Patient verification

### 4. ZATCA E-Invoicing (Saudi Tax)

**Integration**: ✅ Configured  
**Environment**: Production  
**Purpose**: E-invoice generation and submission

**Certificate Status**: ⚠️ Awaiting renewal (expires 2025-06-30)

**Verification**:
```bash
# Check certificate validity
openssl x509 -in $ZATCA_CERTIFICATE_PATH -noout -dates
```

**Features**:
- QR code generation on invoices
- Real-time submission to ZATCA
- VAT calculation (15%)
- Invoice archival (6 years)

### 5. Database & Cache

#### PostgreSQL
**Host**: Configured in secrets  
**Status**: ✅ Connected  
**Version**: PostgreSQL 14+

**Verification**:
```bash
# Test database connectivity
psql "$DATABASE_URL" -c "SELECT version();"
```

**Backup Strategy**:
- Daily automated backups
- Point-in-time recovery enabled
- Retention: 30 days

#### Redis
**Host**: Configured in secrets  
**Status**: ✅ Connected  
**Purpose**: Session storage, caching, rate limiting

**Verification**:
```bash
# Test Redis connectivity
redis-cli -u "$REDIS_URL" PING
```

**TTL Settings**:
- Sessions: 30 minutes
- API cache: 5 minutes
- Product cache: 1 hour

### 6. Monitoring & Analytics

#### Sentry (Error Tracking)
**Integration**: ✅ Configured  
**DSN**: Configured in secrets  
**Environments**: Development, Staging, Production

**Verification**:
```bash
# Test Sentry integration
curl -X POST https://sentry.io/api/0/projects/$SENTRY_PROJECT_ID/keys/ \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN"
```

#### Google Analytics
**Integration**: ⚠️ Configured (Frontend only)  
**Measurement ID**: Configured in frontend environment

#### HealthLinc Logs
**Integration**: ✅ Active  
**Endpoint**: https://healthlinc-logs.fadil.workers.dev  
**Purpose**: Centralized logging and monitoring

**Log Shipping**:
- Application logs from all services
- Audit logs for compliance
- Performance metrics
- Error tracking

### 7. Email & SMS Services

#### SMTP (Email)
**Provider**: Configured in secrets  
**Status**: ✅ Active  
**Usage**: Order confirmations, password resets, notifications

**Verification**:
```bash
# Test SMTP connectivity (Python)
python -c "
import smtplib
server = smtplib.SMTP('$SMTP_HOST', $SMTP_PORT)
server.starttls()
server.login('$SMTP_USERNAME', '$SMTP_PASSWORD')
server.quit()
print('✅ SMTP connection successful')
"
```

#### SMS (Saudi Arabia)
**Provider**: Unifonic / Taqnyat  
**Status**: ✅ Configured  
**Usage**: OTP, order notifications (Arabic)

---

## Integration Testing Matrix

| Service | Integration Type | Status | Last Verified | Auto-Test |
|---------|-----------------|--------|---------------|-----------|
| Cloudflare Workers | API | ✅ Active | 2025-01-09 | Yes |
| Cloudflare Pages | Hosting | ✅ Active | 2025-01-09 | Yes |
| Stripe | Payment | ✅ Active | 2025-01-09 | No |
| PayPal | Payment | ✅ Active | 2025-01-09 | No |
| Mada | Payment | ⚠️ Pending | N/A | No |
| STC Pay | Payment | ⚠️ Pending | N/A | No |
| NPHIES | Healthcare | ✅ Test | 2025-01-09 | No |
| ZATCA | Tax | ✅ Active | 2025-01-09 | No |
| PostgreSQL | Database | ✅ Active | 2025-01-09 | Yes |
| Redis | Cache | ✅ Active | 2025-01-09 | Yes |
| Sentry | Monitoring | ✅ Active | 2025-01-09 | No |
| SMTP | Email | ✅ Active | 2025-01-09 | No |
| SMS | Notifications | ✅ Active | 2025-01-09 | No |
| GIVC API | Healthcare | ✅ Active | 2025-01-09 | Yes |
| HealthLinc Logs | Monitoring | ✅ Active | 2025-01-09 | Yes |
| MCP ServerLinc | AI Context | ✅ Active | 2025-01-09 | Yes |

---

## Webhook Configuration

### Inbound Webhooks (BrainSAIT Store Receives)

| Source | Endpoint | Events | Status |
|--------|----------|--------|--------|
| Stripe | `/api/v1/payments/stripe/webhook` | payment.*, customer.* | ✅ Active |
| PayPal | `/api/v1/payments/paypal/webhook` | PAYMENT.*, BILLING.* | ✅ Active |
| GIVC | `/webhooks/givc/claim-status` | claim.submitted, claim.approved | ✅ Active |
| GIVC | `/webhooks/givc/authorization` | auth.approved, auth.denied | ✅ Active |
| HealthLinc | `/webhooks/healthlinc/payment` | payment.received | ✅ Active |
| LinkedIn | `/webhooks/linkedin/lead-notifications` | lead.generated | ✅ Active |

**Webhook Security**:
- HMAC signature verification
- Timestamp validation (5-minute window)
- IP whitelist (where supported)
- Rate limiting (per source)

### Outbound Webhooks (BrainSAIT Store Sends)

| Target | Event | Endpoint | Status |
|--------|-------|----------|--------|
| GIVC | order.completed | `/webhooks/brainsait/order` | ✅ Active |
| GIVC | provider.created | `/webhooks/brainsait/provider` | ✅ Active |
| HealthLinc | service.provisioned | `/webhooks/brainsait/provision` | ⚠️ Planned |

---

## Secrets & Environment Variables

### Secret Management

**Production Secrets** (HashiCorp Vault):
- Database credentials
- JWT signing keys
- API keys (payment gateways, NPHIES)
- SMTP passwords
- ZATCA certificates

**Cloudflare Workers Secrets**:
```bash
# List all secrets for production workers
wrangler secret list --env production
```

**Expected Secrets**:
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `GIVC_API_KEY`
- `NPHIES_CLIENT_SECRET`
- `STRIPE_SECRET_KEY`
- `PAYPAL_SECRET`

**Rotation Schedule**: Every 90 days (automated)

---

## CI/CD Deployment Pipeline

### Deployment Stages

```
1. Development
   ├── Local development (localhost)
   ├── Feature branches
   └── Auto-deploy to dev environment

2. Staging
   ├── develop branch
   ├── Automated tests
   ├── Integration tests with GIVC
   └── Deploy to staging environment

3. Production
   ├── main branch
   ├── Manual approval required
   ├── Blue-green deployment
   └── Deploy to production
```

### Deployment Commands

**Frontend (Cloudflare Pages)**:
```bash
cd frontend
npm run build
wrangler pages deploy out --project-name=brainsait-store
```

**Backend (Docker/K8s)**:
```bash
cd backend
docker build -t brainsait-store-backend:latest .
docker push registry.brainsait.com/store-backend:latest
kubectl rollout restart deployment brainsait-backend
```

**API Gateway (Cloudflare Workers)**:
```bash
cd infrastructure/cloudflare/workers
wrangler deploy --env production
```

---

## Monitoring & Health Checks

### Service Health Endpoints

```bash
# Check all services
curl https://brainsait-api-gateway.fadil.workers.dev/health
curl https://givc-healthcare-api.fadil.workers.dev/health
curl https://healthlinc-logs.fadil.workers.dev/health
curl https://mcp-serverlinc.fadil.workers.dev/health
curl https://api.store.brainsait.io/health  # Backend API
```

**Expected Response Format**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-09T12:00:00Z",
  "services": {
    "database": "operational",
    "redis": "operational",
    "givc": "operational"
  }
}
```

### Uptime Monitoring

**Tool**: External monitoring service (e.g., UptimeRobot, Pingdom)  
**Endpoints Monitored**:
- Frontend: https://store.brainsait.io
- API Gateway: https://brainsait-api-gateway.fadil.workers.dev/health
- GIVC API: https://givc-healthcare-api.fadil.workers.dev/health

**Alert Thresholds**:
- Downtime > 2 minutes: Alert
- Response time > 2 seconds: Warning
- Error rate > 1%: Alert

---

## Integration Issues & Resolution

### Common Issues

1. **Webhook Delivery Failure**
   - Check webhook URL is publicly accessible
   - Verify signature validation
   - Check rate limiting
   - Review webhook logs

2. **NPHIES Connection Timeout**
   - Verify certificate validity
   - Check network connectivity
   - Confirm OAuth token not expired
   - Review NPHIES status page

3. **Payment Gateway Errors**
   - Verify API keys are current
   - Check webhook signature secrets
   - Confirm account is active
   - Review payment gateway dashboard

4. **JWT Token Validation Failure**
   - Confirm JWT secrets are synchronized
   - Check token expiration settings
   - Verify audience claims
   - Review token format

---

## Verification Scripts

### Complete Integration Check

```bash
#!/bin/bash
# scripts/verify_all_integrations.sh

echo "Verifying all integrations..."

# Check Cloudflare Workers
echo "Checking Cloudflare Workers..."
for url in \
  "https://brainsait-api-gateway.fadil.workers.dev/health" \
  "https://givc-healthcare-api.fadil.workers.dev/health" \
  "https://healthlinc-logs.fadil.workers.dev/health" \
  "https://mcp-serverlinc.fadil.workers.dev/health"
do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$status" = "200" ]; then
    echo "✅ $url"
  else
    echo "❌ $url (status: $status)"
  fi
done

# Check database
echo "Checking database..."
if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
  echo "✅ PostgreSQL connected"
else
  echo "❌ PostgreSQL connection failed"
fi

# Check Redis
echo "Checking Redis..."
if redis-cli -u "$REDIS_URL" PING > /dev/null 2>&1; then
  echo "✅ Redis connected"
else
  echo "❌ Redis connection failed"
fi

# Check Stripe
echo "Checking Stripe..."
if curl -s -o /dev/null -w "%{http_code}" https://api.stripe.com/v1/balance \
  -u "$STRIPE_SECRET_KEY:" | grep -q "200"; then
  echo "✅ Stripe API accessible"
else
  echo "❌ Stripe API not accessible"
fi

echo "Integration verification complete"
```

---

## Contact Information

**CI/CD Issues**: devops@brainsait.com  
**Integration Support**: integration@brainsait.com  
**Security Concerns**: security@brainsait.com  
**On-Call**: +966-xxx-xxx-xxxx

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-09  
**Next Review**: 2025-02-09  
**Owner**: DevOps Team
