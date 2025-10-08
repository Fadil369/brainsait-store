# Quick Start Guide - BrainSAIT Store
## Get Started in 5 Minutes

Welcome to BrainSAIT Store! This guide will help you get up and running quickly.

## 🚀 For End Users

### Browse Products

1. **Visit the Store**
   - Go to [https://store.brainsait.io](https://store.brainsait.io)
   - Browse available products and solutions

2. **Create an Account**
   - Click "Sign Up" in the top right
   - Fill in your details (Email, Name, Password)
   - Verify your email address

3. **Make a Purchase**
   - Select a product
   - Click "Add to Cart"
   - Proceed to checkout
   - Choose payment method (Stripe, PayPal, Apple Pay)
   - Complete purchase

4. **Access Your Products**
   - Go to "My Account" → "My Products"
   - Download purchased products
   - Access documentation and support

### Language Support

**Switch Language:**
- Click the language selector (🌐) in the top right
- Choose between English (EN) and Arabic (AR)
- The entire interface will adapt to your language

## 💻 For Developers

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/Fadil369/brainsait-store.git
cd brainsait-store

# Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# Run in development mode
cd frontend && npm run dev  # Frontend at http://localhost:3000
cd backend && uvicorn app.main:app --reload  # Backend at http://localhost:8000
```

### Environment Setup

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_PAYPAL_CLIENT_ID=your-paypal-client-id
```

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/brainsait_store
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_...
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get products
curl http://localhost:8000/api/products

# API documentation
open http://localhost:8000/api/docs
```

## 🔌 For API Users

### Authentication

1. **Get API Key**
   - Log in to your account
   - Go to "Settings" → "API Keys"
   - Click "Generate New Key"
   - Copy and store securely

2. **Make API Calls**

```bash
# Example: Get products
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.store.brainsait.io/api/products

# Example: Create order
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "123", "quantity": 1}' \
  https://api.store.brainsait.io/api/orders
```

### API Documentation

- **Interactive Docs**: [https://api.store.brainsait.io/api/docs](https://api.store.brainsait.io/api/docs)
- **OpenAPI Schema**: [https://api.store.brainsait.io/api/openapi.json](https://api.store.brainsait.io/api/openapi.json)
- **Full API Guide**: [docs/api/README.md](./api/README.md)

## 🎯 Common Tasks

### Change Language Preference

**User Interface:**
1. Click language selector (🌐) in header
2. Select preferred language (EN/AR)

**Programmatically:**
```javascript
// Set language in localStorage
localStorage.setItem('preferred-language', 'ar');

// Or via Accept-Language header
fetch('/api/products', {
  headers: {
    'Accept-Language': 'ar'
  }
});
```

### Process Payment

**Stripe:**
```javascript
const stripe = Stripe('pk_live_...');

const {error, paymentMethod} = await stripe.createPaymentMethod({
  type: 'card',
  card: cardElement,
});

if (!error) {
  // Send paymentMethod.id to your backend
  await fetch('/api/payments/process', {
    method: 'POST',
    body: JSON.stringify({
      payment_method: paymentMethod.id,
      amount: 9999
    })
  });
}
```

**PayPal:**
```javascript
paypal.Buttons({
  createOrder: function(data, actions) {
    return actions.order.create({
      purchase_units: [{
        amount: {value: '99.99'}
      }]
    });
  },
  onApprove: function(data, actions) {
    return actions.order.capture();
  }
}).render('#paypal-button-container');
```

### Handle Webhooks

**Stripe Webhooks:**
```javascript
const webhook = await stripe.webhooks.constructEvent(
  request.body,
  signature,
  webhookSecret
);

