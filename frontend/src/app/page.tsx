'use client';

import React, { useEffect, useCallback } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Layout } from '@/components/layout/Layout';
import { HeroSection } from '@/components/sections/HeroSection';
import { ProductsSection } from '@/components/sections/ProductsSection';
import { useProductStore, useCartStore, useAppStore } from '@/stores';
import { products, getProductCounts } from '@/data/products';
import { Product, ProductCategory } from '@/types';

export default function HomePage() {
  const { t } = useTranslation('common');
  
  // Store hooks
  const {
    filteredProducts,
    filters,
    isLoading,
    setProducts,
    setCategoryFilter,
    setSearchQuery,
    openDemo,
  } = useProductStore();
  
  const { addItem } = useCartStore();
  const { addNotification } = useAppStore();

  // Initialize products on mount
  useEffect(() => {
    setProducts(products);
  }, [setProducts]);

  // Handlers
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, [setSearchQuery]);

  const handleFilterChange = useCallback((filter: ProductCategory | 'all') => {
    setCategoryFilter(filter);
  }, [setCategoryFilter]);

  const handleAddToCart = useCallback((product: Product) => {
    addItem(product);
    addNotification({
      type: 'success',
      message: t('cart.itemAdded'),
      duration: 3000,
    });
  }, [addItem, addNotification, t]);

  const handleShowDemo = useCallback((product: Product) => {
    openDemo(product);
  }, [openDemo]);

  const handleLoadMore = useCallback(async () => {
    // In a real application, this would load more products from the API
    // For now, it's just a placeholder
  }, []);

  // Get product counts for filter tabs
  const productCounts = getProductCounts();

  return (
    <Layout>
      {/* Hero Section */}
      <HeroSection onSearch={handleSearch} />

      {/* Products Section */}
      <ProductsSection
        products={products}
        filteredProducts={filteredProducts}
        activeFilter={filters.category}
        onFilterChange={handleFilterChange}
        onAddToCart={handleAddToCart}
        onShowDemo={handleShowDemo}
        loading={isLoading}
        hasMore={false}
        onLoadMore={handleLoadMore}
        productCounts={productCounts}
      />

      {/* Additional sections can be added here */}
    </Layout>
  );
}