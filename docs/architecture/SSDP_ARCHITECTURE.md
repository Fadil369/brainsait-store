# SSDP Platform Architecture

## Overview

The SSDP (Saudi Sales & Distribution Platform) is built using a monorepo structure with Domain-Driven Design (DDD) principles, providing a modular, scalable, and maintainable architecture.

## Monorepo Structure

```
brainsait-store/
├── apps/                           # Application layer
│   ├── ssdp-mobile/               # React Native mobile app (Expo)
│   ├── ssdp-web/                  # Next.js web application
│   └── ssdp-native-ios/           # SwiftUI native iOS app
├── services/                       # Microservices layer
│   ├── distribution/              # Order & inventory management
│   ├── sales/                     # Customer & sales operations
│   ├── finance/                   # ZATCA compliance & financials
│   ├── ai-forecasting/            # AI demand prediction
│   └── notifications/             # Multi-channel notifications
├── workers/                        # Cloudflare Workers
│   ├── route-optimizer/           # Delivery route optimization
│   ├── payment/                   # Async payment processing
│   ├── invoice-generator/         # ZATCA invoice generation
│   └── analytics-aggregator/      # Data aggregation pipeline
├── packages/                       # Shared libraries
│   ├── ui-components/             # React component library
│   ├── saudi-compliance/          # ZATCA/Mada/VAT utilities
│   ├── bilingual-utils/           # Arabic/English i18n
│   └── audit-logger/              # Compliance audit logging
├── backend/                        # Legacy FastAPI backend (to be migrated)
├── frontend/                       # Legacy Next.js frontend (to be migrated)
└── infrastructure/                 # Infrastructure as code
    ├── docker/                     # Dockerfiles
    ├── cloudflare/                 # Cloudflare configurations
    └── kubernetes/                 # K8s manifests (future)
```

## Architecture Principles

### 1. Domain-Driven Design (DDD)
- **Bounded Contexts**: Each service represents a distinct business domain
- **Ubiquitous Language**: Consistent terminology across team and code
- **Aggregates**: Encapsulation of domain logic within service boundaries
- **Domain Events**: Asynchronous communication between services

### 2. Microservices Architecture
- **Service Independence**: Each service can be developed, deployed, and scaled independently
- **Technology Diversity**: Choose the right tool for each service
- **Resilience**: Failure isolation prevents cascading failures
- **Scalability**: Scale individual services based on demand

### 3. Monorepo Benefits
- **Code Sharing**: Shared packages reduce duplication
- **Atomic Changes**: Cross-service changes in single PR
- **Consistent Tooling**: Unified development experience
- **Simplified Dependencies**: Internal packages via workspace protocol

## Application Layer

### SSDP Mobile (React Native + Expo)
**Purpose**: Cross-platform mobile application for field sales and distribution

**Features**:
- Offline-first architecture with local storage
- Real-time order tracking
- Biometric authentication
- Push notifications
- Camera integration for barcode scanning
- GPS tracking for delivery routes

**Tech Stack**:
- React Native 0.73
- Expo 50
- Expo Router for navigation
- React Query for data fetching
- AsyncStorage for persistence

### SSDP Web (Next.js 14)
**Purpose**: Web application for back-office operations and management

**Features**:
- Server-side rendering (SSR)
- Real-time analytics dashboard
- Multi-tenant B2B SaaS
- Advanced reporting and exports
- Payment gateway integration
- Document management

**Tech Stack**:
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- TanStack Query
- next-i18next

### SSDP Native iOS (SwiftUI)
**Purpose**: Native iOS application for premium iOS user experience

**Features**:
- Native performance
- Deep iOS integration (Apple Pay, Wallet, etc.)
- Offline capabilities with Core Data
- Widgets and App Clips
- Handoff and Continuity

**Tech Stack**:
- SwiftUI
- Swift Concurrency (async/await)
- Core Data
- Combine framework

## Services Layer

### Distribution Service
**Domain**: Order management, inventory tracking, warehouse operations

**Responsibilities**:
- Create and manage orders
- Track inventory levels across warehouses
- Stock transfers and adjustments
- Integration with route optimizer
- Real-time availability checks

**API Endpoints**:
- POST `/api/orders` - Create order
- GET `/api/orders/:id` - Get order
- GET `/api/inventory` - List inventory
- POST `/api/inventory/transfer` - Transfer stock

**Database**: PostgreSQL with multi-tenant schema

### Sales Service
**Domain**: Customer relationship management, sales pipeline

**Responsibilities**:
- Customer profile management
- Lead tracking and conversion
- Sales pipeline visualization
- Quote and proposal generation
- Sales team performance metrics

**API Endpoints**:
- POST `/api/customers` - Create customer
- GET `/api/pipeline` - Sales pipeline
- POST `/api/leads` - Create lead
- POST `/api/quotes` - Generate quote

**Database**: PostgreSQL with multi-tenant schema

### Finance Service
**Domain**: Financial operations, ZATCA e-invoicing compliance

**Responsibilities**:
- ZATCA-compliant invoice generation
- VAT calculations and reporting
- Payment tracking and reconciliation
- Financial analytics
- Multi-currency support (SAR, USD, EUR)

**API Endpoints**:
- POST `/api/invoices` - Generate ZATCA invoice
- POST `/api/invoices/:id/validate` - Validate with ZATCA
- POST `/api/payments` - Record payment
- GET `/api/reports/vat` - VAT report

