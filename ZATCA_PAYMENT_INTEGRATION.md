# ZATCA & Saudi Payment Integration Guide

## Overview

This document provides comprehensive information about the ZATCA e-invoicing (Phase 2) and Saudi payment gateway integration implemented in the BrainSAIT Store.

## Table of Contents

1. [ZATCA E-Invoicing Compliance](#zatca-e-invoicing-compliance)
2. [Payment Gateway Integration](#payment-gateway-integration)
3. [Configuration](#configuration)
4. [API Endpoints](#api-endpoints)
5. [Testing](#testing)
6. [Compliance & Audit](#compliance--audit)

---

## ZATCA E-Invoicing Compliance

### Features Implemented

#### 1. QR Code Generation (TLV Format)
- Compliant with ZATCA Phase 2 specifications
- Tag-Length-Value (TLV) encoding format
- Includes:
  - Tag 1: Seller Name (UTF-8)
  - Tag 2: VAT Registration Number
  - Tag 3: Timestamp (ISO 8601)
  - Tag 4: Total Amount (with VAT)
  - Tag 5: VAT Amount
  - Tag 6: Invoice Hash (Base64)

#### 2. Invoice Generation (UBL 2.1 XML)
- Universal Business Language (UBL) 2.1 compliant XML
- Standard tax invoice format (InvoiceTypeCode: 388)
- Supports both standard and simplified invoices
- Bilingual support (Arabic/English)

#### 3. VAT Calculation
- Automatic 15% VAT calculation
- Support for VAT-inclusive and VAT-exclusive amounts
- Accurate rounding to 2 decimal places

#### 4. Digital Signatures & Hashing
- SHA-256 cryptographic hashing
- Base64 encoding for invoice hashes
- Invoice integrity verification

#### 5. ZATCA Portal Integration
- API integration for invoice submission
- Support for both reporting and clearance modes
- Automatic status tracking
- Error handling and retry logic

### ZATCA Service Usage

```python
from app.services.zatca_service import ZATCAService

# Initialize service
zatca_service = ZATCAService()

# Generate invoice
invoice_data = await zatca_service.generate_invoice(
    order_id=order_uuid,
    payment_id=payment_uuid,
    db=db_session
)

# Validate invoice before submission
validation = await zatca_service.validate_invoice(invoice_data)
if validation["valid"]:
    # Submit to ZATCA
    result = await zatca_service.submit_to_zatca(
        invoice_id=invoice_uuid,
        submission_type="reporting",  # or "clearance"
        db=db_session
    )

# Calculate VAT
vat_breakdown = zatca_service.calculate_vat(
    amount=Decimal("100.00"),
    vat_inclusive=False
)
# Returns: {"subtotal": 100.00, "vat_amount": 15.00, "total": 115.00}
```

### Invoice Validation Rules

The service validates:
- Required fields (seller info, buyer info, amounts)
- VAT number format (15 digits starting with 3)
- CR number format (minimum 7 digits)
- Amount calculations (total = subtotal + VAT)

---

## Payment Gateway Integration

### Supported Payment Methods

#### 1. **Mada Cards** (Saudi Domestic Debit)
- Direct integration with Mada payment gateway
- HMAC-SHA256 signature verification
- Support for card authentication
- Automatic callback handling

#### 2. **STC Pay** (Digital Wallet)
- QR code generation for payments
- Mobile wallet integration
- Real-time payment status tracking
- SMS and app notifications

#### 3. **Stripe** (International Cards)
- Visa, Mastercard, American Express support
- Payment Intent API
- Strong Customer Authentication (SCA)
- Webhook handling

### Mada Service Usage

```python
from app.services.payment_providers import MadaService

mada = MadaService()

# Create payment intent
result = await mada.create_payment_intent(
    amount=100.00,
    order_id=order_uuid,
    customer_info={
        "name": "Customer Name",
        "email": "customer@example.com",
        "phone": "+966501234567"
    }
)
# Returns: {"payment_id": "...", "redirect_url": "...", "status": "pending"}

# Verify payment status
status = await mada.verify_payment(payment_id)

# Verify webhook signature
is_valid = mada.verify_webhook_signature(payload, signature)
```

### STC Pay Service Usage

```python
from app.services.payment_providers import STCPayService

stc = STCPayService()

# Create payment with QR code
result = await stc.create_payment_intent(
    amount=100.00,
    order_id=order_uuid,
    customer_info={
        "name": "Customer Name",
        "phone": "+966501234567"
    }
)
# Returns: {"transaction_id": "...", "qr_code": "...", "payment_url": "..."}

# Generate QR code only
qr_data = await stc.generate_qr_code(amount=100.00, order_id=order_uuid)

# Verify payment
status = await stc.verify_payment(transaction_id)
```

### Stripe Service Usage

```python
from app.services.payment_providers import StripeService

stripe = StripeService()

# Create payment intent
result = await stripe.create_payment_intent(
    amount=100.00,
    currency="SAR",
    metadata={"order_id": str(order_uuid)}
)
# Returns: {"client_secret": "...", "payment_intent_id": "...", "status": "..."}

# Confirm payment
status = await stripe.confirm_payment(payment_intent_id)
```

---

## Notification Service

### Features

- Email notifications (HTML templates)
- SMS notifications (Unifonic & Taqnyat)
- Bilingual support (Arabic/English)
- Payment confirmation
- Payment failure alerts
- Invoice delivery

### Usage

```python
from app.services.notifications import NotificationService

notif = NotificationService()

# Send payment confirmation email
await notif.send_payment_confirmation(
    email="customer@example.com",
    order_id=order_uuid,
    amount=100.00,
    language="ar"  # or "en"
)

# Send SMS notification
await notif.send_payment_confirmation_sms(
    phone="+966501234567",
    order_id=order_uuid,
    amount=100.00,
    language="ar"
)

# Send invoice notification
await notif.send_invoice_notification(
    email="customer@example.com",
    invoice_number="INV-2024-001",
    invoice_url="https://example.com/invoices/123.pdf",
    language="en"
)
```

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# ZATCA Configuration
ZATCA_ENABLED=true
ZATCA_VAT_NUMBER=300000000000003
ZATCA_CR_NUMBER=1234567890
ZATCA_SELLER_NAME="Your Company Name"
ZATCA_SELLER_NAME_AR="اسم شركتك"

# Mada Payment Gateway
MADA_MERCHANT_ID=your_merchant_id
MADA_API_KEY=your_api_key
MADA_ENDPOINT=https://api.mada.sa

# STC Pay
STC_PAY_MERCHANT_ID=your_merchant_id
STC_PAY_API_KEY=your_api_key
STC_PAY_ENDPOINT=https://api.stcpay.com.sa

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_password
FROM_EMAIL=noreply@brainsait.com
FROM_NAME="BrainSAIT Store"
FROM_NAME_AR="متجر برين سايت"

# SMS Configuration (Choose one)
SMS_PROVIDER=unifonic  # or "taqnyat"

# Unifonic
UNIFONIC_APP_SID=your_app_sid
UNIFONIC_SENDER_ID=your_sender_id

# Taqnyat
TAQNYAT_API_KEY=your_api_key
TAQNYAT_SENDER=your_sender_name

# Application
API_BASE_URL=https://your-domain.com
PRODUCTION=false  # Set to true in production
```

---

## API Endpoints

### Payment Methods

**GET** `/api/v1/payments/methods`

Returns available payment methods for the tenant.

```json
{
  "stripe": {
    "id": "stripe",
    "name": "Credit/Debit Cards",
    "name_ar": "بطاقات الائتمان/الخصم",
    "supported_currencies": ["SAR", "USD", "EUR"],
    "fees": {"percentage": 2.9, "fixed": 0},
    "enabled": true
  },
  "mada": {
    "id": "mada",
    "name": "Mada Cards",
    "name_ar": "بطاقات مدى",
    "supported_currencies": ["SAR"],
    "fees": {"percentage": 1.5, "fixed": 0},
    "enabled": true
  },
  "stc_pay": {
    "id": "stc_pay",
    "name": "STC Pay",
    "name_ar": "إس تي سي باي",
    "supported_currencies": ["SAR"],
    "fees": {"percentage": 1.0, "fixed": 0},
    "enabled": true
  }
}
```

### Create Payment Intent

**POST** `/api/v1/payments/stripe/intent`
**POST** `/api/v1/payments/mada/intent`
**POST** `/api/v1/payments/stc-pay/intent`

Request body:
```json
{
  "order_id": "uuid",
  "amount": 100.00,
  "currency": "SAR",
  "customer_info": {
    "name": "Customer Name",
    "email": "customer@example.com",
    "phone": "+966501234567"
  }
}
```

### Get Invoice

**GET** `/api/v1/payments/invoices/{order_id}`

Returns ZATCA-compliant invoice with QR code.

```json
{
  "id": "uuid",
  "order_id": "uuid",
  "invoice_number": "INV-2024-001",
  "zatca_uuid": "uuid",
  "qr_code": "base64_encoded_qr_data",
  "total_amount": 115.00,
  "tax_amount": 15.00,
  "status": "issued",
  "pdf_url": "https://example.com/invoices/123.pdf",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Webhooks

**POST** `/api/v1/payments/webhooks/stripe`
**POST** `/api/v1/payments/webhooks/mada`
**POST** `/api/v1/payments/webhooks/stc-pay`

These endpoints handle payment status updates from payment providers with signature verification.

---

## Testing

### Running Tests

```bash
# Run all payment service tests
pytest backend/tests/services/test_payment_providers.py -v

# Run ZATCA service tests
pytest backend/tests/services/test_zatca_service.py -v

# Run notification service tests
pytest backend/tests/services/test_notifications.py -v

# Run with coverage
pytest backend/tests/services/ --cov=app/services --cov-report=html
```

### Test Coverage

- **ZATCA Service**: 13 test cases covering:
  - QR code generation
  - Invoice hash generation
  - UBL XML generation
  - Invoice validation
  - VAT calculation
  - ZATCA portal submission

- **Payment Providers**: 18 test cases covering:
  - Stripe payment intents
  - Mada payment creation and verification
  - STC Pay QR code generation
  - Webhook signature verification

- **Notification Service**: 17 test cases covering:
  - Email notifications (English/Arabic)
  - SMS via Unifonic and Taqnyat
  - Template rendering
  - Multi-language support

### Mock Testing

All tests use mocked API responses to avoid external dependencies:

```python
# Example: Testing Mada payment
mock_response = Response(
    status_code=200,
    json={"payment_id": "test_123", "redirect_url": "https://..."}
)
with patch.object(mada_service.client, 'post', return_value=mock_response):
    result = await mada_service.create_payment_intent(...)
```

---

## Compliance & Audit

### ZATCA Compliance Features

1. **Invoice Tracking**: All invoices are tracked in the `invoices` table with ZATCA status
2. **Submission History**: `zatca_submissions` table logs all API submissions
3. **QR Code Storage**: QR codes stored with each invoice
4. **XML Storage**: Full UBL XML stored for audit purposes
5. **Hash Verification**: Cryptographic hashes ensure invoice integrity

### Audit Logging

All payment transactions and ZATCA submissions are logged:

```python
# Automatic logging in services
logger.info(f"ZATCA invoice generated for order {order_id}")
logger.info(f"Payment confirmation sent to {email}")
logger.error(f"ZATCA submission failed: {error}")
```

### Database Schema

**invoices** table:
- `zatca_status`: PENDING, SUBMITTED, APPROVED, REJECTED, CLEARED
- `zatca_uuid`: Unique identifier for ZATCA
- `zatca_hash`: SHA-256 hash of invoice
- `zatca_qr_code`: TLV-encoded QR code
- `zatca_xml`: Full UBL 2.1 XML
- `zatca_response`: ZATCA API response

**zatca_submissions** table:
- Tracks all submission attempts
- Stores request and response payloads
- Records status codes and error messages
- Enables compliance reporting

### Vision 2030 KPIs

The implementation supports Saudi Vision 2030 digital transformation goals:

- **Digital Payment Adoption**: Multiple Saudi payment methods (Mada, STC Pay)
- **Tax Compliance**: Automated ZATCA e-invoicing
- **Financial Transparency**: Complete audit trails
- **Customer Experience**: Bilingual support (Arabic/English)
- **Business Efficiency**: Automated invoice generation and submission

---

## Security Considerations

1. **Webhook Signature Verification**: All webhooks verify HMAC signatures
2. **API Key Protection**: Store API keys in environment variables, never in code
3. **HTTPS Only**: All payment API calls use HTTPS
4. **PCI Compliance**: Stripe handles card data, we never store card numbers
5. **Data Encryption**: Sensitive data encrypted at rest in database

---

## Troubleshooting

### ZATCA Submission Issues

**Problem**: Invoice rejected by ZATCA
**Solution**: 
- Check VAT number format (15 digits starting with 3)
- Verify CR number is valid
- Ensure all required fields are present
- Use `validate_invoice()` method before submission

**Problem**: QR code not scanning
**Solution**:
- Verify TLV encoding is correct
- Check Base64 encoding
- Ensure all 6 tags are present

### Payment Gateway Issues

**Problem**: Mada payment creation fails
**Solution**:
- Verify merchant credentials
- Check signature generation
- Ensure callback URL is accessible

**Problem**: STC Pay QR code expired
**Solution**:
- QR codes have limited lifetime (typically 5-10 minutes)
- Generate new QR code if expired
- Implement expiry checking in frontend

### Notification Issues

**Problem**: Emails not sending
**Solution**:
- Check SMTP credentials
- Verify SMTP server allows connection
- Check firewall/security group settings

**Problem**: SMS not delivered
**Solution**:
- Verify provider credentials (Unifonic/Taqnyat)
- Check phone number format (+966...)
- Ensure sender ID is approved

---

## Support

For issues or questions:
- Technical: support@brainsait.com
- ZATCA Compliance: compliance@brainsait.com
- Payment Gateway: payments@brainsait.com

## References

- [ZATCA E-Invoicing Portal](https://zatca.gov.sa/en/E-Invoicing/Pages/default.aspx)
- [Mada Payment Gateway Documentation](https://mada.com.sa)
- [STC Pay Developer Portal](https://stcpay.com.sa/developers)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [UBL 2.1 Specification](http://docs.oasis-open.org/ubl/UBL-2.1.html)
