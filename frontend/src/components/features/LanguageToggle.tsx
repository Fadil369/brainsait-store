'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/stores';
import { Language } from '@/types';
import { cn } from '@/lib/utils';

interface LanguageToggleProps {
  variant?: 'default' | 'compact';
  className?: string;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({
  variant = 'default',
  className,
}) => {
  const { language, setLanguage } = useAppStore();

  const languages: Array<{
    code: Language;
    label: string;
    nativeLabel: string;
  }> = [
    { code: 'en', label: 'English', nativeLabel: 'English' },
    { code: 'ar', label: 'Arabic', nativeLabel: 'العربية' },
  ];

  if (variant === 'compact') {
    return (
      <div className={cn('flex items-center gap-1', className)}>
        {languages.map((lang) => (
          <Button
            key={lang.code}
            variant={language === lang.code ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setLanguage(lang.code)}
            className={cn(
              'px-3 py-1 text-sm font-medium transition-all duration-300',
              language === lang.code && 'shadow-glow'
            )}
          >
            {lang.code.toUpperCase()}
          </Button>
        ))}
      </div>
    );
  }

  return (
    <div className={cn(
      'glass rounded-xl p-1 inline-flex gap-1 animate-fade-in-up',
      className
    )}>
      {languages.map((lang) => {
        const isActive = language === lang.code;
        
        return (
          <Button
            key={lang.code}
            variant={isActive ? 'primary' : 'ghost'}
            size="md"
            onClick={() => setLanguage(lang.code)}
            className={cn(
              'px-6 py-2 font-medium transition-all duration-300',
              isActive && 'shadow-glow',
              !isActive && 'text-text-secondary hover:text-text-primary'
            )}
          >
            {lang.nativeLabel}
          </Button>
        );
      })}
    </div>
  );
};