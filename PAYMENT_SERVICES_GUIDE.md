# Payment Services Implementation - BrainSAIT Store

This document provides an overview of the complete payment service implementation for Saudi Arabia market compliance.

## 🚀 Overview

The payment infrastructure now supports:
- **Mada Card Processing** - Saudi domestic debit cards
- **STC Pay Integration** - Digital wallet payments
- **ZATCA Tax Compliance** - Saudi tax authority compliance with QR code generation
- **Enhanced Security** - Webhook validation, fraud detection, rate limiting
- **Payment Reconciliation** - Cross-provider payment tracking and matching

## 📁 File Structure

```
backend/app/services/
├── payment_providers.py      # Mada, STC Pay, Stripe service implementations
├── zatca_service.py         # Saudi tax compliance and invoice generation
├── notifications.py         # Email notification system
└── payment_security.py      # Security, fraud detection, reconciliation
```

## 🔧 Configuration

Add these environment variables to your `.env` file:

```bash
# Mada Payment Configuration
MADA_MERCHANT_ID=your_mada_merchant_id
MADA_API_KEY=your_mada_api_key
MADA_ENDPOINT=https://api.mada.sa
MADA_WEBHOOK_SECRET=your_webhook_secret

# STC Pay Configuration
STC_PAY_MERCHANT_ID=your_stc_merchant_id
STC_PAY_API_KEY=your_stc_api_key
STC_PAY_ENDPOINT=https://api.stcpay.com.sa
STC_PAY_WEBHOOK_SECRET=your_webhook_secret

# ZATCA Configuration
ZATCA_ENABLED=true
ZATCA_VAT_NUMBER=300000000000003
ZATCA_CR_NUMBER=1010000001
ZATCA_SELLER_NAME=BrainSAIT Store
ZATCA_SELLER_NAME_AR=متجر برين سايت

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🔒 Saudi Payment Methods

### Mada Card Processing

Create a Mada payment:

```bash
curl -X POST "http://localhost:8000/api/v1/payments/mada/intent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "order_id": "uuid-here",
    "customer_name": "Ahmed Al-Saudi",
    "customer_phone": "0501234567",
    "return_url": "https://brainsait.com/success"
  }'
```

Response:
```json
{
  "payment_intent_id": "mada_payment_id",
  "redirect_url": "https://mada.sa/pay/payment_id",
  "amount": 100.0,
  "currency": "SAR",
  "status": "requires_action"
}
```

### STC Pay Integration

Create an STC Pay payment:

```bash
curl -X POST "http://localhost:8000/api/v1/payments/stc-pay/intent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "order_id": "uuid-here",
    "mobile_number": "0501234567"
  }'
```

## 📄 ZATCA Tax Compliance

### Invoice Generation

The system automatically generates ZATCA-compliant invoices with:
- Proper VAT calculations (15% for Saudi Arabia)
- QR codes with TLV (Tag-Length-Value) format
- Arabic and English support
- B2B and B2C invoice types

Get an invoice:

```bash
curl -X GET "http://localhost:8000/api/v1/payments/invoices/{order_id}" \
  -H "Authorization: Bearer your_token"
```

Response includes:
```json
{
  "invoice_number": "INV-20250815-12345",
  "zatca_uuid": "uuid-here",
  "qr_code": "base64-encoded-qr-data",
  "total_amount": 115.0,
  "tax_amount": 15.0,
  "status": "approved",
  "pdf_url": "/api/v1/invoices/order_id/pdf"
}
```

## 🛡️ Security Features

### Webhook Security

All webhooks are protected with:
- HMAC signature verification
- Timestamp validation (5-minute tolerance)
- Rate limiting (100 requests per 5 minutes per IP)
- Request logging and monitoring

### Fraud Detection

The system analyzes payments for:
- Suspicious amount patterns
- Velocity checks (frequency of payments)
- IP address patterns
- Time-based anomalies

Fraud analysis endpoint:
```bash
curl -X GET "http://localhost:8000/api/v1/payments/fraud-detection/analyze/{order_id}" \
  -H "Authorization: Bearer your_token"
```

## 📊 Payment Reconciliation

### Run Reconciliation

```bash
curl -X POST "http://localhost:8000/api/v1/payments/reconciliation/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T23:59:59Z",
    "provider": "mada"
  }'
```

### Get Reconciliation Report

```bash
curl -X GET "http://localhost:8000/api/v1/payments/reconciliation/report?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z" \
  -H "Authorization: Bearer your_token"
```

## 🔗 Webhook Endpoints

Configure these webhook URLs in your payment provider dashboards:

- **Mada**: `https://your-domain.com/api/v1/payments/webhooks/mada`
- **STC Pay**: `https://your-domain.com/api/v1/payments/webhooks/stc-pay`
- **Stripe**: `https://your-domain.com/api/v1/payments/webhooks/stripe`

## 📧 Notifications

The system sends automatic notifications for:
- Payment confirmations
- Payment failures
- ZATCA invoice generation

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd backend
python test_payment_services.py
```

This validates:
- ✅ Mada payment creation and webhook verification
- ✅ STC Pay mobile number validation and payments
- ✅ ZATCA invoice generation with QR codes
- ✅ Email notification system
- ✅ Fraud detection and security services
- ✅ Complete payment flow integration

## 🚨 Error Handling

The services include comprehensive error handling:

- **Network failures**: Automatic retries with exponential backoff
- **Invalid signatures**: Webhook requests are rejected with 401 status
- **Rate limiting**: Excessive requests return 429 status
- **Fraud detection**: High-risk payments are blocked with 403 status
- **Service unavailability**: Graceful degradation with 500 status

## 📈 Monitoring

Monitor payment services through:

- **Logs**: Comprehensive logging for all payment operations
- **Metrics**: Payment success/failure rates by provider
- **Alerts**: Fraud detection alerts and webhook failures
- **Reports**: Daily/weekly reconciliation reports

## 🔐 Production Deployment

For production deployment:

1. **Security**: Use strong webhook secrets and rotate them regularly
2. **SSL/TLS**: Ensure all webhook endpoints use HTTPS
3. **Rate Limiting**: Configure Redis for distributed rate limiting
4. **Database**: Use PostgreSQL with proper indexes for payment tables
5. **Monitoring**: Set up alerts for payment failures and fraud detection
6. **Backup**: Regular backups of payment and invoice data

## 📞 Support

For technical support or questions about the payment implementation:
- Review the test suite output for validation
- Check logs for specific error messages
- Verify webhook signatures are properly configured
- Ensure all environment variables are set correctly

## 🔄 Future Enhancements

Planned improvements:
- Real-time payment status updates via WebSocket
- Advanced fraud detection with machine learning
- Multi-currency support beyond SAR
- Payment scheduling and recurring payments
- Enhanced reconciliation with automatic dispute resolution