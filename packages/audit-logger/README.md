# Audit Logger Package

Compliance audit logging utility for BrainSAIT applications.

## Features

- Structured audit logging
- Compliance-ready log format
- Multi-level logging (info, warn, error)
- User action tracking
- GDPR/Privacy compliance
- Log retention policies
- Tamper-proof logging
- Export capabilities (JSON, CSV)

## Log Types

### User Actions
- Authentication (login, logout, failed attempts)
- Authorization (permission checks)
- Data access (read, create, update, delete)
- Configuration changes

### System Events
- Service start/stop
- Errors and exceptions
- Performance metrics
- Security events

### Business Events
- Order creation/updates
- Payment transactions
- Invoice generation
- Data exports

## Usage

### Basic Logging

```typescript
import { AuditLogger } from '@brainsait/audit-logger';

const logger = new AuditLogger({
  serviceName: 'distribution-service',
  environment: 'production'
});

// Log user action
logger.logUserAction({
  userId: '123',
  action: 'order.create',
  resource: 'order',
  resourceId: 'ORD-456',
  metadata: {
    total: 1500.00,
    items: 5
  }
});
```

### Security Events

```typescript
logger.logSecurityEvent({
  type: 'authentication',
  severity: 'high',
  userId: '123',
  action: 'failed_login_attempt',
  ipAddress: '192.168.1.1',
  metadata: {
    reason: 'invalid_password',
    attempts: 3
  }
});
```

### Data Access Logging

```typescript
logger.logDataAccess({
  userId: '123',
  action: 'read',
  resource: 'customer',
  resourceId: 'CUST-789',
  fields: ['name', 'email', 'phone'],
  reason: 'customer_support_inquiry'
});
```

### Query Audit Logs

```typescript
// Get logs for specific user
const userLogs = await logger.queryLogs({
  userId: '123',
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});

// Get security events
const securityEvents = await logger.queryLogs({
  type: 'security',
  severity: 'high'
});

// Export logs
await logger.exportLogs({
  format: 'csv',
  startDate: '2024-01-01',
  endDate: '2024-12-31',
  output: './audit-logs-2024.csv'
});
```

## Configuration

```typescript
const logger = new AuditLogger({
  serviceName: 'my-service',
  environment: 'production',
  retention: 365, // days
  storage: {
    type: 'postgres',
    url: process.env.DATABASE_URL
  },
  encryption: {
    enabled: true,
    key: process.env.ENCRYPTION_KEY
  }
});
```

## Development

```bash
npm install
npm run dev
```

## Testing

```bash
npm test
```
