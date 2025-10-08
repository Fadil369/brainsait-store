# Finance Service

Microservice for financial operations and ZATCA e-invoicing compliance.

## Features

- ZATCA-compliant e-invoicing
- Invoice generation and validation
- Payment tracking and reconciliation
- VAT calculations and reporting
- Financial analytics
- Multi-currency support (SAR, USD, EUR)

## API Endpoints

### Invoices
- `POST /api/invoices` - Generate ZATCA-compliant invoice
- `GET /api/invoices/:id` - Get invoice details
- `POST /api/invoices/:id/validate` - Validate with ZATCA
- `POST /api/invoices/:id/cancel` - Cancel invoice

### Payments
- `POST /api/payments` - Record payment
- `GET /api/payments/:id` - Get payment details
- `POST /api/payments/:id/reconcile` - Reconcile payment

### Reports
- `GET /api/reports/vat` - VAT report
- `GET /api/reports/revenue` - Revenue report

## ZATCA Compliance

This service implements Phase 2 ZATCA requirements:
- QR code generation
- Simplified/Standard tax invoice formats
- Integration with ZATCA API
- Digital signatures (X.509 certificates)

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Service port (default: 3003)
- `ZATCA_API_URL` - ZATCA integration endpoint
- `ZATCA_CERT_PATH` - Path to X.509 certificate
- `VAT_RATE` - Default VAT rate (15%)

## Development

```bash
npm install
npm run dev
```
