const path = require('path');

module.exports = {
  // Remove i18n config for static export compatibility
  // Use react-i18next with manual language detection instead
  fallbackLng: 'en',
  defaultNS: 'common',
  ns: ['common', 'products', 'cart', 'navigation'],
  interpolation: {
    escapeValue: false,
  },
  react: {
    useSuspense: false,
  },
  reloadOnPrerender: process.env.NODE_ENV === 'development',
  
  // Load locales from public directory for static export
  backend: {
    loadPath: '/locales/{{lng}}/{{ns}}.json',
  },
  
  // Default to English, with Arabic support
  supportedLngs: ['en', 'ar'],
  detection: {
    order: ['localStorage', 'navigator', 'htmlTag'],
    caches: ['localStorage'],
  },
};