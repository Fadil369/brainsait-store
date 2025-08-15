# BrainSAIT Store API Documentation

## Overview

The BrainSAIT Store API is a comprehensive B2B SaaS platform API built with FastAPI, featuring multi-tenant architecture with Arabic/English support.

## Quick Start

### Base URL
- **Production**: `https://brainsait-api-gateway.fadil.workers.dev`
- **Development**: `http://localhost:8000`

### Authentication
All API endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Multi-tenant Support
Include the tenant ID in the header for all requests:

```
X-Tenant-ID: <your_tenant_id>
```

## API Documentation

### Interactive Documentation
- **Swagger UI**: `/api/docs` - Interactive API documentation
- **ReDoc**: `/api/redoc` - Alternative documentation interface
- **OpenAPI Schema**: `/api/openapi.json` - Raw OpenAPI specification

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns the system health status and version information.

#### Authentication
```http
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
```

#### Store Management
```http
GET /api/v1/store/products
POST /api/v1/store/products
PUT /api/v1/store/products/{id}
DELETE /api/v1/store/products/{id}
```

#### Payments
```http
POST /api/v1/payments/stripe/create-payment-intent
POST /api/v1/payments/paypal/create-order
GET /api/v1/payments/methods
```

#### Analytics
```http
GET /api/v1/analytics/overview
GET /api/v1/analytics/revenue
GET /api/v1/analytics/customers
```

## Rate Limiting

The API implements rate limiting:
- **Default**: 120 requests per minute per IP
- **Authenticated**: Higher limits based on subscription tier

## Error Handling

The API uses standard HTTP status codes and returns errors in JSON format:

```json
{
  "detail": "Error message",
  "type": "error_type",
  "code": "ERROR_CODE"
}
```

## Supported Languages

The API supports bilingual content:
- **English** (default): `Accept-Language: en`
- **Arabic**: `Accept-Language: ar`

## Next Steps

- [Integration Guide](../integration/README.md)
- [Authentication Guide](../integration/authentication.md)
- [Webhook Guide](../integration/webhooks.md)
- [SDK Documentation](../sdk/README.md)