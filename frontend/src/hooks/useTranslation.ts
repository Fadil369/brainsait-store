// Simple translation hook for App Router compatibility
import { useAppStore } from '@/stores';

// Translation data - simplified for now
const translations = {
  en: {
    common: {
      loading: 'Loading...',
      error: 'Error',
      retry: 'Retry',
      'filters.all': 'All Products',
      'filters.ai': 'AI Solutions',
      'filters.websites': 'Websites',
      'filters.apps': 'Applications', 
      'filters.tools': 'Tools',
      'filters.courses': 'Courses',
      'hero.title': 'BrainSAIT Store',
      'hero.subtitle': 'Digital Innovation Hub',
    }
  },
  ar: {
    common: {
      loading: 'جاري التحميل...',
      error: 'خطأ',
      retry: 'إعادة المحاولة',
      'filters.all': 'جميع المنتجات',
      'filters.ai': 'حلول الذكاء الاصطناعي',
      'filters.websites': 'المواقع الإلكترونية',
      'filters.apps': 'التطبيقات',
      'filters.tools': 'الأدوات',
      'filters.courses': 'الدورات',
      'hero.title': 'متجر برين سايت',
      'hero.subtitle': 'مركز الابتكار الرقمي',
    }
  }
};

export function useTranslation(namespace = 'common') {
  const { language } = useAppStore();
  
  const t = (key: string) => {
    const keys = key.split('.');
    let value: any = translations[language as keyof typeof translations]?.[namespace as keyof typeof translations.en];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    return value || key;
  };
  
  return { t };
}