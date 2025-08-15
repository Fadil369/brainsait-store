const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

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
  webpack: (config, { dev, isServer }) => {
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
        minSize: 20000,
        maxSize: 244000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
            chunks: 'all',
            enforce: true,
          },
          analytics: {
            test: /[\\/]components[\\/]analytics[\\/]/,
            name: 'analytics',
            priority: 8,
            chunks: 'async',
            enforce: true,
          },
          payment: {
            test: /[\\/]components[\\/]payment[\\/]/,
            name: 'payment',
            priority: 8,
            chunks: 'async',
            enforce: true,
          },
          recharts: {
            test: /[\\/]node_modules[\\/]recharts[\\/]/,
            name: 'recharts',
            priority: 9,
            chunks: 'async',
            enforce: true,
          },
          framerMotion: {
            test: /[\\/]node_modules[\\/]framer-motion[\\/]/,
            name: 'framer-motion',
            priority: 9,
            chunks: 'async',
            enforce: true,
          },
          tanstackQuery: {
            test: /[\\/]node_modules[\\/]@tanstack[\\/]react-query[\\/]/,
            name: 'tanstack-query',
            priority: 9,
            chunks: 'all',
            enforce: true,
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: 5,
            chunks: 'initial',
            reuseExistingChunk: true,
          },
        },
      };

      // Add module concatenation
      config.optimization.concatenateModules = true;
      
      // Tree shaking optimization
      config.optimization.usedExports = true;
      config.optimization.sideEffects = false;
    }

    return config;
  },
  // Note: headers, redirects, and rewrites are handled by Cloudflare Pages/Workers
  // in production due to static export configuration

  // Build output configuration for Cloudflare Pages
  output: 'export',
  trailingSlash: true,
  distDir: 'out',

  // Remove default i18n for static export - use runtime i18n instead
  // i18n is handled by next-i18next and react-i18next

  // Compression
  compress: true
};

module.exports = withBundleAnalyzer(nextConfig);
