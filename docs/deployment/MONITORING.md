# Post-Launch Monitoring Guide - BrainSAIT Store

## Overview

This guide provides comprehensive monitoring strategies for the BrainSAIT Store platform to ensure optimal performance, reliability, and user experience post-launch.

## Monitoring Stack

### Infrastructure
- **Cloudflare Analytics**: Worker and Pages metrics
- **Cloudflare Logs**: Request logging and analysis
- **Health Checks**: Custom endpoint monitoring
- **Uptime Monitoring**: External service monitoring

### Application Metrics
- Request rate and volume
- Error rates and types
- Response times (p50, p95, p99)
- Cache hit rates
- Database performance

### Business Metrics
- User registrations
- Payment transactions
- Revenue tracking
- Conversion rates
- User engagement

## Critical Metrics to Monitor

### System Health Metrics

#### 1. Uptime
**Target**: 99.9% (3 nines)
**Alert Threshold**: < 99.5%

```bash
# Monitor via Cloudflare Analytics
wrangler analytics --env production

# External uptime monitoring
curl -f https://api.store.brainsait.io/health || alert_team
```

#### 2. Error Rate
**Target**: < 0.1%
**Alert Thresholds**:
- Warning: > 0.5%
- Critical: > 1%
- Emergency: > 5%

```bash
# Monitor error rates
wrangler tail --env production --format json | \
  jq 'select(.outcome == "exception" or .status >= 500)'
```

#### 3. Response Time
**Targets**:
- P50: < 200ms
- P95: < 500ms
- P99: < 1000ms

**Alert Thresholds**:
- Warning: P95 > 800ms
- Critical: P95 > 1500ms

```bash
# Monitor response times
wrangler analytics --env production | \
  grep "Response Time"
```

#### 4. Request Volume
**Baseline**: Establish during first week
**Alert Thresholds**:
- Sudden drop > 50%: Possible outage
- Sudden spike > 300%: Possible attack or viral traffic

### Application Performance Metrics

#### 1. API Endpoints

Monitor key endpoints:

```bash
# Critical endpoints to monitor
GET  /health                    # Health check
GET  /api/products              # Product listing
POST /api/auth/login            # Authentication
POST /api/payments/checkout     # Payment processing
GET  /api/orders/:id            # Order retrieval
```

**Monitoring Script:**

```javascript
// monitor-endpoints.js
const endpoints = [
  { url: 'https://api.store.brainsait.io/health', maxTime: 500 },
  { url: 'https://api.store.brainsait.io/api/products', maxTime: 800 },
  { url: 'https://store.brainsait.io', maxTime: 1000 },
];

async function monitorEndpoints() {
  for (const endpoint of endpoints) {
    const start = Date.now();
    const response = await fetch(endpoint.url);
    const duration = Date.now() - start;
    
    if (response.status !== 200) {
      alert(`${endpoint.url} returned ${response.status}`);
    }
    
    if (duration > endpoint.maxTime) {
      alert(`${endpoint.url} slow response: ${duration}ms`);
    }
  }
}

// Run every 5 minutes
setInterval(monitorEndpoints, 5 * 60 * 1000);
```

#### 2. Database Performance

```bash
# Monitor database connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor slow queries
psql $DATABASE_URL -c "
  SELECT query, calls, mean_exec_time 
  FROM pg_stat_statements 
  WHERE mean_exec_time > 100 
  ORDER BY mean_exec_time DESC 
  LIMIT 10;
"

# Monitor database size
psql $DATABASE_URL -c "
  SELECT pg_size_pretty(pg_database_size('brainsait_store'));
"
```

**Alert Thresholds:**
- Active connections > 80% of pool size
- Query time > 1000ms
- Database size growth > 20% per day

#### 3. Cache Performance

```bash
# Monitor Redis cache hit rate
redis-cli info stats | grep keyspace

# Calculate cache hit ratio
# Target: > 80% hit rate
```

**Cache Metrics:**
```javascript
{
  hits: 8500,
  misses: 1500,
  hitRate: 85.0, // (hits / (hits + misses)) * 100
  evictions: 10,
  memory_used: '245MB',
  memory_peak: '312MB'
}
```

