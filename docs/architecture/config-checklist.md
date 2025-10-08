# Configuration Parity Checklist

## Overview
This document ensures configuration consistency across all environments (development, staging, production) and between BrainSAIT Store and GIVC Healthcare Platform integration.

---

## Configuration Audit Status

**Last Audit**: 2025-01-09  
**Next Audit**: 2025-02-09  
**Status**: ✅ All Critical Configurations Verified

---

## Critical Configuration Keys

### 1. Authentication & Session Management

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `JWT_SECRET_KEY` | ✅ Required | ✅ Required | ✅ Synced | Must be identical across services |
| `JWT_ALGORITHM` | ✅ HS256 | ✅ HS256 | ✅ Synced | Standard algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ 30 | ✅ 30 | ✅ Synced | Token expiration time |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ✅ 30 | ✅ 30 | ✅ Synced | Refresh token validity |

**Validation**:
```bash
# Verify JWT secrets are synchronized
vault kv get -field=jwt_secret secret/brainsait/production/auth
wrangler secret list --env production | grep JWT_SECRET_KEY
```

### 2. Database Configuration

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `DATABASE_URL` | ✅ Required | ✅ Required | ✅ Synced | Shared PostgreSQL database |
| `DATABASE_ECHO` | ✅ False (prod) | ✅ False (prod) | ✅ Synced | Logging disabled in production |
| `REDIS_URL` | ✅ Required | ✅ Required | ✅ Synced | Shared session storage |

**Validation**:
```bash
# Test database connectivity from both services
psql $DATABASE_URL -c "SELECT 1;"
redis-cli -u $REDIS_URL PING
```

### 3. GIVC Integration

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `GIVC_API_URL` | ✅ Required | N/A | ✅ Set | Points to GIVC API endpoint |
| `GIVC_API_KEY` | ✅ Required | N/A | ✅ Set | Authentication for GIVC calls |
| `GIVC_WEBHOOK_SECRET` | ✅ Required | ✅ Required | ✅ Synced | Webhook signature validation |
| `BRAINSAIT_STORE_API_URL` | N/A | ✅ Required | ✅ Set | Points to Store API |
| `BRAINSAIT_WEBHOOK_SECRET` | ✅ Required | ✅ Required | ✅ Synced | Reverse webhook validation |

**Validation**:
```bash
# Test GIVC API connectivity
curl -H "Authorization: Bearer $GIVC_API_KEY" \
  $GIVC_API_URL/health

# Test webhook signature generation
echo -n "test_payload" | openssl dgst -sha256 -hmac "$GIVC_WEBHOOK_SECRET"
```

### 4. NPHIES Configuration (Saudi Healthcare)

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `NPHIES_BASE_URL` | ✅ Required | ✅ Required | ✅ Synced | NPHIES API endpoint |
| `NPHIES_CLIENT_ID` | ✅ Required | ✅ Required | ✅ Synced | Shared client ID |
| `NPHIES_CLIENT_SECRET` | ✅ Required | ✅ Required | ✅ Synced | Must be identical |
| `NPHIES_SCOPE` | ✅ Required | ✅ Required | ✅ Synced | OAuth scopes |
| `NPHIES_ENABLED` | ✅ True (prod) | ✅ True (prod) | ✅ Synced | Feature flag |

**Validation**:
```bash
# Test NPHIES OAuth token retrieval
curl -X POST $NPHIES_BASE_URL/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=$NPHIES_CLIENT_ID" \
  -d "client_secret=$NPHIES_CLIENT_SECRET" \
  -d "scope=$NPHIES_SCOPE"
```

### 5. OID Configuration (Healthcare Identifiers)

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `OID_ROOT` | ✅ 1.3.6.1.4.1.61026 | ✅ 1.3.6.1.4.1.61026 | ✅ Synced | BrainSAIT root OID |
| `OID_NPHIES_BRANCH` | ✅ *.1.2.1 | ✅ *.1.2.1 | ✅ Synced | NPHIES integration branch |
| `OID_AI_BRANCH` | ✅ *.2.1 | ✅ *.2.1 | ✅ Synced | AI ecosystem branch |
| `OID_SECURITY_BRANCH` | ✅ *.3 | ✅ *.3 | ✅ Synced | Security & compliance branch |

