# SSDP Web Application

Next.js 14 web application for SSDP platform.

## Features

- Server-side rendering (SSR)
- Arabic/English bilingual support with RTL
- Multi-tenant B2B SaaS
- Real-time analytics dashboard
- Payment gateway integration (Stripe, PayPal, Mada)
- ZATCA e-invoicing compliance

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Architecture

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **TanStack Query**: Data fetching and caching
- **next-i18next**: Internationalization

## Testing

```bash
# Run tests in watch mode
npm test

# Run tests in CI mode
npm run test:ci

# Generate coverage report
npm run test:coverage
```

## Deployment

The app is deployed on Cloudflare Pages with automatic deployments from the main branch.
