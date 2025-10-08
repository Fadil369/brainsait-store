# Sales Service

Microservice for managing customers, sales operations, and CRM.

## Features

- Customer relationship management (CRM)
- Sales pipeline management
- Lead tracking and conversion
- Quote and proposal generation
- Sales analytics and reporting
- Multi-tenant B2B operations

## API Endpoints

### Customers
- `POST /api/customers` - Create customer
- `GET /api/customers/:id` - Get customer details
- `PUT /api/customers/:id` - Update customer
- `GET /api/customers` - List customers (paginated)

### Sales Pipeline
- `POST /api/leads` - Create lead
- `PUT /api/leads/:id/convert` - Convert lead to customer
- `GET /api/pipeline` - Get sales pipeline overview
- `POST /api/quotes` - Generate quote

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Service port (default: 3002)
- `API_KEY` - Service authentication key

## Development

```bash
npm install
npm run dev
```
