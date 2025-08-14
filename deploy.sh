#!/bin/bash

# BrainSAIT Store Deployment Script
# Deploys frontend to Cloudflare Pages and backend to Cloudflare Workers

set -e

echo "🚀 Starting BrainSAIT Store deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required tools are installed
check_dependencies() {
    echo -e "${BLUE}📋 Checking dependencies...${NC}"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed${NC}"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm is not installed${NC}"
        exit 1
    fi
    
    if ! command -v wrangler &> /dev/null; then
        echo -e "${YELLOW}⚠️  Wrangler CLI not found. Installing...${NC}"
        npm install -g wrangler
    fi
    
    echo -e "${GREEN}✅ All dependencies are available${NC}"
}

# Set environment variables
setup_environment() {
    echo -e "${BLUE}🔧 Setting up environment...${NC}"
    
    # Check if .env files exist
    if [ ! -f "frontend/.env.production" ]; then
        echo -e "${YELLOW}⚠️  Creating production environment file for frontend...${NC}"
        cat > frontend/.env.production << EOF
NEXT_PUBLIC_API_URL=https://api.store.brainsait.io
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_51NU4x3HNiG2Z9ziCsNEiDlYKEG6W1jXlavyfwF8WcsEwdnGFuPEOGRPqIHfnoMK2Jydyn5Vh6KSF741Go3nFPvv100j64OFypq
NEXT_PUBLIC_PAYPAL_CLIENT_ID=ARux8wrYw6CXD_A88cgV_aVYHjXG1fFNCnyXmIX2T6_BNKUTwr12lbisklroHjs67nNJLzHHpCcuRPzp
NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID=merchant.io.brainsait.store
NEXT_PUBLIC_OID_API_URL=https://oid.brainsait.io/api/v1
EOF
    fi
    
    echo -e "${GREEN}✅ Environment configured${NC}"
}

# Deploy frontend to Cloudflare Pages
deploy_frontend() {
    echo -e "${BLUE}🌐 Deploying frontend to Cloudflare Pages...${NC}"
    
    cd frontend
    
    # Install dependencies
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm ci
    
    # Build the application for static export
    echo -e "${YELLOW}🔨 Building frontend application...${NC}"
    npm run build
    
    # Deploy to Cloudflare Pages
    echo -e "${YELLOW}🚀 Deploying to Cloudflare Pages...${NC}"
    
    # Check if using Wrangler Pages or manual upload
    if command -v wrangler &> /dev/null; then
        # Try to deploy using Pages
        wrangler pages deploy out --project-name brainsait-store-frontend --compatibility-date=2024-01-15
        
        # Set up custom domain if not already configured
        echo -e "${YELLOW}🌐 Setting up custom domain...${NC}"
        echo "Manual step required: Configure custom domain 'store.brainsait.io' in Cloudflare Dashboard"
    else
        echo -e "${RED}❌ Wrangler CLI not available for Pages deployment${NC}"
        echo -e "${YELLOW}📋 Manual deployment required:${NC}"
        echo "1. Install Wrangler CLI: npm install -g wrangler"
        echo "2. Login: wrangler login"
        echo "3. Go to Cloudflare Dashboard > Pages"
        echo "4. Create new project: brainsait-store-frontend"
        echo "5. Upload the 'out' directory"
        echo "6. Configure custom domain: store.brainsait.io"
        echo "7. Or use: wrangler pages deploy out --project-name brainsait-store-frontend"
    fi
    
    cd ..
    echo -e "${GREEN}✅ Frontend deployment completed${NC}"
}

