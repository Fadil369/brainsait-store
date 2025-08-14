# BrainSAIT Store - Cloudflare Deployment Guide

This guide provides step-by-step instructions for deploying the BrainSAIT Store to Cloudflare Workers and Pages.

## Prerequisites

- Node.js (v18 or later)
- npm or yarn
- Cloudflare account
- Wrangler CLI: `npm install -g wrangler`

## Configuration Validation

Before deployment, always validate your wrangler.toml configuration:

```bash
# Validate wrangler.toml syntax
node scripts/validate-wrangler.js

# Or use wrangler directly (will show build errors but validates TOML)
npx wrangler deploy --dry-run
```

**Important**: The wrangler.toml file must not have duplicate table definitions. If you see "Can't redefine existing key" errors, merge duplicate `[env.production.vars]` or other table sections into single blocks.

## Architecture Overview

The BrainSAIT Store uses a modern serverless architecture:

- **Frontend**: Next.js static export deployed to Cloudflare Pages
- **Backend**: Hono.js API Gateway deployed to Cloudflare Workers
- **Database**: Cloudflare D1 (SQLite-compatible)
- **Storage**: Cloudflare KV for caching, R2 for file storage
- **Analytics**: Cloudflare Analytics Engine

## Deployment Steps

### 1. Prepare Environment

```bash
# Clone the repository
git clone <repository-url>
cd brainsait-store

# Install frontend dependencies
cd frontend
npm install

# Install backend workers dependencies
cd ../backend/workers
npm install
```

### 2. Configure Wrangler

```bash
# Login to Cloudflare
wrangler login

# Verify authentication
wrangler whoami
```

### 3. Set up Cloudflare Resources

#### Create KV Namespaces
```bash
cd backend/workers
wrangler kv:namespace create "RATE_LIMIT"
wrangler kv:namespace create "RATE_LIMIT" --env production
```

#### Create D1 Database
```bash
wrangler d1 create brainsait-store-db
wrangler d1 create brainsait-store-db-prod
```

#### Create R2 Bucket
```bash
wrangler r2 bucket create brainsait-store-uploads
```

#### Update wrangler.toml
Update the IDs in `backend/workers/wrangler.toml` with the generated resource IDs from the commands above.

### 4. Set Environment Variables and Secrets

#### Frontend Environment Variables
Create `frontend/.env.production`:
```env
NEXT_PUBLIC_API_URL=https://api.store.brainsait.io
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_PAYPAL_CLIENT_ID=...
NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID=merchant.io.brainsait.store
```

#### Backend Secrets
```bash
cd backend/workers

# Set production secrets
wrangler secret put STRIPE_SECRET_KEY --env production
# Enter: sk_live_51NU4x3HNiG2Z9ziC...

wrangler secret put PAYPAL_SECRET --env production  
# Enter: ARux8wrYw6CXD_A88cgV_aVYHjXG1fFNCnyXmIX2T6_BNKUTwr12lbisklroHjs67nNJLzHHpCcuRPzp

wrangler secret put DATABASE_URL --env production
# Enter: your D1 database connection string

wrangler secret put SECRET_KEY --env production
# Enter: a strong random secret for JWT signing

wrangler secret put APP_STORE_SHARED_SECRET --env production
# Enter: 59b266ddcfed4db4ae2bf3bcc72909d6

# Set staging secrets (optional)
wrangler secret put STRIPE_SECRET_KEY --env staging
# ... repeat for other secrets

# List all secrets to verify
wrangler secret list --env production
```

**Note**: Secrets are encrypted and stored securely in Cloudflare. Use `wrangler secret delete <KEY>` to remove secrets if needed.

### 5. Deploy Frontend to Cloudflare Pages

#### Option A: Using Wrangler CLI
```bash
cd frontend

# Build the application
npm run build

# Deploy to Pages
wrangler pages deploy out --project-name brainsait-store-frontend --compatibility-date=2024-01-15
```