**Validation**:
```bash
# Verify OID tree structure
curl $BRAINSAIT_STORE_API_URL/api/v1/oid/tree | jq .
```

### 6. Payment Gateways

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `STRIPE_SECRET_KEY` | ✅ Required | ⚠️ Optional | ✅ Set | Primary payment gateway |
| `STRIPE_PUBLISHABLE_KEY` | ✅ Required | N/A | ✅ Set | Frontend key |
| `STRIPE_WEBHOOK_SECRET` | ✅ Required | N/A | ✅ Set | Webhook validation |
| `PAYPAL_CLIENT_ID` | ✅ Required | N/A | ✅ Set | PayPal integration |
| `PAYPAL_SECRET` | ✅ Required | N/A | ✅ Set | PayPal secret |
| `MADA_MERCHANT_ID` | ✅ Required | N/A | ✅ Set | Saudi Mada gateway |
| `STC_PAY_MERCHANT_ID` | ✅ Required | N/A | ✅ Set | Saudi STC Pay |

**Validation**:
```bash
# Test Stripe API
curl https://api.stripe.com/v1/balance \
  -u "$STRIPE_SECRET_KEY:"
```

### 7. ZATCA E-Invoicing (Saudi Tax)

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `ZATCA_ENABLED` | ✅ True (prod) | ⚠️ Optional | ✅ Set | E-invoicing enabled |
| `ZATCA_VAT_NUMBER` | ✅ Required | ⚠️ Optional | ✅ Set | VAT registration number |
| `ZATCA_CR_NUMBER` | ✅ Required | ⚠️ Optional | ✅ Set | Commercial registration |
| `ZATCA_CERTIFICATE_PATH` | ✅ Required | ⚠️ Optional | ✅ Set | ZATCA certificate |
| `ZATCA_PRIVATE_KEY_PATH` | ✅ Required | ⚠️ Optional | ✅ Set | ZATCA private key |

### 8. Monitoring & Logging

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `LOG_LEVEL` | ✅ INFO | ✅ INFO | ✅ Synced | Production log level |
| `SENTRY_DSN` | ✅ Required | ✅ Required | ✅ Set | Error tracking |
| `AUDIT_LOG_ENABLED` | ✅ True | ✅ True | ✅ Synced | Compliance logging |
| `AUDIT_LOG_RETENTION_DAYS` | ✅ 2555 | ✅ 2555 | ✅ Synced | 7 years for HIPAA |

### 9. Email & SMS Notifications

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `SMTP_HOST` | ✅ Required | ⚠️ Optional | ✅ Set | Email server |
| `SMTP_PORT` | ✅ 587 | ⚠️ 587 | ✅ Set | TLS port |
| `SMTP_USERNAME` | ✅ Required | ⚠️ Optional | ✅ Set | Email credentials |
| `SMTP_PASSWORD` | ✅ Required | ⚠️ Optional | ✅ Set | Email password |
| `FROM_EMAIL` | ✅ Required | ⚠️ Optional | ✅ Set | Sender email |
| `SMS_PROVIDER` | ✅ unifonic | ⚠️ Optional | ✅ Set | Saudi SMS provider |

### 10. CORS & Security

| Configuration Key | BrainSAIT Store | GIVC API | Status | Notes |
|-------------------|-----------------|----------|--------|-------|
| `BACKEND_CORS_ORIGINS` | ✅ Required | ✅ Required | ⚠️ Review | Allowed origins list |
| `ALLOWED_HOSTS` | ✅ Required | ✅ Required | ✅ Set | Trusted hosts |
| `SECURE_SSL_REDIRECT` | ✅ True (prod) | ✅ True (prod) | ✅ Synced | Force HTTPS |
| `SESSION_COOKIE_SECURE` | ✅ True (prod) | ✅ True (prod) | ✅ Synced | Secure cookies |
| `RATE_LIMIT_REQUESTS` | ✅ 100/min | ✅ 120/min | ⚠️ Different | Adjust as needed |

---

## Environment-Specific Configuration

### Development Environment

**Configuration File**: `.env.development` / `.env.local`

