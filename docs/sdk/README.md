# BrainSAIT Store SDK Documentation

## Overview

The BrainSAIT Store SDKs provide easy-to-use libraries for integrating with the BrainSAIT Store API in multiple programming languages.

## Available SDKs

### JavaScript/TypeScript SDK
- **Package**: `@brainsait/store-sdk`
- **Language**: JavaScript/TypeScript
- **Platform**: Browser, Node.js
- **Status**: Available

### Python SDK
- **Package**: `brainsait-store`
- **Language**: Python
- **Platform**: Python 3.9+
- **Status**: Available

### PHP SDK
- **Package**: `brainsait/store-sdk`
- **Language**: PHP
- **Platform**: PHP 8.0+
- **Status**: Coming Soon

### Go SDK
- **Package**: `github.com/brainsait/store-sdk-go`
- **Language**: Go
- **Platform**: Go 1.19+
- **Status**: Coming Soon

## JavaScript/TypeScript SDK

### Installation

```bash
# Using npm
npm install @brainsait/store-sdk

# Using yarn
yarn add @brainsait/store-sdk

# Using pnpm
pnpm add @brainsait/store-sdk
```

### Quick Start

```typescript
import { BrainSAITStore } from '@brainsait/store-sdk';

// Initialize the client
const store = new BrainSAITStore({
  apiKey: 'your-api-key',
  tenantId: 'your-tenant-id',
  baseURL: 'https://brainsait-api-gateway.fadil.workers.dev',
  timeout: 30000, // 30 seconds
  retries: 3
});

// Basic usage
async function example() {
  try {
    // Get products
    const products = await store.products.list();
    console.log('Products:', products);
    
    // Create an order
    const order = await store.orders.create({
      items: [{ productId: 'prod_123', quantity: 1 }],
      customerEmail: 'customer@example.com'
    });
    console.log('Order created:', order);
    
  } catch (error) {
    console.error('Error:', error);
  }
}

example();
```

### Configuration Options

```typescript
interface BrainSAITStoreConfig {
  apiKey: string;
  tenantId: string;
  baseURL?: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  debug?: boolean;
}

const store = new BrainSAITStore({
  apiKey: process.env.BRAINSAIT_API_KEY!,
  tenantId: process.env.BRAINSAIT_TENANT_ID!,
  baseURL: process.env.BRAINSAIT_API_URL,
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  debug: process.env.NODE_ENV === 'development'
});
```

### Products API

```typescript
// List products with pagination
const products = await store.products.list({
  page: 1,
  limit: 20,
  category: 'software',
  tags: ['ai', 'automation']
});

// Get single product
const product = await store.products.get('prod_123');

// Create product
const newProduct = await store.products.create({
  name: {
    en: 'AI Marketing Tool',
    ar: 'أداة التسويق بالذكاء الاصطناعي'
  },
  description: {
    en: 'Advanced AI-powered marketing automation',
    ar: 'أتمتة التسويق المتقدمة بالذكاء الاصطناعي'
  },
  price: 299.99,
  currency: 'USD',
  category: 'ai-tools',
  tags: ['ai', 'marketing', 'automation'],
  images: ['https://example.com/image1.jpg']
});

// Update product
const updatedProduct = await store.products.update('prod_123', {
  price: 199.99,
  tags: ['ai', 'marketing', 'automation', 'discounted']
});

// Delete product
await store.products.delete('prod_123');
```

### Orders API

```typescript
// List orders
const orders = await store.orders.list({
  status: 'completed',
  limit: 50,
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});

// Get single order
const order = await store.orders.get('order_123');

// Create order
const newOrder = await store.orders.create({
  items: [
    { productId: 'prod_123', quantity: 2, price: 299.99 },
    { productId: 'prod_456', quantity: 1, price: 199.99 }
  ],
  customerEmail: 'customer@example.com',
  customerName: 'John Doe',
  billingAddress: {
    line1: '123 Main St',
    city: 'Riyadh',
    country: 'SA',
    postalCode: '12345'
  },
  metadata: {
    source: 'website',
    campaign: 'summer-sale'
  }
});

// Update order status
const updatedOrder = await store.orders.update('order_123', {
  status: 'shipped',
  trackingNumber: 'TRK123456789'
});
```

### Payments API

