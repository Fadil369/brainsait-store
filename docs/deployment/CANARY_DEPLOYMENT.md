# Canary Deployment Strategy - BrainSAIT Store

## Overview

Canary deployments allow gradual rollout of new versions to a subset of users, minimizing risk and enabling quick rollback if issues are detected.

## Canary Deployment Process

### 1. Prepare Canary Release

```bash
# Tag the canary release
git tag -a v1.1.0-canary -m "Canary release v1.1.0"
git push origin v1.1.0-canary
```

### 2. Deploy to Canary Environment

#### Backend Canary Deployment

Create a canary worker:

```bash
cd infrastructure/cloudflare/workers

# Deploy canary version with unique name
wrangler deploy --name brainsait-store-canary
```

Configure route splitting in Cloudflare dashboard:
- 95% traffic → `brainsait-store` (production)
- 5% traffic → `brainsait-store-canary` (canary)

#### Frontend Canary Deployment

For Cloudflare Pages:

```bash
cd frontend
npm run build

# Deploy as preview/canary
wrangler pages deploy out --project-name brainsait-store --branch canary
```

Use Cloudflare's A/B testing or custom routing:

```javascript
// middleware.ts - Route 5% of traffic to canary
export function middleware(request: NextRequest) {
  const canaryPercentage = 5; // 5% canary traffic
  const random = Math.random() * 100;
  
  if (random < canaryPercentage) {
    // Serve canary version
    const url = request.nextUrl.clone();
    url.hostname = 'canary.store.brainsait.io';
    return NextResponse.rewrite(url);
  }
  
  return NextResponse.next();
}
```

### 3. Monitor Canary Deployment

#### Key Metrics to Watch

```bash
# Monitor canary worker logs
wrangler tail --env canary --format pretty

# Compare error rates
wrangler analytics --env production
wrangler analytics --env canary
```

**Monitor for:**
- Error rate comparison (canary vs production)
- Response time differences
- User engagement metrics
- Payment success rates
- API call patterns

#### Monitoring Dashboard

Create comparison dashboard:

| Metric | Production | Canary | Delta | Status |
|--------|-----------|---------|-------|--------|
| Error Rate | 0.05% | 0.06% | +0.01% | ✅ OK |
| P95 Latency | 450ms | 470ms | +20ms | ✅ OK |
| Conversion Rate | 3.2% | 3.1% | -0.1% | ⚠️ Watch |
| API Success | 99.9% | 99.8% | -0.1% | ✅ OK |

### 4. Gradual Rollout Schedule

**Phase 1: Initial Canary (5% traffic)**
- Duration: 2 hours
- Monitor closely for issues
- Quick rollback if error rate > 0.5%

**Phase 2: Expanded Canary (25% traffic)**
- Duration: 4 hours
- Broader user testing
- Monitor business metrics

**Phase 3: Majority Canary (50% traffic)**
- Duration: 4 hours
- Validate at scale
- Compare performance metrics

**Phase 4: Full Rollout (100% traffic)**
- Switch all traffic to new version
- Keep old version ready for 24 hours
- Monitor for any delayed issues

### 5. Canary Decision Criteria

#### Go/No-Go Metrics

**Proceed with rollout if:**
- ✅ Error rate increase < 0.2%
- ✅ P95 latency increase < 10%
- ✅ No critical bugs reported
- ✅ Payment success rate maintained
- ✅ User engagement stable or improved

**Rollback immediately if:**
- ❌ Error rate increase > 1%
- ❌ Critical functionality broken
- ❌ Payment processing failures
- ❌ Security vulnerability detected
- ❌ P95 latency increase > 50%

### 6. Rollback Canary Deployment

#### Automatic Rollback

Configure automatic rollback based on metrics:

```javascript
// Cloudflare Worker - Auto Rollback
async function monitorCanary() {
  const canaryMetrics = await getMetrics('canary');
  const prodMetrics = await getMetrics('production');
  
  if (canaryMetrics.errorRate > prodMetrics.errorRate * 2) {
    await rollbackCanary();
    await notifyTeam('Automatic canary rollback triggered');
  }
}
```

#### Manual Rollback

```bash
# Route all traffic back to production
wrangler dispatch-namespaces update brainsait-store \
  --routes "api.store.brainsait.io/*" \
  --script brainsait-store-production

# Or simply delete the canary worker
wrangler delete --name brainsait-store-canary

# Frontend rollback
wrangler pages deployment promote <production-deployment-id>
```

### 7. Canary Testing Checklist

- [ ] Canary environment deployed successfully
- [ ] Traffic routing configured (5% to canary)
- [ ] Monitoring dashboards showing data
- [ ] Alert rules configured for canary
- [ ] Team notified of canary deployment
- [ ] Rollback procedure documented
- [ ] Key metrics baseline captured
- [ ] Error tracking configured
- [ ] Performance metrics tracking active

## Advanced Canary Strategies

### Feature Flags with Canary

Combine canary deployment with feature flags:

```typescript
// Feature flag configuration
const featureFlags = {
  newCheckoutFlow: {
    enabled: true,
    canaryPercentage: 10,
    criteria: {
      userSegment: 'premium',
      region: 'us-east',
    }
  }
};

// In application code
if (shouldEnableFeature('newCheckoutFlow', user)) {
  return <NewCheckoutFlow />;
}
return <LegacyCheckoutFlow />;
```

