# SSDP Platform - Implementation Guide

## Overview

This guide helps developers start implementing the scaffolded SSDP platform services and components.

## What's Been Built

### ✅ Complete Scaffolding

**Monorepo Structure**
- Root workspace with npm workspaces configured
- 3 apps, 5 services, 4 workers, 4 packages
- Docker compose for development
- CI/CD pipeline with GitHub Actions

**Documentation** (50,000+ lines)
- Architecture diagrams and detailed docs
- API specifications for each service
- Quick start and development guides
- Component-specific READMEs

**Infrastructure**
- Docker development environment
- Service orchestration configs
- Database schemas (ready for migration)
- Monitoring stack setup

### 🔄 Ready for Implementation

Each component has:
- ✅ Package.json with dependencies
- ✅ README with features and API endpoints
- ✅ TypeScript configuration
- ✅ Testing scaffolds
- ⏳ Business logic (to be implemented)
- ⏳ Database models (to be created)
- ⏳ API routes (to be built)

## Implementation Priority

### Phase 1: Core Services (Weeks 1-4)

#### 1. Distribution Service (Week 1-2)
**Location**: `services/distribution/`

**Tasks**:
```typescript
// 1. Create database models
services/distribution/src/models/
  ├── Order.ts
  ├── Inventory.ts
  └── Warehouse.ts

// 2. Implement API routes
services/distribution/src/routes/
  ├── orders.ts
  ├── inventory.ts
  └── warehouses.ts

// 3. Add business logic
services/distribution/src/services/
  ├── OrderService.ts
  ├── InventoryService.ts
  └── WarehouseService.ts

// 4. Write tests
services/distribution/src/__tests__/
  ├── orders.test.ts
  ├── inventory.test.ts
  └── integration.test.ts
```

**Example Implementation**:
```typescript
// services/distribution/src/routes/orders.ts
import { FastifyInstance } from 'fastify';
import { OrderService } from '../services/OrderService';

export async function orderRoutes(fastify: FastifyInstance) {
  const orderService = new OrderService();

  fastify.post('/api/orders', async (request, reply) => {
    const order = await orderService.create(request.body);
    return reply.code(201).send(order);
  });

  fastify.get('/api/orders/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    const order = await orderService.findById(id);
    if (!order) {
      return reply.code(404).send({ error: 'Order not found' });
    }
    return order;
  });
}
```

#### 2. Finance Service (Week 2-3)
**Location**: `services/finance/`

**Tasks**:
```typescript
// 1. Integrate @brainsait/saudi-compliance package
import { ZATCAInvoice, generateQRCode } from '@brainsait/saudi-compliance';

// 2. Create invoice models
services/finance/src/models/
  ├── Invoice.ts
  ├── Payment.ts
  └── VATReport.ts

// 3. Implement ZATCA e-invoicing
services/finance/src/services/
  ├── InvoiceService.ts
  ├── ZATCAService.ts
  └── PaymentService.ts
```

**Example**:
```typescript
// services/finance/src/services/InvoiceService.ts
import { ZATCAInvoice, generateQRCode } from '@brainsait/saudi-compliance';
import { AuditLogger } from '@brainsait/audit-logger';

export class InvoiceService {
  private logger = new AuditLogger({ serviceName: 'finance' });

  async generateInvoice(orderData: any) {
    // Create ZATCA-compliant invoice
    const invoice = new ZATCAInvoice({
      sellerName: orderData.seller.name,
      vatNumber: orderData.seller.vatNumber,
      timestamp: new Date(),
      total: orderData.total,
      vatAmount: orderData.total * 0.15
    });

    // Generate QR code
    const qrCode = generateQRCode(invoice);

    // Log for audit
    this.logger.logBusinessEvent({
      type: 'invoice_generated',
      invoiceId: invoice.id,
      orderId: orderData.orderId,
      amount: orderData.total
    });

    return { invoice, qrCode };
  }
}
```

#### 3. Sales Service (Week 3-4)
**Location**: `services/sales/`

**Tasks**:
- Customer management (CRM)
- Lead tracking
- Sales pipeline
- Quote generation

### Phase 2: Supporting Services (Weeks 5-6)

#### 4. Notifications Service
**Location**: `services/notifications/`

**Integrations**:
- SendGrid (email)
- Twilio (SMS)
- Firebase Cloud Messaging (push)
- Use `@brainsait/bilingual-utils` for templates

#### 5. AI Forecasting Service
**Location**: `services/ai-forecasting/`

**Features**:
- Demand prediction using OpenAI
- Time series analysis
- Trend detection

### Phase 3: Workers (Weeks 7-8)

#### 6. Payment Worker
**Location**: `workers/payment/`

