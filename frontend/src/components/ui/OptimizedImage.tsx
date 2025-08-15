'use client';

import React, { useState, useRef, useEffect, memo } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
  lazy?: boolean;
  sizes?: string;
  placeholder?: 'blur' | 'empty';
  quality?: number;
  onLoad?: () => void;
  onError?: () => void;
}

const OptimizedImageComponent: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  className,
  priority = false,
  lazy = true,
  sizes = "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw",
  placeholder = 'empty',
  quality = 75,
  onLoad,
  onError,
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(!lazy || priority);
  const imgRef = useRef<HTMLDivElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!lazy || priority || isInView) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px', // Load images 50px before they come into view
        threshold: 0.1,
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [lazy, priority, isInView]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  // Generate responsive srcSet for better performance
  const generateSrcSet = (baseSrc: string) => {
    const sizes = [480, 768, 1024, 1280, 1920];
    return sizes
      .map(size => `${baseSrc}?w=${size}&q=${quality} ${size}w`)
      .join(', ');
  };
  if (hasError) {
    return (
      <div 
        ref={imgRef}
        className={cn(
          'flex items-center justify-center bg-gray-100 text-gray-400',
          className
        )}
        style={{ width, height }}
      >
        <span className="text-sm">Failed to load image</span>
      </div>
    );
  }

  return (
    <div
      ref={imgRef}
      className={cn('relative overflow-hidden', className)}
      style={{ width, height }}
    >
      {/* Loading placeholder */}
      {!isLoaded && isInView && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
      
      {/* Actual image */}
      {isInView && (
        <Image
          src={src}
          alt={alt}
          width={width}
          height={height}
          className={cn(
            'transition-opacity duration-300',
            isLoaded ? 'opacity-100' : 'opacity-0'
          )}
          priority={priority}
          sizes={sizes}
          quality={quality}
          placeholder={placeholder}
          onLoad={handleLoad}
          onError={handleError}
          style={{
            objectFit: 'cover',
            width: '100%',
            height: '100%',
          }}
        />
      )}
    </div>
  );
};

export const OptimizedImage = memo(OptimizedImageComponent);

// Specialized component for product images
interface ProductImageProps {
  product: {
    id: number;
    title: string;
    icon?: string;
    image?: string;
  };
  size?: 'sm' | 'md' | 'lg' | 'xl';
  priority?: boolean;
  className?: string;
}

const sizeMap = {
  sm: { width: 64, height: 64 },
  md: { width: 128, height: 128 },
  lg: { width: 256, height: 256 },
  xl: { width: 512, height: 512 },
};

const ProductImageComponent: React.FC<ProductImageProps> = ({
  product,
  size = 'md',
  priority = false,
  className,
}) => {
  const dimensions = sizeMap[size];
  
  // If product has an image, use it; otherwise fall back to icon or placeholder
  if (product.image) {
    return (
      <OptimizedImage
        src={product.image}
        alt={product.title}
        width={dimensions.width}
        height={dimensions.height}
        className={className}
        priority={priority}
        quality={80}
        sizes={`${dimensions.width}px`}
      />
    );
  }
  
  // Fallback to icon or placeholder
  return (
    <div 
      className={cn(
        'flex items-center justify-center bg-gradient-glass border border-vision-green/30 rounded-2xl text-2xl',
        className
      )}
      style={dimensions}
    >
      {product.icon || '📦'}
    </div>
  );
};

export const ProductImage = memo(ProductImageComponent);