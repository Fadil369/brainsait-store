# SSDP Platform - Saudi Sales & Distribution Platform

## Overview

The SSDP Platform is a comprehensive B2B SaaS solution designed for the Saudi Arabian market, featuring multi-tenant architecture, ZATCA compliance, and AI-powered forecasting.

## 🏗️ Monorepo Structure

This repository follows a monorepo pattern with the following structure:

### 📱 Apps
- **ssdp-mobile** - React Native/Expo mobile app for iOS and Android
- **ssdp-web** - Next.js 14 web application
- **ssdp-native-ios** - Native iOS app built with SwiftUI

### 🔧 Services
- **distribution** - Order and inventory management
- **sales** - Customer relationship management (CRM)
- **finance** - ZATCA-compliant e-invoicing and financial operations
- **ai-forecasting** - AI-powered demand prediction and analytics
- **notifications** - Multi-channel notifications (email, SMS, push)

### ⚡ Workers (Cloudflare)
- **route-optimizer** - Delivery route optimization
- **payment** - Asynchronous payment processing
- **invoice-generator** - ZATCA-compliant invoice generation
- **analytics-aggregator** - Real-time data aggregation

### 📦 Packages
- **ui-components** - Shared React component library
- **saudi-compliance** - ZATCA/Mada/VAT utilities
- **bilingual-utils** - Arabic/English i18n utilities
- **audit-logger** - Compliance audit logging

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm 9+
- Docker & Docker Compose
- Cloudflare account (for workers)
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Clone the repository
git clone https://github.com/Fadil369/brainsait-store.git
cd brainsait-store

# Install all dependencies (monorepo)
npm install

# Start development environment with Docker
docker-compose up -d

# Start all apps and services
npm run dev
```

### Individual Service Development

```bash
# Start specific app
npm run dev --workspace=@brainsait/ssdp-web
npm run dev --workspace=@brainsait/ssdp-mobile

# Start specific service
npm run dev --workspace=@brainsait/service-distribution
npm run dev --workspace=@brainsait/service-sales

# Start specific worker
npm run dev --workspace=@brainsait/worker-payment
```

## 🏃 Development Workflow

### Building

```bash
# Build all
npm run build

# Build specific workspace
npm run build --workspace=@brainsait/ssdp-web
npm run build --workspace=@brainsait/service-finance
```

### Testing

```bash
# Run all tests
npm test

# Test specific workspace
npm test --workspace=@brainsait/saudi-compliance
npm test --workspace=@brainsait/service-sales

# Coverage report
npm run test:coverage
```

### Linting

```bash
# Lint all code
npm run lint

# Lint specific workspace
npm run lint --workspace=@brainsait/ui-components
```

## 📁 Repository Structure

```
brainsait-store/
├── apps/
│   ├── ssdp-mobile/          # React Native + Expo
│   ├── ssdp-web/             # Next.js 14
│   └── ssdp-native-ios/      # SwiftUI
├── services/
│   ├── distribution/         # Order & inventory
│   ├── sales/                # CRM & sales pipeline
│   ├── finance/              # ZATCA & financials
│   ├── ai-forecasting/       # AI predictions
│   └── notifications/        # Multi-channel comms
├── workers/
│   ├── route-optimizer/      # Route optimization
│   ├── payment/              # Payment processing
│   ├── invoice-generator/    # Invoice generation
│   └── analytics-aggregator/ # Data aggregation
├── packages/
│   ├── ui-components/        # UI library
│   ├── saudi-compliance/     # ZATCA utilities
│   ├── bilingual-utils/      # i18n utilities
│   └── audit-logger/         # Audit logging
├── backend/                   # Legacy FastAPI (migration in progress)
├── frontend/                  # Legacy Next.js (migration in progress)
├── infrastructure/
│   ├── docker/               # Dockerfiles
│   ├── cloudflare/           # CF configurations
│   └── kubernetes/           # K8s manifests (future)
├── docs/
│   ├── architecture/         # Architecture docs
│   ├── api/                  # API documentation
│   └── development/          # Dev guides
├── .github/
│   └── workflows/            # CI/CD pipelines
├── package.json              # Root package.json (workspaces)
├── docker-compose.yml        # Local development stack
└── README.md                 # This file
```

## 🔒 Security & Compliance

### ZATCA E-Invoicing
- Phase 2 compliant
- QR code generation
- Digital signatures (X.509)
- XML format (UBL 2.1)

### Data Protection
- Encryption at rest and in transit
- GDPR compliance
- Audit logging
- PII data masking

### Authentication
- JWT with refresh tokens
- OAuth 2.0 / SAML 2.0 SSO
- Biometric authentication (mobile)
- Role-based access control (RBAC)

## 🌍 Internationalization

Full Arabic/English bilingual support:
- RTL layout support
- Arabic/Gregorian calendars
- Eastern Arabic numerals
- Currency formatting (SAR, USD, EUR)
- Localized date/time formats

## 📊 Architecture

See [SSDP Architecture Documentation](./docs/architecture/SSDP_ARCHITECTURE.md) for detailed architecture overview.

### Key Design Patterns
- **Domain-Driven Design (DDD)**: Clear bounded contexts
- **Microservices**: Independent, scalable services
- **Event-Driven**: Asynchronous communication
- **CQRS**: Separate read/write models (future)

## 🚢 Deployment

### Docker

```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloudflare Workers

```bash
# Deploy worker
cd workers/payment
npm run deploy
```

### Production Deployment

```bash
# Build for production
npm run build

# Run deployment script
./scripts/deploy.sh
```

## 📈 Monitoring & Observability

- **Logs**: Structured logging with Winston
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry (future)
- **Alerts**: PagerDuty integration

## 🧪 Testing Strategy

### Unit Tests
- Jest for JavaScript/TypeScript
- Pytest for Python services
- XCTest for Swift (iOS)

### Integration Tests
- API endpoint testing
- Database integration tests
- Service-to-service communication

### E2E Tests
- Playwright for web
- Detox for mobile
- XCUITest for iOS

## 📚 Documentation

- [Architecture Overview](./docs/architecture/SSDP_ARCHITECTURE.md)
- [API Documentation](./docs/api/README.md)
- [Development Guide](./docs/development/README.md)
- [Deployment Guide](./docs/deployment/README.md)

## 🤝 Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## 📝 License

Proprietary software owned by BrainSAIT. All rights reserved.

## 🆘 Support

- **Documentation**: [Complete docs](./docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/Fadil369/brainsait-store/issues)
- **Email**: support@brainsait.io
- **Emergency**: 24/7 support for critical issues

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Monorepo structure
- ✅ Service scaffolding
- ✅ Package creation
- 🔄 Service implementation

### Phase 2 (Q1 2024)
- Legacy backend migration
- Full ZATCA integration
- Mobile app beta launch
- AI forecasting MVP

### Phase 3 (Q2 2024)
- Kubernetes deployment
- GraphQL Federation
- Advanced analytics
- iOS native app release

### Phase 4 (Q3 2024)
- Event sourcing
- CQRS implementation
- Service mesh (Istio)
- Multi-region deployment

---

**Built with ❤️ by BrainSAIT Team**
