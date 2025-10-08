# DISTRIBUTIONLINC Agent Documentation

## Overview

DISTRIBUTIONLINC is an AI-powered intelligence layer for the Saudi Smart Distribution Platform (SSDP). It provides advanced analytics, predictions, and optimizations specifically designed for distribution operations in the Saudi market.

## Core Capabilities

### 1. Demand Forecasting Engine
Predicts future product demand with high accuracy considering multiple factors:

- **Regional Analysis**: Market-specific demand patterns for different Saudi regions
- **Seasonal Patterns**: Accounts for seasonal variations (summer, winter)
- **Weather Impact**: Temperature and weather condition effects on demand
- **Holiday Effects**: Ramadan, Eid, National Day, and other Saudi holidays
- **Trend Analysis**: Long-term growth and decline trends

### 2. Dynamic Pricing Optimizer
AI-driven pricing recommendations to maximize revenue:

- **Inventory-Based**: Adjusts pricing based on stock levels
- **Competitor Analysis**: Considers market pricing
- **Demand Elasticity**: Accounts for price sensitivity
- **Revenue Impact**: Estimates financial outcomes

### 3. Route Intelligence
Optimizes delivery routes for efficiency and cost reduction:

- **Traffic Analysis**: Real-time traffic condition integration
- **Delivery Windows**: Time-constrained delivery optimization
- **Vehicle Capacity**: Load optimization
- **Cost Optimization**: Fuel and time cost minimization

### 4. Inventory Orchestrator
Predictive restocking with intelligent PO suggestions:

- **Stock Depletion Prediction**: When will items run out
- **Safety Stock Calculation**: Minimum required inventory
- **Economic Order Quantity (EOQ)**: Optimal order sizes
- **Risk Assessment**: Stockout risk levels

### 5. Customer Churn Prediction
Identifies at-risk customers and provides retention strategies:

- **Churn Probability**: Mathematical risk assessment
- **Risk Factors**: Recency, frequency, monetary analysis
- **Retention Strategies**: Personalized action recommendations
- **Priority Scoring**: Focus on high-value customers

## API Endpoints

Base URL: `/api/v1/distributionlinc`

### Demand Forecasting
- `POST /forecast/demand` - Generate demand forecast
- `GET /forecast/demand` - List forecasts

### Dynamic Pricing
- `POST /pricing/optimize` - Generate pricing recommendation
- `POST /pricing/approve` - Approve/reject pricing
- `GET /pricing/recommendations` - List recommendations

### Route Optimization
- `POST /route/optimize` - Optimize delivery route
- `GET /route/optimizations` - List optimizations

### Inventory Management
- `POST /inventory/predict` - Predict inventory needs
- `GET /inventory/predictions` - List predictions

### Customer Churn
- `POST /churn/predict` - Predict customer churn
- `POST /churn/action` - Log retention action
- `GET /churn/predictions` - List predictions

### Analytics
- `GET /analytics/distribution` - Get comprehensive analytics

## Bilingual Support

All endpoints support Arabic and English via `Accept-Language` header.

## Role-Based Access

Different roles have different permissions:
- **admin**: Full access
- **analyst**: Read/Create analytics
- **pricing_manager**: Pricing management
- **logistics_manager**: Route & delivery management
- **inventory_manager**: Inventory management
- **sales_manager**: Customer management
- **user**: Limited read/create access

## Quick Start

See [API Documentation](https://api.brainsait.com/api/docs) for interactive examples.

## Testing

```bash
cd backend
pytest tests/test_distributionlinc.py -v
```

Target coverage: >85%

## Support

- Technical: support@brainsait.com
- Arabic: دعم@brainsait.com
