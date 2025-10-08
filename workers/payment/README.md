# Payment Worker

Cloudflare Worker for asynchronous payment processing.

## Features

- Async payment processing
- Webhook handling (Stripe, PayPal, Mada)
- Payment status updates
- Refund processing
- Transaction logging
- Multi-provider support

## Supported Payment Gateways

- Stripe
- PayPal
- Mada (Saudi)
- STC Pay
- Apple Pay

## API

### Endpoints
- `POST /webhooks/stripe` - Stripe webhook
- `POST /webhooks/paypal` - PayPal webhook
- `POST /webhooks/mada` - Mada webhook
- `POST /process` - Manual payment processing

## Security

- Webhook signature verification
- PCI DSS compliance
- Encrypted data storage
- Audit logging

## Configuration

Environment variables:
- `STRIPE_SECRET_KEY` - Stripe API key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `PAYPAL_CLIENT_ID` - PayPal client ID
- `PAYPAL_SECRET` - PayPal secret
- `MADA_API_KEY` - Mada API key

## Development

```bash
npm install
npm run dev
```

## Deployment

```bash
npm run deploy
```