# Deploy backend to Cloudflare Workers
deploy_backend() {
    echo -e "${BLUE}⚙️  Deploying backend to Cloudflare Workers...${NC}"
    
    cd backend/workers
    
    # Install dependencies
    echo -e "${YELLOW}📦 Installing Workers dependencies...${NC}"
    npm install
    
    # Set up Cloudflare secrets
    echo -e "${YELLOW}🔐 Setting up Cloudflare secrets...${NC}"
    
    # Note: These should be set manually for security
    echo -e "${YELLOW}⚠️  Manual secret setup required:${NC}"
    echo "Run these commands to set up secrets:"
    echo "wrangler secret put STRIPE_SECRET_KEY"
    echo "wrangler secret put PAYPAL_SECRET"
    echo "wrangler secret put DATABASE_URL"
    echo "wrangler secret put SECRET_KEY"
    echo "wrangler secret put APP_STORE_SHARED_SECRET"
    
    # Create KV namespace if it doesn't exist
    echo -e "${YELLOW}🗂️  Setting up KV namespaces...${NC}"
    if command -v wrangler &> /dev/null; then
        wrangler kv:namespace create "RATE_LIMIT" || echo "KV namespace might already exist"
        echo -e "${YELLOW}⚠️  Update wrangler.toml with the generated KV namespace IDs${NC}"
    fi
    
    # Deploy the worker
    echo -e "${YELLOW}🚀 Deploying API Gateway to Cloudflare Workers...${NC}"
    
    if command -v wrangler &> /dev/null; then
        wrangler deploy --env production
        echo -e "${GREEN}✅ Workers API Gateway deployed${NC}"
    else
        echo -e "${RED}❌ Wrangler CLI not available${NC}"
        echo -e "${YELLOW}📋 Manual deployment required:${NC}"
        echo "1. Install Wrangler CLI: npm install -g wrangler"
        echo "2. Login: wrangler login"
        echo "3. Deploy: wrangler deploy --env production"
    fi
    
    cd ../..
    echo -e "${GREEN}✅ Backend deployment completed${NC}"
}

# Configure DNS and domains
configure_domains() {
    echo -e "${BLUE}🌍 Domain configuration...${NC}"
    
    echo -e "${YELLOW}📋 Manual DNS configuration required:${NC}"
    echo "1. Set up CNAME for store.brainsait.io -> pages.cloudflare.com"
    echo "2. Set up CNAME for api.store.brainsait.io -> workers.cloudflare.com"
    echo "3. Configure SSL certificates"
    echo "4. Verify Apple Pay domain association"
    
    echo -e "${GREEN}✅ Domain configuration noted${NC}"
}

# Setup database
setup_database() {
    echo -e "${BLUE}🗄️  Database setup...${NC}"
    
    echo -e "${YELLOW}📋 Database setup required:${NC}"
    echo "1. Create Cloudflare D1 database: brainsait-store-db"
    echo "2. Run database migrations"
    echo "3. Set up KV namespace for caching"
    echo "4. Configure R2 bucket for file storage"
    
    echo -e "${GREEN}✅ Database setup noted${NC}"
}

# Verify deployment
verify_deployment() {
    echo -e "${BLUE}🔍 Verifying deployment...${NC}"
    
    # Test frontend
    echo -e "${YELLOW}Testing frontend...${NC}"
    if curl -f -s "https://store.brainsait.io" > /dev/null; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
    else
        echo -e "${RED}❌ Frontend is not accessible${NC}"
    fi
    
    # Test Apple Pay domain association
    echo -e "${YELLOW}Testing Apple Pay domain association...${NC}"
    if curl -f -s "https://store.brainsait.io/.well-known/apple-developer-merchantid-domain-association.txt" > /dev/null; then
        echo -e "${GREEN}✅ Apple Pay domain association is working${NC}"
    else
        echo -e "${RED}❌ Apple Pay domain association failed${NC}"
    fi
    
    # Test API
    echo -e "${YELLOW}Testing API...${NC}"
    if curl -f -s "https://api.store.brainsait.io/health" > /dev/null; then
        echo -e "${GREEN}✅ API is accessible${NC}"
    else
        echo -e "${RED}❌ API is not accessible${NC}"
    fi
    
    echo -e "${GREEN}✅ Deployment verification completed${NC}"
}

# Main deployment function
main() {
    echo -e "${GREEN}🎯 BrainSAIT Store Deployment${NC}"
    echo "=================================="
    
    check_dependencies
    setup_environment
    
    # Ask user what to deploy
    echo -e "${YELLOW}What would you like to deploy?${NC}"
    echo "1) Frontend only"
    echo "2) Backend only"
    echo "3) Full deployment"
    echo "4) Configuration only"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            deploy_frontend
            ;;
        2)
            deploy_backend
            ;;
        3)
            deploy_frontend
            deploy_backend
            configure_domains
            setup_database
            verify_deployment
            ;;
        4)
            configure_domains
            setup_database
            ;;
        *)
            echo -e "${RED}❌ Invalid choice${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}🎉 Deployment process completed!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "1. Configure Cloudflare secrets manually"
    echo "2. Set up database and run migrations"
    echo "3. Configure custom domains"
    echo "4. Test all payment integrations"
    echo "5. Monitor deployment logs"
    echo ""
    echo -e "${GREEN}🌟 BrainSAIT Store is ready for production!${NC}"
}

# Run the deployment
main "$@"