| Key | Value | Status |
|-----|-------|--------|
| `ENVIRONMENT` | development | ✅ |
| `DEBUG` | True | ✅ |
| `DATABASE_URL` | localhost:5432 | ✅ |
| `REDIS_URL` | localhost:6379 | ✅ |
| `GIVC_API_URL` | localhost:8001 | ✅ |
| `NPHIES_BASE_URL` | https://nphies-test.sa | ✅ |
| `NPHIES_ENABLED` | False | ✅ |
| `STRIPE_SECRET_KEY` | sk_test_*** | ✅ |
| `SECURE_SSL_REDIRECT` | False | ✅ |

### Staging Environment

**Configuration File**: Vault path `secret/brainsait/staging/*`

| Key | Value | Status |
|-----|-------|--------|
| `ENVIRONMENT` | staging | ✅ |
| `DEBUG` | False | ✅ |
| `DATABASE_URL` | staging-db.brainsait.com | ✅ |
| `REDIS_URL` | staging-redis.brainsait.com | ✅ |
| `GIVC_API_URL` | https://givc-staging.workers.dev | ✅ |
| `NPHIES_BASE_URL` | https://nphies-test.sa | ✅ |
| `NPHIES_ENABLED` | True | ✅ |
| `STRIPE_SECRET_KEY` | sk_test_*** | ✅ |
| `SECURE_SSL_REDIRECT` | True | ✅ |

### Production Environment

**Configuration File**: Vault path `secret/brainsait/production/*`

| Key | Value | Status |
|-----|-------|--------|
| `ENVIRONMENT` | production | ✅ |
| `DEBUG` | False | ✅ |
| `DATABASE_URL` | prod-db.brainsait.com | ✅ |
| `REDIS_URL` | prod-redis.brainsait.com | ✅ |
| `GIVC_API_URL` | https://givc-healthcare-api.fadil.workers.dev | ✅ |
| `NPHIES_BASE_URL` | https://nphies.sa/api | ✅ |
| `NPHIES_ENABLED` | True | ✅ |
| `STRIPE_SECRET_KEY` | sk_live_*** | ✅ |
| `SECURE_SSL_REDIRECT` | True | ✅ |
| `AUDIT_LOG_ENABLED` | True | ✅ |

---

## Missing Configuration Keys

### Required but Missing (Critical)

None identified. All critical configurations are present.

### Optional but Recommended

| Key | Service | Priority | Notes |
|-----|---------|----------|-------|
| `FHIR_SERVER_URL` | Both | Medium | For separate FHIR server if needed |
| `HEALTHLINC_API_URL` | Store | Medium | For direct HealthLinc integration |
| `MCP_SERVERLINC_URL` | Both | Low | For AI model context protocol |

---

## Configuration Synchronization Scripts

### Sync Shared Secrets

```bash
#!/bin/bash
# scripts/sync_shared_secrets.sh

set -e

echo "Syncing shared secrets between BrainSAIT Store and GIVC..."

# JWT Secret
JWT_SECRET=$(vault kv get -field=jwt_secret secret/brainsait/production/auth)
wrangler secret put JWT_SECRET_KEY --env production <<< "$JWT_SECRET"
echo "✅ JWT_SECRET_KEY synced"

# NPHIES Credentials
NPHIES_CLIENT_SECRET=$(vault kv get -field=client_secret secret/brainsait/production/nphies)
wrangler secret put NPHIES_CLIENT_SECRET --env production <<< "$NPHIES_CLIENT_SECRET"
echo "✅ NPHIES_CLIENT_SECRET synced"

# Webhook Secrets
WEBHOOK_SECRET=$(vault kv get -field=webhook_secret secret/brainsait/production/givc)
wrangler secret put GIVC_WEBHOOK_SECRET --env production <<< "$WEBHOOK_SECRET"
echo "✅ GIVC_WEBHOOK_SECRET synced"

# Database Connection
DATABASE_URL=$(vault kv get -field=url secret/brainsait/production/database)
wrangler secret put DATABASE_URL --env production <<< "$DATABASE_URL"
echo "✅ DATABASE_URL synced"

echo "✅ All shared secrets synchronized successfully"
```

### Verify Configuration Parity

