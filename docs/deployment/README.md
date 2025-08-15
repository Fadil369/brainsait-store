# Deployment Guide - BrainSAIT Store

## Overview

This guide covers deployment strategies for the BrainSAIT Store platform across different environments, from development to production.

## Deployment Architecture

### Production Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Cloudflare     │    │  Cloudflare     │    │  External       │
│  Pages          │◄──►│  Workers        │◄──►│  Services       │
│  (Frontend)     │    │  (API Gateway)  │    │  (Database/Redis)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Next.js        │    │  FastAPI        │    │  Docker         │
│  Dev Server     │◄──►│  Dev Server     │◄──►│  Containers     │
│  (localhost:3000)│    │  (localhost:8000)│    │  (DB/Redis)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### Required Tools
- **Node.js**: 18.0.0 or higher
- **Python**: 3.11 or higher
- **Cloudflare CLI (Wrangler)**: Latest version
- **Git**: Latest version
- **Docker**: (Optional) For local database

### Required Accounts
- **Cloudflare Account**: With Workers and Pages enabled
- **GitHub Account**: For CI/CD
- **Domain**: Custom domain (optional)

### Environment Setup
```bash
# Install Cloudflare Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Verify authentication
wrangler whoami
```

## Development Deployment

### Local Development Setup

#### 1. Backend Development Server
```bash
cd backend

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your local configuration

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Development Server
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

#### 3. Database Setup (Docker)
```bash
# Create docker-compose.yml
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: brainsait_store
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
EOF

# Start services
docker-compose -f docker-compose.dev.yml up -d
```

### Development Environment Variables

#### Backend (.env)
```bash
# Application
APP_NAME="BrainSAIT Store API"
ENVIRONMENT="development"
DEBUG=true

# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/brainsait_store"
REDIS_URL="redis://localhost:6379"

# Security
SECRET_KEY="dev-secret-key-change-in-production"
ALGORITHM="HS256"

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

#### Frontend (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000"
NEXT_PUBLIC_ENVIRONMENT="development"

# Payment Configuration (Test Keys)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
NEXT_PUBLIC_PAYPAL_CLIENT_ID="test-paypal-client-id"

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_PAYMENTS=true
```

## Staging Deployment

### Cloudflare Workers (Backend)

#### 1. Configure wrangler.toml
```toml
name = "brainsait-store-staging"
main = "src/index.js"
compatibility_date = "2024-01-01"

[env.staging]
name = "brainsait-store-staging"
vars = {
  ENVIRONMENT = "staging"
}

[[env.staging.kv_namespaces]]
binding = "RATE_LIMIT_KV"
id = "your-kv-namespace-id"

[env.staging.vars]
APP_NAME = "BrainSAIT Store API"
API_VERSION = "1.0.0"
```

#### 2. Deploy Backend Worker
```bash
cd infrastructure/cloudflare/workers

# Deploy to staging
wrangler deploy --env staging

# Set secrets
wrangler secret put DATABASE_URL --env staging
wrangler secret put REDIS_URL --env staging
wrangler secret put SECRET_KEY --env staging
```

### Cloudflare Pages (Frontend)

#### 1. Configure build settings
```bash
# Build command
npm run build

# Build output directory
out

# Root directory
frontend
```

#### 2. Environment Variables
```bash
# Production API URL
NEXT_PUBLIC_API_URL="https://brainsait-store-staging.fadil.workers.dev"

# Staging payment keys
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
NEXT_PUBLIC_PAYPAL_CLIENT_ID="staging-paypal-client-id"
```

#### 3. Deploy Frontend
```bash
cd frontend

# Build for production
npm run build

# Deploy to Cloudflare Pages (via Git integration)
# Or manual deployment:
wrangler pages deploy out --project-name brainsait-store-staging
```

## Production Deployment

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Database backups configured
- [ ] Monitoring and alerting configured
- [ ] SSL certificates configured
- [ ] DNS records configured

### Production Configuration

#### Backend Production Secrets
```bash
# Set production secrets
wrangler secret put DATABASE_URL --env production
wrangler secret put REDIS_URL --env production
wrangler secret put SECRET_KEY --env production
wrangler secret put STRIPE_SECRET_KEY --env production
wrangler secret put PAYPAL_SECRET --env production
```

#### Frontend Production Environment
```bash
# Production API URL
NEXT_PUBLIC_API_URL="https://brainsait-api-gateway.fadil.workers.dev"

# Live payment keys
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_live_..."
NEXT_PUBLIC_PAYPAL_CLIENT_ID="live-paypal-client-id"