### Business Metrics

#### 1. Payment Processing

**Monitor:**
- Payment success rate (Target: > 99%)
- Payment failures by type
- Average transaction value
- Total revenue

```javascript
// Payment monitoring
const paymentMetrics = {
  total: 1000,
  successful: 990,
  failed: 10,
  successRate: 99.0,
  totalRevenue: 45000.00,
  averageValue: 45.45,
  failures: {
    'card_declined': 5,
    'insufficient_funds': 3,
    'network_error': 2
  }
};
```

**Alert Thresholds:**
- Payment success rate < 95%
- Payment failures spike > 10 in 5 minutes
- Revenue drop > 30% compared to baseline

#### 2. User Engagement

```javascript
// User engagement metrics
const engagement = {
  activeUsers: 2500,
  newRegistrations: 150,
  sessionsPerUser: 3.2,
  avgSessionDuration: '8m 30s',
  bounceRate: 25.5,
  conversionRate: 3.2
};
```

**Key Metrics:**
- Daily Active Users (DAU)
- New user registrations
- Session duration
- Pages per session
- Bounce rate
- Conversion rate

#### 3. E-commerce Metrics

```javascript
// E-commerce KPIs
const ecommerce = {
  cartAdditions: 450,
  cartAbandonmentRate: 68.5,
  checkoutStarted: 142,
  ordersCompleted: 98,
  averageOrderValue: 125.50,
  revenuePerVisitor: 4.25
};
```

## Monitoring Dashboards

### Real-Time Dashboard

Create a dashboard showing:

```
┌─────────────────────────────────────────────────────────────┐
│ BrainSAIT Store - Real-Time Monitoring                      │
├─────────────────────────────────────────────────────────────┤
│ System Health                                               │
│  ✅ Uptime: 99.98%          ✅ Error Rate: 0.05%          │
│  ✅ Response Time (P95): 420ms  🟡 Active Users: 2,345    │
├─────────────────────────────────────────────────────────────┤
│ Traffic                                                      │
│  📊 Requests/min: 1,250     📈 +15% vs baseline           │
│  🌍 Top Countries: SA (45%), AE (22%), US (18%)           │
├─────────────────────────────────────────────────────────────┤
│ Revenue (Today)                                              │
│  💰 Total: $12,450          📦 Orders: 98                  │
│  📈 +8% vs yesterday        ✅ Payment Success: 99.2%      │
├─────────────────────────────────────────────────────────────┤
│ Recent Errors                                                │
│  ⚠️  2 errors in last hour                                  │
│  - API timeout (2x) - Non-critical                          │
└─────────────────────────────────────────────────────────────┘
```

### Weekly Performance Dashboard

```javascript
// Weekly metrics
{
  week: '2025-01-15 to 2025-01-21',
  overview: {
    totalUsers: 18500,
    newUsers: 2340,
    totalOrders: 680,
    revenue: 85600.00,
    uptime: 99.97
  },
  performance: {
    avgResponseTime: 385,
    p95ResponseTime: 520,
    errorRate: 0.08,
    cacheHitRate: 87.5
  },
  topProducts: [
    { name: 'Enterprise Plan', orders: 45, revenue: 35000 },
    { name: 'Professional Plan', orders: 120, revenue: 28000 },
    { name: 'Starter Plan', orders: 180, revenue: 12000 }
  ]
}
```

## Alert Configuration

### Alert Rules

#### Critical Alerts (Immediate Response)

```yaml
alerts:
  - name: "Service Down"
    condition: uptime < 100% for 2 minutes
    severity: critical
    notification: [slack, pagerduty, sms]
    
  - name: "High Error Rate"
    condition: error_rate > 5%
    severity: critical
    notification: [slack, pagerduty, sms]
    
  - name: "Payment Processing Down"
    condition: payment_success_rate < 90%
    severity: critical
    notification: [slack, pagerduty, sms]
    
  - name: "Database Connection Failed"
    condition: db_connection_errors > 0
    severity: critical
    notification: [slack, pagerduty, sms]
```

#### Warning Alerts (Review Within 30 Minutes)

