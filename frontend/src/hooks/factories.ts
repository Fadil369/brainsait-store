import { useQuery, useMutation, useInfiniteQuery, useQueryClient, UseQueryOptions, UseMutationOptions, UseInfiniteQueryOptions } from '@tanstack/react-query';
import { ApiResponse } from '@/types';

// Common query configuration defaults
export const DEFAULT_QUERY_CONFIG = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  gcTime: 10 * 60 * 1000, // 10 minutes  
  retry: (failureCount: number, error: any) => {
    // Don't retry on 4xx errors except 401 (unauthorized)
    if (error?.status >= 400 && error?.status < 500 && error?.status !== 401) {
      return false;
    }
    return failureCount < 3;
  },
};

export const DEFAULT_MUTATION_CONFIG = {
  retry: 1,
};

// Generic query hook factory - supports both ApiResponse<T> and { data: T } patterns
export function createQueryHook<TParams, TData>(
  queryKeyFactory: (params?: TParams) => readonly unknown[],
  queryFn: (params?: TParams) => Promise<ApiResponse<TData> | { data: TData }>,
  defaultOptions?: Partial<UseQueryOptions<ApiResponse<TData> | { data: TData }>>
) {
  return function useDataQuery(
    params?: TParams,
    options?: Partial<UseQueryOptions<ApiResponse<TData> | { data: TData }>>
  ) {
    return useQuery({
      queryKey: queryKeyFactory(params),
      queryFn: () => queryFn(params),
      ...DEFAULT_QUERY_CONFIG,
      ...defaultOptions,
      ...options,
    });
  };
}

// Generic infinite query hook factory - supports both response patterns
export function createInfiniteQueryHook<TParams, TData>(
  queryKeyFactory: (params?: TParams) => readonly unknown[],
  queryFn: (params?: TParams & { page?: number }) => Promise<ApiResponse<TData> | { data: TData }>,
  getNextPageParam: (lastPage: ApiResponse<TData> | { data: TData }) => number | undefined,
  defaultOptions?: Partial<UseInfiniteQueryOptions<ApiResponse<TData> | { data: TData }>>
) {
  return function useInfiniteDataQuery(
    params?: TParams,
    options?: Partial<UseInfiniteQueryOptions<ApiResponse<TData> | { data: TData }>>
  ) {
    return useInfiniteQuery({
      queryKey: queryKeyFactory(params),
      queryFn: ({ pageParam = 1 }) => queryFn({ ...params, page: pageParam as number } as TParams & { page: number }),
      initialPageParam: 1,
      getNextPageParam,
      ...DEFAULT_QUERY_CONFIG,
      ...defaultOptions,
      ...options,
    });
  };
}

// Generic mutation hook factory - supports both response patterns  
export function createMutationHook<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<ApiResponse<TData> | { data: TData }>,
  defaultOptions?: Partial<UseMutationOptions<ApiResponse<TData> | { data: TData }, Error, TVariables>>
) {
  return function useDataMutation(
    options?: Partial<UseMutationOptions<ApiResponse<TData> | { data: TData }, Error, TVariables>>
  ) {
    return useMutation({
      mutationFn,
      ...DEFAULT_MUTATION_CONFIG,
      ...defaultOptions,
      ...options,
    });
  };
}

// Query key factory helpers
export class QueryKeyFactory {
  constructor(private baseKey: string) {}

  all = () => [this.baseKey] as const;
  
  lists = () => [...this.all(), 'list'] as const;
  
  list = (params?: Record<string, any>) => [...this.lists(), params || {}] as const;
  
  details = () => [...this.all(), 'detail'] as const;
  
  detail = (id: string | number) => [...this.details(), id] as const;
  
  search = (query: string, filters?: Record<string, any>) => 
    [...this.all(), 'search', query, filters || {}] as const;
  
  infinite = (params?: Record<string, any>) => 
    [...this.all(), 'infinite', params || {}] as const;

  custom = (key: string, params?: any) => 
    [...this.all(), key, params] as const;
}