# Analytics
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID="GA_MEASUREMENT_ID"
NEXT_PUBLIC_SENTRY_DSN="sentry-dsn"
```

### Production Deployment Steps

#### 1. Database Migration
```bash
# Run database migrations
alembic upgrade head

# Verify migration
alembic current
```

#### 2. Backend Deployment
```bash
# Deploy backend worker
wrangler deploy --env production

# Verify deployment
curl https://brainsait-api-gateway.fadil.workers.dev/health
```

#### 3. Frontend Deployment
```bash
# Build production frontend
npm run build

# Deploy to production
wrangler pages deploy out --project-name brainsait-store
```

#### 4. DNS Configuration
```bash
# Add custom domain (if applicable)
wrangler pages domain add store.brainsait.io
```

### Health Checks

#### Backend Health Check
```bash
# Check API health
curl -X GET https://brainsait-api-gateway.fadil.workers.dev/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "gateway": "operational",
    "backend": "operational",
    "kv_storage": "operational"
  }
}
```

#### Frontend Health Check
```bash
# Check frontend availability
curl -I https://store.brainsait.io

# Expected response: 200 OK
```

## CI/CD Pipeline

### GitHub Actions Workflow

#### Frontend Deployment (.github/workflows/deploy-frontend.yml)
```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
          NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: ${{ secrets.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY }}
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: brainsait-store
          directory: frontend/out
```

#### Backend Deployment (.github/workflows/deploy-backend.yml)
```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths: ['backend/**', 'infrastructure/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest
      
      - name: Deploy to Cloudflare Workers
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          workingDirectory: infrastructure/cloudflare/workers
          command: deploy --env production
```

### Automated Testing

#### Frontend Tests
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Accessibility tests
npm run test:a11y
```

#### Backend Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/
```

## Monitoring and Logging

### Cloudflare Analytics
- **Web Analytics**: Page views, performance metrics
- **Worker Analytics**: Request count, error rates, duration
- **Security Analytics**: Attack patterns, bot traffic

### Application Monitoring

#### Sentry Integration
```javascript
// Frontend error tracking
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```

```python
# Backend error tracking
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    environment=settings.ENVIRONMENT,
)
```

#### Custom Metrics
```javascript
// Worker analytics
export default {
  async fetch(request, env, ctx) {
    const start = Date.now();
    
    try {
      const response = await handleRequest(request);
      
      // Log successful request
      console.log({
        method: request.method,
        url: request.url,
        status: response.status,
        duration: Date.now() - start
      });
      
      return response;
    } catch (error) {
      // Log error
      console.error({
        method: request.method,
        url: request.url,
        error: error.message,
        duration: Date.now() - start
      });
      
      throw error;
    }
  }
};
```

## Security Considerations

### SSL/TLS Configuration
- **Cloudflare SSL**: Full (strict) encryption mode
- **HSTS**: HTTP Strict Transport Security enabled
- **Certificate Transparency**: Monitoring enabled

### Access Control
```bash
# Restrict admin access by IP
wrangler pages deployment list
wrangler pages deployment tail
```

### Secret Management
```bash
# Rotate secrets regularly
wrangler secret put SECRET_KEY --env production
wrangler secret list --env production
```

## Backup and Recovery

### Database Backups
```bash
# Automated daily backups
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Point-in-time recovery setup
# Configure continuous archiving
```

### Application Backups
```bash
# Configuration backup
git archive --format=tar.gz HEAD > config_backup.tar.gz

# Worker deployment backup
wrangler download
```

## Rollback Procedures

### Frontend Rollback
```bash
# List previous deployments
wrangler pages deployment list --project-name brainsait-store

# Promote previous deployment
wrangler pages deployment promote <deployment-id>
```

### Backend Rollback
```bash
# Deploy previous version
git checkout <previous-commit>
wrangler deploy --env production

# Or use versioned deployment
wrangler rollback --env production
```

## Performance Optimization

### Frontend Optimization
- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **CDN Caching**: Cloudflare edge caching
- **Bundle Analysis**: webpack-bundle-analyzer

### Backend Optimization
- **Response Caching**: Redis caching layer
- **Database Optimization**: Connection pooling, query optimization
- **Worker Optimization**: Minimize cold starts

## Troubleshooting

### Common Issues

#### Deployment Failures
```bash
# Check deployment logs
wrangler tail --env production

# Validate configuration
wrangler dev --env production --local
```

#### Performance Issues
```bash
# Monitor resource usage
wrangler analytics --env production

# Check error rates
wrangler tail --format pretty
```

#### Database Connection Issues
```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check connection pool status
# Monitor database logs
```

## Next Steps

- [Monitoring Guide](./monitoring.md)
- [Security Guide](./security.md)
- [Scaling Guide](./scaling.md)
- [API Documentation](../api/README.md)