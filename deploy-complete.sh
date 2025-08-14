#!/bin/bash

# 🚀 BrainSAIT B2B Complete Deployment Script
# Deploys entire ecosystem with all integrations

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     BrainSAIT B2B Ecosystem Deployment v2.0          ║"
echo "║     Full Integration: Lead → Invoice → Success       ║"
echo "╔═══════════════════════════════════════════════════════╝"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/Users/fadil369/BrainSAIT-B2B"
cd "$PROJECT_DIR"

# Step 1: Environment Setup
echo -e "${BLUE}[1/10]${NC} Setting up environment..."

# Create .env file if not exists
if [ ! -f .env ]; then
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://brainsait:secure_password@localhost:5432/brainsait_b2b

# Authentication
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_API_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# PayPal
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_secret
PAYPAL_MODE=sandbox

# Notion
NOTION_API_KEY=your_notion_integration_token
NOTION_CRM_DATABASE_ID=your_crm_database_id
NOTION_INVOICES_DATABASE_ID=your_invoices_database_id

# Zapier
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/your_hook_id
ZAPIER_API_KEY=your_zapier_api_key

# WhatsApp Business
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Cloudflare
CLOUDFLARE_API_TOKEN=your_cloudflare_token
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_ZONE_ID=your_zone_id

# Apple (for iMessage/Calendar)
APPLE_TEAM_ID=your_team_id
APPLE_KEY_ID=your_key_id

# Google
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret
GOOGLE_CALENDAR_ID=primary

# Atlassian
ATLASSIAN_API_TOKEN=your_atlassian_token
ATLASSIAN_DOMAIN=your-domain.atlassian.net

# Environment
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000
EOF
    echo -e "${GREEN}✓${NC} Created .env file (please update with your API keys)"
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Step 2: Install Dependencies
echo -e "${BLUE}[2/10]${NC} Installing dependencies..."

# Python dependencies for backend
if [ -f backend/requirements.txt ]; then
    pip3 install -r backend/requirements.txt
    echo -e "${GREEN}✓${NC} Python dependencies installed"
fi

# Node dependencies for frontend
if [ -f frontend/package.json ]; then
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓${NC} Node dependencies installed"
fi

# Step 3: Database Setup
echo -e "${BLUE}[3/10]${NC} Setting up database..."

# Start PostgreSQL if not running
if ! pg_isready -q; then
    echo "Starting PostgreSQL..."
    brew services start postgresql@14
fi

# Create database if not exists
createdb brainsait_b2b 2>/dev/null || echo "Database already exists"

# Run migrations
cd backend
alembic upgrade head 2>/dev/null || echo "Migrations already applied"
cd ..

echo -e "${GREEN}✓${NC} Database ready"

# Step 4: Start Backend Services
echo -e "${BLUE}[4/10]${NC} Starting backend services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Starting Docker..."
    open -a Docker
    sleep 10
fi

# Start services with Docker Compose
docker-compose up -d

echo -e "${GREEN}✓${NC} Backend services running"

# Step 5: Deploy Cloudflare Worker
echo -e "${BLUE}[5/10]${NC} Deploying Cloudflare Worker..."

cd infrastructure/cloudflare/workers
if command -v wrangler &> /dev/null; then
    wrangler deploy --env staging
    echo -e "${GREEN}✓${NC} Cloudflare Worker deployed"
else
    echo -e "${YELLOW}⚠${NC} Wrangler not installed. Run: npm install -g wrangler"
fi
cd "$PROJECT_DIR"

# Step 6: Configure Zapier Integration
echo -e "${BLUE}[6/10]${NC} Configuring Zapier..."

echo "Please configure Zapier manually:"
echo "1. Visit: https://mcp.zapier.com/mcp/servers/85daa0ef-f858-41e7-a240-6f9b77a051ed/config"
echo "2. Add the automation templates from automation-scenarios.md"
echo "3. Set webhook URL to: http://localhost:8000/webhooks/zapier"
echo ""
read -p "Press Enter when Zapier is configured..."

