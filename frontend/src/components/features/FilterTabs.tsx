'use client';

import React from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Button } from '@/components/ui/Button';
import { ProductCategory } from '@/types';
import { cn } from '@/lib/utils';

interface FilterTab {
  key: ProductCategory | 'all';
  icon: string;
  count?: number;
}

interface FilterTabsProps {
  activeFilter: ProductCategory | 'all';
  onFilterChange: (_newFilter: ProductCategory | 'all') => void;
  productCounts?: Record<ProductCategory | 'all', number>;
  className?: string;
}

export const FilterTabs: React.FC<FilterTabsProps> = ({
  activeFilter,
  onFilterChange,
  productCounts = {},
  className,
}) => {
  const { t } = useTranslation('common');

  const filterTabs: FilterTab[] = [
    { key: 'all', icon: '📦', count: productCounts.all },
    { key: 'ai', icon: '🤖', count: productCounts.ai },
    { key: 'apps', icon: '📱', count: productCounts.apps },
    { key: 'websites', icon: '🌐', count: productCounts.websites },
    { key: 'templates', icon: '📄', count: productCounts.templates },
    { key: 'ebooks', icon: '📚', count: productCounts.ebooks },
    { key: 'courses', icon: '🎓', count: productCounts.courses },
    { key: 'tools', icon: '🛠️', count: productCounts.tools },
  ];

  return (
    <div className={cn('w-full', className)}>
      {/* Horizontal scrollable container for mobile */}
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex gap-3 pb-2 min-w-max px-4 sm:px-0">
          {filterTabs.map((tab) => {
            const isActive = activeFilter === tab.key;
            const hasCount = typeof tab.count === 'number';
            
            return (
              <Button
                key={tab.key}
                variant={isActive ? 'primary' : 'secondary'}
                size="md"
                onClick={() => onFilterChange(tab.key)}
                className={cn(
                  'flex-shrink-0 transition-all duration-300',
                  isActive && 'shadow-glow',
                  !isActive && 'hover:scale-105 hover:glass-hover'
                )}
              >
                <span className="mr-2">{tab.icon}</span>
                <span className="whitespace-nowrap">
                  {t(`categories.${tab.key}`)}
                </span>
                {hasCount && tab.count! > 0 && (
                  <span className={cn(
                    'ml-2 px-2 py-0.5 rounded-full text-xs font-bold',
                    isActive 
                      ? 'bg-dark text-vision-green' 
                      : 'bg-vision-green/20 text-vision-green'
                  )}>
                    {tab.count}
                  </span>
                )}
              </Button>
            );
          })}
        </div>
      </div>

      {/* Filter indicator line for mobile */}
      <div className="flex sm:hidden mt-4 px-4">
        <div className="h-0.5 bg-gradient-to-r from-transparent via-vision-green to-transparent w-full opacity-30" />
      </div>
    </div>
  );
};