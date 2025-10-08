# SSDP Platform Architecture Diagram

## High-Level System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                │
│  │   Mobile     │    │     Web      │    │   iOS App    │                │
│  │  (Expo RN)   │    │  (Next.js)   │    │  (SwiftUI)   │                │
│  │              │    │              │    │              │                │
│  │ iOS/Android  │    │  Dashboard   │    │   Premium    │                │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                │
│         │                   │                   │                         │
└─────────┼───────────────────┼───────────────────┼─────────────────────────┘
          │                   │                   │
          │                   ▼                   │
          │         ┌─────────────────┐           │
          │         │  Cloudflare CDN │           │
          │         │   & Edge Cache  │           │
          │         └────────┬─────────┘          │
          │                  │                    │
          └──────────────────┼────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────────┐
│                          API GATEWAY LAYER                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │           Cloudflare Workers (Edge Computing)                       │  │
│  │  ┌──────────────┐  ┌───────────────┐  ┌────────────────┐          │  │
│  │  │Route Optimize│  │    Payment    │  │Invoice Generator│         │  │
│  │  │   Worker     │  │    Worker     │  │    Worker      │          │  │
│  │  └──────────────┘  └───────────────┘  └────────────────┘          │  │
│  │                                                                     │  │
│  │  ┌──────────────┐                                                  │  │
│  │  │  Analytics   │      Rate Limiting • Auth • Routing              │  │
│  │  │  Aggregator  │      CORS • Caching • Security                   │  │
│  │  └──────────────┘                                                  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                        MICROSERVICES LAYER                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐              │
│  │  Distribution  │  │     Sales      │  │    Finance     │              │
│  │    Service     │  │    Service     │  │    Service     │              │
│  │                │  │                │  │                │              │
│  │ • Orders       │  │ • CRM          │  │ • ZATCA E-inv  │              │
│  │ • Inventory    │  │ • Leads        │  │ • VAT Reports  │              │
│  │ • Warehouses   │  │ • Pipeline     │  │ • Payments     │              │
│  │                │  │ • Quotes       │  │ • Multi-curr   │              │
│  │ Port: 3001     │  │ Port: 3002     │  │ Port: 3003     │              │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘              │
│           │                   │                   │                       │
│  ┌────────▼───────┐  ┌────────▼───────┐                                  │
│  │ AI Forecasting │  │ Notifications  │                                  │
│  │    Service     │  │    Service     │                                  │
│  │                │  │                │                                  │
│  │ • Demand       │  │ • Email        │                                  │
│  │ • Predictions  │  │ • SMS          │                                  │
│  │ • Trends       │  │ • Push         │                                  │
│  │ • ML Models    │  │ • Templates    │                                  │
│  │ Port: 3004     │  │ Port: 3005     │                                  │
│  └────────┬───────┘  └────────┬───────┘                                  │
│           │                   │                                           │
└───────────┼───────────────────┼───────────────────────────────────────────┘
            │                   │
            │    ┌──────────────▼───────────────┐
            │    │     Event Bus (Redis)        │
            │    │  • Pub/Sub                   │
            │    │  • Streams                   │
            │    └──────────────┬───────────────┘
            │                   │
┌───────────▼───────────────────▼───────────────────────────────────────────┐
│                           DATA LAYER                                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────┐    ┌────────────────────────────┐       │
│  │  PostgreSQL 15             │    │  Redis 7                   │       │
│  │  (Multi-tenant)            │    │  (Cache & Sessions)        │       │
│  │                            │    │                            │       │
│  │ • Orders                   │    │ • API Cache                │       │
│  │ • Customers                │    │ • Rate Limits              │       │
│  │ • Inventory                │    │ • Session Store            │       │
│  │ • Invoices                 │    │ • Event Bus                │       │
│  │ • Analytics                │    │                            │       │
│  │                            │    │                            │       │
│  │ Row-level security         │    │ TTL & Eviction             │       │
│  │ Connection pooling         │    │ Pub/Sub                    │       │
│  └────────────────────────────┘    └────────────────────────────┘       │
│                                                                           │
│  ┌────────────────────────────┐                                          │
│  │  MinIO (S3-compatible)     │                                          │
│  │                            │                                          │
│  │ • Documents                │                                          │
│  │ • Invoices                 │                                          │
│  │ • Attachments              │                                          │
│  └────────────────────────────┘                                          │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                      SHARED PACKAGES LAYER                                │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     UI      │  │    Saudi     │  │  Bilingual   │  │    Audit     │ │
│  │ Components  │  │  Compliance  │  │    Utils     │  │   Logger     │ │
│  │             │  │              │  │              │  │              │ │
│  │ • Buttons   │  │ • ZATCA      │  │ • RTL/LTR    │  │ • Events     │ │
│  │ • Forms     │  │ • Mada       │  │ • Numbers    │  │ • Security   │ │
│  │ • Tables    │  │ • VAT        │  │ • Dates      │  │ • Business   │ │
│  │ • Cards     │  │ • Validation │  │ • Currency   │  │ • Compliance │ │
│  └─────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                                            │
│              Used by all apps, services, and workers                      │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                    MONITORING & OBSERVABILITY                             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │ Prometheus  │  │   Grafana    │  │  CloudWatch  │                    │
│  │             │  │              │  │              │                    │
│  │ • Metrics   │  │ • Dashboards │  │ • Logs       │                    │
│  │ • Alerts    │  │ • Alerts     │  │ • Traces     │                    │
│  │ • Time-ser  │  │ • Reports    │  │ • Errors     │                    │
│  └─────────────┘  └──────────────┘  └──────────────┘                    │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

