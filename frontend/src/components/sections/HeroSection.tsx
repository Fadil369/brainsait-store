'use client';

import React from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { SearchBar } from '@/components/features/SearchBar';
import { LanguageToggle } from '@/components/features/LanguageToggle';
import { Badge } from '@/components/ui/Badge';

interface HeroSectionProps {
  onSearch: (_query: string) => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onSearch }) => {
  const { t } = useTranslation('common');

  return (
    <section className="relative py-24 px-4 sm:px-6 lg:px-8 text-center">
      <div className="max-w-6xl mx-auto">
        {/* Vision 2030 Badge */}
        <div className="mb-8 animate-fade-in-up">
          <Badge 
            variant="vision2030" 
            size="lg"
            className="inline-flex items-center gap-2 px-6 py-3 text-base"
          >
            <span className="text-xl">🇸🇦</span>
            {t('hero.badge')}
          </Badge>
        </div>

        {/* Main Heading */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-black mb-6 gradient-text leading-tight animate-fade-in-up animation-delay-100">
          {t('hero.title')}
        </h1>

        {/* Subtitle */}
        <p className="text-xl sm:text-2xl lg:text-3xl text-text-secondary mb-12 max-w-4xl mx-auto leading-relaxed animate-fade-in-up animation-delay-200">
          {t('hero.subtitle')}
        </p>

        {/* Language Toggle */}
        <div className="mb-12 animate-fade-in-up animation-delay-300">
          <LanguageToggle />
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto animate-fade-in-up animation-delay-400">
          <SearchBar onSearch={onSearch} />
        </div>

        {/* Feature highlights */}
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8 text-left animate-fade-in-up animation-delay-500">
          <div className="glass rounded-2xl p-6 hover:glass-hover transition-all duration-300 group">
            <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">
              🚀
            </div>
            <h3 className="font-bold text-text-primary mb-2">
              Digital Innovation
            </h3>
            <p className="text-text-secondary text-sm">
              Cutting-edge solutions powered by AI and modern technology
            </p>
          </div>

          <div className="glass rounded-2xl p-6 hover:glass-hover transition-all duration-300 group">
            <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">
              🇸🇦
            </div>
            <h3 className="font-bold text-text-primary mb-2">
              Vision 2030 Ready
            </h3>
            <p className="text-text-secondary text-sm">
              Aligned with Saudi Arabia's digital transformation goals
            </p>
          </div>

          <div className="glass rounded-2xl p-6 hover:glass-hover transition-all duration-300 group">
            <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">
              🌟
            </div>
            <h3 className="font-bold text-text-primary mb-2">
              Premium Quality
            </h3>
            <p className="text-text-secondary text-sm">
              Enterprise-grade solutions with comprehensive support
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};