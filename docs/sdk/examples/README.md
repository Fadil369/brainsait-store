# Sample Applications and Integration Examples

## Overview

This section provides practical sample applications and code examples demonstrating real-world integration patterns with the BrainSAIT Store API.

## Quick Start Examples

### React Frontend Integration
```typescript
// Complete product listing with cart functionality
import { BrainSAITStore } from '@brainsait/store-sdk';

const store = new BrainSAITStore({
  apiKey: process.env.REACT_APP_BRAINSAIT_API_KEY,
  tenantId: process.env.REACT_APP_BRAINSAIT_TENANT_ID
});

export const ProductList = () => {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    const fetchProducts = async () => {
      const response = await store.products.list({ limit: 20 });
      setProducts(response.data);
    };
    fetchProducts();
  }, []);

  return (
    <div className="products-grid">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
};
```

### Node.js Webhook Handler
```javascript
// Express webhook handler with signature verification
const express = require('express');
const crypto = require('crypto');

app.post('/webhooks/brainsait', express.raw({type: 'application/json'}), (req, res) => {
  const signature = req.headers['x-brainsait-signature'];
  const payload = req.body;
  
  // Verify webhook signature
  const expectedSignature = crypto
    .createHmac('sha256', process.env.WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');
  
  if (signature === expectedSignature) {
    const event = JSON.parse(payload);
    handleWebhookEvent(event);
    res.status(200).send('OK');
  } else {
    res.status(401).send('Invalid signature');
  }
});
```

### Python Django Integration
```python
# Django model sync with BrainSAIT Store
from brainsait_store import BrainSAITStore

class ProductService:
    def __init__(self, tenant):
        self.store = BrainSAITStore(
            api_key=tenant.api_key,
            tenant_id=tenant.brainsait_id
        )
    
    def sync_products(self):
        """Sync products from BrainSAIT to local database"""
        products = self.store.products.list()
        
        for product_data in products['data']:
            Product.objects.update_or_create(
                brainsait_id=product_data['id'],
                defaults={
                    'name': product_data['name']['en'],
                    'price': product_data['price'],
                    'updated_at': timezone.now()
                }
            )
```

### WordPress Plugin
```php
// WordPress shortcode for product display
function brainsait_products_shortcode($atts) {
    $atts = shortcode_atts([
        'category' => '',
        'limit' => 12
    ], $atts);
    
    $api_key = get_option('brainsait_api_key');
    $tenant_id = get_option('brainsait_tenant_id');
    
    $response = wp_remote_get("https://brainsait-api-gateway.fadil.workers.dev/api/v1/store/products", [
        'headers' => [
            'Authorization' => "Bearer {$api_key}",
            'X-Tenant-ID' => $tenant_id
        ]
    ]);
    
    $products = json_decode(wp_remote_retrieve_body($response), true);
    
    ob_start();
    foreach ($products['data'] as $product) {
        echo "<div class='product-card'>";
        echo "<h3>{$product['name']['en']}</h3>";
        echo "<p>\${$product['price']}</p>";
        echo "</div>";
    }
    return ob_get_clean();
}
add_shortcode('brainsait_products', 'brainsait_products_shortcode');
```

## Advanced Integration Patterns

### Microservices Architecture
```typescript
// Order processing microservice
class OrderProcessor {
  private brainSAIT: BrainSAITStore;
  
  constructor() {
    this.brainSAIT = new BrainSAITStore({
      apiKey: process.env.BRAINSAIT_API_KEY,
      tenantId: process.env.BRAINSAIT_TENANT_ID
    });
  }
  
  async processOrder(orderData: any) {
    // Create order in BrainSAIT
    const order = await this.brainSAIT.orders.create(orderData);
    
    // Process payment
    const payment = await this.brainSAIT.payments.createStripeIntent({
      amount: order.total,
      currency: order.currency,
      orderId: order.id
    });
    
    // Send to fulfillment
    await this.fulfillmentService.process(order);
    
    return { order, payment };
  }
}
```

### Event-Driven Integration
```python
# Redis-based event processing
import redis
import json
from brainsait_store import AsyncBrainSAITStore

class EventProcessor:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.store = AsyncBrainSAITStore(
            api_key=os.environ['BRAINSAIT_API_KEY'],
            tenant_id=os.environ['BRAINSAIT_TENANT_ID']
        )
    
    async def process_events(self):
        while True:
            _, event_data = await self.redis.blpop(['events'])
            event = json.loads(event_data)
            
            if event['type'] == 'order.created':
                await self.handle_new_order(event['data'])
            elif event['type'] == 'payment.completed':
                await self.handle_payment_completed(event['data'])
```

## Testing Examples

