'use client';

import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { useAppStore } from '@/stores';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors except 401 (unauthorized)
        if (error?.status >= 400 && error?.status < 500 && error?.status !== 401) {
          return false;
        }
        return failureCount < 3;
      },
    },
    mutations: {
      retry: 1,
    },
  },
});

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const { language, setLanguage } = useAppStore();

  // Initialize language on mount
  useEffect(() => {
    // Set initial language from localStorage or browser preference
    const savedLanguage = localStorage.getItem('brainsait-language');
    const browserLanguage = navigator.language.toLowerCase().startsWith('ar') ? 'ar' : 'en';
    const initialLanguage = (savedLanguage as 'en' | 'ar') || browserLanguage;
    
    if (initialLanguage !== language) {
      setLanguage(initialLanguage);
    }
    
    // Update i18n language
    i18n.changeLanguage(initialLanguage);
  }, [language, setLanguage]);

  // Update i18n when language changes
  useEffect(() => {
    i18n.changeLanguage(language);
  }, [language]);

  return (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        {children}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </I18nextProvider>
    </QueryClientProvider>
  );
}