**Implementation**:
```typescript
// workers/payment/src/index.ts
export default {
  async fetch(request: Request, env: Env) {
    const url = new URL(request.url);

    if (url.pathname === '/webhooks/stripe') {
      return handleStripeWebhook(request, env);
    }

    return new Response('Payment Worker', { status: 200 });
  }
};

async function handleStripeWebhook(request: Request, env: Env) {
  const signature = request.headers.get('stripe-signature');
  const body = await request.text();

  // Verify signature
  // Process payment
  // Update database
  // Send notification

  return new Response(JSON.stringify({ received: true }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```

#### 7. Invoice Generator Worker
**Location**: `workers/invoice-generator/`

**Use**: `@brainsait/saudi-compliance` package

#### 8. Route Optimizer Worker
**Location**: `workers/route-optimizer/`

**Algorithm**: TSP optimization

#### 9. Analytics Aggregator Worker
**Location**: `workers/analytics-aggregator/`

**Cron**: Hourly aggregation

### Phase 4: Shared Packages (Ongoing)

#### 10. UI Components Package
**Location**: `packages/ui-components/`

**Implementation**:
```typescript
// packages/ui-components/src/Button.tsx
import React from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary',
  onClick,
  children 
}) => {
  const className = variant === 'primary' 
    ? 'bg-blue-500 text-white' 
    : 'bg-gray-200 text-gray-800';

  return (
    <button className={className} onClick={onClick}>
      {children}
    </button>
  );
};
```

#### 11. Saudi Compliance Package
**Location**: `packages/saudi-compliance/`

**Implementation**:
```typescript
// packages/saudi-compliance/src/zatca.ts
export class ZATCAInvoice {
  constructor(private data: InvoiceData) {}

  toXML(): string {
    // Generate UBL 2.1 XML
  }

  generateHash(): string {
    // SHA-256 hash
  }

  sign(privateKey: string): string {
    // X.509 digital signature
  }
}

export function generateQRCode(invoice: ZATCAInvoice): string {
  // TLV format QR code
}

export function calculateVAT(amount: number, rate = 0.15): number {
  return amount * rate;
}

export function validateVATNumber(vatNumber: string): boolean {
  return /^\d{15}$/.test(vatNumber);
}
```

#### 12. Bilingual Utils Package
**Location**: `packages/bilingual-utils/`

**Implementation**:
```typescript
// packages/bilingual-utils/src/index.ts
export function getTextDirection(locale: string): 'rtl' | 'ltr' {
  return locale === 'ar' ? 'rtl' : 'ltr';
}

export function formatNumber(num: number, locale: string): string {
  return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US')
    .format(num);
}

export function formatCurrency(
  amount: number,
  currency: string,
  locale: string
): string {
  return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
    style: 'currency',
    currency
  }).format(amount);
}

export function formatDate(date: Date, locale: string): string {
  return new Intl.DateTimeFormat(locale === 'ar' ? 'ar-SA' : 'en-US')
    .format(date);
}
```

#### 13. Audit Logger Package
**Location**: `packages/audit-logger/`

**Implementation**:
```typescript
// packages/audit-logger/src/AuditLogger.ts
import winston from 'winston';

export class AuditLogger {
  private logger: winston.Logger;

  constructor(config: { serviceName: string }) {
    this.logger = winston.createLogger({
      format: winston.format.json(),
      defaultMeta: { service: config.serviceName },
      transports: [
        new winston.transports.File({ filename: 'audit.log' })
      ]
    });
  }

  logUserAction(data: {
    userId: string;
    action: string;
    resource: string;
    resourceId: string;
    metadata?: any;
  }) {
    this.logger.info('user_action', {
      ...data,
      timestamp: new Date().toISOString()
    });
  }

  logSecurityEvent(data: {
    type: string;
    severity: string;
    userId?: string;
    action: string;
    metadata?: any;
  }) {
    this.logger.warn('security_event', {
      ...data,
      timestamp: new Date().toISOString()
    });
  }
}
```

## Development Workflow

### 1. Start with a Service

```bash
# Pick a service to implement
cd services/distribution

# Install dependencies (if not already done)
npm install

# Create src directory structure
mkdir -p src/{models,routes,services,utils}

# Start implementing
touch src/index.ts
```

### 2. Implement Core Functionality

```typescript
// src/index.ts
import Fastify from 'fastify';
import { orderRoutes } from './routes/orders';

const fastify = Fastify({ logger: true });

// Register routes
fastify.register(orderRoutes);

// Start server
const start = async () => {
  try {
    await fastify.listen({ port: 3001, host: '0.0.0.0' });
    console.log('Distribution service running on port 3001');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
```

