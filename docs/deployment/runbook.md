# Deployment Runbook - BrainsAIT Store

## Overview

Comprehensive deployment runbook for the BrainsAIT Store platform, covering frontend, backend, API gateway, and infrastructure deployment procedures.

**Runbook Version**: 1.0  
**Last Updated**: October 2024  
**Owner**: DevOps & Platform Team

---

## 🎯 Deployment Strategy

### Deployment Approach
- **Blue-Green Deployment**: Zero-downtime deployments
- **Staged Rollout**: Gradual traffic shifting
- **Automated Testing**: CI/CD pipeline validation
- **Rollback Ready**: Quick rollback procedures

### Environments
1. **Development**: Feature development and testing
2. **Staging**: Pre-production validation
3. **Production**: Live customer-facing environment

---

## 📋 Pre-Deployment Checklist

### Infrastructure Readiness
- [ ] Database migrations prepared and tested
- [ ] Environment variables configured
- [ ] SSL certificates valid and configured
- [ ] DNS records configured correctly
- [ ] CDN cache purge plan ready
- [ ] Monitoring and alerting active
- [ ] Backup completed within last 24 hours

### Code Readiness
- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed and approved
- [ ] Security scan completed (0 critical vulnerabilities)
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Change log prepared

### Team Readiness
- [ ] Deployment team assembled and briefed
- [ ] Support team notified and on standby
- [ ] Rollback procedures reviewed
- [ ] Communication plan ready
- [ ] Incident response team identified

### Business Readiness
- [ ] Stakeholders notified of deployment window
- [ ] Customer communication prepared (if needed)
- [ ] Feature flags configured (if applicable)
- [ ] Marketing materials ready (for feature launches)

---

## 🚀 Deployment Procedures

### 1. Frontend Deployment (Next.js - Cloudflare Pages)

#### Step 1: Pre-deployment Tasks
```bash
# Navigate to frontend directory
cd /home/runner/work/brainsait-store/brainsait-store/frontend

# Install dependencies
npm ci

# Run linting
npm run lint

# Run tests
npm run test:ci

# Build for production
npm run build

# Verify build output
ls -la .next/
```

**Expected Output**: Clean build with no errors, warnings reviewed

#### Step 2: Deploy to Staging
```bash
# Deploy to Cloudflare Pages staging
npx wrangler pages deploy .next/ \
  --project-name=brainsait-store \
  --branch=staging \
  --commit-hash=$(git rev-parse HEAD)

# Note the deployment URL
# Example: https://staging-abc123.brainsait-store.pages.dev
```

**Verification**:
- [ ] Visit staging URL
- [ ] Test critical user flows
- [ ] Verify language switching
- [ ] Check mobile responsiveness
- [ ] Validate payment flows (test mode)

#### Step 3: Deploy to Production
```bash
# Deploy to production
npx wrangler pages deploy .next/ \
  --project-name=brainsait-store \
  --branch=main \
  --commit-hash=$(git rev-parse HEAD)

# Deployment URL: https://store.brainsait.io
```

#### Step 4: Post-Deployment Verification
```bash
# Test production endpoint
curl -I https://store.brainsait.io

# Expected: HTTP/2 200
# Content-Type: text/html

# Test API connectivity
curl https://store.brainsait.io/api/health

# Expected: {"status": "healthy"}
```

**Smoke Tests**:
- [ ] Homepage loads correctly
- [ ] Product catalog accessible
- [ ] User authentication works
- [ ] Checkout flow functional
- [ ] Arabic/English switching works

---

### 2. Backend Deployment (FastAPI)

#### Step 1: Prepare Backend
```bash
# Navigate to backend directory
cd /home/runner/work/brainsait-store/brainsait-store/backend

# Create virtual environment (if needed)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run linting
black --check .
isort --check-only .

# Run tests
pytest --cov=app --cov-report=term-missing

# Expected: All tests pass, coverage > 80%
```

#### Step 2: Database Migrations
```bash
# Check current database version
python db_manager.py status

# Create backup before migration
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations in staging first
export ENV=staging
alembic upgrade head

# Verify migration success
python db_manager.py validate

# If successful, run in production
export ENV=production
alembic upgrade head
```

