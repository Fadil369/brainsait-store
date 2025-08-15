// Centralized configuration management for BrainSAIT Store

// Environment-specific configuration
export const ENV = {
  NODE_ENV: process.env.NODE_ENV || 'development',
  IS_DEVELOPMENT: process.env.NODE_ENV === 'development',
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
  IS_TEST: process.env.NODE_ENV === 'test',
} as const;

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 10000, // 10 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
  
  // Feature flags
  USE_MOCK_API: process.env.NEXT_PUBLIC_USE_MOCK_API === 'true',
  
  // Endpoints
  ENDPOINTS: {
    PRODUCTS: '/products',
    ORDERS: '/orders',
    PAYMENTS: '/payments',
    AUTH: '/auth',
    USERS: '/users',
  },
} as const;

// Payment Configuration
export const PAYMENT_CONFIG = {
  // Stripe
  STRIPE: {
    PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
    WEBHOOK_SECRET: process.env.STRIPE_WEBHOOK_SECRET || '',
  },
  
  // PayPal
  PAYPAL: {
    CLIENT_ID: process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID || '',
    ENVIRONMENT: (process.env.NEXT_PUBLIC_PAYPAL_ENVIRONMENT as 'live' | 'sandbox') || 'sandbox',
    CURRENCY: process.env.NEXT_PUBLIC_PAYPAL_CURRENCY || 'SAR',
  },
  
  // Apple Pay
  APPLE_PAY: {
    MERCHANT_ID: process.env.NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID || '',
    DISPLAY_NAME: process.env.NEXT_PUBLIC_APPLE_PAY_DISPLAY_NAME || 'BrainSAIT Solutions',
  },
  
  // Default URLs
  URLS: {
    SUCCESS: '/payment/success',
    CANCEL: '/payment/cancel',
    ERROR: '/payment/error',
  },
  
  // Supported currencies
  SUPPORTED_CURRENCIES: ['SAR', 'USD', 'EUR'],
  DEFAULT_CURRENCY: 'SAR',
} as const;

// UI Configuration
export const UI_CONFIG = {
  // Themes
  THEMES: {
    DEFAULT: 'dark',
    AVAILABLE: ['light', 'dark', 'auto'],
  },
  
  // Languages
  LANGUAGES: {
    DEFAULT: 'en',
    SUPPORTED: ['en', 'ar'],
    RTL_LANGUAGES: ['ar'],
  },
  
  // Pagination
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 12,
    PAGE_SIZE_OPTIONS: [6, 12, 24, 48],
    MAX_PAGE_SIZE: 100,
  },
  
  // Animations
  ANIMATIONS: {
    DURATION: {
      FAST: 150,
      NORMAL: 300,
      SLOW: 500,
    },
    EASING: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
  
  // Breakpoints (matching Tailwind)
  BREAKPOINTS: {
    SM: 640,
    MD: 768,
    LG: 1024,
    XL: 1280,
    '2XL': 1536,
  },
} as const;

// Cache Configuration
export const CACHE_CONFIG = {
  // Query cache times (in milliseconds)
  STALE_TIME: {
    SHORT: 1 * 60 * 1000,      // 1 minute
    MEDIUM: 5 * 60 * 1000,     // 5 minutes
    LONG: 15 * 60 * 1000,      // 15 minutes
    VERY_LONG: 30 * 60 * 1000, // 30 minutes
  },
  
  GC_TIME: {
    SHORT: 2 * 60 * 1000,      // 2 minutes
    MEDIUM: 10 * 60 * 1000,    // 10 minutes
    LONG: 30 * 60 * 1000,      // 30 minutes
    VERY_LONG: 60 * 60 * 1000, // 1 hour
  },
  
  // Local storage keys
  STORAGE_KEYS: {
    AUTH_TOKEN: 'brainsait-auth-token',
    REFRESH_TOKEN: 'brainsait-refresh-token',
    LANGUAGE: 'brainsait-language',
    THEME: 'brainsait-theme',
    CART: 'brainsait-cart',
    USER_PREFERENCES: 'brainsait-user-preferences',
  },
} as const;