### 3. Add Tests

```typescript
// src/__tests__/orders.test.ts
import { describe, expect, it } from '@jest/globals';
import { OrderService } from '../services/OrderService';

describe('OrderService', () => {
  it('should create an order', async () => {
    const service = new OrderService();
    const order = await service.create({
      customerId: '123',
      items: [{ sku: 'ABC', quantity: 2 }]
    });

    expect(order).toBeDefined();
    expect(order.customerId).toBe('123');
  });
});
```

### 4. Run and Test

```bash
# Run service in dev mode
npm run dev

# In another terminal, test the endpoint
curl http://localhost:3001/api/orders

# Run tests
npm test
```

### 5. Use Shared Packages

```typescript
// Import from shared packages
import { Button } from '@brainsait/ui-components';
import { calculateVAT } from '@brainsait/saudi-compliance';
import { formatCurrency } from '@brainsait/bilingual-utils';
import { AuditLogger } from '@brainsait/audit-logger';

// Use them in your service
const vat = calculateVAT(100);
const formatted = formatCurrency(115, 'SAR', 'ar');
logger.logUserAction({ userId: '123', action: 'order.create', ... });
```

## Database Setup

### 1. Create Prisma Schema

```typescript
// services/distribution/prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Order {
  id         String   @id @default(uuid())
  customerId String
  status     String
  total      Float
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  items OrderItem[]
}

model OrderItem {
  id       String @id @default(uuid())
  orderId  String
  sku      String
  quantity Int
  price    Float

  order Order @relation(fields: [orderId], references: [id])
}
```

### 2. Run Migrations

```bash
cd services/distribution
npx prisma migrate dev --name init
npx prisma generate
```

### 3. Use in Code

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export class OrderService {
  async create(data: CreateOrderDto) {
    return prisma.order.create({
      data: {
        customerId: data.customerId,
        total: data.total,
        items: {
          create: data.items
        }
      },
      include: { items: true }
    });
  }
}
```

## Inter-Service Communication

### Event-Driven with Redis

```typescript
// services/distribution/src/events/publisher.ts
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export async function publishOrderCreated(order: Order) {
  await redis.publish('orders', JSON.stringify({
    type: 'order.created',
    data: order
  }));
}

// services/finance/src/events/subscriber.ts
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

redis.subscribe('orders');

redis.on('message', (channel, message) => {
  const event = JSON.parse(message);

  if (event.type === 'order.created') {
    // Generate invoice
    invoiceService.generateInvoice(event.data);
  }
});
```

## Docker Development

### Build and Run

```bash
# Build service image
docker build -t ssdp-distribution -f infrastructure/docker/Dockerfile.service services/distribution

# Run with docker-compose
docker-compose -f docker-compose.ssdp.yml up distribution-service
```

## Testing Strategy

### Unit Tests
```bash
# Test individual functions
npm test --workspace=@brainsait/saudi-compliance
```

### Integration Tests
```bash
# Test service APIs
npm test --workspace=@brainsait/service-distribution
```

### E2E Tests
```bash
# Test complete workflows
npm run test:e2e
```

## Deployment

### Cloudflare Workers

```bash
cd workers/payment
npm run deploy
```

### Services (Docker)

```bash
# Build
docker-compose -f docker-compose.ssdp.yml build

# Deploy to production
./scripts/deploy-production.sh
```

## Monitoring

### Add Metrics

```typescript
import { Counter, Histogram } from 'prom-client';

const orderCounter = new Counter({
  name: 'orders_created_total',
  help: 'Total orders created'
});

const orderDuration = new Histogram({
  name: 'order_creation_duration_seconds',
  help: 'Order creation duration'
});

// In your service
orderCounter.inc();
const end = orderDuration.startTimer();
await createOrder();
end();
```

## Tips for Success

1. **Start Small**: Pick one service and implement it fully before moving to the next
2. **Use Shared Packages**: Avoid duplication by using the shared packages
3. **Write Tests**: Add tests as you implement features
4. **Document**: Update READMEs as you add features
5. **Follow Patterns**: Use consistent patterns across services
6. **Use TypeScript**: Take advantage of type safety
7. **Event-Driven**: Use events for inter-service communication
8. **Audit Everything**: Use audit-logger for compliance

## Getting Help

- 📖 [Architecture Docs](./docs/architecture/SSDP_ARCHITECTURE.md)
- 📖 [Quick Start](./QUICKSTART.md)
- 📖 [API Docs](./docs/api/README.md)
- 🐛 [GitHub Issues](https://github.com/Fadil369/brainsait-store/issues)
- 📧 support@brainsait.io

---

**Ready to build? Pick a service and start coding!** 🚀
