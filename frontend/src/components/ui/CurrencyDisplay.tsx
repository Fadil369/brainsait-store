'use client';

import React from 'react';
import { SaudiRiyalIcon } from './SaudiRiyalIcon';
import { formatSAR } from '@/lib/currency';

interface CurrencyDisplayProps {
  amount: number;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showSymbol?: boolean;
  showCode?: boolean;
  isArabic?: boolean;
  compact?: boolean;
  className?: string;
  symbolClassName?: string;
}

const sizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl',
};

const iconSizes = {
  sm: 14,
  md: 16,
  lg: 20,
  xl: 24,
};

/**
 * Currency Display Component with New Saudi Riyal Symbol
 * Renders amounts with the beautiful new 2025 SAR symbol
 */
export const CurrencyDisplay: React.FC<CurrencyDisplayProps> = ({
  amount,
  size = 'md',
  showSymbol = true,
  showCode = false,
  isArabic = false,
  compact = false,
  className = '',
  symbolClassName = '',
}) => {
  const formatted = formatSAR(amount, { showSymbol, showCode, isArabic, compact });
  const iconSize = iconSizes[size];
  
  if (formatted.useNewSymbol && showSymbol) {
    return (
      <span className={`inline-flex items-center gap-1 ${sizeClasses[size]} ${className}`}>
        <SaudiRiyalIcon 
          size={iconSize} 
          className={`flex-shrink-0 ${symbolClassName}`}
        />
        <span className="font-medium">{formatted.amount}</span>
        {formatted.currency && (
          <span className="text-sm opacity-75">{formatted.currency}</span>
        )}
      </span>
    );
  }

  return (
    <span className={`${sizeClasses[size]} ${className}`}>
      {formatted.formatted}
    </span>
  );
};

/**
 * Compact Currency Display for Cards and Lists
 */
export const CompactCurrencyDisplay: React.FC<{
  amount: number;
  isArabic?: boolean;
  className?: string;
}> = ({ amount, isArabic = false, className = '' }) => {
  return (
    <CurrencyDisplay
      amount={amount}
      size="sm"
      isArabic={isArabic}
      compact={true}
      className={`font-semibold text-green-600 ${className}`}
      symbolClassName="text-green-600"
    />
  );
};

/**
 * Large Currency Display for Headlines
 */
export const HeadlineCurrencyDisplay: React.FC<{
  amount: number;
  isArabic?: boolean;
  className?: string;
}> = ({ amount, isArabic = false, className = '' }) => {
  return (
    <CurrencyDisplay
      amount={amount}
      size="xl"
      isArabic={isArabic}
      className={`font-bold ${className}`}
      symbolClassName="text-primary"
    />
  );
};

/**
 * Price Tag Component with Strike-through for Discounts
 */
export const PriceTag: React.FC<{
  originalPrice?: number;
  currentPrice: number;
  isArabic?: boolean;
  showDiscount?: boolean;
  className?: string;
}> = ({ 
  originalPrice, 
  currentPrice, 
  isArabic = false, 
  showDiscount = true,
  className = '' 
}) => {
  const hasDiscount = originalPrice && originalPrice > currentPrice;
  const discountPercentage = hasDiscount 
    ? Math.round(((originalPrice - currentPrice) / originalPrice) * 100)
    : 0;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <CurrencyDisplay
        amount={currentPrice}
        size="lg"
        isArabic={isArabic}
        className="font-bold text-green-600"
        symbolClassName="text-green-600"
      />
      
      {hasDiscount && (
        <>
          <CurrencyDisplay
            amount={originalPrice}
            size="sm"
            isArabic={isArabic}
            className="line-through text-gray-500"
            symbolClassName="text-gray-500"
          />
          
          {showDiscount && (
            <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded">
              {isArabic ? `خصم ${discountPercentage}%` : `${discountPercentage}% OFF`}
            </span>
          )}
        </>
      )}
    </div>
  );
};

/**
 * Payment Method Currency Display
 */
export const PaymentCurrencyDisplay: React.FC<{
  amount: number;
  paymentMethod: 'stripe' | 'paypal' | 'mada' | 'stc' | 'apple_pay';
  className?: string;
}> = ({ amount, paymentMethod, className = '' }) => {
  const isArabicMethod = paymentMethod === 'mada' || paymentMethod === 'stc';
  
  return (
    <CurrencyDisplay
      amount={amount}
      size="md"
      isArabic={isArabicMethod}
      className={`font-semibold ${className}`}
      symbolClassName="text-primary"
    />
  );
};

export default CurrencyDisplay;