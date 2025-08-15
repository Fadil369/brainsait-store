# Integration Guide - BrainSAIT Store API

## Overview

This guide provides comprehensive instructions for integrating with the BrainSAIT Store API, including authentication, webhooks, and common integration patterns.

## Quick Start Integration

### 1. API Access Setup

#### Get API Credentials
1. Login to your admin panel at `https://store.brainsait.io/admin`
2. Navigate to **Settings** → **API Keys**
3. Generate a new API key with appropriate scopes
4. Save your API key securely

#### Basic Authentication
```bash
# Test API access
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "X-Tenant-ID: your-tenant-id" \
     https://brainsait-api-gateway.fadil.workers.dev/health
```

### 2. Environment Setup

#### Production Environment
```bash
API_BASE_URL="https://brainsait-api-gateway.fadil.workers.dev"
API_KEY="your-production-api-key"
TENANT_ID="your-tenant-id"
```

#### Development Environment
```bash
API_BASE_URL="http://localhost:8000"
API_KEY="your-development-api-key"
TENANT_ID="your-tenant-id"
```

## Authentication Guide

### JWT Token Authentication

#### Login and Get Token
```javascript
// JavaScript/Node.js example
const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': 'your-tenant-id'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});

const { access_token, refresh_token } = await response.json();
```

#### Using Access Token
```javascript
// Include token in subsequent requests
const apiCall = await fetch(`${API_BASE_URL}/api/v1/store/products`, {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'X-Tenant-ID': 'your-tenant-id'
  }
});
```

#### Token Refresh
```javascript
// Refresh expired token
const refreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': 'your-tenant-id'
  },
  body: JSON.stringify({
    refresh_token: refresh_token
  })
});

const { access_token: new_token } = await refreshResponse.json();
```

### API Key Authentication

#### For Server-to-Server Communication
```python
# Python example
import requests

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'X-Tenant-ID': 'your-tenant-id',
    'Content-Type': 'application/json'
}

response = requests.get(
    f'{API_BASE_URL}/api/v1/analytics/overview',
    headers=headers
)

data = response.json()
```

## Core API Integration Patterns

### 1. Product Management

#### Fetch Products
```javascript
async function getProducts(page = 1, limit = 20) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/store/products?page=${page}&limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': tenantId
      }
    }
  );
  
  return await response.json();
}
```

#### Create Product
```javascript
async function createProduct(productData) {
  const response = await fetch(`${API_BASE_URL}/api/v1/store/products`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': tenantId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(productData)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// Example usage
const newProduct = await createProduct({
  name: {
    en: "Digital Marketing Tool",
    ar: "أداة التسويق الرقمي"
  },
  description: {
    en: "Comprehensive digital marketing automation",
    ar: "أتمتة شاملة للتسويق الرقمي"
  },
  price: 299.99,
  currency: "USD",
  category: "software",
  tags: ["marketing", "automation", "digital"]
});
```

### 2. Payment Integration

#### Create Payment Intent (Stripe)
```javascript
async function createPaymentIntent(amount, currency = 'USD') {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/payments/stripe/create-payment-intent`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': tenantId,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount: amount * 100, // Stripe expects cents
        currency: currency.toLowerCase()
      })
    }
  );
  
  return await response.json();
}
```

#### Process PayPal Order
```javascript
async function createPayPalOrder(items) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/payments/paypal/create-order`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': tenantId,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        items,
        currency: 'USD'
      })
    }
  );
  
  return await response.json();
}
```

### 3. Analytics Integration

#### Get Analytics Overview
```python
# Python example for analytics
def get_analytics_overview(date_range=None):
    params = {}
    if date_range:
        params['start_date'] = date_range['start']
        params['end_date'] = date_range['end']
    
    response = requests.get(
        f'{API_BASE_URL}/api/v1/analytics/overview',
        headers=headers,
        params=params
    )
    
    return response.json()

# Usage
analytics = get_analytics_overview({
    'start': '2024-01-01',
    'end': '2024-01-31'
})
```

