# BrainSAIT Store - System Architecture

## Overview

The BrainSAIT Store is a enterprise-grade B2B SaaS platform built with modern technologies and designed for scalability, security, and maintainability. It features deep integration with the GIVC Healthcare Platform, providing a unified ecosystem for healthcare services, e-commerce, and AI-powered medical processing.

### Key Documentation
- **[GIVC Integration Architecture](./givc-integration.md)** - Cross-repo integration patterns and data flows
- **[Service Inventory](./service-inventory.md)** - Complete inventory of all services and data flows
- **[Secrets Management](../security/secrets-management.md)** - Security and compliance procedures

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Next.js 14 Frontend (React/TypeScript)                        │
│  ├── Arabic/English Support (i18n)                             │
│  ├── Responsive Design (Tailwind CSS)                          │
│  ├── Real-time Updates (WebSocket)                             │
│  └── Payment Integration (Stripe, PayPal, Apple Pay)           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  Cloudflare Workers                                             │
│  ├── Rate Limiting (120 req/min)                               │
│  ├── CORS Handling                                             │
│  ├── Request Routing                                           │
│  └── Health Monitoring                                         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Python 3.11+)                               │
│  ├── Multi-tenant Architecture                                 │
│  ├── JWT Authentication                                        │
│  ├── Async/Await Support                                       │
│  ├── OpenAPI Documentation                                     │
│  └── Middleware Stack                                          │
│      ├── CORS Middleware                                       │
│      ├── Tenant Middleware                                     │
│      ├── Localization Middleware                               │
│      └── Security Middleware                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic Services                                       │
│  ├── Store Service (Product Management)                        │
│  ├── Payment Service (Multi-provider)                          │
│  ├── Analytics Service (Metrics & Reporting)                   │
│  ├── Integration Service (LinkedIn, OID)                       │
│  ├── Auth Service (JWT, OAuth, SSO)                            │
│  ├── Notification Service (Email, SMS)                         │
│  └── GIVC Integration Service (Healthcare)                     │
│      ├── Provider Management                                   │
│      ├── NPHIES Integration                                    │
│      ├── FHIR Resource Management                              │
│      └── Service Provisioning                                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│             GIVC Healthcare Services (Cross-Repo)              │
├─────────────────────────────────────────────────────────────────┤
│  ├── GIVC Healthcare API (AI Medical Processing)               │
│  ├── HealthLinc EHR/RCM (Electronic Health Records)            │
│  ├── HealthLinc Logs (Monitoring & Alerting)                   │
│  └── MCP ServerLinc (AI Model Context Protocol)                │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                          Redis Cache       │
│  ├── Multi-tenant Schema                     ├── Session Store  │
│  ├── Products & Orders                       ├── Rate Limiting  │
│  ├── Users & Tenants                         └── API Cache      │
│  ├── Analytics Data                                             │
│  └── Payment Records                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: TanStack Query (React Query)
- **Internationalization**: next-i18next (Arabic/English)
- **Testing**: Jest with React Testing Library

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for session and API caching
- **Authentication**: JWT with refresh tokens
- **API Documentation**: OpenAPI/Swagger auto-generated

### Infrastructure
- **Hosting**: Cloudflare Pages (Frontend) + Workers (API Gateway)
- **Database**: PostgreSQL (production-ready)
- **CDN**: Cloudflare CDN with global distribution
- **Monitoring**: Prometheus metrics with health checks

### Payment Systems
- **Stripe**: Live environment configured
- **PayPal**: Business account integration
- **Apple Pay**: Domain verified for store.brainsait.io
- **Saudi Gateways**: Mada, STC Pay with ZATCA compliance

## Key Architectural Principles

### 1. Multi-Tenant Architecture
- **Tenant Isolation**: Data separation per tenant
- **Shared Infrastructure**: Cost-efficient resource utilization
- **Custom Branding**: Per-tenant customization support

### 2. Microservices-Ready Design
- **Service Layer**: Clear separation of business logic
- **Async Communication**: Event-driven architecture support
- **Independent Scaling**: Service-specific scaling capabilities

### 3. Security-First Approach
- **JWT Authentication**: Stateless token-based auth
- **Role-Based Access Control**: Granular permissions
- **Data Encryption**: At rest and in transit
- **CORS Protection**: Strict origin validation

### 4. Internationalization
- **RTL Support**: Arabic language interface
- **Localized Content**: Database-level localization
- **Currency Support**: Multi-currency pricing
- **Date/Time Formatting**: Locale-aware formatting

### 5. Performance Optimization
- **Caching Strategy**: Multi-layer caching
- **Database Optimization**: Indexed queries and connection pooling
- **CDN Integration**: Global content delivery
- **Lazy Loading**: Component and data lazy loading

## Data Flow

