# Saudi Compliance Package

Utilities for Saudi Arabia regulatory compliance (ZATCA, Mada, VAT).

## Features

### ZATCA E-Invoicing (Phase 2)
- QR code generation (TLV format)
- Invoice hash calculation (SHA-256)
- XML invoice generation (UBL 2.1)
- Digital signatures (X.509)
- UUID generation (RFC 4122)
- Invoice validation

### VAT Calculations
- Standard VAT rate (15%)
- VAT-inclusive/exclusive calculations
- VAT report generation
- Multi-line item calculations

### Mada Payment Gateway
- Payment request formatting
- Response validation
- 3D Secure support
- Webhook verification

### Saudi Commercial Registry
- CR number validation
- VAT number validation (15 digits)
- IBAN validation (SA format)

## Usage

### ZATCA Invoice

```typescript
import { ZATCAInvoice, generateQRCode } from '@brainsait/saudi-compliance';

const invoice = new ZATCAInvoice({
  sellerName: 'Company Name',
  vatNumber: '123456789012345',
  timestamp: new Date(),
  total: 115.00,
  vatAmount: 15.00
});

const qrCode = generateQRCode(invoice);
const xml = invoice.toXML();
```

### VAT Calculations

```typescript
import { calculateVAT, VAT_RATE } from '@brainsait/saudi-compliance';

const priceExcludingVAT = 100;
const vat = calculateVAT(priceExcludingVAT);
const totalIncludingVAT = priceExcludingVAT + vat;
// totalIncludingVAT = 115
```

### Validation

```typescript
import { validateVATNumber, validateCRNumber } from '@brainsait/saudi-compliance';

const isValidVAT = validateVATNumber('123456789012345'); // true
const isValidCR = validateCRNumber('1234567890'); // true
```

## Development

```bash
npm install
npm run dev
```

## Testing

```bash
npm test
```
