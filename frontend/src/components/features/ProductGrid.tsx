'use client';

import React, { memo, useMemo, useCallback } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { ProductCard } from './ProductCard';
import { Product } from '@/types';
import { cn } from '@/lib/utils';

interface ProductGridProps {
  products: Product[];
  onAddToCart: (_product: Product) => void;
  onShowDemo: (_product: Product) => void;
  loading?: boolean;
  className?: string;
}

// Memoize the loading skeleton to prevent recreation
const LoadingSkeleton = memo(() => (
  <div className="glass rounded-2xl p-6 animate-pulse">
    <div className="flex items-start gap-4 mb-4">
      <div className="w-16 h-16 bg-gray/20 rounded-2xl" />
      <div className="flex-1">
        <div className="h-6 bg-gray/20 rounded mb-2" />
        <div className="h-4 bg-gray/20 rounded w-24" />
      </div>
    </div>
    <div className="space-y-2 mb-4">
      <div className="h-4 bg-gray/20 rounded" />
      <div className="h-4 bg-gray/20 rounded w-3/4" />
    </div>
    <div className="space-y-3 mb-6">
      <div className="h-3 bg-gray/20 rounded w-32" />
      {[...Array(3)].map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="w-3 h-3 bg-gray/20 rounded-full" />
          <div className="h-3 bg-gray/20 rounded flex-1" />
        </div>
      ))}
    </div>
    <div className="pt-4 border-t border-gray/20">
      <div className="h-8 bg-gray/20 rounded mb-4" />
      <div className="flex gap-3">
        <div className="h-10 bg-gray/20 rounded flex-1" />
        <div className="h-10 bg-gray/20 rounded flex-1" />
      </div>
    </div>
  </div>
));

LoadingSkeleton.displayName = 'LoadingSkeleton';

// Memoize the empty state to prevent recreation
const EmptyState = memo(() => {
  const { t } = useTranslation('common');
  
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-16 px-4">
      <div className="text-6xl mb-6 opacity-50">🔍</div>
      <h3 className="text-xl font-bold text-text-primary mb-2">
        {t('filters.noResults')}
      </h3>
      <p className="text-text-secondary text-center max-w-md">
        {t('filters.tryAdjusting')}
      </p>
    </div>
  );
});

EmptyState.displayName = 'EmptyState';

const ProductGridComponent: React.FC<ProductGridProps> = ({
  products,
  onAddToCart,
  onShowDemo,
  loading = false,
  className,
}) => {
  // Memoize loading skeletons array
  const loadingSkeletons = useMemo(() => 
    [...Array(8)].map((_, index) => (
      <LoadingSkeleton key={index} />
    )), []
  );

  // Memoize the product cards to reduce re-renders
  const productCards = useMemo(() => 
    products.map((product, index) => (
      <div
        key={product.id}
        className="animate-fade-in-up"
        style={{
          animationDelay: `${index * 100}ms`,
          animationFillMode: 'both'
        }}
      >
        <ProductCard
          product={product}
          onAddToCart={onAddToCart}
          onShowDemo={onShowDemo}
        />
      </div>
    )), [products, onAddToCart, onShowDemo]
  );

  return (
    <div className={cn('w-full', className)}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {loading ? (
          loadingSkeletons
        ) : products.length === 0 ? (
          <EmptyState />
        ) : (
          productCards
        )}
      </div>
    </div>
  );
};

// Memoize the entire component
export const ProductGrid = memo(ProductGridComponent);