```typescript
// Create Stripe payment intent
const stripeIntent = await store.payments.createStripeIntent({
  amount: 299.99,
  currency: 'USD',
  orderId: 'order_123',
  customerEmail: 'customer@example.com',
  metadata: {
    productId: 'prod_123'
  }
});

// Create PayPal order
const paypalOrder = await store.payments.createPayPalOrder({
  amount: 299.99,
  currency: 'USD',
  orderId: 'order_123',
  items: [
    {
      name: 'AI Marketing Tool',
      quantity: 1,
      price: 299.99
    }
  ]
});

// Get payment methods
const paymentMethods = await store.payments.getMethods();

// Process refund
const refund = await store.payments.refund('payment_123', {
  amount: 100.00,
  reason: 'customer_request'
});
```

### Analytics API

```typescript
// Get overview analytics
const overview = await store.analytics.getOverview({
  startDate: '2024-01-01',
  endDate: '2024-01-31',
  granularity: 'day'
});

// Get revenue analytics
const revenue = await store.analytics.getRevenue({
  startDate: '2024-01-01',
  endDate: '2024-01-31',
  groupBy: 'product'
});

// Get customer analytics
const customers = await store.analytics.getCustomers({
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});

// Export analytics data
const exportData = await store.analytics.export({
  type: 'revenue',
  format: 'csv',
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});
```

### Error Handling

```typescript
import { BrainSAITError, AuthenticationError, RateLimitError } from '@brainsait/store-sdk';

try {
  const products = await store.products.list();
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Authentication failed:', error.message);
    // Handle authentication error
  } else if (error instanceof RateLimitError) {
    console.error('Rate limit exceeded:', error.message);
    // Wait and retry
    await new Promise(resolve => setTimeout(resolve, error.retryAfter * 1000));
  } else if (error instanceof BrainSAITError) {
    console.error('API error:', error.message, error.code);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### TypeScript Types

```typescript
// Product types
interface Product {
  id: string;
  name: LocalizedString;
  description: LocalizedString;
  price: number;
  currency: string;
  category: string;
  tags: string[];
  images: string[];
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

interface LocalizedString {
  en: string;
  ar?: string;
}

// Order types
interface Order {
  id: string;
  status: OrderStatus;
  items: OrderItem[];
  customerEmail: string;
  customerName?: string;
  total: number;
  currency: string;
  createdAt: string;
  updatedAt: string;
}

type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
  name?: string;
}
```

## Python SDK

### Installation

```bash
# Using pip
pip install brainsait-store

# Using poetry
poetry add brainsait-store
```

### Quick Start

```python
from brainsait_store import BrainSAITStore
from brainsait_store.exceptions import BrainSAITError, AuthenticationError

# Initialize the client
store = BrainSAITStore(
    api_key='your-api-key',
    tenant_id='your-tenant-id',
    base_url='https://brainsait-api-gateway.fadil.workers.dev',
    timeout=30,
    retries=3
)

# Basic usage
try:
    # Get products
    products = store.products.list(page=1, limit=20)
    print(f"Found {len(products['data'])} products")
    
    # Create an order
    order = store.orders.create({
        'items': [{'product_id': 'prod_123', 'quantity': 1}],
        'customer_email': 'customer@example.com'
    })
    print(f"Order created: {order['id']}")
    
except AuthenticationError:
    print("Authentication failed - check your API key")
except BrainSAITError as e:
    print(f"API error: {e.message} ({e.code})")
```

### Configuration

```python
from brainsait_store import BrainSAITStore
import os

store = BrainSAITStore(
    api_key=os.environ['BRAINSAIT_API_KEY'],
    tenant_id=os.environ['BRAINSAIT_TENANT_ID'],
    base_url=os.environ.get('BRAINSAIT_API_URL'),
    timeout=30,
    retries=3,
    retry_delay=1.0,
    debug=os.environ.get('DEBUG', 'false').lower() == 'true'
)
```

### Products API

```python
# List products
products = store.products.list(
    page=1,
    limit=20,
    category='software',
    tags=['ai', 'automation']
)

# Get single product
product = store.products.get('prod_123')

# Create product
new_product = store.products.create({
    'name': {
        'en': 'AI Marketing Tool',
        'ar': 'أداة التسويق بالذكاء الاصطناعي'
    },
    'description': {
        'en': 'Advanced AI-powered marketing automation',
        'ar': 'أتمتة التسويق المتقدمة بالذكاء الاصطناعي'
    },
    'price': 299.99,
    'currency': 'USD',
    'category': 'ai-tools',
    'tags': ['ai', 'marketing', 'automation']
})

# Update product
updated_product = store.products.update('prod_123', {
    'price': 199.99
})

