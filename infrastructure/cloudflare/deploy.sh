#!/bin/bash

# BrainSAIT Cloudflare Worker Deployment Script
# Deploys API Gateway with multi-tenant routing and Zapier integration

echo "🚀 Deploying BrainSAIT Cloudflare Worker..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "Installing Wrangler CLI..."
    npm install -g wrangler
fi

cd /Users/fadil369/BrainSAIT-B2B/infrastructure/cloudflare/workers || exit 1
echo "Using existing wrangler.toml and src/index.js"

# Login to Cloudflare
echo "Logging into Cloudflare..."
wrangler login

# Create KV namespace
echo "Creating KV namespace..."
# Create KV namespace if not exists (id should be updated in wrangler.toml)
wrangler kv:namespace create "RATE_LIMIT" || true

# Create R2 bucket
echo "Creating R2 bucket..."
wrangler r2 bucket create brainsait-documents || true

# Deploy to staging
echo "Deploying to staging..."
wrangler deploy --env staging

# Test the deployment
echo "Testing deployment..."
curl https://staging-api.brainsait.com/

echo "✅ Staging deployment complete!"
echo ""
echo "To deploy to production:"
echo "wrangler deploy --env production"
echo ""
echo "Dashboard: https://dash.cloudflare.com"