### E2E Testing with Playwright
```typescript
// Complete purchase flow test
test('user can complete purchase', async ({ page }) => {
  await page.goto('/products');
  
  // Add product to cart
  await page.click('.product-card:first-child .add-to-cart');
  await expect(page.locator('.cart-count')).toHaveText('1');
  
  // Checkout
  await page.click('.checkout-button');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="cardNumber"]', '4242424242424242');
  await page.click('button[type="submit"]');
  
  // Verify success
  await expect(page.locator('.success-message')).toBeVisible();
});
```

### Integration Testing
```javascript
// API integration tests
describe('BrainSAIT Store Integration', () => {
  test('should create and retrieve products', async () => {
    const product = await store.products.create({
      name: { en: 'Test Product' },
      price: 99.99,
      category: 'software'
    });
    
    expect(product.id).toBeDefined();
    
    const retrieved = await store.products.get(product.id);
    expect(retrieved.name.en).toBe('Test Product');
  });
});
```

## Deployment Examples

### Docker Compose
```yaml
# Complete development environment
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_BRAINSAIT_API_KEY=${BRAINSAIT_API_KEY}
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - BRAINSAIT_API_KEY=${BRAINSAIT_API_KEY}
      - BRAINSAIT_TENANT_ID=${BRAINSAIT_TENANT_ID}
```

### Kubernetes Deployment
```yaml
# Production deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: brainsait-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: brainsait-app
  template:
    spec:
      containers:
      - name: app
        image: your-registry/brainsait-app:latest
        env:
        - name: BRAINSAIT_API_KEY
          valueFrom:
            secretKeyRef:
              name: brainsait-secrets
              key: api-key
```

## Performance Examples

### Caching Strategy
```javascript
// Redis caching for product data
const redis = require('redis');
const client = redis.createClient();

async function getCachedProducts(category) {
  const cacheKey = `products:${category}`;
  
  // Try cache first
  const cached = await client.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }
  
  // Fetch from API
  const products = await store.products.list({ category });
  
  // Cache for 5 minutes
  await client.setex(cacheKey, 300, JSON.stringify(products));
  
  return products;
}
```

### Load Testing
```python
# Locust load testing
from locust import HttpUser, task, between

class BrainSAITUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Authenticate
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    @task(3)
    def get_products(self):
        self.client.get("/api/v1/store/products")
    
    @task(1)
    def create_order(self):
        self.client.post("/api/v1/orders", json={
            "items": [{"product_id": "prod-123", "quantity": 1}],
            "customer_email": "customer@example.com"
        })
```

## Real-World Use Cases

### E-commerce Marketplace
```typescript
// Multi-vendor marketplace integration
class MarketplaceService {
  async syncVendorProducts(vendorId: string) {
    const vendor = await this.getVendor(vendorId);
    const brainSAIT = new BrainSAITStore({
      apiKey: vendor.apiKey,
      tenantId: vendor.tenantId
    });
    
    const products = await brainSAIT.products.list();
    
    for (const product of products.data) {
      await this.marketplace.products.upsert({
        ...product,
        vendorId,
        commission: vendor.commissionRate
      });
    }
  }
}
```

### Content Creator Platform
```php
// WordPress/WooCommerce integration
class ContentCreatorStore {
    public function sync_digital_products() {
        $products = $this->brainsait_api->get_products(['category' => 'digital']);
        
        foreach ($products['data'] as $product) {
            $wc_product = new WC_Product_Simple();
            $wc_product->set_name($product['name']['en']);
            $wc_product->set_price($product['price']);
            $wc_product->set_virtual(true);
            $wc_product->set_downloadable(true);
            
            // Add download files
            $downloads = [];
            foreach ($product['files'] as $file) {
                $downloads[] = new WC_Product_Download([
                    'name' => $file['name'],
                    'file' => $file['url']
                ]);
            }
            $wc_product->set_downloads($downloads);
            
            $wc_product->save();
        }
    }
}
```

### SaaS Application Integration
```python
# Django SaaS platform integration
class SaaSPlatform:
    def provision_customer_store(self, customer):
        """Create a new BrainSAIT tenant for customer"""
        tenant_data = {
            'name': customer.company_name,
            'plan': customer.subscription_plan,
            'settings': {
                'currency': customer.preferred_currency,
                'language': customer.locale
            }
        }
        
        # Create tenant via admin API
        tenant = self.brainsait_admin.tenants.create(tenant_data)
        
        # Save tenant info
        customer.brainsait_tenant_id = tenant['id']
        customer.brainsait_api_key = tenant['api_key']
        customer.save()
        
        # Set up default products
        self.setup_default_products(customer)
        
        return tenant
```

## Next Steps

For more detailed examples and complete source code:

- [GitHub Examples Repository](https://github.com/brainsait/store-examples)
- [Integration Guide](../README.md)
- [SDK Documentation](../README.md)
- [API Reference](../../api/README.md)