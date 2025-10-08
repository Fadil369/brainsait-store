# AI Forecasting Service

AI-powered demand forecasting and predictive analytics service.

## Features

- Sales demand forecasting
- Inventory optimization predictions
- Seasonal trend analysis
- Customer behavior prediction
- Market trend insights
- ML model training and inference

## API Endpoints

### Forecasting
- `POST /api/forecast/demand` - Predict product demand
- `POST /api/forecast/sales` - Sales forecast
- `GET /api/forecast/trends` - Market trends analysis

### Analytics
- `POST /api/analytics/customer-behavior` - Analyze customer patterns
- `POST /api/analytics/inventory-optimization` - Optimize inventory levels

## ML Models

- Time series forecasting (LSTM/Prophet)
- Regression models for demand prediction
- Classification for customer segmentation
- Anomaly detection for fraud prevention

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Service port (default: 3004)
- `OPENAI_API_KEY` - OpenAI API key
- `MODEL_PATH` - Path to trained ML models

## Development

```bash
npm install
npm run dev
```