**Migration Verification**:
```sql
-- Connect to database and verify
SELECT * FROM alembic_version;
-- Should show latest migration version

-- Check table structures
\dt
-- All expected tables should be present
```

#### Step 3: Deploy Backend Application

**Option A: Traditional Server Deployment**
```bash
# SSH to application server
ssh deploy@backend.brainsait.io

# Pull latest code
cd /var/www/brainsait-backend
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart application
sudo systemctl restart brainsait-backend

# Check status
sudo systemctl status brainsait-backend
```

**Option B: Docker Deployment**
```bash
# Build Docker image
docker build -t brainsait-backend:$(git rev-parse --short HEAD) .

# Tag as latest
docker tag brainsait-backend:$(git rev-parse --short HEAD) brainsait-backend:latest

# Push to registry
docker push your-registry/brainsait-backend:latest

# Deploy with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

#### Step 4: Verify Backend Health
```bash
# Health check
curl https://api.brainsait.io/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}

# API documentation
curl https://api.brainsait.io/docs

# Should return Swagger UI HTML
```

**Functional Tests**:
```bash
# Test authentication
curl -X POST https://api.brainsait.io/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test product listing
curl https://api.brainsait.io/api/v1/products

# Test protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://api.brainsait.io/api/v1/user/profile
```

---

### 3. API Gateway Deployment (Cloudflare Workers)

#### Step 1: Prepare Wrangler Configuration
```bash
# Navigate to root directory
cd /home/runner/work/brainsait-store/brainsait-store

# Verify wrangler.toml configuration
cat wrangler.toml

# Test configuration validity
npx wrangler deploy --dry-run
```

**Expected wrangler.toml**:
```toml
name = "brainsait-api-gateway"
main = "src/index.ts"
compatibility_date = "2024-10-01"

[vars]
ENVIRONMENT = "production"