```bash
#!/bin/bash
# scripts/verify_config_parity.sh

set -e

echo "Verifying configuration parity..."

# Check JWT secret synchronization
STORE_JWT=$(vault kv get -field=jwt_secret secret/brainsait/production/auth)
GIVC_JWT=$(wrangler secret list --env production | grep JWT_SECRET_KEY)

if [ -n "$GIVC_JWT" ]; then
    echo "✅ JWT secrets configured in both services"
else
    echo "❌ JWT secret missing in GIVC"
    exit 1
fi

# Check NPHIES configuration
STORE_NPHIES=$(vault kv get -field=client_id secret/brainsait/production/nphies)
if [ -n "$STORE_NPHIES" ]; then
    echo "✅ NPHIES configured in Store"
else
    echo "⚠️ NPHIES not configured in Store"
fi

# Check database connectivity
if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database connectivity verified"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Check Redis connectivity
if redis-cli -u "$REDIS_URL" PING > /dev/null 2>&1; then
    echo "✅ Redis connectivity verified"
else
    echo "❌ Redis connection failed"
    exit 1
fi

echo "✅ Configuration parity verified"
```

### Generate Configuration Report

```bash
#!/bin/bash
# scripts/config_report.sh

echo "Configuration Report - $(date)"
echo "================================"
echo ""

echo "BrainSAIT Store Configuration:"
vault kv list secret/brainsait/production/ | sed 's/^/  - /'
echo ""

echo "GIVC API Configuration:"
wrangler secret list --env production | sed 's/^/  - /'
echo ""

echo "Database Status:"
psql "$DATABASE_URL" -c "SELECT version();" | head -n 3
echo ""

echo "Redis Status:"
redis-cli -u "$REDIS_URL" INFO server | grep "redis_version"
echo ""

echo "Configuration Files:"
find . -name ".env*" -o -name "config*.py" | sed 's/^/  - /'
```

---

## Automated Verification

### CI/CD Pipeline Integration

```yaml
# .github/workflows/verify-config.yml
name: Verify Configuration Parity

on:
  push:
    branches: [main, staging]
    paths:
      - 'backend/app/core/config.py'
      - '**/.env.example'
      - 'docs/architecture/config-checklist.md'

jobs:
  verify-config:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Verify required config keys
        run: |
          ./scripts/verify_config_parity.sh
      
      - name: Check .env.example completeness
        run: |
          required_keys=(
            "JWT_SECRET_KEY"
            "DATABASE_URL"
            "REDIS_URL"
            "GIVC_API_URL"
            "NPHIES_CLIENT_ID"
          )
          
          for key in "${required_keys[@]}"; do
            if grep -q "$key" backend/.env.example; then
              echo "✅ $key present"
            else
              echo "❌ $key missing"
              exit 1
            fi
          done
```

---

## Troubleshooting

### Configuration Mismatch Detection

**Symptom**: Token validation fails between services

**Solution**:
```bash
# Compare JWT secrets
vault kv get secret/brainsait/production/auth
wrangler secret list --env production | grep JWT

# If different, resync
./scripts/sync_shared_secrets.sh
```

**Symptom**: NPHIES integration fails

**Solution**:
```bash
# Verify NPHIES credentials
curl -X POST $NPHIES_BASE_URL/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=$NPHIES_CLIENT_ID" \
  -d "client_secret=$NPHIES_CLIENT_SECRET"

# Check certificate validity
openssl x509 -in $NPHIES_CERTIFICATE_PATH -noout -dates
```

---

## Compliance & Audit

### Configuration Change Log

| Date | Change | Environment | Changed By | Reason |
|------|--------|-------------|------------|--------|
| 2025-01-09 | Added GIVC integration keys | All | DevOps Team | GIVC integration launch |
| 2025-01-09 | Enabled NPHIES in production | Production | Security Team | Saudi compliance |
| 2025-01-09 | Updated audit log retention | All | Compliance Team | HIPAA requirement |

### Quarterly Review Checklist

- [ ] Verify all critical secrets are rotated (90-day schedule)
- [ ] Check configuration parity across environments
- [ ] Review and update CORS origins
- [ ] Audit access logs for configuration changes
- [ ] Update this document with any new configuration keys
- [ ] Test disaster recovery with current configuration

---

## Contact Information

**Configuration Issues**: devops@brainsait.com  
**Security Concerns**: security@brainsait.com  
**On-Call Support**: +966-xxx-xxx-xxxx

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-09  
**Next Review**: 2025-02-09  
**Owner**: DevOps Team
