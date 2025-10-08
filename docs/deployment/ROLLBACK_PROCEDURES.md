# Rollback Procedures - BrainSAIT Store

## Overview

This document provides detailed rollback procedures for the BrainSAIT Store platform, ensuring quick recovery from problematic deployments.

## When to Rollback

### Critical Issues (Immediate Rollback)
- 🔴 Payment processing failures
- 🔴 Security vulnerabilities discovered
- 🔴 Data corruption or loss
- 🔴 Authentication system failures
- 🔴 Error rate > 5%
- 🔴 Complete service outage

### Major Issues (Rollback Within 15 Minutes)
- 🟡 Error rate > 2%
- 🟡 Performance degradation > 50%
- 🟡 Critical features not functioning
- 🟡 Database connection issues
- 🟡 Third-party integration failures

### Minor Issues (Evaluate Before Rollback)
- 🟢 Error rate 0.5-2%
- 🟢 Performance degradation 20-50%
- 🟢 Non-critical feature issues
- 🟢 UI/UX problems
- 🟢 Minor bugs affecting limited users

## Pre-Rollback Checklist

- [ ] Verify the issue is deployment-related (not infrastructure)
- [ ] Capture current error logs and metrics
- [ ] Document the issue and symptoms
- [ ] Notify team in incident channel
- [ ] Identify last known good version
- [ ] Verify rollback target is stable
- [ ] Prepare rollback commands
- [ ] Alert stakeholders of rollback

## Rollback Procedures

### Frontend Rollback

#### Method 1: Cloudflare Pages Deployment Promotion (Recommended)

```bash
# 1. List recent deployments
wrangler pages deployment list --project-name brainsait-store

# Output example:
# ID: abc123def456  Branch: main  Created: 2025-01-15 10:30:00  Status: ACTIVE
# ID: xyz789ghi012  Branch: main  Created: 2025-01-15 09:00:00  Status: RETIRED

# 2. Identify the last good deployment ID (xyz789ghi012)

# 3. Promote previous deployment to production
wrangler pages deployment promote xyz789ghi012 --project-name brainsait-store

# 4. Verify rollback
curl -I https://store.brainsait.io
# Should return 200 OK

# 5. Check deployment status
wrangler pages deployment list --project-name brainsait-store
```

**Expected Time**: 2-3 minutes

#### Method 2: Redeploy Previous Version

```bash
# 1. Checkout previous release tag
git fetch --tags
git checkout v1.0.5  # Last stable version

# 2. Rebuild frontend
cd frontend
npm ci
npm run build

# 3. Deploy to production
wrangler pages deploy out --project-name brainsait-store --branch main

# 4. Verify deployment
curl https://store.brainsait.io
```

**Expected Time**: 5-8 minutes (due to rebuild)

### Backend Rollback

#### Method 1: Cloudflare Workers Version Rollback (Recommended)

```bash
# 1. List recent worker versions
wrangler deployments list --name brainsait-store

# Output:
# Version: v2  Created: 2025-01-15 10:30:00  Status: ACTIVE
# Version: v1  Created: 2025-01-15 09:00:00  Status: RETIRED

# 2. Rollback to previous version
wrangler rollback --name brainsait-store --message "Rollback due to high error rate"

# 3. Verify health check
curl https://api.store.brainsait.io/health

# Response should be:
# {"status":"healthy","version":"1.0.5","environment":"production"}
```

**Expected Time**: 1-2 minutes

#### Method 2: Redeploy Previous Version

```bash
# 1. Checkout last stable release
git checkout v1.0.5

# 2. Deploy backend worker
cd infrastructure/cloudflare/workers
wrangler deploy --env production

# 3. Verify API health
curl https://api.store.brainsait.io/health | jq

# 4. Test critical endpoints
curl https://api.store.brainsait.io/api/products
curl -X POST https://api.store.brainsait.io/api/auth/verify
```

**Expected Time**: 3-5 minutes

### Database Rollback

#### Schema Rollback (If Migration Issues)

```bash
# 1. Connect to database
psql $DATABASE_URL

# 2. Check migration status
SELECT * FROM alembic_version;

# 3. Rollback to previous migration
# Using Alembic (Python)
cd backend
alembic downgrade -1  # Rollback one migration

# Or specify version
alembic downgrade abc123  # Rollback to specific version

# 4. Verify schema
\dt  # List tables
\d table_name  # Describe table structure
```

