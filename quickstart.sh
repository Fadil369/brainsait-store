#!/bin/bash

# BrainSAIT B2B Quick Start Script
# One-command deployment with Zapier integration

set -e

echo "🚀 BrainSAIT B2B Platform - Quick Start"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Create environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cat > .env << 'EOF'
# BrainSAIT B2B Environment
ENVIRONMENT=development

# Database
DB_PASSWORD=BrainSAIT2024!
REDIS_PASSWORD=Redis2024!

# Security
SECRET_KEY=$(openssl rand -hex 32 || echo "dev-secret-key-change-in-production")
JWT_SECRET=$(openssl rand -hex 32 || echo "dev-jwt-secret-change-in-production")

# Zapier Integration
ZAPIER_APP_KEY=brainsait_app_key
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/

# Payment Gateways
STRIPE_SECRET_KEY=sk_test_51234567890
STRIPE_PUBLISHABLE_KEY=pk_test_51234567890
MADA_MERCHANT_ID=MADA_TEST_MERCHANT
MADA_API_KEY=mada_test_key

# Cloudflare
CLOUDFLARE_ACCOUNT_ID=519d80ce438f427d096a3e3bdd98a7e0
CLOUDFLARE_API_TOKEN=your_token_here

# Default Admin
ADMIN_EMAIL=admin@brainsait.com
ADMIN_PASSWORD=Admin2024!
EOF
    echo "✅ Environment file created"
else
    echo "✅ Environment file exists"
fi

# Pull required Docker images
echo "📦 Pulling Docker images..."
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull nginx:alpine

# Start core services only
echo "🔧 Starting core services..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for database..."
sleep 5

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec -T postgres psql -U brainsait -d brainsait_b2b << 'SQL'
-- Create schemas for multi-tenancy
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS tenant_demo;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tenants table
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'starter',
    zapier_webhook_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create demo tenant
INSERT INTO public.tenants (name, subdomain, plan)
VALUES ('Demo Company', 'demo', 'starter')
ON CONFLICT (subdomain) DO NOTHING;

-- Create API keys table
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id),
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

GRANT ALL PRIVILEGES ON SCHEMA public TO brainsait;
GRANT ALL PRIVILEGES ON SCHEMA tenant_demo TO brainsait;
SQL

echo "✅ Database initialized"

# Create quick API test
echo "🧪 Creating API test endpoint..."
mkdir -p test-api
cat > test-api/server.js << 'EOF'
const express = require('express');
const app = express();
app.use(express.json());

// CORS for Zapier
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'BrainSAIT B2B API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      zapier_webhook: '/webhooks/zapier',
      test_trigger: '/trigger/test'
    }
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date() });
});

// Zapier webhook receiver
app.post('/webhooks/zapier', (req, res) => {
  console.log('Zapier webhook received:', req.body);
  res.json({ 
    status: 'received', 
    data: req.body,
    message: 'Webhook processed successfully'
  });
});

// Test trigger for Zapier
app.post('/trigger/test', (req, res) => {
  const testData = {
    id: 'test_' + Date.now(),
    type: 'test_event',
    data: {
      customer: 'أحمد محمد',
      amount: 2999,
      currency: 'SAR',
      timestamp: new Date()
    }
  };
  console.log('Triggering test event:', testData);
  res.json(testData);
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`🚀 BrainSAIT API running on http://localhost:${PORT}`);
});
EOF

# Check if Node.js is available and start test server
if command -v node > /dev/null 2>&1; then
    cd test-api
    npm init -y > /dev/null 2>&1
    npm install express > /dev/null 2>&1
    node server.js &
    TEST_SERVER_PID=$!
    cd ..
    echo "✅ Test API server started (PID: $TEST_SERVER_PID)"
else
    echo "⚠️  Node.js not found - skipping test API server"
fi

echo ""
echo "=========================================="
echo "✅ BrainSAIT B2B Platform Ready!"
echo "=========================================="
echo ""
echo "🔗 Access Points:"
echo "  • API Test: http://localhost:8000"
echo "  • Database: postgresql://localhost:5432/brainsait_b2b"
echo "  • Redis: redis://localhost:6379"
echo ""
echo "🔌 Zapier Integration:"
echo "  1. Go to: https://zapier.com/app/editor"
echo "  2. Create new Zap with Webhooks by Zapier"
echo "  3. Use webhook URL: http://localhost:8000/webhooks/zapier"
echo "  4. Test with: curl -X POST http://localhost:8000/trigger/test"
echo ""
echo "📚 Next Steps:"
echo "  1. Configure your Zapier account"
echo "  2. Set up webhook automations"
echo "  3. Connect payment gateways"
echo "  4. Deploy to production"
echo ""
echo "💡 Quick Commands:"
echo "  • Stop services: docker-compose down"
echo "  • View logs: docker-compose logs -f"
echo "  • Reset all: docker-compose down -v"
echo ""
echo "📧 Support: support@brainsait.com"
echo "📅 Book Demo: https://calendly.com/fadil369"
echo ""