## Webhook Integration

### Setting Up Webhooks

#### Configure Webhook Endpoints
1. Navigate to **Settings** → **Webhooks** in admin panel
2. Add your webhook endpoint URL
3. Select events to subscribe to
4. Configure webhook secret for verification

#### Webhook Events
```json
{
  "events": [
    "payment.completed",
    "payment.failed",
    "order.created",
    "order.updated",
    "user.created",
    "tenant.updated"
  ]
}
```

### Webhook Implementation

#### Express.js Webhook Handler
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

// Webhook secret from admin panel
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;

// Middleware to verify webhook signature
function verifyWebhookSignature(req, res, next) {
  const signature = req.headers['x-webhook-signature'];
  const payload = JSON.stringify(req.body);
  
  const expectedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');
  
  if (signature !== `sha256=${expectedSignature}`) {
    return res.status(401).send('Invalid signature');
  }
  
  next();
}

// Webhook endpoint
app.post('/webhook/brainsait', verifyWebhookSignature, (req, res) => {
  const { event, data } = req.body;
  
  switch (event) {
    case 'payment.completed':
      handlePaymentCompleted(data);
      break;
    case 'order.created':
      handleOrderCreated(data);
      break;
    default:
      console.log(`Unhandled event: ${event}`);
  }
  
  res.status(200).send('OK');
});

function handlePaymentCompleted(data) {
  console.log('Payment completed:', data);
  // Update local database, send notifications, etc.
}

function handleOrderCreated(data) {
  console.log('Order created:', data);
  // Process new order, update inventory, etc.
}
```

#### Python Flask Webhook Handler
```python
from flask import Flask, request, abort
import hmac
import hashlib
import json

app = Flask(__name__)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')

def verify_signature(payload, signature):
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f'sha256={expected_signature}', signature)

