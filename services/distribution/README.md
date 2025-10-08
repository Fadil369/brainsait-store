# Distribution Service

Microservice for managing orders, inventory, and distribution operations.

## Features

- Order management (create, update, track)
- Inventory tracking and management
- Warehouse management
- Stock level monitoring
- Distribution route planning integration
- Multi-tenant support

## API Endpoints

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders/:id` - Get order details
- `PUT /api/orders/:id` - Update order
- `GET /api/orders` - List orders (paginated)
- `POST /api/orders/:id/fulfill` - Mark order as fulfilled

### Inventory
- `GET /api/inventory` - List inventory items
- `GET /api/inventory/:sku` - Get item details
- `PUT /api/inventory/:sku` - Update stock levels
- `POST /api/inventory/transfer` - Transfer between warehouses

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Service port (default: 3001)
- `API_KEY` - Service authentication key
- `REDIS_URL` - Cache connection string

## Development

```bash
npm install
npm run dev
```

## Testing

```bash
npm test
```

## Deployment

```bash
npm run build
npm start
```
