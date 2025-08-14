// Re-export all API modules
export * from './client';
export { default as productsApi } from './products';
export * from './orders';

// API configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 10000,
  USE_MOCK: process.env.NEXT_PUBLIC_USE_MOCK_API === 'true',
  VERSION: 'v1',
};

// API endpoints
export const ENDPOINTS = {
  // Products
  PRODUCTS: '/products',
  PRODUCT_BY_ID: (id: number) => `/products/${id}`,
  PRODUCTS_BY_CATEGORY: (category: string) => `/products/category/${category}`,
  PRODUCT_SEARCH: '/products/search',
  FEATURED_PRODUCTS: '/products/featured',
  PRODUCT_RECOMMENDATIONS: (id: number) => `/products/${id}/recommendations`,
  
  // Orders
  ORDERS: '/orders',
  ORDER_BY_ID: (id: string) => `/orders/${id}`,
  USER_ORDERS: '/orders/user',
  ORDER_STATUS: (id: string) => `/orders/${id}/status`,
  CANCEL_ORDER: (id: string) => `/orders/${id}/cancel`,
  
  // Payments
  PAYMENT_INTENT: '/payments/intent',
  CONFIRM_PAYMENT: (id: string) => `/payments/${id}/confirm`,
  PAYMENT_STATUS: (id: string) => `/payments/${id}/status`,
  REFUND: '/payments/refund',
  
  // Analytics (if needed)
  ANALYTICS_EVENTS: '/analytics/events',
  ANALYTICS_PRODUCTS: '/analytics/products',
  
  // Contact/Support
  CONTACT: '/contact',
  SUPPORT_TICKET: '/support/tickets',
};