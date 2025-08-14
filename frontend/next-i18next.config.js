const path = require('path');

module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ar'],
    localePath: path.resolve('./public/locales'),
  },
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
};