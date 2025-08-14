/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // appDir is now default in Next.js 14
  },
  
  // Disable ESLint during build for deployment
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // Image optimization
  images: {
    domains: [
      'store.brainsait.io',
      'brainsait.io',
      'api.store.brainsait.io',
      'localhost',
      'api.brainsait.com'
    ],
    formats: ['image/webp', 'image/avif'],
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://api.store.brainsait.io',
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
    NEXT_PUBLIC_PAYPAL_CLIENT_ID: process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID,
    NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID: process.env.NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID,
  },

  // Enable SWC minifier for better performance
  swcMinify: true,
  // Optimize performance
  poweredByHeader: false,
  reactStrictMode: true,
  
  // Configure for Arabic RTL support and bundle optimization
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }

    // Add support for importing .wasm files
    config.experiments = {
      asyncWebAssembly: true,
      layers: true,
    };

    // Optimize bundle
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
            chunks: 'all',
          },
          analytics: {
            test: /[\\/]components[\\/]analytics[\\/]/,
            name: 'analytics',
            priority: 5,
            chunks: 'all',
          },
          payment: {
            test: /[\\/]components[\\/]payment[\\/]/,
            name: 'payment',
            priority: 5,
            chunks: 'all',
          },
        },
      };
    }

    return config;
  },
  // Security and Apple Pay headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'geolocation=(), microphone=(), camera=()',
          },
        ],
      },
      {
        source: '/.well-known/apple-developer-merchantid-domain-association.txt',
        headers: [
          {
            key: 'Content-Type',
            value: 'text/plain',
          },
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400',
          },
        ],
      },
      {
        source: '/.well-known/apple-developer-merchantid-domain-association',
        headers: [
          {
            key: 'Content-Type',
            value: 'text/plain',
          },
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400',
          },
        ],
      },
    ];
  },

  // Redirects and rewrites
  async redirects() {
    return [
      {
        source: '/admin',
        destination: '/dashboard',
        permanent: true,
      },
    ];
  },

  async rewrites() {
    const rewrites = [
      {
        source: '/.well-known/apple-developer-merchantid-domain-association.txt',
        destination: '/.well-known/apple-developer-merchantid-domain-association.txt',
      },
    ];

    // API proxy for development
    if (process.env.NODE_ENV === 'development') {
      rewrites.push({
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      });
    }

    return rewrites;
  },

  // Build output configuration for Cloudflare Pages
  output: 'export',
  trailingSlash: true,
  distDir: 'out',
  
  // Remove default i18n for static export - use runtime i18n instead
  // i18n is handled by next-i18next and react-i18next

  // Trailing slash
  trailingSlash: false,
};

module.exports = nextConfig;