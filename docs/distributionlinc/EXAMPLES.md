# DISTRIBUTIONLINC Agent - Usage Examples

## Quick Start

### 1. Generate Demand Forecast

```bash
curl -X POST "https://api.brainsait.com/api/v1/distributionlinc/forecast/demand" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept-Language: en" \
  -d '{
    "product_id": "PROD123",
    "region": "Riyadh",
    "forecast_horizon_days": 30,
    "include_factors": true
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "product_id": "PROD123",
  "product_name": "Sample Product",
  "product_name_ar": "منتج عينة",
  "region": "Riyadh",
  "region_ar": "الرياض",
  "predicted_quantity": 1250.50,
  "confidence_score": 0.87,
  "lower_bound": 1100.00,
  "upper_bound": 1400.00,
  "factors": {
    "seasonal_factor": 1.2,
    "weather_impact": 1.05,
    "holiday_impact": 1.0,
    "trend_factor": 1.05
  }
}
```

### 2. Optimize Pricing

```bash
curl -X POST "https://api.brainsait.com/api/v1/distributionlinc/pricing/optimize" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD123",
    "consider_competitors": true,
    "consider_inventory": true,
    "consider_demand": true
  }'
```

### 3. Optimize Delivery Route

```bash
curl -X POST "https://api.brainsait.com/api/v1/distributionlinc/route/optimize" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept-Language: ar" \
  -d '{
    "route_name": "Riyadh to Jeddah",
    "route_name_ar": "الرياض إلى جدة",
    "origin": "Riyadh Warehouse",
    "destination": "Jeddah Outlet",
    "waypoints": ["Rest Stop Makkah"],
    "vehicle_capacity_kg": 1000,
    "cargo_weight_kg": 750,
    "consider_traffic": true
  }'
```

### 4. Predict Inventory Needs

```bash
curl -X POST "https://api.brainsait.com/api/v1/distributionlinc/inventory/predict" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD123",
    "warehouse_id": "WH001",
    "current_stock": 150.0,
    "lead_time_days": 7,
    "include_po_suggestion": true
  }'
```

### 5. Predict Customer Churn

```bash
curl -X POST "https://api.brainsait.com/api/v1/distributionlinc/churn/predict" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST123",
    "include_recommendations": true
  }'
```

## Python Integration

### Complete Workflow Example

```python
import asyncio
import httpx

class DistributionLincClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept-Language": "en"  # or "ar" for Arabic
        }
    
    async def forecast_demand(self, product_id: str, region: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/distributionlinc/forecast/demand",
                headers=self.headers,
                json={
                    "product_id": product_id,
                    "region": region,
                    "forecast_horizon_days": 30
                }
            )
            return response.json()
    
    async def optimize_pricing(self, product_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/distributionlinc/pricing/optimize",
                headers=self.headers,
                json={"product_id": product_id}
            )
            return response.json()
    
    async def check_inventory(self, product_id: str, warehouse_id: str, current_stock: float):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/distributionlinc/inventory/predict",
                headers=self.headers,
                json={
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "current_stock": current_stock,
                    "lead_time_days": 7
                }
            )
            return response.json()

# Usage
async def main():
    client = DistributionLincClient(
        base_url="https://api.brainsait.com",
        api_token="your_token_here"
    )
    
    # Forecast demand
    forecast = await client.forecast_demand("PROD123", "Riyadh")
    print(f"Predicted demand: {forecast['predicted_quantity']}")
    
    # Optimize pricing
    pricing = await client.optimize_pricing("PROD123")
    print(f"Recommended price: {pricing['recommended_price']} SAR")
    
    # Check inventory
    inventory = await client.check_inventory("PROD123", "WH001", 150.0)
    print(f"Risk level: {inventory['risk_level']}")
    if inventory['po_suggested']:
        print(f"Reorder {inventory['recommended_reorder_quantity']} units")

asyncio.run(main())
```

## JavaScript/TypeScript Integration

```typescript
class DistributionLincClient {
  constructor(
    private baseUrl: string,
    private apiToken: string,
    private language: 'en' | 'ar' = 'en'
  ) {}

  async forecastDemand(productId: string, region: string) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/distributionlinc/forecast/demand`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiToken}`,
          'Content-Type': 'application/json',
          'Accept-Language': this.language
        },
        body: JSON.stringify({
          product_id: productId,
          region: region,
          forecast_horizon_days: 30
        })
      }
    );
    return await response.json();
  }

  async optimizeRoute(origin: string, destination: string, waypoints: string[] = []) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/distributionlinc/route/optimize`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiToken}`,
          'Content-Type': 'application/json',
          'Accept-Language': this.language
        },
        body: JSON.stringify({
          route_name: `Route from ${origin} to ${destination}`,
          origin,
          destination,
          waypoints,
          consider_traffic: true
        })
      }
    );
    return await response.json();
  }

  async predictChurn(customerId: string) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/distributionlinc/churn/predict`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiToken}`,
          'Content-Type': 'application/json',
          'Accept-Language': this.language
        },
        body: JSON.stringify({
          customer_id: customerId,
          include_recommendations: true
        })
      }
    );
    return await response.json();
  }

  async getAnalytics(startDate?: Date, endDate?: Date) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate.toISOString());
    if (endDate) params.append('end_date', endDate.toISOString());

    const response = await fetch(
      `${this.baseUrl}/api/v1/distributionlinc/analytics/distribution?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${this.apiToken}`,
          'Accept-Language': this.language
        }
      }
    );
    return await response.json();
  }
}

// Usage
const client = new DistributionLincClient(
  'https://api.brainsait.com',
  'your_token_here',
  'ar'  // Use Arabic
);

// Forecast demand (with Arabic response)
const forecast = await client.forecastDemand('PROD123', 'Riyadh');
console.log(`التوقع: ${forecast.predicted_quantity}`);  // "Forecast: <quantity>"

// Optimize route (with Arabic response)
const route = await client.optimizeRoute('Riyadh', 'Jeddah', ['Makkah']);
console.log(`المسافة: ${route.estimated_distance_km} كم`);  // "Distance: <km> km"

// Check for at-risk customers (with Arabic response)
const churn = await client.predictChurn('CUST123');
if (churn.risk_level === 'high' || churn.risk_level === 'critical') {
  console.log(`عميل في خطر! احتمال التسرب: ${churn.churn_probability}`);  // "Customer at risk! Churn probability: <probability>"
  console.log('استراتيجيات الاحتفاظ:', churn.retention_strategies);  // "Retention strategies:"
}

// Get analytics
const analytics = await client.getAnalytics();
console.log('إحصائيات التوزيع:', analytics);
```

