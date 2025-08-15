'use client';

import React, { memo, useMemo, useCallback } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PriceTag } from '@/components/ui/CurrencyDisplay';
import { Product } from '@/types';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/stores';

interface ProductCardProps {
  product: Product;
  onAddToCart: (_product: Product) => void;
  onShowDemo: (_product: Product) => void;
  className?: string;
}

const ProductCardComponent: React.FC<ProductCardProps> = ({
  product,
  onAddToCart,
  onShowDemo,
  className,
}) => {
  const { t } = useTranslation('common');
  const { language, isRTL } = useAppStore();

  // Memoize badge variant calculation
  const badgeVariant = useMemo(() => {
    switch (product.badgeType) {
      case 'new': return 'new';
      case 'hot': return 'hot';
      case 'pro': return 'pro';
      default: return 'default';
    }
  }, [product.badgeType]);

  // Memoize localized content
  const localizedContent = useMemo(() => {
    return {
      title: language === 'ar' && product.arabicTitle 
        ? product.arabicTitle 
        : product.title,
      description: language === 'ar' && product.arabicDescription 
        ? product.arabicDescription 
        : product.description,
      features: language === 'ar' && product.arabicFeatures 
        ? product.arabicFeatures 
        : product.features,
    };
  }, [language, product.arabicTitle, product.title, product.arabicDescription, product.description, product.arabicFeatures, product.features]);

  // Memoize badge text
  const badgeText = useMemo(() => {
    if (!product.badge) return null;
    
    switch (product.badge) {
      case 'VISION 2030': return t('product.vision2030Badge');
      case 'NEW': return t('product.newBadge');
      case 'HOT': return t('product.hotBadge');
      case 'PRO': return t('product.proBadge');
      default: return product.badge;
    }
  }, [product.badge, t]);

  // Memoize callback functions to prevent unnecessary re-renders
  const handleAddToCart = useCallback(() => {
    onAddToCart(product);
  }, [onAddToCart, product]);

  const handleShowDemo = useCallback(() => {
    onShowDemo(product);
  }, [onShowDemo, product]);

  return (
    <div className={cn(
      'glass rounded-2xl p-6 transition-all duration-300 hover:card-hover group relative overflow-hidden',
      className
    )}>
      {/* Badge */}
      {product.badge && (
        <div className={cn(
          'absolute top-6 z-10',
          isRTL ? 'left-6' : 'right-6'
        )}>
          <Badge variant={badgeVariant}>
            {badgeText}
          </Badge>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-16 h-16 bg-gradient-glass border border-vision-green/30 rounded-2xl flex items-center justify-center text-2xl transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 group-hover:border-vision-green flex-shrink-0">
          {product.icon}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="text-xl font-bold text-text-primary mb-1 line-clamp-2 group-hover:text-vision-green transition-colors">
            {localizedContent.title}
          </h3>
          <p className="text-vision-green text-sm font-semibold uppercase tracking-wider">
            {product.category.toUpperCase()}
          </p>
        </div>
      </div>

      {/* Description */}
      <p className="text-text-secondary mb-4 text-sm leading-relaxed line-clamp-3">
        {localizedContent.description}
      </p>

      {/* Features */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-text-primary mb-3">
          {t('product.features')}
        </h4>
        <ul className="space-y-2">
          {localizedContent.features.slice(0, 4).map((feature, index) => (
            <li 
              key={index}
              className="flex items-center gap-3 text-sm text-text-secondary"
            >
              <span className="text-vision-green font-bold">✓</span>
              {feature}
            </li>
          ))}
        </ul>
      </div>

      {/* Footer */}
      <div className="mt-auto pt-4 border-t border-glass-border">
        {/* Price with New SAR Symbol */}
        <div className="mb-4">
          <PriceTag
            currentPrice={product.price}
            originalPrice={product.originalPrice}
            isArabic={language === 'ar'}
            className="justify-start"
          />
          <p className="text-xs text-text-secondary mt-1">
            {language === 'ar' ? 'شامل ضريبة القيمة المضافة 15%' : 'Including 15% VAT'}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="primary"
            size="md"
            onClick={handleAddToCart}
            className="flex-1"
          >
            {t('product.addToCart')}
          </Button>
          
          <Button
            variant="outline"
            size="md"
            onClick={handleShowDemo}
            className="flex-1"
          >
            {t('product.tryDemo')}
          </Button>
        </div>
      </div>

      {/* Hover animation line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-vision-green to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
    </div>
  );
};

// Memoize the component to prevent unnecessary re-renders
export const ProductCard = memo(ProductCardComponent);