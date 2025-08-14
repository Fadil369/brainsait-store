import { api, createQueryString } from './client';
import { Product, ProductCategory, SearchResult, PaginatedResponse, ProductFilters } from '@/types';

// Product API endpoints
export const productsApi = {
  // Get all products
  getProducts: async (params?: {
    page?: number;
    limit?: number;
    category?: ProductCategory | 'all';
    search?: string;
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
  }) => {
    const queryString = params ? createQueryString(params) : '';
    const url = `/products${queryString ? `?${queryString}` : ''}`;
    return api.get<PaginatedResponse<Product>>(url);
  },

  // Get product by ID
  getProduct: async (id: number) => {
    return api.get<Product>(`/products/${id}`);
  },

  // Search products
  searchProducts: async (query: string, filters?: Partial<ProductFilters>) => {
    const params = {
      search: query,
      ...filters,
    };
    const queryString = createQueryString(params);
    return api.get<SearchResult>(`/products/search?${queryString}`);
  },

  // Get products by category
  getProductsByCategory: async (category: ProductCategory, params?: {
    page?: number;
    limit?: number;
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
  }) => {
    const queryString = params ? createQueryString(params) : '';
    const url = `/products/category/${category}${queryString ? `?${queryString}` : ''}`;
    return api.get<PaginatedResponse<Product>>(url);
  },

  // Get featured products
  getFeaturedProducts: async () => {
    return api.get<Product[]>('/products/featured');
  },

  // Get product recommendations
  getRecommendations: async (productId: number) => {
    return api.get<Product[]>(`/products/${productId}/recommendations`);
  },

  // Get product statistics
  getProductStats: async () => {
    return api.get<{
      totalProducts: number;
      categoryCounts: Record<ProductCategory, number>;
      averagePrice: number;
      averageRating: number;
    }>('/products/stats');
  },
};

// Mock implementation for development (when backend is not available)
export const mockProductsApi = {
  getProducts: async (params?: any): Promise<{ data: PaginatedResponse<Product> }> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const { products } = await import('@/data/products');
    
    let filtered = [...products];
    
    // Apply category filter
    if (params?.category && params.category !== 'all') {
      filtered = filtered.filter(p => p.category === params.category);
    }
    
    // Apply search
    if (params?.search) {
      const query = params.search.toLowerCase();
      filtered = filtered.filter(p => 
        p.title.toLowerCase().includes(query) ||
        p.description.toLowerCase().includes(query) ||
        p.arabicTitle?.toLowerCase().includes(query) ||
        p.arabicDescription?.toLowerCase().includes(query)
      );
    }
    
    // Apply sorting
    if (params?.sortBy) {
      filtered.sort((a, b) => {
        let comparison = 0;
        switch (params.sortBy) {
          case 'price':
            comparison = a.price - b.price;
            break;
          case 'rating':
            comparison = (a.rating || 0) - (b.rating || 0);
            break;
          case 'popular':
            comparison = (a.reviewCount || 0) - (b.reviewCount || 0);
            break;
          default:
            comparison = a.id - b.id;
        }
        return params.sortDirection === 'asc' ? comparison : -comparison;
      });
    }
    
    // Apply pagination
    const page = params?.page || 1;
    const limit = params?.limit || 12;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedProducts = filtered.slice(startIndex, endIndex);
    
    return {
      data: {
        data: paginatedProducts,
        pagination: {
          page,
          limit,
          total: filtered.length,
          totalPages: Math.ceil(filtered.length / limit),
        }
      }
    };
  },

  getProduct: async (id: number) => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const { products } = await import('@/data/products');
    const product = products.find(p => p.id === id);
    if (!product) {
      throw new Error('Product not found');
    }
    return { data: product };
  },

  searchProducts: async (query: string, filters?: any) => {
    await new Promise(resolve => setTimeout(resolve, 400));
    const { searchProducts } = await import('@/data/products');
    const results = searchProducts(query, filters?.category);
    
    return {
      data: {
        products: results,
        totalCount: results.length,
        facets: {
          categories: [],
          priceRanges: [],
        }
      }
    };
  },

  getFeaturedProducts: async () => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const { products } = await import('@/data/products');
    const featured = products.filter(p => p.badge).slice(0, 6);
    return { data: featured };
  },
};

// Choose API based on environment
const shouldUseMockApi = process.env.NODE_ENV === 'development' && 
                        process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

export default shouldUseMockApi ? mockProductsApi : productsApi;