# Onboarding Guide - BrainSAIT Store
## Complete Onboarding for All User Types

Welcome to BrainSAIT Store! This comprehensive guide will help you get started based on your role and objectives.

## 👤 Choose Your Path

- [End User Onboarding](#end-user-onboarding) - Browse and purchase products
- [Developer Onboarding](#developer-onboarding) - Build integrations
- [Enterprise Onboarding](#enterprise-onboarding) - Deploy for your organization
- [Admin Onboarding](#admin-onboarding) - Manage the platform

---

## End User Onboarding

### Step 1: Create Your Account (5 minutes)

1. **Visit the Store**
   ```
   https://store.brainsait.io
   ```

2. **Sign Up**
   - Click "Sign Up" button
   - Fill in your details:
     - Full Name
     - Email Address
     - Password (min 8 characters, with uppercase, number, symbol)
     - Select Country
   - Accept Terms of Service
   - Click "Create Account"

3. **Verify Email**
   - Check your email inbox
   - Click verification link
   - You'll be redirected to the store

**✅ Checkpoint**: You should now be logged in with access to your dashboard.

### Step 2: Explore the Platform (10 minutes)

1. **Tour the Interface**
   - **Home**: Browse featured products
   - **Products**: View all available solutions
   - **My Account**: Access your profile and purchases
   - **Support**: Get help when needed

2. **Set Your Preferences**
   - Go to **Settings**
   - Choose language (English/Arabic)
   - Set notification preferences
   - Configure payment methods

3. **Browse Products**
   - Filter by category, price, technology
   - Read product descriptions
   - Check demo links
   - Review documentation

**✅ Checkpoint**: You understand the layout and can navigate easily.

### Step 3: Make Your First Purchase (15 minutes)

1. **Select a Product**
   - Choose a product that fits your needs
   - Click "View Details"
   - Review features and pricing
   - Check system requirements

2. **Add to Cart**
   - Click "Add to Cart"
   - Review cart contents
   - Apply discount code (if any)
   - Proceed to checkout

3. **Complete Payment**
   - Choose payment method:
     - 💳 **Credit Card** (Stripe)
     - 💰 **PayPal**
     - 🍎 **Apple Pay**
     - 🇸🇦 **MADA** (Saudi Arabia)
   - Enter payment details
   - Confirm purchase
   - Save receipt

**✅ Checkpoint**: Payment successful, product available in "My Products".

### Step 4: Access Your Products (5 minutes)

1. **Navigate to My Products**
   - Click "My Account" → "My Products"
   - See list of purchased items

2. **Download & Install**
   - Click product name
   - Download source code or files
   - Access documentation
   - Get API keys (if applicable)

3. **Access Support**
   - Read documentation
   - Watch tutorial videos
   - Contact support if needed
   - Join community forums

**✅ Checkpoint**: You can access and use your purchased products.

### Next Steps

- ⭐ **Rate Your Purchase**: Help others by leaving a review
- 🔔 **Set Alerts**: Get notified about updates
- 🤝 **Refer Friends**: Share with colleagues
- 📚 **Learn More**: Explore documentation

---

## Developer Onboarding

### Step 1: Environment Setup (30 minutes)

#### Prerequisites

Install required tools:

```bash
# Node.js (v18+)
node --version  # Should show v18.x.x or higher

# Python (3.11+)
python --version  # Should show 3.11.x or higher

# Git
git --version

# Cloudflare CLI
npm install -g wrangler
wrangler --version
```

#### Clone Repository

```bash
# Clone the repository
git clone https://github.com/Fadil369/brainsait-store.git
cd brainsait-store

# Explore structure
ls -la
```

**Project Structure:**
```
brainsait-store/
├── frontend/          # Next.js frontend
├── backend/           # FastAPI backend
├── docs/             # Documentation
├── infrastructure/   # Cloudflare Workers
└── scripts/          # Utility scripts
```

**✅ Checkpoint**: Repository cloned and structure understood.

### Step 2: Local Development Setup (45 minutes)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should now be running at `http://localhost:8000`

Test it:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

#### Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local
nano .env.local

# Start development server
npm run dev
```

Frontend should now be running at `http://localhost:3000`

**✅ Checkpoint**: Both backend and frontend running locally.

### Step 3: Make Your First API Call (15 minutes)

#### Generate API Key

1. Log in to your account at `http://localhost:3000`
2. Go to Settings → API Keys
3. Click "Generate New Key"
4. Copy and save the key securely

#### Test API Endpoints

```bash
# Store your API key
export API_KEY="your_api_key_here"

# Test authenticated endpoint
curl -H "Authorization: Bearer $API_KEY" \
  http://localhost:8000/api/products

# Test creating an order
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "1", "quantity": 1}' \
  http://localhost:8000/api/orders

# View API documentation
open http://localhost:8000/api/docs
```

**✅ Checkpoint**: Successfully making authenticated API calls.

### Step 4: Build Your First Integration (30 minutes)

#### Example: Product List Integration

Create a simple integration that fetches and displays products:

```javascript
// my-integration.js
const BrainSAITClient = require('./brainsait-client');

const client = new BrainSAITClient({
  apiKey: process.env.BRAINSAIT_API_KEY,
  baseUrl: 'https://api.store.brainsait.io'
});

async function listProducts() {
  try {
    const products = await client.products.list({
      page: 1,
      per_page: 10
    });
    
    console.log('Products:', products);
    return products;
  } catch (error) {
    console.error('Error:', error.message);
  }
}

listProducts();
```

#### Example: Webhook Handler

```javascript
// webhook-handler.js
const express = require('express');
const app = express();

app.use(express.json());

app.post('/webhooks/brainsait', (req, res) => {
  const event = req.body;
  
  switch (event.type) {
    case 'order.created':
      console.log('New order:', event.data);
      // Handle new order
      break;
      
    case 'payment.succeeded':
      console.log('Payment succeeded:', event.data);
      // Handle successful payment
      break;
      
    default:
      console.log('Unknown event:', event.type);
  }
  
  res.json({ received: true });
});

app.listen(3000, () => {
  console.log('Webhook handler listening on port 3000');
});
```

**✅ Checkpoint**: You've built your first integration!

### Step 5: Deploy to Production (45 minutes)

See [Deployment Guide](./deployment/README.md) for detailed instructions.

Quick deployment:

```bash
# Validate configuration
node scripts/validate-wrangler.js

# Deploy backend
cd infrastructure/cloudflare/workers
wrangler deploy --env production

# Deploy frontend
cd ../../../frontend
npm run build
wrangler pages deploy out --project-name brainsait-store
```

**✅ Checkpoint**: Application deployed to production!

### Next Steps for Developers

- 📖 **Read API Docs**: [docs/api/README.md](./api/README.md)
- 🏗️ **Explore Architecture**: [docs/architecture/README.md](./architecture/README.md)
- 🧪 **Write Tests**: [docs/development/testing.md](./development/testing.md)
- 🔧 **Customize**: Extend functionality for your needs

---

## Enterprise Onboarding

### Step 1: Initial Setup (1-2 hours)

#### Contact Sales

Email: sales@brainsait.io

Provide:
- Company name and size
- Use case and requirements
- Expected user count
- Integration needs
- Timeline

#### Receive Tenant Account

You'll receive:
- Tenant ID
- Admin credentials
- API keys
- SSO configuration details
- Support contact

**✅ Checkpoint**: Tenant account created and credentials received.

### Step 2: Configure Your Tenant (2-4 hours)

#### Brand Customization

```bash
POST /api/admin/tenant/branding
{
  "company_name": "Your Company",
  "logo_url": "https://your-company.com/logo.png",
  "primary_color": "#0066cc",
  "secondary_color": "#00cc66",
  "custom_domain": "store.your-company.com"
}
```

#### SSO Configuration

**SAML Setup:**
```bash
POST /api/admin/sso/configure
{
  "type": "saml",
  "entity_id": "https://your-idp.com/entity",
  "sso_url": "https://your-idp.com/sso",
  "certificate": "MIID..."
}
```

**Active Directory:**
```bash
POST /api/admin/sso/configure
{
  "type": "azure_ad",
  "tenant_id": "your-tenant-id",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret"
}
```

#### User Management

```bash
# Import users via CSV
POST /api/admin/users/import
Content-Type: multipart/form-data

# Or via API
POST /api/admin/users
{
  "email": "user@your-company.com",
  "name": "John Doe",
  "role": "user",
  "department": "Engineering"
}
```

**✅ Checkpoint**: Tenant configured with branding and SSO.

### Step 3: Integration & Testing (4-6 hours)

#### API Integration

```javascript
// Enterprise API client
const BrainSAIT = require('@brainsait/enterprise-sdk');

const client = new BrainSAIT({
  tenantId: 'your-tenant-id',
  apiKey: process.env.BRAINSAIT_API_KEY,
  environment: 'staging' // Test first
});

// Sync users from your system
await client.users.sync(yourUsers);

// Configure webhooks
await client.webhooks.create({
  url: 'https://your-company.com/webhooks/brainsait',
  events: ['order.created', 'user.registered']
});
```

#### Staging Environment Testing

1. Deploy to staging
2. Test SSO login
3. Verify user access
4. Test integrations
5. Validate data sync
6. Performance testing

**✅ Checkpoint**: Integration tested and working in staging.

### Step 4: Production Deployment (2-4 hours)

#### Pre-Production Checklist

- [ ] All tests passing in staging
- [ ] SSO working correctly
- [ ] User access verified
- [ ] Data migration completed
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Support team briefed
- [ ] Users notified

#### Deploy to Production

```bash
# Switch to production environment
export BRAINSAIT_ENV=production

# Deploy with enterprise configuration
./deploy-enterprise.sh
```

#### Post-Deployment Validation

```bash
# Verify deployment
curl https://store.your-company.com/health

# Test SSO
# Test critical user flows
# Verify integrations
# Check monitoring dashboards
```

**✅ Checkpoint**: Production deployment successful!

### Step 5: User Rollout (1-2 weeks)

#### Phased Rollout

**Week 1: Pilot Group (10% of users)**
- Select tech-savvy users
- Gather feedback
- Fix issues
- Document FAQs

**Week 2: Department Rollout (50% of users)**
- Roll out by department
- Provide training
- Monitor adoption
- Support users

**Week 3+: Company-Wide**
- Full rollout
- Ongoing support
- Track metrics
- Continuous improvement

**✅ Checkpoint**: All users onboarded successfully!

### Next Steps for Enterprises

- 📊 **Analytics**: Set up custom reporting
- 🔒 **Security**: Complete security audit
- 📈 **Scale**: Plan for growth
- 🎓 **Training**: Ongoing user education

---

## Admin Onboarding

### Step 1: Admin Access Setup (15 minutes)

#### Log in to Admin Panel

```
https://store.brainsait.io/admin
```

Credentials:
- Email: (provided by system admin)
- Password: (change on first login)
- 2FA: Enable immediately

#### Explore Admin Dashboard

- **Overview**: System metrics
- **Users**: User management
- **Products**: Product catalog
- **Orders**: Order management
- **Analytics**: Business insights
- **Settings**: System configuration

**✅ Checkpoint**: Admin access configured with 2FA.

### Step 2: User Management (30 minutes)

#### Create Users

```bash
# Via admin panel
Users → Create New User

# Required fields:
- Email
- Name
- Role (User, Admin, Super Admin)
- Status (Active, Inactive, Suspended)
```

#### Manage Roles

**Role Permissions:**

| Feature | User | Admin | Super Admin |
|---------|------|-------|-------------|
| Browse Products | ✅ | ✅ | ✅ |
| Purchase | ✅ | ✅ | ✅ |
| View Reports | ❌ | ✅ | ✅ |
| Manage Users | ❌ | ✅ | ✅ |
| System Config | ❌ | ❌ | ✅ |

**✅ Checkpoint**: Users created and roles assigned.

### Step 3: Product Management (45 minutes)

#### Add Products

```bash
Products → Add New Product

Fields:
- Name (EN/AR)
- Description (EN/AR)
- Price
- Category
- Technology Stack
- GitHub Repository
- Demo URL
- Documentation
```

#### Configure Pricing

```javascript
{
  "product_id": "starter-template",
  "pricing": {
    "individual": 49.99,
    "professional": 199.99,
    "enterprise": 9999.99
  },
  "currency": "USD",
  "billing_period": "one-time"
}
```

**✅ Checkpoint**: Products added and priced.

### Step 4: Analytics & Reporting (30 minutes)

#### View Dashboards

- **Revenue Dashboard**: Track sales and revenue
- **User Dashboard**: Monitor user activity
- **Product Dashboard**: Analyze product performance

#### Generate Reports

```bash
Analytics → Reports → Generate

Options:
- Date range
- Report type (Sales, Users, Products)
- Format (PDF, CSV, JSON)
- Schedule (One-time, Daily, Weekly, Monthly)
```

**✅ Checkpoint**: Reports configured and generating.

### Next Steps for Admins

- 🔔 **Alerts**: Configure system alerts
- 📧 **Communications**: Set up email templates
- 🛠️ **Maintenance**: Schedule regular maintenance
- 📚 **Training**: Learn advanced features

---

## Support & Resources

### Getting Help

**Documentation:**
- [Main Documentation](./README.md)
- [API Reference](./api/README.md)
- [Deployment Guide](./deployment/README.md)

**Support Channels:**
- Email: support@brainsait.io
- Live Chat: Available 9 AM - 5 PM GMT
- Emergency: 24/7 for critical issues

### Community

- **Discord**: Developer community
- **LinkedIn**: Professional network
- **YouTube**: Video tutorials
- **GitHub**: Open issues and discussions

---

**Document Version**: 1.0.0  
**Last Updated**: January 2025  
**Language**: English | [العربية](./ONBOARDING_AR.md)