### 1. Request Processing
```
User Request → Cloudflare → FastAPI → Service Layer → Database
              ↓              ↓           ↓              ↓
           Rate Limit    Authentication  Business     Data
           CORS Check    Tenant Check    Logic        Retrieval
```

### 2. Response Flow
```
Database → Service Layer → FastAPI → Cloudflare → User
   ↓           ↓             ↓           ↓          ↓
Transform   Business     JSON API    CDN Cache   Frontend
  Data       Logic      Response     Delivery    Rendering
```

## Deployment Architecture

### Production Environment
- **Frontend**: Cloudflare Pages with automatic deployments
- **Backend**: Cloudflare Workers with edge computing
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis cluster for high availability

### Development Environment
- **Frontend**: Local Next.js development server
- **Backend**: Local FastAPI with hot reload
- **Database**: Docker PostgreSQL container
- **Cache**: Docker Redis container

## Scalability Considerations

### Horizontal Scaling
- **API Workers**: Auto-scaling Cloudflare Workers
- **Database**: Read replicas and connection pooling
- **Cache**: Redis cluster with sharding
- **CDN**: Global edge distribution

### Vertical Scaling
- **Database**: Resource scaling based on load
- **Worker Memory**: Cloudflare Worker resource allocation
- **Cache Memory**: Redis memory optimization

## Security Architecture

### Authentication & Authorization
```
User Login → JWT Generation → Token Validation → Role Check → Access Grant
     ↓              ↓              ↓               ↓            ↓
  Credentials   Secure Storage   Middleware    Permission   Resource
  Validation    (HttpOnly)       Validation     Matrix      Access
```

### Data Protection
- **Encryption**: AES-256 for sensitive data
- **Secrets Management**: Environment variables
- **API Security**: Rate limiting and CORS
- **Database**: Parameterized queries (SQL injection protection)

## Monitoring & Observability

### Metrics Collection
- **Application Metrics**: Prometheus metrics
- **Performance Monitoring**: Response times and error rates
- **Business Metrics**: Revenue, conversion rates
- **Infrastructure**: Resource utilization

### Logging Strategy
- **Structured Logging**: JSON format with correlation IDs
- **Error Tracking**: Sentry integration
- **Audit Logging**: User actions and system events
- **Performance Logging**: Slow query identification

## Disaster Recovery

### Backup Strategy
- **Database**: Automated daily backups with point-in-time recovery
- **Application**: Git-based version control
- **Configuration**: Infrastructure as code

### High Availability
- **Multi-Region**: Cloudflare global network
- **Failover**: Automatic failover mechanisms
- **Health Checks**: Continuous monitoring with alerts

## GIVC Healthcare Integration

### Unified Architecture
BrainSAIT Store integrates seamlessly with GIVC Healthcare Platform to provide:

- **Single Sign-On (SSO)**: Unified authentication across BrainSAIT Store and GIVC services
- **Healthcare Product Provisioning**: Automatic setup of GIVC services on purchase
- **NPHIES Integration**: Saudi healthcare system integration for claims and authorizations
- **FHIR Compliance**: Standard healthcare data formats (FHIR R4)
- **OID Management**: Healthcare provider identification using ISO OID tree (1.3.6.1.4.1.61026.*)

### Cross-Service Data Flow
```
BrainSAIT Store → API Gateway → GIVC Healthcare API → NPHIES
       ↓                                ↓                  ↓
   PostgreSQL                      AI Processing     Saudi Payers
   (Shared)                        FHIR Resources    Claims/Auth
```

### Key Integration Points
1. **Authentication**: JWT tokens validated across both systems
2. **Healthcare Providers**: Synchronized via OID Integration Service
3. **Medical Claims**: GIVC processes claims, BrainSAIT tracks transactions
4. **Audit Logging**: Unified compliance logging for HIPAA and Saudi regulations

For detailed integration architecture, see [GIVC Integration Documentation](./givc-integration.md).

## Security & Compliance

### Healthcare Compliance
- **HIPAA**: Protected Health Information (PHI) encryption and access controls
- **NPHIES**: Saudi healthcare integration standards
- **FHIR R4**: Standard healthcare resource formats
- **Audit Logging**: Complete audit trail for healthcare data access

### Encryption Standards
- **Data at Rest**: AES-256-GCM encryption
- **Data in Transit**: TLS 1.3 (minimum TLS 1.2)
- **Secrets Management**: HashiCorp Vault + Cloudflare Workers Secrets
- **Token Security**: JWT with HS256 algorithm, 30-minute expiration

For detailed security procedures, see [Secrets Management Documentation](../security/secrets-management.md).

## Next Steps

- [GIVC Integration Architecture](./givc-integration.md)
- [Service Inventory & Data Flows](./service-inventory.md)
- [Database Schema Documentation](./database.md)
- [API Design Patterns](./api-patterns.md)
- [Security & Secrets Management](../security/secrets-management.md)
- [Deployment Guide](../deployment/README.md)