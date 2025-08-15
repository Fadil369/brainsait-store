# Webhook Integration Guide

## Overview

BrainSAIT Store webhooks allow your application to receive real-time notifications when events occur in the platform. This guide covers webhook setup, verification, and handling.

## Webhook Events

### Available Events

#### Payment Events
- `payment.completed` - Payment successfully processed
- `payment.failed` - Payment processing failed
- `payment.refunded` - Payment refunded

#### Order Events
- `order.created` - New order created
- `order.updated` - Order status changed
- `order.cancelled` - Order cancelled
- `order.shipped` - Order shipped

#### User Events
- `user.created` - New user registered
- `user.updated` - User profile updated
- `user.deleted` - User account deleted

#### Tenant Events
- `tenant.created` - New tenant created
- `tenant.updated` - Tenant settings updated
- `tenant.suspended` - Tenant suspended

### Event Structure

All webhook events follow this structure:
```json
{
  "id": "evt_1234567890",
  "event": "payment.completed",
  "created": "2024-01-15T10:30:00Z",
  "data": {
    "object": {
      "id": "pay_abc123",
      "amount": 29999,
      "currency": "USD",
      "status": "completed",
      "customer_email": "customer@example.com"
    }
  },
  "tenant_id": "company_xyz",
  "api_version": "2024-01-01"
}
```

## Setting Up Webhooks

### 1. Configure Webhook Endpoint

#### Admin Panel Configuration
1. Login to admin panel
2. Navigate to **Settings** → **Webhooks**
3. Click **Add Webhook Endpoint**
4. Configure:
   - **URL**: Your webhook endpoint URL
   - **Events**: Select events to subscribe to
   - **Secret**: Webhook signing secret (generated automatically)
   - **Active**: Enable/disable webhook

#### API Configuration
```javascript
// Create webhook endpoint via API
const webhook = await fetch('/api/v1/webhooks', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': 'your-tenant-id',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://your-app.com/webhooks/brainsait',
    events: ['payment.completed', 'order.created'],
    description: 'Main webhook endpoint'
  })
});
```

### 2. Webhook Endpoint Implementation

#### Express.js Implementation
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

// Use raw body parser for webhook verification
app.use('/webhooks', express.raw({ type: 'application/json' }));

const WEBHOOK_SECRET = process.env.BRAINSAIT_WEBHOOK_SECRET;

function verifyWebhookSignature(payload, signature) {
  const expectedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}

app.post('/webhooks/brainsait', (req, res) => {
  const signature = req.headers['x-brainsait-signature'];
  const payload = req.body;
  
  // Verify webhook signature
  if (!verifyWebhookSignature(payload, signature)) {
    console.error('Invalid webhook signature');
    return res.status(401).send('Invalid signature');
  }
  
  const event = JSON.parse(payload.toString());
  
  try {
    handleWebhookEvent(event);
    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook handling error:', error);
    res.status(500).send('Internal server error');
  }
});

function handleWebhookEvent(event) {
  switch (event.event) {
    case 'payment.completed':
      handlePaymentCompleted(event.data.object);
      break;
    case 'order.created':
      handleOrderCreated(event.data.object);
      break;
    case 'user.created':
      handleUserCreated(event.data.object);
      break;
    default:
      console.log(`Unhandled event type: ${event.event}`);
  }
}

function handlePaymentCompleted(payment) {
  console.log('Payment completed:', payment.id);
  
  // Update local database
  // Send confirmation email
  // Update analytics
  // Fulfill order
}

function handleOrderCreated(order) {
  console.log('New order created:', order.id);
  
  // Process inventory
  // Send order confirmation
  // Update CRM
  // Generate invoice
}
```

#### Python Flask Implementation
```python
from flask import Flask, request, abort
import hmac
import hashlib
import json
import os

app = Flask(__name__)
WEBHOOK_SECRET = os.environ.get('BRAINSAIT_WEBHOOK_SECRET')

