'use client';

import { lazy } from 'react';
import { LazyWrapper } from '@/components/ui/LazyWrapper';

// Lazy load heavy components - using default exports
const AnalyticsDashboardLazy = lazy(() => 
  import('@/components/analytics/AnalyticsDashboard')
);

const RealTimeMetricsLazy = lazy(() => 
  import('@/components/analytics/RealTimeMetrics')
);

const PaymentMethodsLazy = lazy(() => 
  import('@/components/payment/PaymentMethods')
);

// Export wrapped components
export const AnalyticsDashboard = (props: any) => (
  <LazyWrapper fallback={
    <div className="glass rounded-2xl p-6 animate-pulse">
      <div className="h-8 bg-gray/20 rounded mb-4" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 bg-gray/20 rounded" />
        ))}
      </div>
      <div className="h-64 bg-gray/20 rounded" />
    </div>
  }>
    <AnalyticsDashboardLazy {...props} />
  </LazyWrapper>
);

export const RealTimeMetrics = (props: any) => (
  <LazyWrapper fallback={
    <div className="glass rounded-2xl p-6 animate-pulse">
      <div className="h-6 bg-gray/20 rounded mb-4 w-32" />
      <div className="grid grid-cols-2 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-16 bg-gray/20 rounded" />
        ))}
      </div>
    </div>
  }>
    <RealTimeMetricsLazy {...props} />
  </LazyWrapper>
);

export const PaymentMethods = (props: any) => (
  <LazyWrapper fallback={
    <div className="glass rounded-2xl p-6 animate-pulse">
      <div className="h-6 bg-gray/20 rounded mb-4 w-40" />
      <div className="space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="w-12 h-8 bg-gray/20 rounded" />
            <div className="h-4 bg-gray/20 rounded flex-1" />
          </div>
        ))}
      </div>
    </div>
  }>
    <PaymentMethodsLazy {...props} />
  </LazyWrapper>
);