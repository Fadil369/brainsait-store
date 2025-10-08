# Deployment Checklist - BrainSAIT Store

## Pre-Deployment Verification

### Code Quality & Testing
- [ ] All unit tests passing (frontend & backend)
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Security scanning completed (CodeQL)
- [ ] No critical vulnerabilities detected
- [ ] Code review completed and approved
- [ ] All PR comments resolved

### Configuration Validation
- [ ] Validate wrangler.toml configuration
  ```bash
  node scripts/validate-wrangler.js
  npx wrangler deploy --dry-run
  ```
- [ ] Environment variables configured for staging
- [ ] Environment variables configured for production
- [ ] Secrets properly set in Cloudflare dashboard
- [ ] API keys and credentials secured

### Database & Storage
- [ ] Database migrations tested in staging
- [ ] Database backup strategy configured
- [ ] Connection pooling configured
- [ ] Redis cache configured
- [ ] Cloudflare KV namespaces created
- [ ] D1 database initialized

## Staging Environment Verification

### Backend Deployment
- [ ] Deploy backend to staging environment
  ```bash
  cd infrastructure/cloudflare/workers
  wrangler deploy --env staging
  ```
- [ ] Health check endpoint responds
  ```bash
  curl https://brainsait-store-staging.fadil.workers.dev/health
  ```
- [ ] API documentation accessible at `/api/docs`
- [ ] Rate limiting functional
- [ ] CORS headers configured correctly
- [ ] Authentication working (JWT tokens)
- [ ] Database connectivity verified

### Frontend Deployment
- [ ] Deploy frontend to staging
  ```bash
  cd frontend
  npm run build
  wrangler pages deploy out --project-name brainsait-store-staging
  ```
- [ ] Site loads correctly at staging URL
- [ ] Multi-language support working (EN/AR)
- [ ] RTL layout working for Arabic
- [ ] Responsive design on mobile/tablet/desktop
- [ ] All pages loading without errors
- [ ] Navigation working correctly

### Integration Testing (Staging)
- [ ] API endpoints responding correctly
- [ ] Payment gateway test mode working
  - [ ] Stripe test payments
  - [ ] PayPal sandbox payments
  - [ ] Apple Pay test environment
- [ ] Email notifications sending
- [ ] Webhook endpoints receiving events
- [ ] Analytics tracking events
- [ ] Error logging to monitoring system

### Performance Testing
- [ ] Load testing completed
- [ ] Page load times < 3 seconds
- [ ] API response times < 500ms
- [ ] Lighthouse score > 90
- [ ] Core Web Vitals passing
- [ ] CDN caching working correctly

### Security Verification
- [ ] SSL/TLS certificates valid
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] API rate limiting tested
- [ ] SQL injection testing passed
- [ ] XSS protection verified
- [ ] CSRF tokens working
- [ ] Apple Pay domain verification
  ```bash
  curl https://store.brainsait.io/.well-known/apple-developer-merchantid-domain-association.txt
  ```

## CI/CD Pipeline Verification

### GitHub Actions
- [ ] Workflow files validated
  - [ ] `.github/workflows/codeql.yml`
  - [ ] `.github/workflows/validate-wrangler.yml`
