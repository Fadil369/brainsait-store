import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import commonEn from '../../public/locales/en/common.json';
import commonAr from '../../public/locales/ar/common.json';
import productsEn from '../../public/locales/en/products.json';
import productsAr from '../../public/locales/ar/products.json';
import cartEn from '../../public/locales/en/cart.json';
import cartAr from '../../public/locales/ar/cart.json';
import navigationEn from '../../public/locales/en/navigation.json';
import navigationAr from '../../public/locales/ar/navigation.json';

const resources = {
  en: {
    common: commonEn,
    products: productsEn,
    cart: cartEn,
    navigation: navigationEn,
  },
  ar: {
    common: commonAr,
    products: productsAr,
    cart: cartAr,
    navigation: navigationAr,
  },
};

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // Default language
    fallbackLng: 'en',
    
    // Namespace configuration
    defaultNS: 'common',
    ns: ['common', 'products', 'cart', 'navigation'],
    
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false, // React already does escaping
    },
    
    // Language detection options
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      lookupLocalStorage: 'brainsait-language',
      caches: ['localStorage'],
    },
    
    // Backend options for loading translations
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    
    // React-specific options
    react: {
      useSuspense: false, // Disable suspense for SSR compatibility
      bindI18n: 'languageChanged',
      bindI18nStore: '',
    },
  });

export default i18n;