### User-Based Canary

Target specific user segments:

```typescript
// Route beta users to canary
export function middleware(request: NextRequest) {
  const userId = getUserId(request);
  const user = await getUser(userId);
  
  if (user.betaTester || user.segment === 'early-adopters') {
    return routeToCanary(request);
  }
  
  return routeToProduction(request);
}
```

### Geographic Canary

Roll out by region:

```javascript
// Cloudflare Worker - Geographic routing
async function handleRequest(request) {
  const country = request.cf.country;
  
  // Test in specific countries first
  const canaryCountries = ['SA', 'AE', 'EG'];
  
  if (canaryCountries.includes(country)) {
    return canaryVersion.fetch(request);
  }
  
  return productionVersion.fetch(request);
}
```

## Monitoring & Alerting

### Canary-Specific Alerts

```yaml
# Alert configuration
alerts:
  - name: "Canary Error Rate High"
    condition: canary.errors > production.errors * 1.5
    action: notify_team
    severity: warning
    
  - name: "Canary Critical Error"
    condition: canary.errors > production.errors * 3
    action: auto_rollback
    severity: critical
    
  - name: "Canary Performance Degradation"
    condition: canary.p95_latency > production.p95_latency * 1.3
    action: notify_team
    severity: warning
```

### Real-Time Dashboard

Key metrics to display:

```javascript
{
  production: {
    requests: 10000,
    errors: 5,
    errorRate: 0.05,
    p95Latency: 450,
    activeUsers: 2500
  },
  canary: {
    requests: 500,
    errors: 1,
    errorRate: 0.20,
    p95Latency: 480,
    activeUsers: 125
  },
  comparison: {
    errorRateDelta: +0.15,
    latencyDelta: +30,
    status: 'MONITORING'
  }
}
```

## Canary Deployment Scripts

### Automated Canary Script

```bash
#!/bin/bash
# deploy-canary.sh

set -e

VERSION=$1
PERCENTAGE=${2:-5}

if [ -z "$VERSION" ]; then
  echo "Usage: ./deploy-canary.sh <version> [percentage]"
  exit 1
fi

echo "🐤 Deploying canary version: $VERSION"
echo "📊 Traffic percentage: $PERCENTAGE%"

# Deploy canary worker
cd infrastructure/cloudflare/workers
wrangler deploy --name brainsait-store-canary --env canary

# Deploy canary frontend
cd ../../../frontend
npm run build
wrangler pages deploy out --project-name brainsait-store --branch canary

# Configure traffic split
echo "⚙️  Configuring traffic split..."
# Use Cloudflare API or dashboard to set traffic percentage

echo "✅ Canary deployment complete"
echo "📈 Monitor at: https://dash.cloudflare.com"
echo "🔄 Promote with: ./promote-canary.sh"
echo "↩️  Rollback with: ./rollback-canary.sh"
```

### Promote Canary Script

```bash
#!/bin/bash
# promote-canary.sh

set -e

echo "🚀 Promoting canary to production..."

# Verify canary health
echo "🔍 Checking canary health..."
HEALTH=$(curl -s https://canary.store.brainsait.io/health | jq -r '.status')

if [ "$HEALTH" != "healthy" ]; then
  echo "❌ Canary is not healthy. Aborting promotion."
  exit 1
fi

# Gradually increase traffic
for PERCENTAGE in 25 50 75 100; do
  echo "📊 Routing $PERCENTAGE% traffic to canary..."
  # Update traffic split
  sleep 300 # Wait 5 minutes between increases
  
  # Check metrics
  echo "📈 Checking metrics at $PERCENTAGE%..."
  # Verify error rates acceptable
done

echo "✅ Canary promoted to production"
echo "🏷️  Tag production release: git tag -a v1.1.0 -m 'Release v1.1.0'"
```

## Best Practices

1. **Start Small**: Begin with 1-5% traffic
2. **Monitor Closely**: Watch metrics in real-time during initial rollout
3. **Define Success Criteria**: Clear metrics for go/no-go decisions
4. **Automate When Possible**: Automatic rollback on critical failures
5. **Gradual Increase**: Don't jump from 5% to 100%
6. **Keep Production Ready**: Maintain ability to rollback for 24-48 hours
7. **Document Everything**: Record observations and decisions
8. **Test Thoroughly**: Ensure canary testing includes all critical paths

## Troubleshooting

### Canary Shows Higher Error Rate

```bash
# Compare error logs
wrangler tail --env production > prod_errors.log &
wrangler tail --env canary > canary_errors.log &

# Analyze differences
diff prod_errors.log canary_errors.log
```

### Canary Performance Issues

```bash
# Profile canary requests
wrangler tail --env canary --format json | \
  jq 'select(.outcome == "exception" or .status >= 500)'

# Check for slow database queries
# Review code changes for performance impacts
```

### Traffic Not Routing to Canary

```bash
# Verify route configuration
wrangler routes list

# Test canary directly
curl -H "X-Canary: true" https://api.store.brainsait.io/health
```

---

**Document Version**: 1.0.0  
**Last Updated**: January 2025  
**Related Documents**: 
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md)
- [Monitoring Guide](./MONITORING.md)