// Validation Configuration
export const VALIDATION_CONFIG = {
  // Password requirements
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_NUMBERS: true,
    REQUIRE_SPECIAL_CHARS: true,
  },
  
  // File upload limits
  FILE_UPLOAD: {
    MAX_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    MAX_FILES: 5,
  },
  
  // Form validation patterns
  PATTERNS: {
    EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    SAUDI_PHONE: /^(\+966|966|0)?[5][0-9]{8}$/,
    SAUDI_VAT: /^[0-9]{15}$/,
    IBAN: /^SA[0-9]{2}[0-9]{18}$/,
  },
  
  // Input limits
  LIMITS: {
    PRODUCT_NAME: { MIN: 3, MAX: 100 },
    PRODUCT_DESCRIPTION: { MIN: 10, MAX: 1000 },
    REVIEW_TEXT: { MIN: 10, MAX: 500 },
    COMPANY_NAME: { MIN: 2, MAX: 100 },
  },
} as const;

// Business Configuration
export const BUSINESS_CONFIG = {
  // Company information
  COMPANY: {
    NAME: 'BrainSAIT Solutions',
    NAME_AR: 'حلول برين سايت',
    VAT_NUMBER: process.env.NEXT_PUBLIC_VAT_NUMBER || '',
    CR_NUMBER: process.env.NEXT_PUBLIC_CR_NUMBER || '',
    EMAIL: 'info@brainsait.com',
    PHONE: '+966501234567',
    ADDRESS: 'Riyadh, Saudi Arabia',
    ADDRESS_AR: 'الرياض، المملكة العربية السعودية',
  },
  
  // Tax configuration
  TAX: {
    VAT_RATE: 0.15, // 15% VAT in Saudi Arabia
    ENABLED: true,
    INCLUSIVE: false, // Tax added on top of price
  },
  
  // Shipping configuration
  SHIPPING: {
    FREE_SHIPPING_THRESHOLD: 500, // SAR
    STANDARD_RATE: 25, // SAR
    EXPRESS_RATE: 50, // SAR
    DELIVERY_DAYS: {
      STANDARD: '3-5',
      EXPRESS: '1-2',
    },
  },
  
  // Product categories
  CATEGORIES: [
    { id: 'ai', name: 'AI Solutions', nameAr: 'حلول الذكاء الاصطناعي' },
    { id: 'apps', name: 'Mobile Apps', nameAr: 'تطبيقات الجوال' },
    { id: 'websites', name: 'Websites', nameAr: 'المواقع الإلكترونية' },
    { id: 'templates', name: 'Templates', nameAr: 'القوالب' },
    { id: 'ebooks', name: 'E-books', nameAr: 'الكتب الإلكترونية' },
    { id: 'courses', name: 'Courses', nameAr: 'الدورات' },
    { id: 'tools', name: 'Tools', nameAr: 'الأدوات' },
  ],
  
  // License types
  LICENSE_TYPES: [
    { id: 'app_only', name: 'App Only', nameAr: 'التطبيق فقط', price_multiplier: 1 },
    { id: 'app_with_source', name: 'App + Source Code', nameAr: 'التطبيق + الكود المصدري', price_multiplier: 2.5 },
    { id: 'enterprise', name: 'Enterprise License', nameAr: 'ترخيص المؤسسات', price_multiplier: 5 },
  ],
} as const;