switch (webhook.type) {
  case 'payment_intent.succeeded':
    // Handle successful payment
    break;
  case 'payment_intent.failed':
    // Handle failed payment
    break;
}
```

## 🏢 For Enterprise Users

### Multi-Tenant Setup

1. **Request Tenant Account**
   - Contact: sales@brainsait.io
   - Provide company details
   - Receive tenant credentials

2. **Configure Tenant**
   - Set company branding
   - Configure SSO (SAML/OAuth)
   - Set up team members
   - Configure billing

3. **Integrate Systems**
   - Use tenant-specific API keys
   - Configure webhooks
   - Set up data sync
   - Test integration

### SSO Integration

**SAML 2.0:**
```bash
# Configure SSO in admin panel
POST /api/admin/sso/configure
{
  "type": "saml",
  "entity_id": "https://your-idp.com/entity",
  "sso_url": "https://your-idp.com/sso",
  "certificate": "MIIDXTCCAkWgAwIBAgIJ..."
}
```

**OAuth 2.0:**
```bash
# Configure OAuth
POST /api/admin/sso/configure
{
  "type": "oauth2",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "authorize_url": "https://provider.com/oauth/authorize",
  "token_url": "https://provider.com/oauth/token"
}
```

## 📚 Next Steps

### Learn More

- **Architecture**: [docs/architecture/README.md](./architecture/README.md)
- **API Reference**: [docs/api/README.md](./api/README.md)
- **Deployment**: [docs/deployment/README.md](./deployment/README.md)
- **Development**: [docs/development/README.md](./development/README.md)

### Get Help

- **Documentation**: [docs/README.md](./docs/README.md)
- **Support Email**: support@brainsait.io
- **GitHub Issues**: [github.com/Fadil369/brainsait-store/issues](https://github.com/Fadil369/brainsait-store/issues)

### Join Community

- **Discord**: Join our developer community
- **LinkedIn**: Follow BrainSAIT on LinkedIn
- **YouTube**: Video tutorials and demos

## 🔒 Security Best Practices

1. **API Keys**: Never commit API keys to version control
2. **HTTPS**: Always use HTTPS in production
3. **Secrets**: Store secrets in environment variables
4. **Authentication**: Use strong passwords and 2FA
5. **Updates**: Keep dependencies up to date

## 💡 Tips & Tricks

### Performance Optimization

```javascript
// Use pagination for large lists
fetch('/api/products?page=1&per_page=20');

// Cache responses
const cache = new Map();
if (cache.has(key)) {
  return cache.get(key);
}

// Use compression
headers: {
  'Accept-Encoding': 'gzip, deflate, br'
}
```

### Error Handling

```javascript
try {
  const response = await fetch('/api/products');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  console.error('Failed to fetch products:', error);
  // Show user-friendly error message
}
```

### Testing

```bash
# Run frontend tests
cd frontend && npm test

# Run backend tests
cd backend && pytest

# Run E2E tests
cd frontend && npm run test:e2e
```

## 🎓 Tutorials

### Tutorial 1: Create Your First Integration

1. Generate API key
2. Make test API call
3. Handle authentication
4. Process webhook events
5. Deploy to production

**Estimated Time**: 30 minutes

### Tutorial 2: Build a Custom Store

1. Clone the repository
2. Customize branding
3. Add custom products
4. Configure payment gateways
5. Deploy to Cloudflare

**Estimated Time**: 2 hours

### Tutorial 3: Multi-Language Support

1. Add translation files
2. Configure i18n
3. Test RTL layout
4. Deploy bilingual site

**Estimated Time**: 1 hour

## 📞 Support

### Need Help?

**Quick Links:**
- [FAQ](./docs/FAQ.md)
- [Troubleshooting](./docs/deployment/TROUBLESHOOTING.md)
- [API Status](https://status.brainsait.io)

**Contact:**
- **General**: support@brainsait.io
- **Sales**: sales@brainsait.io
- **Security**: security@brainsait.io
- **Emergency**: Available 24/7 for critical issues

---

**Document Version**: 1.0.0  
**Last Updated**: January 2025  
**Language**: English | [العربية](./QUICKSTART_AR.md)
