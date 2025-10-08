# Analytics Aggregator Worker

Cloudflare Worker for aggregating and processing analytics data.

## Features

- Real-time data aggregation
- Metrics calculation
- Time-series data processing
- Event tracking and logging
- KPI computation
- Data export (JSON/CSV)

## Metrics Collected

- Sales metrics (revenue, orders, AOV)
- Customer metrics (CAC, LTV, churn)
- Product metrics (views, conversions)
- Performance metrics (response times, errors)

## API

### Endpoints
- `POST /track` - Track event
- `POST /aggregate` - Run aggregation job
- `GET /metrics` - Get aggregated metrics
- `GET /export` - Export data

## Data Processing

- Scheduled aggregation via Cron Triggers
- Real-time metric updates
- Time-window calculations (hourly, daily, monthly)
- Anomaly detection

## Configuration

Environment variables:
- `DATABASE_URL` - Analytics database connection
- `AGGREGATION_SCHEDULE` - Cron schedule
- `RETENTION_DAYS` - Data retention period (default: 90)

## Development

```bash
npm install
npm run dev
```

## Deployment

```bash
npm run deploy
```

## Cron Triggers

```toml
# In wrangler.toml
[triggers]
crons = ["0 * * * *"]  # Run hourly
```
