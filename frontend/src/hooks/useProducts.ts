import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productsApi } from '@/lib/api';
import { Product, ProductCategory, ProductFilters } from '@/types';

// Query keys
export const PRODUCTS_QUERY_KEYS = {
  all: ['products'] as const,
  lists: () => [...PRODUCTS_QUERY_KEYS.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...PRODUCTS_QUERY_KEYS.lists(), filters] as const,
  details: () => [...PRODUCTS_QUERY_KEYS.all, 'detail'] as const,
  detail: (id: number) => [...PRODUCTS_QUERY_KEYS.details(), id] as const,
  search: (query: string) => [...PRODUCTS_QUERY_KEYS.all, 'search', query] as const,
  featured: () => [...PRODUCTS_QUERY_KEYS.all, 'featured'] as const,
  recommendations: (id: number) => [...PRODUCTS_QUERY_KEYS.all, 'recommendations', id] as const,
};

// Hook for fetching products with pagination
export const useProducts = (params?: {
  page?: number;
  limit?: number;
  category?: ProductCategory | 'all';
  search?: string;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
  enabled?: boolean;
}) => {
  return useQuery({
    queryKey: PRODUCTS_QUERY_KEYS.list(params || {}),
    queryFn: () => productsApi.getProducts(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime in v5)
    enabled: params?.enabled !== false,
  });
};

// Hook for infinite scrolling products
export const useInfiniteProducts = (params?: {
  limit?: number;
  category?: ProductCategory | 'all';
  search?: string;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
}) => {
  return useInfiniteQuery({
    queryKey: PRODUCTS_QUERY_KEYS.list(params || {}),
    queryFn: ({ pageParam = 1 }) => 
      productsApi.getProducts({ ...params, page: pageParam as number }),
    initialPageParam: 1,
    getNextPageParam: (lastPage: any) => {
      const { pagination } = lastPage.data;
      return pagination.page < pagination.totalPages ? pagination.page + 1 : undefined;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// Hook for fetching a single product
export const useProduct = (id: number, enabled = true) => {
  return useQuery({
    queryKey: PRODUCTS_QUERY_KEYS.detail(id),
    queryFn: () => productsApi.getProduct(id),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    enabled: enabled && !!id,
  });
};

// Hook for searching products
export const useSearchProducts = (
  query: string,
  filters?: Partial<ProductFilters>,
  enabled = true
) => {
  return useQuery({
    queryKey: PRODUCTS_QUERY_KEYS.search(query + JSON.stringify(filters || {})),
    queryFn: () => productsApi.searchProducts(query, filters) as any,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
    enabled: enabled && !!query.trim(),
  });
};

// Hook for featured products
export const useFeaturedProducts = (enabled = true) => {
  return useQuery({
    queryKey: PRODUCTS_QUERY_KEYS.featured(),
    queryFn: () => productsApi.getFeaturedProducts(),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    enabled,
  });
};

// Hook for product recommendations
export const useProductRecommendations = (productId: number, enabled = true) => {
  return useQuery({
    queryKey: PRODUCTS_QUERY_KEYS.recommendations(productId),
    queryFn: () => productsApi.getFeaturedProducts(), // Fallback to featured products
    staleTime: 15 * 60 * 1000, // 15 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    enabled: enabled && !!productId,
  });
};

// Hook for prefetching products (useful for optimization)
export const usePrefetchProducts = () => {
  const queryClient = useQueryClient();

  const prefetchProducts = (params?: Parameters<typeof useProducts>[0]) => {
    return queryClient.prefetchQuery({
      queryKey: PRODUCTS_QUERY_KEYS.list(params || {}),
      queryFn: () => productsApi.getProducts(params),
      staleTime: 5 * 60 * 1000,
    });
  };

  const prefetchProduct = (id: number) => {
    return queryClient.prefetchQuery({
      queryKey: PRODUCTS_QUERY_KEYS.detail(id),
      queryFn: () => productsApi.getProduct(id),
      staleTime: 10 * 60 * 1000,
    });
  };

  return { prefetchProducts, prefetchProduct };
};

// Custom hook for managing product filters
export const useProductFilters = () => {
  const queryClient = useQueryClient();

  const invalidateProducts = () => {
    return queryClient.invalidateQueries({
      queryKey: PRODUCTS_QUERY_KEYS.lists(),
    });
  };

  const refetchProducts = (filters: Record<string, any>) => {
    return queryClient.refetchQueries({
      queryKey: PRODUCTS_QUERY_KEYS.list(filters),
    });
  };

  return { invalidateProducts, refetchProducts };
};