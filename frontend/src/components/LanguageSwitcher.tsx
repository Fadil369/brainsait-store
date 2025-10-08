'use client';

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores';

export function LanguageSwitcher() {
  const { t } = useTranslation('common');
  const { language, setLanguage } = useAppStore();

  const toggleLanguage = () => {
    const newLanguage = language === 'en' ? 'ar' : 'en';
    setLanguage(newLanguage);
    localStorage.setItem('brainsait-language', newLanguage);
  };

  return (
    <button
      onClick={toggleLanguage}
      className="group relative flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all duration-300"
      aria-label={t('language.switchTo', { language: language === 'en' ? t('language.arabic') : t('language.english') })}
    >
      {/* Globe Icon */}
      <svg
        className="w-5 h-5 text-gray-300 group-hover:text-primary transition-colors"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
        />
      </svg>
      
      {/* Language Labels */}
      <span className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">
        {language === 'en' ? 'العربية' : 'English'}
      </span>

      {/* Animated indicator */}
      <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-primary/0 via-primary/10 to-primary/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    </button>
  );
}

export default LanguageSwitcher;