# Delete product
store.products.delete('prod_123')
```

### Orders API

```python
# List orders
orders = store.orders.list(
    status='completed',
    limit=50,
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# Create order
new_order = store.orders.create({
    'items': [
        {'product_id': 'prod_123', 'quantity': 2, 'price': 299.99}
    ],
    'customer_email': 'customer@example.com',
    'customer_name': 'John Doe',
    'billing_address': {
        'line1': '123 Main St',
        'city': 'Riyadh',
        'country': 'SA',
        'postal_code': '12345'
    }
})
```

### Analytics API

```python
# Get overview analytics
overview = store.analytics.get_overview(
    start_date='2024-01-01',
    end_date='2024-01-31',
    granularity='day'
)

# Get revenue analytics
revenue = store.analytics.get_revenue(
    start_date='2024-01-01',
    end_date='2024-01-31',
    group_by='product'
)

# Export data
export_data = store.analytics.export(
    type='revenue',
    format='csv',
    start_date='2024-01-01',
    end_date='2024-01-31'
)
```

### Async Support

```python
import asyncio
from brainsait_store import AsyncBrainSAITStore

async def main():
    store = AsyncBrainSAITStore(
        api_key='your-api-key',
        tenant_id='your-tenant-id'
    )
    
    # Async operations
    products = await store.products.list()
    order = await store.orders.create({
        'items': [{'product_id': 'prod_123', 'quantity': 1}],
        'customer_email': 'customer@example.com'
    })
    
    await store.close()  # Clean up aiohttp session

# Run async function
asyncio.run(main())
```

## SDK Development

### Building Your Own SDK

If you need an SDK for a language we don't support yet, here's a basic structure:

#### 1. HTTP Client Setup
```python
import requests
from typing import Dict, Any, Optional

class BrainSAITClient:
    def __init__(self, api_key: str, tenant_id: str, base_url: str = None):
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.base_url = base_url or 'https://brainsait-api-gateway.fadil.workers.dev'
        self.session = requests.Session()
        
    def _headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'X-Tenant-ID': self.tenant_id,
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = self._headers()
        
        response = self.session.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        
        return response.json()
```

#### 2. Resource Classes
```python
class ProductsResource:
    def __init__(self, client: BrainSAITClient):
        self.client = client
    
    def list(self, **params) -> Dict[str, Any]:
        return self.client._request('GET', '/api/v1/store/products', params=params)
    
    def get(self, product_id: str) -> Dict[str, Any]:
        return self.client._request('GET', f'/api/v1/store/products/{product_id}')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.client._request('POST', '/api/v1/store/products', json=data)
```

#### 3. Main SDK Class
```python
class BrainSAITStore:
    def __init__(self, api_key: str, tenant_id: str, **kwargs):
        self.client = BrainSAITClient(api_key, tenant_id, **kwargs)
        self.products = ProductsResource(self.client)
        self.orders = OrdersResource(self.client)
        self.analytics = AnalyticsResource(self.client)
```

### Contributing to SDKs

We welcome contributions to our SDKs! Here's how to contribute:

1. **Fork the repository**
2. **Create a feature branch**
3. **Add tests for new functionality**
4. **Update documentation**
5. **Submit a pull request**

#### Development Setup
```bash
# JavaScript SDK
git clone https://github.com/brainsait/store-sdk-js
cd store-sdk-js
npm install
npm test

# Python SDK
git clone https://github.com/brainsait/store-sdk-python
cd store-sdk-python
pip install -e ".[dev]"
pytest
```

## Support and Community

### Getting Help
- **Documentation**: [docs.brainsait.io](https://docs.brainsait.io)
- **GitHub Issues**: Report bugs and request features
- **Discord Community**: Join our developer community
- **Email Support**: sdk-support@brainsait.io

### SDK Roadmap
- ✅ JavaScript/TypeScript SDK
- ✅ Python SDK
- 🚧 PHP SDK (Q2 2024)
- 🚧 Go SDK (Q2 2024)
- 📋 .NET SDK (Q3 2024)
- 📋 Ruby SDK (Q3 2024)

### Version Compatibility

| SDK Version | API Version | Min Language Version |
|-------------|-------------|---------------------|
| 1.x.x       | v1          | Node.js 16+, Python 3.9+ |
| 2.x.x       | v2          | Node.js 18+, Python 3.11+ |

## Next Steps

- [Integration Guide](../integration/README.md)
- [API Reference](../api/README.md)
- [Sample Applications](./examples/README.md)
- [Migration Guide](./migration.md)