// Hook for managing query invalidation and refetching
export function createQueryManagerHook(baseKey: string) {
  return function useQueryManager() {
    const queryClient = useQueryClient();
    const keyFactory = new QueryKeyFactory(baseKey);

    return {
      // Invalidate specific query patterns
      invalidateAll: () => queryClient.invalidateQueries({ queryKey: keyFactory.all() }),
      invalidateLists: () => queryClient.invalidateQueries({ queryKey: keyFactory.lists() }),
      invalidateDetails: () => queryClient.invalidateQueries({ queryKey: keyFactory.details() }),
      invalidateDetail: (id: string | number) => 
        queryClient.invalidateQueries({ queryKey: keyFactory.detail(id) }),

      // Refetch specific queries
      refetchAll: () => queryClient.refetchQueries({ queryKey: keyFactory.all() }),
      refetchList: (params?: Record<string, any>) => 
        queryClient.refetchQueries({ queryKey: keyFactory.list(params) }),
      refetchDetail: (id: string | number) => 
        queryClient.refetchQueries({ queryKey: keyFactory.detail(id) }),

      // Remove queries from cache
      removeAll: () => queryClient.removeQueries({ queryKey: keyFactory.all() }),
      removeList: (params?: Record<string, any>) => 
        queryClient.removeQueries({ queryKey: keyFactory.list(params) }),
      removeDetail: (id: string | number) => 
        queryClient.removeQueries({ queryKey: keyFactory.detail(id) }),

      // Prefetch queries
      prefetchList: (
        queryFn: () => Promise<any>,
        params?: Record<string, any>,
        options?: { staleTime?: number }
      ) => queryClient.prefetchQuery({
        queryKey: keyFactory.list(params),
        queryFn,
        staleTime: options?.staleTime || DEFAULT_QUERY_CONFIG.staleTime,
      }),

      prefetchDetail: (
        id: string | number,
        queryFn: () => Promise<any>,
        options?: { staleTime?: number }
      ) => queryClient.prefetchQuery({
        queryKey: keyFactory.detail(id),
        queryFn,
        staleTime: options?.staleTime || DEFAULT_QUERY_CONFIG.staleTime,
      }),

      // Set query data manually
      setListData: (data: any, params?: Record<string, any>) =>
        queryClient.setQueryData(keyFactory.list(params), data),
      setDetailData: (id: string | number, data: any) =>
        queryClient.setQueryData(keyFactory.detail(id), data),

      // Get query data
      getListData: (params?: Record<string, any>) =>
        queryClient.getQueryData(keyFactory.list(params)),
      getDetailData: (id: string | number) =>
        queryClient.getQueryData(keyFactory.detail(id)),
    };
  };
}

// Standard pagination helper for infinite queries - supports both response patterns
export function createPaginationHelper<T>() {
  return {
    getNextPageParam: (lastPage: ApiResponse<{ data: T[]; pagination: any }> | { data: { data: T[]; pagination: any } }) => {
      // Handle both ApiResponse<T> and { data: T } patterns
      const responseData = 'success' in lastPage ? lastPage.data : lastPage.data;
      const pagination = responseData.pagination;
      return pagination?.page < pagination?.totalPages ? pagination.page + 1 : undefined;
    },
    
    getFlatData: (data: any) => {
      return data?.pages?.flatMap((page: any) => {
        const pageData = 'success' in page ? page.data : page.data;
        return pageData.data || pageData;
      }) || [];
    },
    
    getTotalCount: (data: any) => {
      if (!data?.pages?.[0]) return 0;
      const firstPage = data.pages[0];
      const pageData = 'success' in firstPage ? firstPage.data : firstPage.data;
      return pageData?.pagination?.total || 0;
    },
  };
}

// Optimistic update helper
export function createOptimisticUpdateHelper<TData>(
  queryKey: readonly unknown[],
  idField: keyof TData = 'id' as keyof TData
) {
  return function useOptimisticUpdate() {
    const queryClient = useQueryClient();

    return {
      // Add item optimistically
      addItem: (newItem: TData) => {
        queryClient.setQueryData(queryKey, (oldData: any) => {
          if (!oldData) return { data: [newItem] };
          if (Array.isArray(oldData.data)) {
            return { ...oldData, data: [newItem, ...oldData.data] };
          }
          return oldData;
        });
      },

      // Update item optimistically
      updateItem: (id: any, updatedItem: Partial<TData>) => {
        queryClient.setQueryData(queryKey, (oldData: any) => {
          if (!oldData?.data || !Array.isArray(oldData.data)) return oldData;
          
          return {
            ...oldData,
            data: oldData.data.map((item: TData) =>
              item[idField] === id ? { ...item, ...updatedItem } : item
            ),
          };
        });
      },

      // Remove item optimistically
      removeItem: (id: any) => {
        queryClient.setQueryData(queryKey, (oldData: any) => {
          if (!oldData?.data || !Array.isArray(oldData.data)) return oldData;
          
          return {
            ...oldData,
            data: oldData.data.filter((item: TData) => item[idField] !== id),
          };
        });
      },

      // Revert changes
      revert: () => {
        queryClient.invalidateQueries({ queryKey });
      },
    };
  };
}

// Error boundary hook for queries
export function createErrorBoundaryHook() {
  return function useQueryErrorBoundary() {
    return {
      onError: (error: Error) => {
        console.error('Query error:', error);
        // Could integrate with error reporting service here
      },
      
      retry: (failureCount: number, error: any) => {
        // Custom retry logic
        if (error?.status === 404) return false;
        if (error?.status >= 500) return failureCount < 2;
        return DEFAULT_QUERY_CONFIG.retry(failureCount, error);
      },
    };
  };
}