[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id"
```

#### Step 2: Deploy to Staging
```bash
# Deploy to staging environment
npx wrangler deploy --env staging

# Note the worker URL
# https://brainsait-api-gateway-staging.fadil.workers.dev
```

**Staging Tests**:
```bash
# Health check
curl https://brainsait-api-gateway-staging.fadil.workers.dev/health

# Test routing
curl https://brainsait-api-gateway-staging.fadil.workers.dev/api/v1/products

# Test rate limiting
for i in {1..150}; do 
  curl https://brainsait-api-gateway-staging.fadil.workers.dev/api/v1/products
done
# Should hit rate limit around request 120
```

#### Step 3: Deploy to Production
```bash
# Deploy to production
npx wrangler deploy --env production

# Production URL: https://brainsait-api-gateway.fadil.workers.dev
```

#### Step 4: Update DNS (if needed)
```bash
# If using custom domain, update DNS CNAME
# api.brainsait.io -> brainsait-api-gateway.fadil.workers.dev

# Verify DNS propagation
dig api.brainsait.io
nslookup api.brainsait.io
```

---

### 4. GIVC Healthcare API Deployment

#### Step 1: Deploy GIVC Worker
```bash
# Navigate to GIVC worker directory (if separate)
cd /path/to/givc-healthcare-worker

# Deploy to production
npx wrangler deploy --env production

# Verify deployment
curl https://givc-healthcare-api.fadil.workers.dev/health

# Expected:
{
  "status": "healthy",
  "service": "givc-healthcare-api",
  "version": "1.0.0"
}
```

#### Step 2: Test GIVC Integration
```bash
# Test NPHIES endpoint
curl -X POST https://givc-healthcare-api.fadil.workers.dev/api/v1/nphies/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"12345","provider_id":"67890"}'

# Test medical data processing
curl -X POST https://givc-healthcare-api.fadil.workers.dev/api/v1/medical/process \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data":"medical-data"}'
```

---

## 🔄 Staged Rollout Procedure

### Phase 1: Canary Deployment (10% Traffic)
```bash
# Configure canary routing in Cloudflare
# Send 10% of traffic to new version

# Monitor for 30 minutes
# Check metrics:
# - Error rate < 0.1%
# - Response time < 200ms (p95)
# - No critical errors in logs

# If metrics good, proceed to Phase 2
# If issues detected, rollback immediately
```

### Phase 2: Gradual Rollout (50% Traffic)
```bash
# Increase traffic to 50%
# Monitor for 1 hour

# Check metrics:
# - Error rate stable or decreasing
# - Response time within SLA
# - Database performance stable
# - No user complaints

# If metrics good, proceed to Phase 3
```

### Phase 3: Full Rollout (100% Traffic)
```bash
# Send all traffic to new version
# Monitor for 2 hours

# Final verification:
# - All systems operational
# - No critical errors
# - Performance within SLA
# - User feedback positive

# Mark deployment as complete
```

---

## 📊 Post-Deployment Monitoring

### Immediate Monitoring (First Hour)

**Key Metrics to Watch**:
```bash
# Error rate
target: < 0.5%

# API response time
target: < 200ms (p95)

# Database connections
target: < 80% of pool

# Memory usage
target: < 80%

# CPU usage
target: < 70%
```

**Monitoring Commands**:
```bash
# Check application logs
tail -f /var/log/brainsait-backend/app.log

# Check error logs
tail -f /var/log/brainsait-backend/error.log

# Monitor with systemctl
sudo systemctl status brainsait-backend

# Check Cloudflare Workers analytics
npx wrangler tail --env production
```

### Critical User Flows to Test

1. **User Registration & Login**
   ```bash
   # Test registration
   curl -X POST https://api.brainsait.io/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'
   
   # Test login
   curl -X POST https://api.brainsait.io/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test123!"}'
   ```

2. **Product Browsing**
   ```bash
   # List products
   curl https://api.brainsait.io/api/v1/products
   
   # Get product details
   curl https://api.brainsait.io/api/v1/products/5
   ```

3. **Checkout Flow**
   ```bash
   # Add to cart
   curl -X POST https://api.brainsait.io/api/v1/cart \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"product_id":5,"quantity":1}'
   
   # Initiate checkout
   curl -X POST https://api.brainsait.io/api/v1/checkout \
     -H "Authorization: Bearer $TOKEN"
   ```

4. **Payment Processing**
   ```bash
   # Test payment (test mode)
   curl -X POST https://api.brainsait.io/api/v1/payments \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"payment_method":"test","amount":14999}'
   ```

### Alerting Thresholds

**Critical Alerts** (Page immediately):
- Error rate > 2%
- API response time > 1 second (p95)
- Database connection failures
- Payment processing failures > 5%
- Service completely down

**Warning Alerts** (Notify within 15 minutes):
- Error rate > 0.5%
- API response time > 500ms (p95)
- Memory usage > 85%
- CPU usage > 80%
- Disk space > 85%

---

## 🔙 Rollback Procedures

### When to Rollback

**Immediate Rollback Triggers**:
- Critical functionality broken
- Error rate > 5%
- Data corruption detected
- Security breach suspected
- Payment processing completely failing

**Consider Rollback**:
- Error rate > 2% sustained for 5+ minutes
- Response time > 2x baseline
- User complaints about critical features
- Database performance degradation

### Frontend Rollback

#### Option 1: Cloudflare Pages Rollback
```bash
# List previous deployments
npx wrangler pages deployments list --project-name=brainsait-store

# Rollback to previous deployment
npx wrangler pages deployment rollback [DEPLOYMENT_ID] \
  --project-name=brainsait-store

# Verify rollback
curl -I https://store.brainsait.io
```

#### Option 2: Manual Rollback
```bash
# Checkout previous version
git checkout [PREVIOUS_COMMIT_HASH]

# Rebuild and redeploy
npm run build
npx wrangler pages deploy .next/ --project-name=brainsait-store

# Verify
curl -I https://store.brainsait.io
```

### Backend Rollback

#### Option 1: Git Rollback
```bash
# Checkout previous version
git checkout [PREVIOUS_COMMIT_HASH]

# Reinstall dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart brainsait-backend

# Verify
curl https://api.brainsait.io/health
```

#### Option 2: Docker Rollback
```bash
# Find previous image
docker images | grep brainsait-backend

# Update docker-compose.yml to use previous tag
# backend:
#   image: brainsait-backend:[PREVIOUS_TAG]

# Restart containers
docker-compose down
docker-compose up -d

# Verify
curl https://api.brainsait.io/health
```

### Database Rollback

⚠️ **WARNING**: Database rollbacks are risky. Only perform if absolutely necessary.

```bash
# Option 1: Rollback migration
alembic downgrade -1

# Option 2: Restore from backup
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME backup_20241008_120000.sql

# Verify data integrity
python db_manager.py validate
```

### Worker Rollback

```bash
# List previous deployments
npx wrangler deployments list

# Rollback worker
npx wrangler rollback [DEPLOYMENT_ID]

# Verify
curl https://brainsait-api-gateway.fadil.workers.dev/health
```

---

## 📞 Communication

### Stakeholder Notifications

**Pre-Deployment**:
```
Subject: Scheduled Deployment - BrainsAIT Store

Team,

We will be deploying updates to the BrainsAIT Store platform:

Date: [DATE]
Time: [TIME] (GMT+3)
Duration: ~30 minutes
Expected Impact: None (zero-downtime deployment)

Changes:
- [Brief list of changes]

The deployment team will be monitoring closely. If you notice any issues, please report immediately to #incidents channel.

Thank you,
DevOps Team
```

**Post-Deployment Success**:
```
Subject: Deployment Complete - BrainsAIT Store

Team,

The deployment completed successfully at [TIME].

✅ All systems operational
✅ Smoke tests passed
✅ Monitoring stable

New features now live:
- [List of features]

Please report any issues to #support.

Thank you,
DevOps Team
```

**Post-Deployment Issues**:
```
Subject: [URGENT] Deployment Issue - BrainsAIT Store

Team,

We've detected an issue with the latest deployment:

Issue: [Description]
Impact: [User impact]
Status: [Investigating/Rolling back/Fixed]

We are [action being taken].

Updates will be provided every 15 minutes.

DevOps Team
```

### Incident Response

**Severity Levels**:
- **P0 - Critical**: System down, data loss, security breach
- **P1 - High**: Major feature broken, significant user impact
- **P2 - Medium**: Minor feature broken, limited user impact
- **P3 - Low**: Cosmetic issues, no user impact

**Escalation**:
```
P0: Immediate page → Engineering Director + CTO
P1: 15 min notification → Engineering Manager
P2: 1 hour notification → Team Lead
P3: Next business day → Team Lead
```

---

## ✅ Deployment Completion Checklist

### Technical Verification
- [ ] All services responding correctly
- [ ] Database migrations successful
- [ ] Cache cleared and repopulated
- [ ] SSL certificates valid
- [ ] DNS propagation complete (if changed)
- [ ] Monitoring dashboards updated
- [ ] Alerts configured correctly

### Functional Verification
- [ ] User registration and login working
- [ ] Product browsing functional
- [ ] Checkout flow working
- [ ] Payment processing operational
- [ ] Admin dashboard accessible
- [ ] Arabic/English switching working
- [ ] Mobile responsive design working

### Business Verification
- [ ] No critical user complaints
- [ ] Error rates within acceptable range
- [ ] Performance metrics meeting SLA
- [ ] Revenue tracking functioning
- [ ] Analytics collecting data

### Documentation
- [ ] Deployment notes updated
- [ ] Change log updated
- [ ] Runbook updated (if procedures changed)
- [ ] Known issues documented
- [ ] Post-mortem scheduled (if issues occurred)

---

## 📚 References

### Internal Documentation
- [Architecture Overview](../architecture/README.md)
- [Database Schema](../architecture/database.md)
- [API Documentation](../api/README.md)
- [Monitoring Guide](./monitoring.md)
- [Rollback Procedures](./rollback.md)

### External Resources
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

### Contact Information
- **On-Call Engineer**: See PagerDuty schedule
- **Engineering Manager**: manager@brainsait.io
- **DevOps Lead**: devops@brainsait.io
- **Emergency Hotline**: +966-XXX-XXXX

---

**Document Owner**: DevOps Team  
**Last Updated**: October 2024  
**Next Review**: After each major deployment  
**Version**: 1.0
