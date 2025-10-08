# Route Optimizer Worker

Cloudflare Worker for optimizing delivery routes using AI algorithms.

## Features

- Real-time route optimization
- Multi-stop delivery planning
- Traffic-aware routing
- Distance and time estimation
- Geographic clustering
- Cost optimization

## API

### Endpoints
- `POST /optimize` - Optimize delivery route
  - Input: Array of delivery locations
  - Output: Optimized route with ETAs

## Algorithm

Uses combination of:
- Traveling Salesman Problem (TSP) optimization
- Google Maps/Mapbox routing APIs
- Traffic data integration
- Machine learning for predictions

## Configuration

Cloudflare Worker environment variables:
- `MAPS_API_KEY` - Google Maps or Mapbox API key
- `MAX_STOPS` - Maximum stops per route (default: 50)

## Development

```bash
npm install
npm run dev
```

## Deployment

```bash
npm run deploy
```
