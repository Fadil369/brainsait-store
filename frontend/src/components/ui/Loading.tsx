'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

// Loading spinner sizes
export type LoadingSize = 'sm' | 'md' | 'lg' | 'xl';

// Base loading spinner component
export interface LoadingSpinnerProps {
  size?: LoadingSize;
  className?: string;
  color?: 'primary' | 'secondary' | 'white' | 'gray';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  className,
  color = 'primary',
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6', 
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  };

  const colorClasses = {
    primary: 'text-vision-green',
    secondary: 'text-text-secondary',
    white: 'text-white',
    gray: 'text-gray-500',
  };

  return (
    <Loader2 
      className={cn(
        'animate-spin',
        sizeClasses[size],
        colorClasses[color],
        className
      )} 
    />
  );
};

// Full-screen loading overlay
export interface LoadingOverlayProps {
  show: boolean;
  message?: string;
  backdrop?: boolean;
  size?: LoadingSize;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  show,
  message = 'Loading...',
  backdrop = true,
  size = 'lg',
}) => {
  if (!show) return null;

  return (
    <div className={cn(
      'fixed inset-0 z-50 flex items-center justify-center',
      backdrop && 'bg-black/50 backdrop-blur-sm'
    )}>
      <div className="flex flex-col items-center space-y-4 rounded-xl bg-white/10 backdrop-blur-md p-6 border border-white/20">
        <LoadingSpinner size={size} color="white" />
        {message && (
          <p className="text-white text-sm font-medium">{message}</p>
        )}
      </div>
    </div>
  );
};

// Inline loading state for content areas
export interface LoadingContentProps {
  loading: boolean;
  error?: string | null;
  children: React.ReactNode;
  loadingComponent?: React.ReactNode;
  errorComponent?: React.ReactNode;
  emptyComponent?: React.ReactNode;
  isEmpty?: boolean;
}

export const LoadingContent: React.FC<LoadingContentProps> = ({
  loading,
  error,
  children,
  loadingComponent,
  errorComponent,
  emptyComponent,
  isEmpty = false,
}) => {
  if (loading) {
    return loadingComponent || (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center space-y-3">
          <LoadingSpinner size="lg" />
          <p className="text-text-secondary text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return errorComponent || (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-text-primary mb-2">Something went wrong</h3>
          <p className="text-text-secondary text-sm max-w-md">{error}</p>
        </div>
      </div>
    );
  }

  if (isEmpty) {
    return emptyComponent || (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-text-secondary text-5xl mb-4">📭</div>
          <h3 className="text-lg font-semibold text-text-primary mb-2">No data found</h3>
          <p className="text-text-secondary text-sm">There's nothing to display at the moment.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

// Skeleton loading components for better UX
export interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  rounded?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  width,
  height,
  rounded = false,
}) => {
  return (
    <div 
      className={cn(
        'animate-pulse bg-gray-200 dark:bg-gray-700',
        rounded ? 'rounded-full' : 'rounded',
        className
      )}
      style={{ 
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height 
      }}
    />
  );
};

// Card skeleton for product/content cards
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('glass rounded-xl p-6 space-y-4', className)}>
      <Skeleton width="100%" height={200} />
      <div className="space-y-2">
        <Skeleton width="80%" height={20} />
        <Skeleton width="60%" height={16} />
      </div>
      <div className="flex justify-between items-center">
        <Skeleton width={80} height={24} />
        <Skeleton width={100} height={36} />
      </div>
    </div>
  );
};

// List skeleton for table/list items
export const ListSkeleton: React.FC<{ 
  count?: number; 
  className?: string;
}> = ({ count = 3, className }) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center space-x-4 p-4 glass rounded-lg">
          <Skeleton width={48} height={48} rounded />
          <div className="flex-1 space-y-2">
            <Skeleton width="70%" height={16} />
            <Skeleton width="40%" height={14} />
          </div>
          <Skeleton width={80} height={32} />
        </div>
      ))}
    </div>
  );
};

// Button loading state
export interface LoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  loadingText?: string;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  loadingText,
  children,
  disabled,
  className,
  ...props
}) => {
  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center rounded-xl font-semibold transition-all duration-300',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vision-green focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        className
      )}
    >
      {loading && (
        <LoadingSpinner size="sm" className="mr-2" />
      )}
      {loading ? (loadingText || 'Loading...') : children}
    </button>
  );
};

// Higher-order component for loading states
export function withLoadingState<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return React.forwardRef<any, P & { 
    loading?: boolean; 
    error?: string | null;
    isEmpty?: boolean;
  }>((props, ref) => {
    const { loading, error, isEmpty, ...rest } = props;

    return (
      <LoadingContent 
        loading={loading || false}
        error={error}
        isEmpty={isEmpty}
      >
        <WrappedComponent {...(rest as P)} ref={ref} />
      </LoadingContent>
    );
  });
}

// Hook for managing loading states
export function useLoadingState(initialLoading: boolean = false) {
  const [loading, setLoading] = React.useState(initialLoading);
  const [error, setError] = React.useState<string | null>(null);

  const startLoading = React.useCallback(() => {
    setLoading(true);
    setError(null);
  }, []);

  const stopLoading = React.useCallback(() => {
    setLoading(false);
  }, []);

  const setErrorState = React.useCallback((errorMessage: string) => {
    setLoading(false);
    setError(errorMessage);
  }, []);

  const reset = React.useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return {
    loading,
    error,
    startLoading,
    stopLoading,
    setError: setErrorState,
    reset,
    isError: !!error,
  };
}

// Export all components
export default {
  LoadingSpinner,
  LoadingOverlay,
  LoadingContent,
  Skeleton,
  CardSkeleton,
  ListSkeleton,
  LoadingButton,
  withLoadingState,
  useLoadingState,
};