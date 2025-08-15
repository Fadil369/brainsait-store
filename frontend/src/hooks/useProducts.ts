import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { productsApi as api } from '@/lib/api/products';
import { Product, ProductCategory, ProductFilters, PaginatedResponse, SearchResult } from '@/types';
import { 
  createQueryHook, 
  createInfiniteQueryHook, 
  createQueryManagerHook, 
  createPaginationHelper,
  QueryKeyFactory 
} from './factories';

// Query keys using the factory pattern
const productKeys = new QueryKeyFactory('products');

// Enhanced query keys with more specific patterns
export const PRODUCTS_QUERY_KEYS = {
  ...productKeys,
  featured: () => productKeys.custom('featured'),
  recommendations: (id: number) => productKeys.custom('recommendations', id),
  stats: () => productKeys.custom('stats'),
  category: (category: ProductCategory, params?: any) => productKeys.custom('category', { category, ...params }),
};

// Type definitions for hook parameters
interface ProductListParams {
  page?: number;
  limit?: number;
  category?: ProductCategory | 'all';
  search?: string;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
  enabled?: boolean;
}

interface ProductSearchParams {
  query: string;
  filters?: Partial<ProductFilters>;
  enabled?: boolean;
}

// Pagination helper for products
const productPagination = createPaginationHelper<Product>();

// Create standardized product hooks using factories
export const useProducts = createQueryHook(
  (params?: ProductListParams) => PRODUCTS_QUERY_KEYS.list(params),
  (params?: ProductListParams) => api.getProducts(params),
  {
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  }
);

export const useInfiniteProducts = createInfiniteQueryHook(
  (params?: Omit<ProductListParams, 'page'>) => PRODUCTS_QUERY_KEYS.infinite(params),
  (params?: ProductListParams) => api.getProducts(params),
  productPagination.getNextPageParam,
  {
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  }
);

export const useProduct = createQueryHook(
  (id?: number) => id ? PRODUCTS_QUERY_KEYS.detail(id) : ['products', 'detail', null],
  (id?: number) => {
    if (!id) throw new Error('Product ID is required');
    return api.getProduct(id);
  },
  {
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  }
);

export const useSearchProducts = createQueryHook(
  (params?: ProductSearchParams) => 
    PRODUCTS_QUERY_KEYS.search(params?.query || '', params?.filters),
  (params?: ProductSearchParams) => {
    if (!params?.query?.trim()) {
      throw new Error('Search query is required');
    }
    return api.searchProducts(params.query, params.filters);
  },
  {
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  }
);

export const useFeaturedProducts = createQueryHook(
  () => PRODUCTS_QUERY_KEYS.featured(),
  () => api.getFeaturedProducts(),
  {
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  }
);

export const useProductRecommendations = createQueryHook(
  (productId?: number) => productId ? PRODUCTS_QUERY_KEYS.recommendations(productId) : ['products', 'recommendations', null],
  (productId?: number) => {
    if (!productId) throw new Error('Product ID is required for recommendations');
    // For now, fallback to featured products as in original
    return api.getFeaturedProducts();
  },
  {
    staleTime: 15 * 60 * 1000, // 15 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  }
);

// Hook for products by category using the factory pattern
export const useProductsByCategory = createQueryHook(
  (params?: { category: ProductCategory } & Omit<ProductListParams, 'category'>) => 
    PRODUCTS_QUERY_KEYS.category(params?.category || 'apps', params),
  (params?: { category: ProductCategory } & Omit<ProductListParams, 'category'>) => {
    if (!params?.category) throw new Error('Category is required');
    return api.getProductsByCategory(params.category, params);
  }
);

// Hook for product statistics
export const useProductStats = createQueryHook(
  () => PRODUCTS_QUERY_KEYS.stats(),
  () => api.getProductStats(),
  {
    staleTime: 30 * 60 * 1000, // 30 minutes - stats don't change often
    gcTime: 60 * 60 * 1000, // 1 hour
  }
);

// Query management hook for products
export const useProductsManager = createQueryManagerHook('products');

// Convenience hooks that combine the manager with specific operations
export const useProductFilters = () => {
  const manager = useProductsManager();

  return {
    // Legacy compatibility
    invalidateProducts: manager.invalidateLists,
    refetchProducts: (filters: Record<string, any>) => manager.refetchList(filters),
    
    // Enhanced functionality
    clearFilters: () => manager.invalidateLists(),
    refreshCategory: (category: ProductCategory) => {
      manager.refetchList({ category });
    },
    refreshSearch: (query: string, filters?: any) => {
      const queryClient = manager;
      // This would need to be enhanced to handle search-specific invalidation
      manager.invalidateAll();
    },
  };
};

// Prefetching hook with enhanced functionality
export const usePrefetchProducts = () => {
  const manager = useProductsManager();

  return {
    // Enhanced prefetch with better typing
    prefetchProducts: (params?: ProductListParams) => 
      manager.prefetchList(
        () => api.getProducts(params),
        params,
        { staleTime: 5 * 60 * 1000 }
      ),

    prefetchProduct: (id: number) =>
      manager.prefetchDetail(
        id,
        () => api.getProduct(id),
        { staleTime: 10 * 60 * 1000 }
      ),

    // New prefetch methods
    prefetchCategory: (category: ProductCategory, params?: any) =>
      manager.prefetchList(
        () => api.getProductsByCategory(category, params),
        { category, ...params }
      ),

    prefetchFeatured: () =>
      manager.prefetchList(
        () => api.getFeaturedProducts(),
        { featured: true }
      ),
  };
};

// Helper functions for working with product data
export const useProductHelpers = () => {
  return {
    // Extract flat data from infinite query
    getFlatProducts: productPagination.getFlatData,
    
    // Get total count from paginated data
    getTotalProductCount: productPagination.getTotalCount,
    
    // Check if product is in cart (would need cart context)
    isProductInCart: (productId: number) => {
      // This would integrate with cart state
      return false;
    },
    
    // Format product price
    formatProductPrice: (product: Product, locale: string = 'en') => {
      // This could use the PaymentUtils from the payment service
      return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
        style: 'currency',
        currency: 'SAR',
        minimumFractionDigits: 0,
      }).format(product.price);
    },
  };
};