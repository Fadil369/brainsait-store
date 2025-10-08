# Invoice Generator Worker

Cloudflare Worker for generating ZATCA-compliant invoices.

## Features

- ZATCA Phase 2 compliant invoices
- PDF generation with QR codes
- XML invoice format
- Digital signatures
- Simplified & Standard tax invoices
- Multi-language support (Arabic/English)

## API

### Endpoints
- `POST /generate` - Generate invoice
  - Input: Invoice data
  - Output: PDF + XML formats

- `POST /validate` - Validate invoice
  - Checks ZATCA compliance

## ZATCA Compliance

Implements:
- QR code generation (TLV format)
- Invoice hash calculation
- X.509 digital signatures
- UUID generation
- VAT calculations

## Configuration

Environment variables:
- `ZATCA_CERT` - X.509 certificate (base64)
- `ZATCA_PRIVATE_KEY` - Private key (base64)
- `COMPANY_VAT_NUMBER` - Company VAT registration number

## Development

```bash
npm install
npm run dev
```

## Deployment

```bash
npm run deploy
```
