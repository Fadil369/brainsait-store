'use client';

import React, { Suspense, memo } from 'react';
import { cn } from '@/lib/utils';

interface LazyWrapperProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  className?: string;
}

// Default loading component
const DefaultLoading = memo(() => (
  <div className="glass rounded-2xl p-6 animate-pulse">
    <div className="flex items-center justify-center h-32">
      <div className="loading-enhanced" />
    </div>
  </div>
));

DefaultLoading.displayName = 'DefaultLoading';

const LazyWrapperComponent: React.FC<LazyWrapperProps> = ({
  children,
  fallback = <DefaultLoading />,
  className,
}) => {
  return (
    <div className={cn('w-full', className)}>
      <Suspense fallback={fallback}>
        {children}
      </Suspense>
    </div>
  );
};

export const LazyWrapper = memo(LazyWrapperComponent);