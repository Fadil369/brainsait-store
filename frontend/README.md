# BrainSAIT Store - Next.js Frontend

A modern, bilingual e-commerce platform built with Next.js 14, TypeScript, and Tailwind CSS. Supporting Saudi Vision 2030 with Arabic/English internationalization and premium digital solutions.

## 🚀 Features

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** with custom design system
- **Bilingual Support** (Arabic/English) with RTL
- **State Management** with Zustand
- **API Integration** with React Query
- **Responsive Design** mobile-first approach
- **Glassmorphism UI** with modern animations
- **Cart & Checkout** functionality
- **Product Demo** modals
- **Vision 2030** compliance branding

## 🛠️ Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Internationalization**: react-i18next
- **Icons**: Heroicons
- **Animations**: Framer Motion
- **Forms**: React Hook Form + Zod
- **Notifications**: React Hot Toast

## 🚀 Quick Start

### Prerequisites

- Node.js 18.17 or later
- npm or yarn or pnpm

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd brainsait-store/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Environment Setup**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` with your configuration:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_USE_MOCK_API=true
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

5. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
src/
├── app/                    # Next.js 14 App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── features/         # Feature-specific components
│   ├── layout/           # Layout components
│   ├── sections/         # Page sections
│   └── ui/               # Reusable UI components
├── data/                 # Static data and mock data
├── hooks/                # Custom React hooks
├── lib/                  # Utility libraries
│   ├── api/             # API integration
│   ├── i18n.ts          # Internationalization setup
│   ├── providers.tsx    # App providers
│   └── utils.ts         # Utility functions
├── stores/               # Zustand stores
├── types/                # TypeScript type definitions
└── public/
    └── locales/         # Translation files
        ├── en/          # English translations
        └── ar/          # Arabic translations
```

## 🎨 Design System

### Colors
- **Primary**: `#00d4aa` (Vision Green)
- **Secondary**: `#00a886`
- **Accent**: `#ff6b35`
- **Vision Purple**: `#7c3aed`
- **Dark**: `#000000`
- **Text Primary**: `#ffffff`
- **Text Secondary**: `#94a3b8`

### Typography
- **Font Family**: Inter (Latin), Noto Sans Arabic (Arabic)
- **Responsive Sizes**: Using clamp() for fluid typography
- **Font Weights**: 300-900 range

### Components
All components follow the glassmorphism design pattern with:
- Semi-transparent backgrounds
- Backdrop blur effects
- Subtle borders
- Smooth animations

## 🌐 Internationalization

The app supports Arabic and English with:

- **RTL Support**: Automatic text direction switching
- **Translation Files**: JSON-based translations in `/public/locales`
- **Dynamic Language**: Runtime language switching
- **Localized Content**: Product titles, descriptions, and features
- **Cultural Adaptation**: Date formats, number formats, currency

### Adding Translations

1. Edit translation files in `/public/locales/{lang}/{namespace}.json`
2. Use the `useTranslation` hook in components
3. Follow the existing key structure for consistency

## 🛒 Cart & E-commerce Features

- **Persistent Cart**: Saved in localStorage
- **Real-time Updates**: Instant quantity and price updates
- **VAT Calculation**: Automatic 15% Saudi VAT
- **Multiple Currencies**: SAR support with proper formatting
- **Checkout Flow**: Integrated payment processing ready

## 📱 Responsive Design

Built mobile-first with breakpoints:
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px - 1399px
- **Large Desktop**: 1400px+

## 🎭 Animations & Performance

- **Framer Motion**: Smooth page transitions
- **CSS Animations**: Lightweight hover effects
- **Lazy Loading**: Images and components
- **Code Splitting**: Automatic with Next.js
- **Optimized Bundle**: Tree-shaking and minification

## 🔌 API Integration

### Development Mode
- Uses mock data by default
- Enable with `NEXT_PUBLIC_USE_MOCK_API=true`
- All endpoints return simulated responses

### Production Mode
- Connects to FastAPI backend
- Full CRUD operations
- Error handling and retry logic
- Request/response interceptors

## 🧪 Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
npm run test:ci      # Run tests for CI
```

## 📦 Dependencies

### Core Dependencies
- `next`: 14.1.0
- `react`: 18.2.0
- `typescript`: 5.3.3
- `tailwindcss`: 3.4.1

### State & Data
- `zustand`: 4.4.7
- `@tanstack/react-query`: 5.17.9
- `axios`: 1.6.5

### UI & Animation
- `framer-motion`: 10.18.0
- `@headlessui/react`: 1.7.17
- `@heroicons/react`: 2.1.1

### Internationalization
- `next-i18next`: 15.2.0
- `react-i18next`: 14.0.0
- `i18next`: 23.7.16

### Forms & Validation
- `react-hook-form`: 7.48.2
- `zod`: 3.22.4
- `@hookform/resolvers`: 3.3.4

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Configure environment variables
3. Deploy automatically on push to main

### Manual Deployment
```bash
npm run build
npm run start
```

### Environment Variables
Required for production:
```env
NEXT_PUBLIC_API_URL=https://api.brainsait.com/v1
NEXT_PUBLIC_USE_MOCK_API=false
NEXT_PUBLIC_APP_URL=https://store.brainsait.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Dr. Fadil**
- LinkedIn: [@fadil369](https://linkedin.com/in/fadil369)
- Twitter: [@brainsait369](https://x.com/brainsait369)
- GitHub: [@fadil369](https://github.com/fadil369)

## 🇸🇦 Saudi Vision 2030

This project proudly supports Saudi Arabia's Vision 2030 digital transformation goals by:
- Promoting local digital innovation
- Supporting Arabic language technology
- Enabling e-commerce growth
- Fostering tech entrepreneurship

---

Built with ❤️ for Saudi Arabia's digital future