// Feature Flags
export const FEATURES = {
  // Payment features
  STRIPE_ENABLED: !!PAYMENT_CONFIG.STRIPE.PUBLISHABLE_KEY,
  PAYPAL_ENABLED: !!PAYMENT_CONFIG.PAYPAL.CLIENT_ID,
  APPLE_PAY_ENABLED: !!PAYMENT_CONFIG.APPLE_PAY.MERCHANT_ID,
  
  // UI features
  DARK_MODE: true,
  RTL_SUPPORT: true,
  ANIMATIONS: !ENV.IS_TEST, // Disable animations in tests
  
  // Advanced features
  MULTI_CURRENCY: false,
  AFFILIATE_PROGRAM: false,
  REVIEWS_ENABLED: true,
  WISHLIST_ENABLED: true,
  COMPARISON_ENABLED: true,
  
  // Analytics and tracking
  ANALYTICS_ENABLED: ENV.IS_PRODUCTION,
  ERROR_TRACKING: ENV.IS_PRODUCTION,
  PERFORMANCE_MONITORING: ENV.IS_PRODUCTION,
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK: 'Network error. Please check your internet connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Internal server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  PAYMENT_FAILED: 'Payment processing failed. Please try again.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',
  
  // Form-specific errors
  REQUIRED_FIELD: 'This field is required.',
  INVALID_EMAIL: 'Please enter a valid email address.',
  INVALID_PHONE: 'Please enter a valid phone number.',
  PASSWORD_TOO_SHORT: `Password must be at least ${VALIDATION_CONFIG.PASSWORD.MIN_LENGTH} characters long.`,
  PASSWORDS_DO_NOT_MATCH: 'Passwords do not match.',
  FILE_TOO_LARGE: `File size must be less than ${VALIDATION_CONFIG.FILE_UPLOAD.MAX_SIZE / (1024 * 1024)}MB.`,
  INVALID_FILE_TYPE: 'Invalid file type. Please upload an image.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  PAYMENT_SUCCESS: 'Payment completed successfully!',
  ORDER_CREATED: 'Order created successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
  PASSWORD_CHANGED: 'Password changed successfully!',
  EMAIL_SENT: 'Email sent successfully!',
  ITEM_ADDED_TO_CART: 'Item added to cart!',
  ITEM_REMOVED_FROM_CART: 'Item removed from cart!',
  REVIEW_SUBMITTED: 'Review submitted successfully!',
  SUBSCRIPTION_SUCCESS: 'Subscription successful!',
} as const;

// SEO Configuration
export const SEO_CONFIG = {
  DEFAULT_TITLE: 'BrainSAIT Store - Premium Digital Solutions',
  DEFAULT_TITLE_AR: 'متجر برين سايت - حلول رقمية متميزة',
  DEFAULT_DESCRIPTION: 'Discover premium mobile apps, AI solutions, and digital products for your business.',
  DEFAULT_DESCRIPTION_AR: 'اكتشف تطبيقات الجوال المتميزة وحلول الذكاء الاصطناعي والمنتجات الرقمية لعملك.',
  DEFAULT_KEYWORDS: 'mobile apps, AI solutions, digital products, Saudi Arabia, BrainSAIT',
  DEFAULT_KEYWORDS_AR: 'تطبيقات الجوال، حلول الذكاء الاصطناعي، المنتجات الرقمية، السعودية، برين سايت',
  
  SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || 'https://brainsait.com',
  LOGO_URL: '/logo.png',
  
  SOCIAL: {
    TWITTER: '@brainsait',
    FACEBOOK: 'brainsait',
    LINKEDIN: 'brainsait-solutions',
    INSTAGRAM: 'brainsait',
  },
} as const;

// Helper functions to get configuration
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

export const getPaymentReturnUrl = (type: 'success' | 'cancel' | 'error' = 'success'): string => {
  return `${typeof window !== 'undefined' ? window.location.origin : ''}${PAYMENT_CONFIG.URLS[type.toUpperCase() as keyof typeof PAYMENT_CONFIG.URLS]}`;
};

export const isFeatureEnabled = (feature: keyof typeof FEATURES): boolean => {
  return FEATURES[feature];
};

export const getStorageKey = (key: keyof typeof CACHE_CONFIG.STORAGE_KEYS): string => {
  return CACHE_CONFIG.STORAGE_KEYS[key];
};

// Type exports for better TypeScript support
export type SupportedLanguage = typeof UI_CONFIG.LANGUAGES.SUPPORTED[number];
export type SupportedCurrency = typeof PAYMENT_CONFIG.SUPPORTED_CURRENCIES[number];
export type ProductCategory = typeof BUSINESS_CONFIG.CATEGORIES[number]['id'];
export type LicenseType = typeof BUSINESS_CONFIG.LICENSE_TYPES[number]['id'];

// Export main configuration object
export const CONFIG = {
  ENV,
  API: API_CONFIG,
  PAYMENT: PAYMENT_CONFIG,
  UI: UI_CONFIG,
  CACHE: CACHE_CONFIG,
  VALIDATION: VALIDATION_CONFIG,
  BUSINESS: BUSINESS_CONFIG,
  FEATURES,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  SEO: SEO_CONFIG,
} as const;

export default CONFIG;