## Service Communication Patterns

### Synchronous (REST)
```
Client ──HTTP──> API Gateway ──HTTP──> Service
   │                                      │
   └────────────── JSON ─────────────────┘
```

### Asynchronous (Events)
```
Service A ──Event──> Redis Streams ──Event──> Service B
                          │
                          ├──Event──> Service C
                          └──Event──> Service D
```

### Real-time (WebSocket)
```
Client <──WebSocket──> API Gateway <──Redis Pub/Sub──> Services
```

## Data Flow: Order Processing

```
┌─────────┐
│ Mobile  │
│  App    │
└────┬────┘
     │
     │ 1. Create Order
     ▼
┌─────────────┐
│   Worker    │
│Rate Limit + │──────────> [Reject if rate exceeded]
│    Auth     │
└─────┬───────┘
      │
      │ 2. Validated Request
      ▼
┌──────────────┐         ┌─────────────┐
│Distribution  │────────>│  PostgreSQL │
│   Service    │ 3. Save │             │
└──────┬───────┘         └─────────────┘
       │
       │ 4. Publish Event
       ▼
┌──────────────┐
│Redis Streams │
└──────┬───────┘
       │
       ├────────────────────────────────┐
       │                                │
       │ 5. Consume Events              │
       ▼                                ▼
┌──────────────┐                 ┌──────────────┐
│   Finance    │                 │Notifications │
│   Service    │                 │   Service    │
│              │                 │              │
│ • Invoice    │                 │ • Email      │
│ • Payment    │                 │ • SMS        │
└──────┬───────┘                 └──────┬───────┘
       │                                │
       │ 6. Invoice Generated           │ 7. Customer Notified
       ▼                                ▼
┌──────────────┐                 ┌──────────────┐
│Invoice Worker│                 │   Customer   │
│              │                 │              │
│ • PDF + XML  │                 │  📧 ✅       │
│ • QR Code    │                 │              │
└──────────────┘                 └──────────────┘
```

## Deployment Architecture

### Development
```
Developer Laptop
├── Docker Compose
│   ├── PostgreSQL
│   ├── Redis
│   ├── All Services (local)
│   └── Monitoring Stack
└── Hot Reload Enabled
```

### Staging
```
Cloudflare
├── Workers (Edge)
│   ├── Route Optimizer
│   ├── Payment
│   ├── Invoice Generator
│   └── Analytics
└── Pages (ssdp-web)

AWS/GCP
├── ECS/GKE Cluster
│   ├── Distribution Service
│   ├── Sales Service
│   ├── Finance Service
│   ├── AI Forecasting Service
│   └── Notifications Service
├── RDS PostgreSQL
├── ElastiCache Redis
└── S3 Storage
```

### Production
```
Multi-Region Deployment

Region 1 (Middle East)     Region 2 (Europe)      Region 3 (Asia)
├── Cloudflare Edge        ├── Cloudflare Edge    ├── Cloudflare Edge
├── Service Cluster        ├── Service Cluster    ├── Service Cluster
├── Primary DB             ├── Read Replica       ├── Read Replica
└── Redis Cluster          └── Redis Cluster      └── Redis Cluster
```

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│ Layer 7: Application Security                          │
│ • Input Validation • SQL Injection Prevention          │
│ • XSS Protection • CSRF Tokens                         │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Layer 6: Authentication & Authorization                 │
│ • JWT Tokens • OAuth 2.0 • RBAC                        │
│ • Biometric • MFA                                       │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Layer 5: API Security                                   │
│ • Rate Limiting • API Keys • CORS                       │
│ • Request Signing • Webhook Verification                │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Layer 4: Network Security                               │
│ • TLS 1.3 • Certificate Pinning                        │
│ • Private Subnets • Security Groups                     │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Layer 3: Data Security                                  │
│ • Encryption at Rest (AES-256)                         │
│ • Encryption in Transit (TLS) • PII Masking            │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Layer 2: Infrastructure Security                        │
│ • Container Scanning • Image Signing                   │
│ • Secrets Management • IAM Roles                        │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Layer 1: Audit & Compliance                            │
│ • Audit Logs • ZATCA Compliance                        │
│ • GDPR Compliance • Regular Audits                     │
└─────────────────────────────────────────────────────────┘
```

---

**Legend:**
- `──>` : HTTP/REST API call
- `~~>` : WebSocket connection
- `▶▶>` : Event/Message queue
- `[?]` : Decision point
- `[!]` : Error/Exception