**Expected Time**: 2-5 minutes (depending on migration complexity)

#### Data Rollback (If Data Corruption)

```bash
# 1. Stop application writes
# Temporary maintenance mode or read-only mode

# 2. Identify backup to restore
pg_dump --list backup_20250115_0900.sql

# 3. Restore from backup
psql $DATABASE_URL < backup_20250115_0900.sql

# 4. Verify data integrity
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM orders;"

# 5. Resume application
```

**Expected Time**: 10-30 minutes (depending on database size)

### Configuration Rollback

#### Secrets and Environment Variables

```bash
# 1. List current secrets
wrangler secret list --env production

# 2. Restore previous secret values
wrangler secret put DATABASE_URL --env production
# Enter previous value when prompted

wrangler secret put API_KEY --env production
# Enter previous value when prompted

# 3. Verify worker uses new secrets
wrangler tail --env production
```

**Expected Time**: 2-3 minutes

## Complete Rollback Procedure

### Full Stack Rollback (All Components)

```bash
#!/bin/bash
# complete-rollback.sh - Full system rollback

set -e

VERSION=$1  # e.g., v1.0.5

if [ -z "$VERSION" ]; then
  echo "Usage: ./complete-rollback.sh <version>"
  echo "Example: ./complete-rollback.sh v1.0.5"
  exit 1
fi

echo "🔄 Starting complete rollback to $VERSION"

# 1. Checkout version
echo "📦 Checking out version $VERSION..."
git fetch --tags
git checkout $VERSION

# 2. Rollback backend
echo "⚙️  Rolling back backend..."
cd infrastructure/cloudflare/workers
wrangler deploy --env production

# Wait for deployment
sleep 10

# Verify backend
echo "✅ Verifying backend..."
HEALTH=$(curl -s https://api.store.brainsait.io/health | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
  echo "❌ Backend rollback failed!"
  exit 1
fi
echo "✅ Backend rollback successful"

# 3. Rollback frontend
echo "🎨 Rolling back frontend..."
cd ../../../frontend
npm ci
npm run build
wrangler pages deploy out --project-name brainsait-store --branch main

# Wait for deployment
sleep 10

# Verify frontend
echo "✅ Verifying frontend..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://store.brainsait.io)
if [ "$STATUS" != "200" ]; then
  echo "❌ Frontend rollback failed!"
  exit 1
fi
echo "✅ Frontend rollback successful"

# 4. Verify integration
echo "🔍 Verifying system integration..."
# Test critical user flow
curl -s https://store.brainsait.io > /dev/null
curl -s https://api.store.brainsait.io/health > /dev/null

echo "✅ Complete rollback to $VERSION successful!"
echo "📊 Monitor at: https://dash.cloudflare.com"
echo "📝 Document incident and rollback in postmortem"
```

## Post-Rollback Actions

### Immediate Actions (0-15 minutes)
- [ ] Verify all critical systems operational
- [ ] Monitor error rates return to normal
- [ ] Check key metrics (response time, uptime)
- [ ] Test critical user flows
- [ ] Notify stakeholders rollback complete
- [ ] Update status page

### Short-term Actions (15-60 minutes)
- [ ] Analyze logs from failed deployment
- [ ] Identify root cause of issues
- [ ] Document what went wrong
- [ ] Create incident report
- [ ] Plan fix for issues
- [ ] Update tests to catch issue

### Long-term Actions (1-24 hours)
- [ ] Complete postmortem analysis
- [ ] Share learnings with team
- [ ] Update deployment procedures
- [ ] Improve monitoring/alerting
- [ ] Fix identified issues
- [ ] Plan next deployment

## Rollback Testing

### Test Rollback Procedures in Staging

```bash
# 1. Deploy current version to staging
wrangler deploy --env staging

# 2. Deliberately introduce a "breaking change"
# (use a test branch with intentional issue)

# 3. Practice rollback procedure
wrangler rollback --env staging

# 4. Verify rollback successful
curl https://brainsait-store-staging.fadil.workers.dev/health

# 5. Document time taken and any issues
```

**Recommendation**: Test rollback procedures monthly

## Emergency Contacts

### Incident Response Team