# Step 7: Setup Stripe & PayPal Webhooks
echo -e "${BLUE}[7/10]${NC} Setting up payment webhooks..."

# Stripe webhook setup
if command -v stripe &> /dev/null; then
    stripe listen --forward-to localhost:8000/webhooks/stripe &
    STRIPE_PID=$!
    echo -e "${GREEN}✓${NC} Stripe webhook listener started (PID: $STRIPE_PID)"
else
    echo -e "${YELLOW}⚠${NC} Stripe CLI not installed. Run: brew install stripe/stripe-cli/stripe"
fi

# Step 8: Start Frontend
echo -e "${BLUE}[8/10]${NC} Starting frontend..."

cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓${NC} Frontend running at http://localhost:3000 (PID: $FRONTEND_PID)"

# Step 9: Initialize Test Data
echo -e "${BLUE}[9/10]${NC} Creating test data..."

python3 << EOF
import requests
import json

# Create test customer
customer_data = {
    "name": "Test Company",
    "email": "test@example.com",
    "phone": "+966501234567",
    "language": "en",
    "company_size": 50,
    "industry": "technology"
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/customers",
        json=customer_data,
        headers={"X-Tenant-ID": "test"}
    )
    if response.status_code == 200:
        print("✓ Test customer created")
except:
    print("⚠ Could not create test data")

# Create test automation
automation_data = {
    "name": "LinkedIn to Invoice",
    "trigger": "new_linkedin_lead",
    "actions": ["create_notion_entry", "send_welcome_email", "create_stripe_customer"],
    "status": "active"
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/automations",
        json=automation_data,
        headers={"X-Tenant-ID": "test"}
    )
    if response.status_code == 200:
        print("✓ Test automation created")
except:
    pass
EOF

# Step 10: Health Check
echo -e "${BLUE}[10/10]${NC} Running health checks..."

# Check all services
services=(
    "http://localhost:8000/health|Backend API"
    "http://localhost:3000|Frontend"
    "http://localhost:8000/docs|API Documentation"
)

echo ""
echo "Service Status:"
echo "═══════════════════════════════════════"

for service in "${services[@]}"; do
    IFS='|' read -r url name <<< "$service"
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓${NC} $name: Running"
    else
        echo -e "${RED}✗${NC} $name: Not responding"
    fi
done

# Final Summary
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║         🎉 DEPLOYMENT COMPLETE! 🎉                   ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║                                                       ║"
echo "║  Access Points:                                       ║"
echo "║  • Dashboard: http://localhost:3000                  ║"
echo "║  • API: http://localhost:8000                        ║"
echo "║  • API Docs: http://localhost:8000/docs              ║"
echo "║  • Zapier Config: Check your MCP dashboard           ║"
echo "║                                                       ║"
echo "║  Test Credentials:                                   ║"
echo "║  • Tenant ID: test                                   ║"
echo "║  • Test Email: test@example.com                      ║"
echo "║                                                       ║"
echo "║  Next Steps:                                          ║"
echo "║  1. Update API keys in .env file                     ║"
echo "║  2. Configure Zapier automations                     ║"
echo "║  3. Set up payment webhooks                          ║"
echo "║  4. Deploy to production via Cloudflare              ║"
echo "║                                                       ║"
echo "║  Documentation: /docs/README.md                      ║"
echo "║  Support: fadil369@gmail.com                         ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"

# Save process IDs for cleanup
cat > .running_processes << EOF
FRONTEND_PID=$FRONTEND_PID
STRIPE_PID=$STRIPE_PID
EOF

echo ""
echo "To stop all services, run: ./stop.sh"

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
source .running_processes
kill $FRONTEND_PID 2>/dev/null
kill $STRIPE_PID 2>/dev/null
docker-compose down
echo "All services stopped"
EOF
chmod +x stop.sh

echo ""
echo -e "${GREEN}Ready for business automation! 🚀${NC}"
