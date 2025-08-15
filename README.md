# BrainSAIT Store - Enterprise B2B Platform

A comprehensive B2B SaaS platform built with modern technologies, featuring multi-tenant architecture, advanced analytics, and enterprise-grade security.

## 🌟 Features

### Core Platform
- **Multi-tenant B2B SaaS** with Arabic/English support
- **Enterprise SSO** (SAML 2.0, OAuth 2.0, Active Directory)
- **Advanced Analytics** with real-time reporting
- **Mobile-responsive** design with RTL support

### Payment Systems
- **Stripe Integration** (Live environment ready)
- **PayPal Business** (Configured with live credentials)
- **Apple Pay** (Domain verified for store.brainsait.io)
- **App Store Connect API** (Receipt validation & subscriptions)
- **Saudi Gateways** (Mada, STC Pay with ZATCA compliance)

### Analytics & Insights
- Real-time metrics dashboard
- Revenue, customer, and product analytics
- Executive summary with KPIs
- Export functionality (JSON/CSV)
- Interactive charts and visualizations

### OID System Integration
- Connected to BrainSAIT unified platform ecosystem
- Tree visualization of components
- Automatic product synchronization
- B2B solution discovery

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   OID System    │
│   (Next.js 14)  │◄──►│   (FastAPI)      │◄──►│   Integration   │
│   Cloudflare    │    │   Cloudflare     │    │   (External)    │
│   Pages         │    │   Workers        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Cloudflare account
- Git

### Installation

1. **Clone the repository**
```bash
git clone git@github.com:Fadil369/brainsait-store.git
cd brainsait-store
```

2. **Install dependencies**
```bash
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
```

3. **Validate configuration**
```bash
# Validate wrangler.toml before deployment
node scripts/validate-wrangler.js
```

4. **Deploy**
```bash
./deploy.sh
```

## 💳 Payment Configuration (Live)

- **Stripe**: pk_live_51NU4x3HNiG2Z9ziCsNEiDlYKEG6W1jXlavyfwF8WcsEwdnGFuPEOGRPqIHfnoMK2Jydyn5Vh6KSF741Go3nFPvv100j64OFypq
- **PayPal**: ARux8wrYw6CXD_A88cgV_aVYHjXG1fFNCnyXmIX2T6_BNKUTwr12lbisklroHjs67nNJLzHHpCcuRPzp
- **Apple Pay**: merchant.io.brainsait.store
- **App Store**: WMQ3ZFI6RQAM

## 📊 B2B Pricing

- **Enterprise**: $19,999 (Full source code)
- **Professional**: $9,999 (Compiled app)
- **Starter**: $4,999 (Basic features)

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, PostgreSQL, Redis
- **Infrastructure**: Cloudflare Workers/Pages
- **Payments**: Stripe, PayPal, Apple Pay, Saudi gateways

## 📚 Documentation

### Comprehensive Documentation Hub
Explore our complete documentation at [`/docs`](./docs/README.md):

#### For Developers
- 🚀 [Development Setup](./docs/development/README.md) - Get started with local development
- 🏗️ [System Architecture](./docs/architecture/README.md) - Complete architecture overview
- 📡 [API Documentation](./docs/api/README.md) - RESTful API reference
- 🔗 [Integration Guide](./docs/integration/README.md) - Third-party integrations
- 📦 [SDK Documentation](./docs/sdk/README.md) - Official SDKs and libraries

#### For Administrators
- 👥 [Admin User Guide](./docs/admin/README.md) - Complete admin interface guide
- 🏢 [Tenant Management](./docs/admin/README.md#tenant-management) - Multi-tenant administration
- 📊 [Analytics Dashboard](./docs/admin/README.md#analytics-and-reporting) - Business intelligence

#### For DevOps
- 🚀 [Deployment Guide](./docs/deployment/README.md) - Production deployment
- 📈 [Monitoring & Operations](./docs/deployment/README.md#monitoring-and-logging) - System monitoring
- 🔄 [CI/CD Pipeline](./docs/deployment/README.md#cicd-pipeline) - Automated deployments

### Quick Reference
- **API Docs**: https://brainsait-api-gateway.fadil.workers.dev/api/docs
- **Health Check**: https://brainsait-api-gateway.fadil.workers.dev/health
- **Integration Examples**: [/docs/integration](./docs/integration/README.md)
- **SDK Samples**: [/docs/sdk](./docs/sdk/README.md)

## 🆘 Support

### Getting Help
- 📖 **Documentation**: [Complete documentation hub](./docs/README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Fadil369/brainsait-store/issues)
- 📧 **Email**: support@brainsait.io
- 🚨 **Emergency**: 24/7 support for critical issues

### Community Resources
- 💬 **Discord**: Developer community
- 📺 **YouTube**: Video tutorials and demos
- 📱 **LinkedIn**: BrainSAIT Developers Group

## 📄 License

Proprietary software owned by BrainSAIT. All rights reserved.

---

🌟 **Ready for Enterprise Deployment at store.brainsait.io**  
📚 **[Explore Complete Documentation](./docs/README.md)**