| Role | Contact | Availability |
|------|---------|--------------|
| DevOps Lead | devops@brainsait.io | 24/7 |
| Technical Lead | tech@brainsait.io | 24/7 |
| Database Admin | dba@brainsait.io | 24/7 |
| Security Team | security@brainsait.io | 24/7 |

### Escalation Path

1. **Level 1**: On-call engineer (response < 5 min)
2. **Level 2**: DevOps lead (response < 15 min)
3. **Level 3**: Technical lead + CTO (response < 30 min)

## Rollback Decision Matrix

| Error Rate | Response Time | User Impact | Action | Max Decision Time |
|------------|---------------|-------------|--------|-------------------|
| > 10% | Any | High | Immediate rollback | < 2 minutes |
| 5-10% | Any | High | Immediate rollback | < 5 minutes |
| 2-5% | > 2x baseline | Medium | Rollback likely | < 10 minutes |
| 1-2% | > 1.5x baseline | Low-Medium | Evaluate & decide | < 15 minutes |
| < 1% | < 1.5x baseline | Low | Monitor, fix forward | < 30 minutes |

## Common Rollback Scenarios

### Scenario 1: API Breaking Change

**Symptoms:**
- Frontend cannot connect to API
- 500 errors on API endpoints
- Authentication failures

**Rollback:**
```bash
# Quick backend rollback
wrangler rollback --env production

# Verify
curl https://api.store.brainsait.io/health
```

### Scenario 2: Database Migration Issues

**Symptoms:**
- Database errors in logs
- Slow queries
- Data inconsistencies

**Rollback:**
```bash
# Rollback migration
cd backend
alembic downgrade -1

# Verify
psql $DATABASE_URL -c "\d"  # Check schema
```

### Scenario 3: Frontend Build Issue

**Symptoms:**
- Blank page
- JavaScript errors
- Assets not loading

**Rollback:**
```bash
# Promote previous deployment
wrangler pages deployment list --project-name brainsait-store
wrangler pages deployment promote <previous-id>
```

### Scenario 4: Payment Gateway Integration

**Symptoms:**
- Payment processing failures
- Stripe/PayPal errors
- Transaction timeouts

**Rollback:**
```bash
# Rollback both frontend and backend
git checkout v1.0.5
./complete-rollback.sh v1.0.5

# Verify payment test
curl -X POST https://api.store.brainsait.io/api/payments/test
```

## Rollback Validation

### Validation Checklist

After any rollback:

- [ ] **Health checks passing**
  ```bash
  curl https://api.store.brainsait.io/health
  ```

- [ ] **Error rates normal** (< 0.1%)
  ```bash
  wrangler analytics --env production
  ```

- [ ] **Response times acceptable** (< 500ms p95)

- [ ] **Critical flows working**
  - [ ] User login
  - [ ] Product browsing
  - [ ] Checkout
  - [ ] Payment processing

- [ ] **Database connectivity**
  ```bash
  psql $DATABASE_URL -c "SELECT 1;"
  ```

- [ ] **External integrations working**
  - [ ] Stripe
  - [ ] PayPal
  - [ ] Email service

## Documentation & Communication

### Incident Report Template

```markdown
# Rollback Incident Report

## Incident Details
- **Date/Time**: 2025-01-15 14:30 UTC
- **Duration**: 12 minutes
- **Severity**: High
- **Version Rolled Back From**: v1.1.0
- **Version Rolled Back To**: v1.0.5

## Issue Description
[Detailed description of what went wrong]

## Impact
- Users affected: ~500 users
- Services affected: Payment processing
- Revenue impact: $0 (caught before transactions)

## Timeline
- 14:30 - Deployment of v1.1.0 started
- 14:35 - Error rate spike detected (5%)
- 14:37 - Rollback decision made
- 14:38 - Rollback initiated
- 14:42 - Rollback completed and verified
- 14:45 - Normal operation resumed

## Root Cause
[Technical explanation of the issue]

## Resolution
[How the rollback resolved the issue]

## Lessons Learned
1. [Lesson 1]
2. [Lesson 2]

## Action Items
- [ ] Fix identified issue in v1.1.1
- [ ] Add test coverage for this scenario
- [ ] Update deployment checklist
```

---

**Document Version**: 1.0.0  
**Last Updated**: January 2025  
**Related Documents**:
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- [Canary Deployment](./CANARY_DEPLOYMENT.md)
- [Monitoring Guide](./MONITORING.md)