```yaml
  - name: "Elevated Error Rate"
    condition: error_rate > 1%
    severity: warning
    notification: [slack, email]
    
  - name: "Slow Response Time"
    condition: p95_response_time > 1000ms
    severity: warning
    notification: [slack, email]
    
  - name: "High Cache Miss Rate"
    condition: cache_hit_rate < 70%
    severity: warning
    notification: [slack]
    
  - name: "Elevated Traffic"
    condition: requests_per_minute > baseline * 2
    severity: warning
    notification: [slack]
```

#### Info Alerts (Review Daily)

```yaml
  - name: "Revenue Drop"
    condition: daily_revenue < baseline * 0.8
    severity: info
    notification: [email]
    
  - name: "Low Conversion Rate"
    condition: conversion_rate < baseline * 0.9
    severity: info
    notification: [email]
```

### Alert Channels

```javascript
// Notification configuration
const alertChannels = {
  critical: {
    slack: '#incidents',
    pagerduty: 'on-call-team',
    sms: ['+966501234567', '+966507654321'],
    email: ['oncall@brainsait.io']
  },
  warning: {
    slack: '#monitoring',
    email: ['devops@brainsait.io']
  },
  info: {
    email: ['team@brainsait.io']
  }
};
```

## Monitoring Scripts

### Health Check Script

```bash
#!/bin/bash
# health-check.sh - Comprehensive health check

echo "🔍 BrainSAIT Store Health Check"
echo "================================"

# Backend health
echo "🔧 Backend API..."
BACKEND_HEALTH=$(curl -s https://api.store.brainsait.io/health | jq -r '.status')
if [ "$BACKEND_HEALTH" == "healthy" ]; then
  echo "✅ Backend: Healthy"
else
  echo "❌ Backend: Unhealthy"
  exit 1
fi

# Frontend health
echo "🎨 Frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://store.brainsait.io)
if [ "$FRONTEND_STATUS" == "200" ]; then
  echo "✅ Frontend: OK"
else
  echo "❌ Frontend: Error ($FRONTEND_STATUS)"
  exit 1
fi

# Database health
echo "🗄️  Database..."
DB_CHECK=$(psql $DATABASE_URL -c "SELECT 1;" 2>&1)
if [[ $DB_CHECK == *"1 row"* ]]; then
  echo "✅ Database: Connected"
else
  echo "❌ Database: Connection failed"
  exit 1
fi

# Payment gateway check
echo "💳 Payment Gateways..."
STRIPE_CHECK=$(curl -s https://api.stripe.com/v1/charges \
  -u $STRIPE_SECRET_KEY: | jq -r '.object')
if [ "$STRIPE_CHECK" == "list" ]; then
  echo "✅ Stripe: Connected"
else
  echo "⚠️  Stripe: Check connection"
fi

echo "================================"
echo "✅ All systems operational"
```

### Performance Monitoring Script

```bash
#!/bin/bash
# monitor-performance.sh - Track performance metrics

TIMESTAMP=$(date +%s)

# Measure API response time
measure_endpoint() {
  URL=$1
  START=$(date +%s%N)
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" $URL)
  END=$(date +%s%N)
  DURATION=$(( ($END - $START) / 1000000 ))
  
  echo "URL: $URL, Status: $STATUS, Time: ${DURATION}ms"
  
  # Log to monitoring system
  echo "$TIMESTAMP,$URL,$STATUS,$DURATION" >> /var/log/brainsait/performance.log
}

# Monitor critical endpoints
measure_endpoint "https://api.store.brainsait.io/health"
measure_endpoint "https://api.store.brainsait.io/api/products"
measure_endpoint "https://store.brainsait.io"

# Check if any response time > 1000ms
SLOW_REQUESTS=$(awk -F',' '$4 > 1000' /var/log/brainsait/performance.log | wc -l)
if [ $SLOW_REQUESTS -gt 5 ]; then
  echo "⚠️  Warning: $SLOW_REQUESTS slow requests detected"
  # Send alert
fi
```

### Log Analysis Script

