'use client';

import React, { useState, useCallback } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { Input } from '@/components/ui/Input';
import { debounce } from '@/lib/utils';

interface SearchBarProps {
  onSearch: (_query: string) => void;
  placeholder?: string;
  className?: string;
  defaultValue?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder,
  className,
  defaultValue = '',
}) => {
  const { t } = useTranslation('common');
  const [value, setValue] = useState(defaultValue);

  // Debounced search function to avoid too many API calls  
  const debouncedSearch = useCallback((query: string) => {
    const debouncedFn = debounce((q: string) => {
      onSearch(q);
    }, 300);
    debouncedFn(query);
  }, [onSearch]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    debouncedSearch(newValue);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(value);
  };

  return (
    <form onSubmit={handleSubmit} className={className}>
      <div className="relative max-w-2xl mx-auto">
        <Input
          type="text"
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder || t('hero.searchPlaceholder')}
          className="w-full pr-12 text-lg h-14 glass hover:glass-hover focus:border-vision-green focus:ring-vision-green/20"
          leftIcon={<MagnifyingGlassIcon className="h-5 w-5" />}
        />
      </div>
    </form>
  );
};