@app.route('/webhook/brainsait', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.get_data()
    
    if not verify_signature(payload, signature):
        abort(401)
    
    data = request.json
    event = data.get('event')
    
    if event == 'payment.completed':
        handle_payment_completed(data['data'])
    elif event == 'order.created':
        handle_order_created(data['data'])
    
    return 'OK', 200
```

## SDK Examples

### JavaScript/TypeScript SDK

#### Installation
```bash
npm install @brainsait/store-sdk
```

#### Usage
```typescript
import { BrainSAITStore } from '@brainsait/store-sdk';

const store = new BrainSAITStore({
  apiKey: 'your-api-key',
  tenantId: 'your-tenant-id',
  baseURL: 'https://brainsait-api-gateway.fadil.workers.dev'
});

// Get products
const products = await store.products.list({
  page: 1,
  limit: 20,
  category: 'software'
});

// Create order
const order = await store.orders.create({
  items: [
    { productId: 'prod_123', quantity: 1 }
  ],
  customerEmail: 'customer@example.com'
});

// Process payment
const payment = await store.payments.createStripeIntent({
  amount: 299.99,
  currency: 'USD',
  orderId: order.id
});
```

### Python SDK

#### Installation
```bash
pip install brainsait-store
```

#### Usage
```python
from brainsait_store import BrainSAITStore

store = BrainSAITStore(
    api_key='your-api-key',
    tenant_id='your-tenant-id',
    base_url='https://brainsait-api-gateway.fadil.workers.dev'
)

# Get analytics
analytics = store.analytics.get_overview(
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# Create product
product = store.products.create({
    'name': {'en': 'AI Tool', 'ar': 'أداة الذكاء الاصطناعي'},
    'price': 199.99,
    'category': 'ai-tools'
})

# Get orders
orders = store.orders.list(
    status='completed',
    limit=50
)
```

## Integration Patterns

### 1. E-commerce Integration

#### WooCommerce Plugin Example
```php
<?php
// WooCommerce integration
class BrainSAIT_WooCommerce_Integration {
    private $api_client;
    
    public function __construct() {
        $this->api_client = new BrainSAIT_API_Client(
            get_option('brainsait_api_key'),
            get_option('brainsait_tenant_id')
        );
        
        add_action('woocommerce_order_status_completed', [$this, 'sync_order']);
    }
    
    public function sync_order($order_id) {
        $order = wc_get_order($order_id);
        
        $this->api_client->orders->create([
            'external_id' => $order_id,
            'customer_email' => $order->get_billing_email(),
            'total' => $order->get_total(),
            'items' => $this->get_order_items($order)
        ]);
    }
}
```

### 2. CRM Integration

#### Salesforce Integration
```javascript
// Salesforce integration example
class SalesforceBrainSAITSync {
  constructor(salesforceClient, brainSAITClient) {
    this.sf = salesforceClient;
    this.bs = brainSAITClient;
  }
  
  async syncOpportunities() {
    const opportunities = await this.sf.query(
      "SELECT Id, Name, Amount, StageName FROM Opportunity WHERE StageName = 'Closed Won'"
    );
    
    for (const opp of opportunities.records) {
      await this.bs.orders.create({
        externalId: opp.Id,
        amount: opp.Amount,
        source: 'salesforce'
      });
    }
  }
}
```

## Error Handling

### Common Error Responses
```json
{
  "detail": "Authentication required",
  "type": "authentication_error",
  "code": "AUTH_001"
}
```

### Error Handling Best Practices
```javascript
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`API Error: ${error.detail} (${error.code})`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    
    // Implement retry logic for transient errors
    if (error.code === 'RATE_LIMIT_EXCEEDED') {
      await new Promise(resolve => setTimeout(resolve, 60000));
      return apiCall(endpoint, options); // Retry after 1 minute
    }
    
    throw error;
  }
}
```

## Rate Limiting

### Rate Limit Headers
```javascript
function handleRateLimit(response) {
  const remaining = response.headers.get('X-Rate-Limit-Remaining');
  const resetTime = response.headers.get('X-Rate-Limit-Reset');
  
  console.log(`Requests remaining: ${remaining}`);
  console.log(`Rate limit resets at: ${new Date(resetTime * 1000)}`);
}
```

### Rate Limit Best Practices
- **Exponential Backoff**: Implement exponential backoff for retries
- **Request Queuing**: Queue requests to avoid hitting limits
- **Caching**: Cache responses to reduce API calls
- **Batch Operations**: Use batch endpoints when available

## Testing

### Integration Testing
```javascript
// Jest test example
describe('BrainSAIT API Integration', () => {
  test('should create and retrieve product', async () => {
    const product = await store.products.create({
      name: { en: 'Test Product' },
      price: 99.99
    });
    
    expect(product.id).toBeDefined();
    
    const retrieved = await store.products.get(product.id);
    expect(retrieved.name.en).toBe('Test Product');
  });
});
```

### Mock API for Development
```javascript
// Mock server for development
const mockServer = require('json-server');
const server = mockServer.create();

server.get('/api/v1/store/products', (req, res) => {
  res.json({
    data: [
      { id: 1, name: { en: 'Mock Product' }, price: 99.99 }
    ],
    pagination: { page: 1, total: 1 }
  });
});

server.listen(3001);
```

## Security Best Practices

### API Key Security
- **Environment Variables**: Store API keys in environment variables
- **Key Rotation**: Regularly rotate API keys
- **Scope Limitation**: Use minimal required scopes
- **Audit Logging**: Monitor API key usage

### Data Validation
```javascript
// Validate data before sending to API
function validateProductData(product) {
  const required = ['name', 'price', 'category'];
  
  for (const field of required) {
    if (!product[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  if (typeof product.price !== 'number' || product.price <= 0) {
    throw new Error('Price must be a positive number');
  }
}
```

## Next Steps

- [SDK Documentation](../sdk/README.md)
- [Webhook Reference](./webhooks.md)
- [Authentication Details](./authentication.md)
- [API Reference](../api/README.md)