#### Option B: Using Cloudflare Dashboard
1. Go to Cloudflare Dashboard > Pages
2. Create a new project: "brainsait-store-frontend"
3. Upload the `frontend/out` directory
4. Configure build settings:
   - Build command: `npm run build`
   - Build output directory: `out`
   - Node.js version: 18

### 6. Deploy Backend to Cloudflare Workers

```bash
cd backend/workers

# Deploy to staging
wrangler deploy --env staging

# Test staging deployment
curl https://staging-api.store.brainsait.io/health

# Deploy to production
wrangler deploy --env production

# Test production deployment
curl https://api.store.brainsait.io/health
```

### 7. Configure Custom Domains

#### Pages Domain
1. Go to Cloudflare Dashboard > Pages > brainsait-store-frontend
2. Click "Custom domains"
3. Add domain: `store.brainsait.io`
4. Configure DNS record in your domain's zone

#### Workers Domain
1. Go to Cloudflare Dashboard > Workers & Pages > brainsait-store-api-prod
2. Click "Settings" > "Triggers"
3. Add custom domain: `api.store.brainsait.io`
4. Configure DNS record in your domain's zone

### 8. Automated Deployment Script

Use the provided deployment script for streamlined deployment:

```bash
# Make the script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Follow the interactive prompts to choose what to deploy
```

## Deployment Verification

After deployment, verify the following:

### Frontend Checks
- [ ] Site loads at https://store.brainsait.io
- [ ] Apple Pay domain verification works: https://store.brainsait.io/.well-known/apple-developer-merchantid-domain-association.txt
- [ ] Multi-language support (English/Arabic)
- [ ] Responsive design on mobile/desktop

### Backend Checks
- [ ] API health check: https://api.store.brainsait.io/health
- [ ] Rate limiting works
- [ ] CORS headers configured correctly
- [ ] Analytics data collection

### Integration Checks
- [ ] Stripe payment integration
- [ ] PayPal payment integration
- [ ] Apple Pay functionality
- [ ] MADA payment support (Saudi Arabia)

## Monitoring and Maintenance

### Cloudflare Analytics
- Monitor traffic and performance in Cloudflare Dashboard
- Set up alerts for downtime or high error rates
- Review analytics data regularly

### Logs and Debugging
```bash
# View Workers logs
wrangler tail --env production

# View Pages deployment logs
wrangler pages deployment list
```

### Updates and Rollbacks
```bash
# Deploy new version
wrangler deploy --env production

# Rollback if needed
wrangler rollback --env production
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **HTTPS Only**: All production traffic should use HTTPS
3. **Rate Limiting**: Configured via KV storage
4. **CORS**: Properly configured for your domains only
5. **Content Security Policy**: Implemented in Next.js headers

## Troubleshooting

### Common Issues

#### Build Failures
- Ensure all dependencies are installed
- Check Node.js version compatibility
- Verify environment variables are set

#### wrangler.toml Parse Errors
- **"Can't redefine existing key"**: This means you have duplicate table definitions in wrangler.toml
  - Solution: Merge duplicate `[env.production.vars]` or other table sections
  - Run `node scripts/validate-wrangler.js` to validate the fix
- **Invalid TOML syntax**: Check for missing quotes, brackets, or commas
  - Use an online TOML validator if needed
  - Ensure arrays-of-tables use `[[...]]` format for bindings

#### Runtime Errors
- Check Workers logs: `wrangler tail`
- Verify environment variables and secrets
- Test API endpoints individually

### Getting Help

- Cloudflare Workers Documentation: https://developers.cloudflare.com/workers/
- Cloudflare Pages Documentation: https://developers.cloudflare.com/pages/
- BrainSAIT Support: support@brainsait.com

## Cost Optimization

- **Workers**: Free tier includes 100,000 requests/day
- **Pages**: Free tier includes 500 builds/month
- **KV**: Free tier includes 100,000 reads/day
- **D1**: Free tier includes 100,000 reads/day
- **R2**: Pay-as-you-go for storage and operations

Monitor usage in Cloudflare Dashboard and upgrade plans as needed.