```bash
#!/bin/bash
# analyze-logs.sh - Analyze application logs

echo "📊 Log Analysis - Last Hour"
echo "============================"

# Get logs from last hour
wrangler tail --env production --format json > /tmp/logs_1h.json &
TAIL_PID=$!
sleep 3600  # Collect for 1 hour
kill $TAIL_PID

# Analyze errors
ERRORS=$(jq 'select(.outcome == "exception")' /tmp/logs_1h.json | wc -l)
echo "Errors: $ERRORS"

# Top error types
echo -e "\nTop Error Types:"
jq -r 'select(.outcome == "exception") | .exceptions[0].name' /tmp/logs_1h.json | \
  sort | uniq -c | sort -rn | head -5

# Slowest requests
echo -e "\nSlowest Requests:"
jq -r 'select(.scriptDuration > 500) | "\(.scriptDuration)ms - \(.request.url)"' \
  /tmp/logs_1h.json | sort -rn | head -10

# Geographic distribution
echo -e "\nRequests by Country:"
jq -r '.request.cf.country' /tmp/logs_1h.json | \
  sort | uniq -c | sort -rn | head -10
```

## First 24 Hours Monitoring Plan

### Hour-by-Hour Checklist

**Hour 0-1 (Launch)**
- [ ] Monitor deployment completion
- [ ] Verify all health checks passing
- [ ] Check error rates every 5 minutes
- [ ] Test critical user flows manually
- [ ] Monitor payment processing
- [ ] Team on high alert

**Hours 1-4**
- [ ] Check error rates every 15 minutes
- [ ] Monitor response times
- [ ] Review user feedback
- [ ] Verify analytics tracking
- [ ] Check payment success rates
- [ ] Monitor traffic patterns

**Hours 4-12**
- [ ] Check metrics every 30 minutes
- [ ] Review accumulated errors
- [ ] Analyze user behavior
- [ ] Monitor conversion rates
- [ ] Check cache performance
- [ ] Verify backup processes

**Hours 12-24**
- [ ] Check metrics hourly
- [ ] Compile incident report (if any)
- [ ] Review performance trends
- [ ] Plan optimizations
- [ ] Prepare status update
- [ ] Reduce alert frequency

### Success Criteria (First 24 Hours)

✅ **Uptime**: > 99.9%
✅ **Error Rate**: < 0.5%
✅ **Response Time**: P95 < 600ms
✅ **Payment Success**: > 98%
✅ **Zero Critical Incidents**
✅ **User Satisfaction**: No major complaints

## Monitoring Best Practices

1. **Establish Baselines**: First week data sets normal operating ranges
2. **Set Realistic Alerts**: Avoid alert fatigue with too many false positives
3. **Monitor User Impact**: Focus on metrics that affect user experience
4. **Document Everything**: Record all incidents and resolutions
5. **Regular Reviews**: Weekly metric review meetings
6. **Continuous Improvement**: Update monitoring based on learnings
7. **Test Alerts**: Verify alert routing works correctly
8. **Keep Context**: Correlate metrics with deployments and events

## Troubleshooting Common Issues

### High Error Rate

```bash
# 1. Check error logs
wrangler tail --env production --format json | \
  jq 'select(.outcome == "exception")'

# 2. Identify error pattern
# Are errors isolated to specific endpoints?
# Are errors correlated with specific users/regions?

# 3. Check recent deployments
git log --oneline -10

# 4. Consider rollback if errors > 5%
```

### Slow Response Times

```bash
# 1. Profile slow requests
wrangler tail --env production --format json | \
  jq 'select(.scriptDuration > 1000)'

# 2. Check database query times
psql $DATABASE_URL -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# 3. Review cache hit rates
# Low cache hit rate can cause slow responses

# 4. Check for external API timeouts
```

### Payment Failures

```bash
# 1. Check Stripe dashboard
# https://dashboard.stripe.com/logs

# 2. Review payment logs
grep "payment" /var/log/brainsait/app.log | tail -100

# 3. Test payment endpoints
curl -X POST https://api.store.brainsait.io/api/payments/test

# 4. Verify webhook delivery
# Check Stripe webhook logs
```

---

**Document Version**: 1.0.0  
**Last Updated**: January 2025  
**Related Documents**:
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md)
- [Canary Deployment](./CANARY_DEPLOYMENT.md)
