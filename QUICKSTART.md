# SSDP Platform - Quick Start Guide

Get up and running with the SSDP platform in under 10 minutes!

## Prerequisites

Before you begin, ensure you have:

- ✅ **Node.js** 18 or higher ([Download](https://nodejs.org/))
- ✅ **npm** 9 or higher (comes with Node.js)
- ✅ **Docker** & **Docker Compose** ([Download](https://www.docker.com/))
- ✅ **Git** ([Download](https://git-scm.com/))

### Optional (for specific components)
- **Xcode** 15+ (for iOS development)
- **Android Studio** (for Android development)
- **Python** 3.11+ (for legacy backend)

## Step 1: Clone the Repository

```bash
git clone https://github.com/Fadil369/brainsait-store.git
cd brainsait-store
```

## Step 2: Install Dependencies

The monorepo uses npm workspaces, so a single install command handles everything:

```bash
npm install
```

This will install dependencies for:
- Root workspace
- All apps (ssdp-mobile, ssdp-web, ssdp-native-ios)
- All services (distribution, sales, finance, ai-forecasting, notifications)
- All workers (route-optimizer, payment, invoice-generator, analytics-aggregator)
- All packages (ui-components, saudi-compliance, bilingual-utils, audit-logger)

## Step 3: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Database
DB_PASSWORD=SecurePassword123!
DATABASE_URL=postgresql://ssdp:SecurePassword123!@localhost:5432/ssdp_platform

# Redis
REDIS_PASSWORD=RedisPassword123!
REDIS_URL=redis://:RedisPassword123!@localhost:6379/0

# Services
ZATCA_API_URL=https://api.zatca.gov.sa
ZATCA_CERT_PATH=/path/to/cert.pem
VAT_RATE=0.15

# Third-party APIs
OPENAI_API_KEY=your_openai_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
STRIPE_SECRET_KEY=your_stripe_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin123
```

## Step 4: Start Infrastructure with Docker

Start PostgreSQL, Redis, and monitoring stack:

```bash
docker-compose -f docker-compose.ssdp.yml up -d postgres redis prometheus grafana
```

Wait for services to be healthy (about 30 seconds):

```bash
docker-compose -f docker-compose.ssdp.yml ps
```

## Step 5: Run Database Migrations

```bash
# Distribution service
npm run migrate --workspace=@brainsait/service-distribution

# Sales service
npm run migrate --workspace=@brainsait/service-sales

# Finance service
npm run migrate --workspace=@brainsait/service-finance
```

## Step 6: Start Development Servers

### Option A: Start All Services

```bash
npm run dev
```

This starts all apps, services, and workers in development mode.

### Option B: Start Specific Components

**Start the web app:**
```bash
npm run dev --workspace=@brainsait/ssdp-web
```

**Start a specific service:**
```bash
npm run dev --workspace=@brainsait/service-distribution
```

**Start a specific worker:**
```bash
npm run dev --workspace=@brainsait/worker-payment
```

### Option C: Use Docker for Everything

```bash
docker-compose -f docker-compose.ssdp.yml up -d
```

## Step 7: Verify Everything is Running

### Check Web App
Open your browser to: http://localhost:3000

### Check Services
- Distribution Service: http://localhost:3001/health
- Sales Service: http://localhost:3002/health
- Finance Service: http://localhost:3003/health
- AI Forecasting: http://localhost:3004/health
- Notifications: http://localhost:3005/health

### Check Monitoring
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin123)

### Check Database
```bash
docker exec -it ssdp_postgres psql -U ssdp -d ssdp_platform
```

## Common Development Tasks

### Building

```bash
# Build all
npm run build

# Build specific component
npm run build --workspace=@brainsait/ssdp-web
npm run build --workspace=@brainsait/service-finance
```

### Testing

```bash
# Run all tests
npm test

# Test specific component
npm test --workspace=@brainsait/saudi-compliance
npm test --workspace=@brainsait/service-sales

# Coverage report
npm run test:coverage
```

### Linting

```bash
# Lint all
npm run lint

# Lint specific component
npm run lint --workspace=@brainsait/ui-components
```

### Viewing Logs

**Docker logs:**
```bash
# All services
docker-compose -f docker-compose.ssdp.yml logs -f

# Specific service
docker-compose -f docker-compose.ssdp.yml logs -f distribution-service
```

**Individual service logs:**
```bash
# Services log to console in dev mode
npm run dev --workspace=@brainsait/service-distribution
```

## Mobile App Development

### React Native (iOS + Android)

```bash
cd apps/ssdp-mobile

# Start Metro bundler
npm run dev

# Run on iOS (requires Xcode)
npm run ios

# Run on Android (requires Android Studio)
npm run android
```

### Native iOS (SwiftUI)

```bash
cd apps/ssdp-native-ios

# Open in Xcode
open SSDP.xcodeproj

# Or build from command line
xcodebuild -scheme SSDP -configuration Debug
```

## Cloudflare Workers Development

```bash
# Route Optimizer
cd workers/route-optimizer
npm run dev

# Payment Worker
cd workers/payment
npm run dev

# Invoice Generator
cd workers/invoice-generator
npm run dev

# Analytics Aggregator
cd workers/analytics-aggregator
npm run dev
```

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

```bash
# Check what's using the port
lsof -i :3000  # Replace 3000 with your port

# Kill the process
kill -9 <PID>
```

### Docker Issues

```bash
# Stop all containers
docker-compose -f docker-compose.ssdp.yml down

# Remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.ssdp.yml down -v

# Rebuild images
docker-compose -f docker-compose.ssdp.yml build --no-cache
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec -it ssdp_postgres psql -U ssdp -d ssdp_platform -c "SELECT 1"

# View PostgreSQL logs
docker logs ssdp_postgres
```

### npm Install Issues

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules
rm -rf apps/*/node_modules
rm -rf services/*/node_modules
rm -rf workers/*/node_modules
rm -rf packages/*/node_modules

# Reinstall
npm install
```

## Next Steps

Now that you're up and running:

1. 📖 **Read the Architecture**: [SSDP Architecture](./docs/architecture/SSDP_ARCHITECTURE.md)
2. 📖 **Explore the Platform**: [SSDP Platform Guide](./SSDP_PLATFORM.md)
3. 🔧 **Check the API Docs**: [API Documentation](./docs/api/README.md)
4. 💻 **Start Coding**: Pick a service and start implementing!
5. 🧪 **Write Tests**: Add tests as you build features
6. 📝 **Update Docs**: Keep documentation current

## Getting Help

- 📖 **Documentation**: [Complete docs](./docs/README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Fadil369/brainsait-store/issues)
- 📧 **Email**: support@brainsait.io
- 💬 **Slack**: #ssdp-platform

## Useful Commands Cheat Sheet

```bash
# Development
npm run dev                                    # Start all
npm run dev --workspace=@brainsait/ssdp-web   # Start web app
npm run dev --workspace=@brainsait/service-*  # Start service

# Building
npm run build                                  # Build all
npm run build --workspace=@brainsait/*        # Build specific

# Testing
npm test                                       # Test all
npm test --workspace=@brainsait/*            # Test specific
npm run test:coverage                         # Coverage report

# Docker
docker-compose -f docker-compose.ssdp.yml up -d      # Start
docker-compose -f docker-compose.ssdp.yml logs -f    # Logs
docker-compose -f docker-compose.ssdp.yml down       # Stop

# Monitoring
open http://localhost:9090                    # Prometheus
open http://localhost:3001                    # Grafana
```

---

🎉 **You're all set! Happy coding!** 🎉
