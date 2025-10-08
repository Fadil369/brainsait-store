# ZATCA & Payment Integration - Quick Reference

## 🚀 Quick Start

### 1. Configure Environment Variables
```bash
# Copy example configuration
cp backend/.env.example.zatca backend/.env

# Edit with your credentials
nano backend/.env
```

### 2. Test Services
```python
# Test imports
python3 -c "from app.services.zatca_service import ZATCAService; print('✅ Ready')"

# Run tests
pytest backend/tests/services/ -v
```

### 3. Make First API Call
```bash
# Get available payment methods
curl http://localhost:8000/api/v1/payments/methods

# Create Mada payment
curl -X POST http://localhost:8000/api/v1/payments/mada/intent \
  -H "Content-Type: application/json" \
  -d '{"order_id":"uuid","amount":100.00}'
```

---

## 📋 Service API Cheat Sheet

### ZATCA Service

```python
from app.services.zatca_service import ZATCAService

zatca = ZATCAService()

# Generate invoice with QR code
invoice = await zatca.generate_invoice(order_id, payment_id, db)
# Returns: {invoice_number, zatca_uuid, qr_code, invoice_hash, xml_invoice}

# Validate invoice
validation = await zatca.validate_invoice(invoice_data)
# Returns: {valid: bool, errors: [], warnings: []}

# Calculate VAT
vat = zatca.calculate_vat(Decimal("100.00"), vat_inclusive=False)
# Returns: {subtotal: 100.00, vat_amount: 15.00, total: 115.00}

# Submit to ZATCA
result = await zatca.submit_to_zatca(invoice_id, "reporting", db)
# Returns: {status: "approved", zatca_response: {...}}
```

### Mada Service

```python
from app.services.payment_providers import MadaService

mada = MadaService()

# Create payment
payment = await mada.create_payment_intent(
    amount=100.00,
    order_id=uuid,
    customer_info={"name":"...", "email":"...", "phone":"..."}
)
# Returns: {payment_id, redirect_url, status, expires_at}

# Verify payment
status = await mada.verify_payment(payment_id)
# Returns: {payment_id, status, amount, card_last4, card_brand}

# Verify webhook
is_valid = mada.verify_webhook_signature(payload, signature)
```

### STC Pay Service

```python
from app.services.payment_providers import STCPayService

stc = STCPayService()

# Create payment with QR
payment = await stc.create_payment_intent(
    amount=100.00,
    order_id=uuid,
    customer_info={"name":"...", "phone":"..."}
)
# Returns: {transaction_id, qr_code, payment_url, status}

# Generate QR only
qr = await stc.generate_qr_code(amount=100.00, order_id=uuid)
# Returns: {qr_code, qr_code_url, expires_at}

# Verify payment
status = await stc.verify_payment(transaction_id)
```

### Notification Service

```python
from app.services.notifications import NotificationService

notif = NotificationService()

# Email (English)
await notif.send_payment_confirmation(
    email="customer@example.com",
    order_id=uuid,
    amount=100.00,
    language="en"
)

# SMS (Arabic)
await notif.send_payment_confirmation_sms(
    phone="+966501234567",
    order_id=uuid,
    amount=100.00,
    language="ar"
)

# Invoice notification
await notif.send_invoice_notification(
    email="customer@example.com",
    invoice_number="INV-2024-001",
    invoice_url="https://...",
    language="ar"
)
```

---

## 🔑 Configuration Quick Reference

### Essential Variables
```bash
# ZATCA
ZATCA_ENABLED=true
ZATCA_VAT_NUMBER=300000000000XXX  # 15 digits, starts with 3
ZATCA_CR_NUMBER=1234567890XXX
ZATCA_SELLER_NAME="Company Name"
ZATCA_SELLER_NAME_AR="اسم الشركة"

# Mada
MADA_MERCHANT_ID=mada_merchant_XXX
MADA_API_KEY=mada_key_XXX
MADA_ENDPOINT=https://api.mada.sa

# STC Pay
STC_PAY_MERCHANT_ID=stcpay_merchant_XXX
STC_PAY_API_KEY=stcpay_key_XXX
STC_PAY_ENDPOINT=https://api.stcpay.com.sa

# Stripe
STRIPE_SECRET_KEY=sk_test_XXX
STRIPE_WEBHOOK_SECRET=whsec_XXX

# SMS (Unifonic)
SMS_PROVIDER=unifonic
UNIFONIC_APP_SID=your_app_sid
UNIFONIC_SENDER_ID=YourBrand

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## 📊 API Endpoints Quick Reference

### Payment Methods
```
GET  /api/v1/payments/methods
```

### Create Payment Intents
```
POST /api/v1/payments/stripe/intent
POST /api/v1/payments/mada/intent
POST /api/v1/payments/stc-pay/intent
```

### Webhooks
```
POST /api/v1/payments/webhooks/stripe
POST /api/v1/payments/webhooks/mada
POST /api/v1/payments/webhooks/stc-pay
```

### Invoices
```
GET  /api/v1/payments/invoices/{order_id}
```

---

## 🧪 Testing Commands

```bash
# Run all payment tests
pytest backend/tests/services/ -v