## Batch Operations

### Batch Demand Forecasting

```python
async def batch_forecast(client, products, region):
    tasks = [
        client.forecast_demand(product_id, region)
        for product_id in products
    ]
    results = await asyncio.gather(*tasks)
    return results

# Usage
products = ['PROD1', 'PROD2', 'PROD3', 'PROD4', 'PROD5']
forecasts = await batch_forecast(client, products, 'Riyadh')
```

### Batch Churn Analysis

```python
async def identify_at_risk_customers(client):
    # Get high-risk customers
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{client.base_url}/api/v1/distributionlinc/churn/predictions",
            headers=client.headers,
            params={
                "risk_level": "high",
                "limit": 100
            }
        )
        return response.json()

# Usage
at_risk = await identify_at_risk_customers(client)
for customer in at_risk:
    print(f"Customer {customer['customer_id']}: {customer['churn_probability']:.0%} churn risk")
    for strategy in customer.get('retention_strategies', []):
        print(f"  - {strategy['description']}")
```

## Integration with Existing Systems

### Webhook Integration

```python
from fastapi import FastAPI, Request
import hmac
import hashlib

app = FastAPI()

@app.post("/webhooks/distributionlinc")
async def handle_distributionlinc_webhook(request: Request):
    """Handle DISTRIBUTIONLINC webhooks for automated actions"""
    payload = await request.json()
    
    if payload['event_type'] == 'inventory_critical':
        # Auto-generate purchase order
        await create_purchase_order(
            product_id=payload['product_id'],
            quantity=payload['recommended_quantity']
        )
    
    elif payload['event_type'] == 'customer_churn_risk':
        # Trigger retention campaign
        await send_retention_email(
            customer_id=payload['customer_id'],
            discount=payload['recommended_discount']
        )
    
    return {"status": "processed"}
```

### Scheduler Integration

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=1)  # Run daily at 1 AM
async def daily_forecasts():
    """Generate daily demand forecasts for all products"""
    products = await get_all_products()
    regions = ['Riyadh', 'Jeddah', 'Dammam', 'Makkah', 'Madinah']
    
    for product in products:
        for region in regions:
            await client.forecast_demand(product.id, region)

@scheduler.scheduled_job('cron', hour=2)  # Run daily at 2 AM
async def daily_churn_analysis():
    """Identify at-risk customers daily"""
    at_risk = await identify_at_risk_customers(client)
    
    # Alert sales team
    for customer in at_risk:
        if customer['risk_level'] == 'critical':
            await send_alert_to_sales(customer)

scheduler.start()
```

## Best Practices

### 1. Caching Results

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedClient(DistributionLincClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
    
    async def forecast_demand_cached(self, product_id: str, region: str):
        cache_key = f"{product_id}:{region}"
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(hours=1):
                return cached_data
        
        result = await self.forecast_demand(product_id, region)
        self._cache[cache_key] = (datetime.now(), result)
        return result
```

### 2. Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class ResilientClient(DistributionLincClient):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def forecast_demand_with_retry(self, product_id: str, region: str):
        try:
            return await self.forecast_demand(product_id, region)
        except httpx.HTTPError as e:
            print(f"Request failed: {e}. Retrying...")
            raise
```

### 3. Monitoring

```python
import time
from prometheus_client import Counter, Histogram

forecast_requests = Counter('distributionlinc_forecast_requests_total', 'Total forecast requests')
forecast_duration = Histogram('distributionlinc_forecast_duration_seconds', 'Forecast request duration')

class MonitoredClient(DistributionLincClient):
    async def forecast_demand(self, product_id: str, region: str):
        forecast_requests.inc()
        start_time = time.time()
        
        try:
            result = await super().forecast_demand(product_id, region)
            return result
        finally:
            forecast_duration.observe(time.time() - start_time)
```

## Support

For more examples and support:
- 📧 Technical Support: support@brainsait.com
- 📧 Arabic Support: support-ar@brainsait.com
- 📚 Full API Documentation: https://api.brainsait.com/api/docs
- 🔗 GitHub: https://github.com/Fadil369/brainsait-store