**Compliance**: ZATCA Phase 2, Saudi VAT regulations

### AI Forecasting Service
**Domain**: Predictive analytics, demand forecasting

**Responsibilities**:
- Sales demand prediction
- Inventory optimization
- Seasonal trend analysis
- Customer behavior modeling
- Market trend insights

**API Endpoints**:
- POST `/api/forecast/demand` - Predict demand
- POST `/api/forecast/sales` - Sales forecast
- GET `/api/forecast/trends` - Market trends

**ML Stack**: OpenAI API, time-series models, regression

### Notifications Service
**Domain**: Multi-channel communication

**Responsibilities**:
- Email notifications (transactional & marketing)
- SMS notifications (OTP, alerts)
- Push notifications (iOS/Android)
- Notification templates (bilingual)
- Delivery tracking and analytics

**API Endpoints**:
- POST `/api/notifications/email` - Send email
- POST `/api/notifications/sms` - Send SMS
- POST `/api/notifications/push` - Send push

**Channels**: SendGrid (email), Twilio (SMS), FCM (push)

## Workers Layer (Cloudflare Workers)

### Route Optimizer Worker
**Purpose**: Real-time delivery route optimization

**Algorithm**: TSP optimization with traffic data integration

**Performance**: Sub-100ms response time, handles 1000+ locations

### Payment Worker
**Purpose**: Asynchronous payment processing

**Providers**: Stripe, PayPal, Mada, STC Pay, Apple Pay

**Security**: PCI DSS compliant, webhook signature verification

### Invoice Generator Worker
**Purpose**: Generate ZATCA-compliant invoices

**Output**: PDF + XML (UBL 2.1), QR codes, digital signatures

**Compliance**: ZATCA Phase 2 certified

### Analytics Aggregator Worker
**Purpose**: Real-time data aggregation and metrics calculation

**Schedule**: Runs hourly via Cron Triggers

**Metrics**: Sales, customer, product, performance KPIs

## Packages Layer

### @brainsait/ui-components
Shared React component library with Tailwind CSS, Storybook documentation, and RTL support.

### @brainsait/saudi-compliance
ZATCA e-invoicing, VAT calculations, Mada integration, validation utilities.

### @brainsait/bilingual-utils
Arabic/English i18n utilities: text direction, number/date formatting, currency, translation.

### @brainsait/audit-logger
Compliance audit logging with structured logs, GDPR compliance, tamper-proof storage.

## Infrastructure

### Docker
Each service has its own Dockerfile optimized for production:
- Multi-stage builds
- Layer caching
- Security scanning
- Health checks

### Database
- **PostgreSQL**: Multi-tenant with row-level security
- **Redis**: Session storage, caching, rate limiting
- **MinIO**: S3-compatible object storage

### CI/CD Pipeline
- **Build**: Parallel builds for all services
- **Test**: Unit, integration, E2E tests
- **Security**: Dependency scanning, SAST
- **Deploy**: Automated deployment to Cloudflare

### Monitoring
- **Logs**: Structured logging with audit trails
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Alerts**: PagerDuty integration

## Communication Patterns

### Synchronous (REST APIs)
- Service-to-service via internal APIs
- Client-to-service via API Gateway
- Request/response pattern

### Asynchronous (Events)
- Message queue (Redis Streams/RabbitMQ)
- Event-driven architecture
- Eventual consistency

### Real-time (WebSockets)
- Live order tracking
- Real-time notifications
- Dashboard updates

## Security

### Authentication
- JWT tokens with refresh mechanism
- OAuth 2.0 / SAML 2.0 for SSO
- Biometric authentication (mobile)

### Authorization
- Role-based access control (RBAC)
- Tenant isolation
- API key authentication for services

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PII data masking
- GDPR compliance

## Scalability

### Horizontal Scaling
- Stateless services enable easy scaling
- Load balancing across instances
- Auto-scaling based on metrics

### Vertical Scaling
- Resource optimization
- Connection pooling
- Caching strategies

### Database Scaling
- Read replicas for analytics
- Sharding by tenant
- Connection pooling

## Development Workflow

### Local Development
```bash
# Install dependencies
npm install

# Start all services
npm run dev

# Start specific service
npm run dev --workspace=@brainsait/service-distribution
```

### Testing
```bash
# Run all tests
npm test

# Test specific service
npm test --workspace=@brainsait/service-sales
```

### Deployment
```bash
# Build all services
npm run build

# Deploy to production
./scripts/deploy.sh
```

## Migration Strategy

### Phase 1: Parallel Operation
- New services run alongside legacy backend
- Gradual feature migration
- Traffic split testing

### Phase 2: Data Migration
- Incremental data migration
- Dual-write pattern
- Validation and reconciliation

### Phase 3: Cutover
- Service-by-service cutover
- Rollback capability
- Monitoring and validation

### Phase 4: Decommission
- Remove legacy code
- Cleanup and optimization
- Documentation update

## Future Roadmap

- **Kubernetes**: Container orchestration for complex deployments
- **GraphQL Federation**: Unified API gateway across services
- **Event Sourcing**: Full audit trail with event replay
- **CQRS**: Separate read/write models for optimization
- **Service Mesh**: Advanced traffic management with Istio/Linkerd