# Run specific service tests
pytest backend/tests/services/test_zatca_service.py -v
pytest backend/tests/services/test_payment_providers.py -v
pytest backend/tests/services/test_notifications.py -v

# With coverage
pytest backend/tests/services/ --cov=app/services --cov-report=html

# Run single test
pytest backend/tests/services/test_zatca_service.py::TestZATCAService::test_generate_zatca_qr_code -v
```

---

## 🐛 Common Issues & Quick Fixes

### ZATCA QR Code Not Scanning
```python
# Verify TLV encoding
import base64
decoded = base64.b64decode(qr_code)
print(f"QR Size: {len(decoded)} bytes")  # Should be > 100
```

### Mada Signature Verification Failed
```python
# Check signature generation
payload = {"merchant_id": "...", "amount": "100.00"}
signature = mada._generate_signature(payload)
print(f"Signature: {signature}")  # Should be 64 chars (SHA-256)
```

### Email Not Sending
```bash
# Test SMTP connection
python3 -c "
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('email@gmail.com', 'app_password')
print('✅ SMTP OK')
"
```

### SMS Not Delivered
```python
# Check phone format
phone = "+966501234567"  # Must start with +966
assert phone.startswith("+966"), "Invalid Saudi phone number"
```

---

## 📈 Monitoring & Logging

### Check Logs
```python
import logging
logger = logging.getLogger(__name__)

# ZATCA logs
logger.info(f"ZATCA invoice generated for order {order_id}")
logger.error(f"ZATCA submission failed: {error}")

# Payment logs
logger.info(f"Payment {payment_id} status: {status}")
logger.error(f"Payment webhook verification failed")
```

### Database Queries
```sql
-- Check ZATCA submissions
SELECT * FROM zatca_submissions 
WHERE status != 'APPROVED' 
ORDER BY created_at DESC;

-- Check payment status
SELECT * FROM payments 
WHERE status = 'FAILED'
ORDER BY created_at DESC;

-- Invoice audit
SELECT invoice_number, zatca_status, created_at 
FROM invoices 
WHERE zatca_status = 'REJECTED';
```

---

## 🔗 Quick Links

- **Full Documentation**: [ZATCA_PAYMENT_INTEGRATION.md](./ZATCA_PAYMENT_INTEGRATION.md)
- **Configuration**: [.env.example.zatca](./backend/.env.example.zatca)
- **ZATCA Portal**: https://zatca.gov.sa
- **Mada**: https://mada.com.sa
- **STC Pay**: https://stcpay.com.sa
- **Stripe**: https://stripe.com/docs

---

## 💡 Tips

1. **Always test in sandbox first** - Use test credentials before production
2. **Verify webhooks** - Always check HMAC signatures
3. **Log everything** - Audit trail is crucial for compliance
4. **Handle failures gracefully** - Implement retry logic
5. **Keep credentials secure** - Use environment variables
6. **Monitor regularly** - Check ZATCA submission status daily
7. **Rotate keys** - Change API keys periodically
8. **Test bilingual** - Test both Arabic and English flows

---

## 🆘 Support

- Technical Issues: support@brainsait.com
- ZATCA Compliance: compliance@brainsait.com
- Payment Gateway: payments@brainsait.com

---

## ✅ Pre-Production Checklist

- [ ] All environment variables set
- [ ] Production credentials configured
- [ ] ZATCA credentials verified
- [ ] Webhook endpoints configured
- [ ] SSL certificates installed
- [ ] Email/SMS providers tested
- [ ] Backup and monitoring set up
- [ ] Tests passing in production environment
- [ ] Documentation reviewed
- [ ] Team trained on new features

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-09  
**Status**: Production Ready ✅
