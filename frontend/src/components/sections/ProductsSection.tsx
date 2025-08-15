'use client';

import React from 'react';
import { FilterTabs } from '@/components/features/FilterTabs';
import { ProductGrid } from '@/components/features/ProductGrid';
import { Button } from '@/components/ui/Button';
import { ProductCategory, Product } from '@/types';
import { cn } from '@/lib/utils';

interface ProductsSectionProps {
  products: Product[];
  filteredProducts: Product[];
  activeFilter: ProductCategory | 'all';
  onFilterChange: (_filter: ProductCategory | 'all') => void;
  onAddToCart: (_product: Product) => void;
  onShowDemo: (_product: Product) => void;
  loading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  productCounts?: Record<ProductCategory | 'all', number>;
  className?: string;
}

export const ProductsSection: React.FC<ProductsSectionProps> = ({
  products,
  filteredProducts,
  activeFilter,
  onFilterChange,
  onAddToCart,
  onShowDemo,
  loading = false,
  hasMore = false,
  onLoadMore,
  productCounts,
  className,
}) => {

  return (
    <section 
      id="products"
      className={cn('py-16 px-4 sm:px-6 lg:px-8', className)}
    >
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold gradient-text mb-6">
            Our Digital Solutions
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto">
            Discover premium digital products and services designed to accelerate your business growth
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="mb-12">
          <FilterTabs
            activeFilter={activeFilter}
            onFilterChange={onFilterChange}
            productCounts={productCounts}
          />
        </div>

        {/* Results Info */}
        <div className="mb-8 text-center">
          <p className="text-text-secondary">
            {loading 
              ? 'Loading products...'
              : `Showing ${filteredProducts.length} products`
            }
          </p>
        </div>

        {/* Products Grid */}
        <ProductGrid
          products={filteredProducts}
          onAddToCart={onAddToCart}
          onShowDemo={onShowDemo}
          loading={loading}
        />

        {/* Load More Button */}
        {!loading && hasMore && filteredProducts.length > 0 && (
          <div className="text-center mt-12">
            <Button
              variant="outline"
              size="lg"
              onClick={onLoadMore}
              className="px-8"
            >
              Load More Products
            </Button>
          </div>
        )}

        {/* Stats Section */}
        {!loading && filteredProducts.length > 0 && (
          <div className="mt-20 pt-16 border-t border-glass-border">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-8 text-center">
              <div className="glass rounded-2xl p-6">
                <div className="text-3xl font-bold text-vision-green mb-2">
                  {products.length}+
                </div>
                <p className="text-text-secondary">Digital Products</p>
              </div>
              
              <div className="glass rounded-2xl p-6">
                <div className="text-3xl font-bold text-vision-green mb-2">
                  10K+
                </div>
                <p className="text-text-secondary">Happy Customers</p>
              </div>
              
              <div className="glass rounded-2xl p-6">
                <div className="text-3xl font-bold text-vision-green mb-2">
                  99%
                </div>
                <p className="text-text-secondary">Satisfaction Rate</p>
              </div>
              
              <div className="glass rounded-2xl p-6">
                <div className="text-3xl font-bold text-vision-green mb-2">
                  24/7
                </div>
                <p className="text-text-secondary">Support</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};