- [ ] Build process succeeds
- [ ] Test execution completes
- [ ] Deployment steps working
- [ ] Secrets configured in GitHub
  - [ ] `CLOUDFLARE_API_TOKEN`
  - [ ] `CLOUDFLARE_ACCOUNT_ID`
  - [ ] `NEXT_PUBLIC_API_URL`
  - [ ] `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

### Automated Deployment
- [ ] Staging deploys on push to `develop` branch
- [ ] Production requires manual approval
- [ ] Rollback mechanism tested
- [ ] Deployment notifications configured

## Production Deployment

### Pre-Production Checklist
- [ ] Staging environment stable for 24+ hours
- [ ] No critical bugs reported in staging
- [ ] Performance metrics meeting targets
- [ ] Security audit completed
- [ ] Backup verification completed
- [ ] Rollback plan documented and tested
- [ ] Team notified of deployment schedule
- [ ] Maintenance window communicated to users

### Production Configuration
- [ ] Production environment variables set
- [ ] Production API keys configured
- [ ] Production database ready
- [ ] Production Redis configured
- [ ] CDN settings optimized
- [ ] DNS records configured
  - [ ] `store.brainsait.io` → Cloudflare Pages
  - [ ] `api.store.brainsait.io` → Cloudflare Workers
- [ ] SSL certificates validated

### Deployment Execution
- [ ] Create deployment tag
  ```bash
  git tag -a v1.0.0 -m "Production release v1.0.0"
  git push origin v1.0.0
  ```
- [ ] Deploy backend to production
  ```bash
  wrangler deploy --env production
  ```
- [ ] Verify backend health check
  ```bash
  curl https://api.store.brainsait.io/health
  ```
- [ ] Deploy frontend to production
  ```bash
  cd frontend
  npm run build
  wrangler pages deploy out --project-name brainsait-store
  ```
- [ ] Verify frontend loads
- [ ] Verify API integration working

### Post-Deployment Verification
- [ ] All critical user flows tested
  - [ ] User registration/login
  - [ ] Product browsing
  - [ ] Add to cart
  - [ ] Checkout process
  - [ ] Payment processing
- [ ] Monitor error rates (should be < 0.1%)
- [ ] Monitor response times
- [ ] Check analytics data collection
- [ ] Verify email notifications
- [ ] Test payment processing (small real transaction)

## Monitoring & Alerting

### Monitoring Setup
- [ ] Cloudflare Analytics configured
- [ ] Health check monitoring active
- [ ] Error tracking configured
- [ ] Performance monitoring active
- [ ] Uptime monitoring configured
- [ ] Alert rules configured
  - [ ] Error rate > 1%
  - [ ] Response time > 2s
  - [ ] Uptime < 99.5%

### Metrics to Monitor
- [ ] Request rate (requests/min)
- [ ] Error rate (errors/min)
- [ ] Response time (p50, p95, p99)
- [ ] Database connection pool usage
- [ ] Cache hit rate
- [ ] CPU/Memory usage (Workers)

## Rollback Plan

### Rollback Triggers
- Critical bugs affecting core functionality
- Security vulnerabilities discovered
- Error rate > 5%
- Performance degradation > 50%
- Payment processing failures

### Rollback Procedure
See [ROLLBACK_PROCEDURES.md](./ROLLBACK_PROCEDURES.md) for detailed steps.

### Quick Rollback Commands
```bash
# Frontend rollback
wrangler pages deployment list --project-name brainsait-store
wrangler pages deployment promote <previous-deployment-id>

# Backend rollback
git checkout <previous-release-tag>
wrangler deploy --env production
```

## Post-Launch Activities

### First 24 Hours
- [ ] Monitor error rates continuously
- [ ] Monitor performance metrics
- [ ] Monitor payment processing
- [ ] Verify analytics collection
- [ ] Check user feedback channels
- [ ] Team on-call and available

### First Week
- [ ] Review performance trends
- [ ] Analyze user behavior
- [ ] Address minor issues
- [ ] Optimize based on real traffic
- [ ] Collect user feedback
- [ ] Plan next iteration

### Documentation Updates
- [ ] Update API documentation with production URLs
- [ ] Update onboarding guides
- [ ] Create troubleshooting guides based on issues
- [ ] Update runbooks with lessons learned

## Sign-Off

### Required Approvals
- [ ] Technical Lead: _________________ Date: _______
- [ ] DevOps Lead: _________________ Date: _______
- [ ] Security Lead: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______

### Deployment Notes
```
Date: ____________________
Version: __________________
Deployed by: ______________
Special considerations: 
________________________________
________________________________
________________________________
```

---

**Document Version**: 1.0.0  
**Last Updated**: January 2025  
**Next Review**: After first production deployment