def verify_webhook_signature(payload, signature):
    """Verify webhook signature"""
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@app.route('/webhooks/brainsait', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-BrainSAIT-Signature')
    payload = request.get_data()
    
    if not verify_webhook_signature(payload, signature):
        abort(401, 'Invalid signature')
    
    try:
        event = json.loads(payload.decode())
        handle_webhook_event(event)
        return 'OK', 200
    except Exception as e:
        print(f'Webhook error: {e}')
        return 'Error', 500

def handle_webhook_event(event):
    """Handle different webhook events"""
    event_type = event['event']
    data = event['data']['object']
    
    handlers = {
        'payment.completed': handle_payment_completed,
        'order.created': handle_order_created,
        'user.created': handle_user_created,
    }
    
    handler = handlers.get(event_type)
    if handler:
        handler(data)
    else:
        print(f'Unhandled event type: {event_type}')

def handle_payment_completed(payment):
    """Handle completed payment"""
    print(f'Payment completed: {payment["id"]}')
    
    # Update order status
    # Send receipt email
    # Update analytics
    # Process fulfillment

def handle_order_created(order):
    """Handle new order"""
    print(f'Order created: {order["id"]}')
    
    # Validate inventory
    # Create fulfillment task
    # Send confirmation
    # Update CRM
```

#### Next.js API Route Implementation
```typescript
// pages/api/webhooks/brainsait.ts
import { NextApiRequest, NextApiResponse } from 'next';
import crypto from 'crypto';

const WEBHOOK_SECRET = process.env.BRAINSAIT_WEBHOOK_SECRET!;

interface WebhookEvent {
  id: string;
  event: string;
  created: string;
  data: {
    object: any;
  };
  tenant_id: string;
}

function verifySignature(payload: string, signature: string): boolean {
  const expectedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const signature = req.headers['x-brainsait-signature'] as string;
  const payload = JSON.stringify(req.body);
  
  if (!verifySignature(payload, signature)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  try {
    const event: WebhookEvent = req.body;
    await handleWebhookEvent(event);
    res.status(200).json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

async function handleWebhookEvent(event: WebhookEvent) {
  switch (event.event) {
    case 'payment.completed':
      await handlePaymentCompleted(event.data.object);
      break;
    case 'order.created':
      await handleOrderCreated(event.data.object);
      break;
    default:
      console.log(`Unhandled event: ${event.event}`);
  }
}
```

## Event Details

### Payment Events

#### payment.completed
```json
{
  "event": "payment.completed",
  "data": {
    "object": {
      "id": "pay_1234567890",
      "amount": 29999,
      "currency": "USD",
      "status": "completed",
      "payment_method": "stripe",
      "customer_email": "customer@example.com",
      "order_id": "ord_1234567890",
      "created_at": "2024-01-15T10:30:00Z",
      "metadata": {
        "order_number": "ORD-2024-001"
      }
    }
  }
}
```

#### payment.failed
```json
{
  "event": "payment.failed",
  "data": {
    "object": {
      "id": "pay_1234567890",
      "amount": 29999,
      "currency": "USD",
      "status": "failed",
      "error_code": "card_declined",
      "error_message": "Your card was declined",
      "customer_email": "customer@example.com",
      "order_id": "ord_1234567890"
    }
  }
}
```

### Order Events

#### order.created
```json
{
  "event": "order.created",
  "data": {
    "object": {
      "id": "ord_1234567890",
      "number": "ORD-2024-001",
      "status": "pending",
      "total": 299.99,
      "currency": "USD",
      "customer": {
        "email": "customer@example.com",
        "name": "John Doe"
      },
      "items": [
        {
          "product_id": "prod_123",
          "name": "AI Marketing Tool",
          "quantity": 1,
          "price": 299.99
        }
      ],
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

## Error Handling

### Retry Logic
BrainSAIT Store automatically retries failed webhook deliveries:

- **Initial delivery**: Immediate
- **Retry 1**: After 5 minutes
- **Retry 2**: After 30 minutes  
- **Retry 3**: After 2 hours
- **Retry 4**: After 12 hours
- **Retry 5**: After 24 hours

### Status Codes
Your webhook endpoint should respond with:
- **200-299**: Success (stops retries)
- **300-399**: Redirect (treated as failure, retries)
- **400-499**: Client error (stops retries, except 429)
- **429**: Rate limited (retries with backoff)
- **500-599**: Server error (retries)

### Error Response Handling
```javascript
app.post('/webhooks/brainsait', async (req, res) => {
  try {
    const event = req.body;
    await processWebhook(event);
    
    // Success
    res.status(200).send('OK');
  } catch (error) {
    if (error.code === 'TEMPORARY_ERROR') {
      // Temporary error - let BrainSAIT retry
      res.status(500).send('Temporary error');
    } else {
      // Permanent error - don't retry
      res.status(400).send('Permanent error');
    }
  }
});
```

## Security Best Practices

### Signature Verification
Always verify webhook signatures:

```javascript
function verifyWebhook(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  
  // Use timing-safe comparison
  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}
```

### HTTPS Only
- **Always use HTTPS** for webhook endpoints
- **Verify SSL certificates** in production
- **Use secure headers** (HSTS, CSP, etc.)

### Rate Limiting
Implement rate limiting on webhook endpoints:

```javascript
const rateLimit = require('express-rate-limit');

const webhookLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many webhook requests'
});

app.use('/webhooks', webhookLimiter);
```

## Testing Webhooks

### Webhook Testing Tools

#### Local Development with ngrok
```bash
# Install ngrok
npm install -g ngrok

# Expose local server
ngrok http 3000

# Use the generated URL for webhook endpoint
# https://abc123.ngrok.io/webhooks/brainsait
```

#### Webhook Testing Service
```javascript
// Test webhook endpoint
async function testWebhook() {
  const testEvent = {
    id: 'evt_test_123',
    event: 'payment.completed',
    created: new Date().toISOString(),
    data: {
      object: {
        id: 'pay_test_123',
        amount: 2999,
        currency: 'USD',
        status: 'completed'
      }
    },
    tenant_id: 'test_tenant'
  };
  
  const signature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(JSON.stringify(testEvent))
    .digest('hex');
  
  const response = await fetch('http://localhost:3000/webhooks/brainsait', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-BrainSAIT-Signature': signature
    },
    body: JSON.stringify(testEvent)
  });
  
  console.log('Test response:', response.status);
}
```

### Unit Testing
```javascript
// Jest test for webhook handler
describe('Webhook Handler', () => {
  test('should handle payment.completed event', async () => {
    const event = {
      event: 'payment.completed',
      data: {
        object: {
          id: 'pay_123',
          amount: 2999,
          status: 'completed'
        }
      }
    };
    
    const result = await handleWebhookEvent(event);
    expect(result).toBe(true);
  });
  
  test('should verify signature correctly', () => {
    const payload = '{"test": "data"}';
    const secret = 'test_secret';
    const signature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');
    
    expect(verifyWebhookSignature(payload, signature, secret)).toBe(true);
  });
});
```

## Monitoring Webhooks

### Webhook Logs
Monitor webhook delivery in the admin panel:
- **Delivery Status**: Success/failure rates
- **Response Times**: Endpoint performance
- **Error Logs**: Failed delivery details
- **Retry History**: Retry attempt tracking

### Alerting
Set up alerts for:
- **High failure rates** (>5% failures)
- **Slow responses** (>5 second response time)
- **Endpoint downtime** (multiple consecutive failures)

### Metrics to Track
```javascript
// Example webhook metrics
const webhookMetrics = {
  total_deliveries: 1000,
  successful_deliveries: 950,
  failed_deliveries: 50,
  average_response_time: 250, // milliseconds
  retry_rate: 0.05,
  endpoints: {
    'https://app.example.com/webhooks': {
      success_rate: 0.95,
      avg_response_time: 200
    }
  }
};
```

## Best Practices

### Idempotency
Handle duplicate webhook deliveries:

```javascript
const processedEvents = new Set();

function handleWebhookEvent(event) {
  // Check if event already processed
  if (processedEvents.has(event.id)) {
    console.log(`Event ${event.id} already processed`);
    return;
  }
  
  // Process event
  processEvent(event);
  
  // Mark as processed
  processedEvents.add(event.id);
}
```

### Async Processing
Use queues for heavy processing:

```javascript
const Queue = require('bull');
const webhookQueue = new Queue('webhook processing');

app.post('/webhooks/brainsait', (req, res) => {
  // Quickly acknowledge receipt
  res.status(200).send('OK');
  
  // Queue for async processing
  webhookQueue.add('process-webhook', req.body);
});

webhookQueue.process('process-webhook', async (job) => {
  const event = job.data;
  await processWebhookEvent(event);
});
```

### Error Logging
Comprehensive error logging:

```javascript
function handleWebhookError(error, event) {
  console.error('Webhook processing error:', {
    error: error.message,
    stack: error.stack,
    event_id: event.id,
    event_type: event.event,
    tenant_id: event.tenant_id,
    timestamp: new Date().toISOString()
  });
}
```