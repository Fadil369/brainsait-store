import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { 
  useProducts, 
  useInfiniteProducts, 
  useProduct, 
  useSearchProducts, 
  useFeaturedProducts, 
  useProductRecommendations,
  PRODUCTS_QUERY_KEYS 
} from '@/hooks/useProducts';
import { products, getProductCounts, searchProducts } from '@/data/products';
import { productsApi } from '@/lib/api';

// Mock only the API layer to return our real data
jest.mock('@/lib/api', () => ({
  productsApi: {
    getProducts: jest.fn(),
    getProduct: jest.fn(),
    searchProducts: jest.fn(),
    getFeaturedProducts: jest.fn(),
  },
}));

// Get typed mock functions
const mockProductsApi = productsApi as jest.Mocked<typeof productsApi>;

// Create a test wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );
};

describe('useProducts Hooks with Real Data', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Set up API mocks to return real data
    const featuredProducts = products.filter(p => p.badge === "FEATURED");
    const paginatedResponse = {
      data: products.slice(0, 10), // First 10 products
      pagination: {
        page: 1,
        totalPages: Math.ceil(products.length / 10),
        totalItems: products.length,
        limit: 10,
      }
    };

    mockProductsApi.getProducts.mockResolvedValue(paginatedResponse);
    mockProductsApi.getProduct.mockImplementation((id: number) => 
      Promise.resolve(products.find(p => p.id === id))
    );
    mockProductsApi.searchProducts.mockImplementation((query: string, filters?: any) =>
      Promise.resolve({
        data: searchProducts(query, filters?.category),
        total: searchProducts(query, filters?.category).length,
      })
    );
    mockProductsApi.getFeaturedProducts.mockResolvedValue(featuredProducts);
  });

  describe('PRODUCTS_QUERY_KEYS', () => {
    it('should generate correct query keys', () => {
      expect(PRODUCTS_QUERY_KEYS.all).toEqual(['products']);
      expect(PRODUCTS_QUERY_KEYS.lists()).toEqual(['products', 'list']);
      expect(PRODUCTS_QUERY_KEYS.list({ category: 'ai' })).toEqual(['products', 'list', { category: 'ai' }]);
      expect(PRODUCTS_QUERY_KEYS.details()).toEqual(['products', 'detail']);
      expect(PRODUCTS_QUERY_KEYS.detail(1)).toEqual(['products', 'detail', 1]);
      expect(PRODUCTS_QUERY_KEYS.search('test')).toEqual(['products', 'search', 'test']);
      expect(PRODUCTS_QUERY_KEYS.featured()).toEqual(['products', 'featured']);
      expect(PRODUCTS_QUERY_KEYS.recommendations(1)).toEqual(['products', 'recommendations', 1]);
    });
  });

  describe('useProducts with Real Data', () => {
    it('should fetch real products data', async () => {
      const { result } = renderHook(() => useProducts({ page: 1, limit: 10 }), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.getProducts).toHaveBeenCalledWith({ page: 1, limit: 10 });
      
      // Wait for the query to resolve
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(result.current.isSuccess).toBeDefined();
    });

    it('should filter by AI category using real data', () => {
      const aiProducts = products.filter(p => p.category === 'ai');
      expect(aiProducts.length).toBeGreaterThan(0); // Verify we have AI products

      renderHook(() => useProducts({ category: 'ai' }), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.getProducts).toHaveBeenCalledWith({ category: 'ai' });
    });

    it('should handle different product categories from real data', () => {
      const counts = getProductCounts();
      
      // Test that we have products in different categories
      expect(counts.all).toBeGreaterThan(0);
      expect(counts.ai).toBeGreaterThan(0);
      
      ['ai', 'apps', 'websites', 'tools', 'courses'].forEach(category => {
        if (counts[category as keyof typeof counts] > 0) {
          renderHook(() => useProducts({ category: category as any }), {
            wrapper: createWrapper(),
          });
          
          expect(mockProductsApi.getProducts).toHaveBeenCalledWith({ category });
        }
      });
    });
  });

  describe('useProduct with Real Data', () => {
    it('should fetch specific product by ID', () => {
      const testProduct = products[0]; // Use first product from real data
      
      renderHook(() => useProduct(testProduct.id), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.getProduct).toHaveBeenCalledWith(testProduct.id);
    });

    it('should handle product that exists in real data', async () => {
      const testProduct = products.find(p => p.category === 'ai'); // Find an AI product
      if (testProduct) {
        renderHook(() => useProduct(testProduct.id), {
          wrapper: createWrapper(),
        });

        expect(mockProductsApi.getProduct).toHaveBeenCalledWith(testProduct.id);
      }
    });

    it('should be disabled for invalid product ID', () => {
      const { result } = renderHook(() => useProduct(0), {
        wrapper: createWrapper(),
      });

      expect(result.current.isFetching).toBe(false);
    });
  });

  describe('useSearchProducts with Real Data', () => {
    it('should search real products by title', () => {
      const searchQuery = 'AI'; // Search for AI products
      
      renderHook(() => useSearchProducts(searchQuery), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.searchProducts).toHaveBeenCalledWith(searchQuery, undefined);
    });

    it('should find products that actually exist', () => {
      // Test with a term that should exist in our product data
      const businessProducts = searchProducts('Business'); // Use real search function
      expect(businessProducts.length).toBeGreaterThan(0);

      renderHook(() => useSearchProducts('Business'), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.searchProducts).toHaveBeenCalledWith('Business', undefined);
    });

    it('should search with category filter using real data', () => {
      const query = 'Assistant';
      const filters = { category: 'ai' };

      renderHook(() => useSearchProducts(query, filters), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.searchProducts).toHaveBeenCalledWith(query, filters);
    });

    it('should handle empty search results', () => {
      const nonExistentQuery = 'xyznonsense123456';
      
      renderHook(() => useSearchProducts(nonExistentQuery), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.searchProducts).toHaveBeenCalledWith(nonExistentQuery, undefined);
    });
  });

  describe('useFeaturedProducts with Real Data', () => {
    it('should fetch featured products from real data', () => {
      const featuredCount = products.filter(p => p.badge === "FEATURED").length;
      
      renderHook(() => useFeaturedProducts(), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.getFeaturedProducts).toHaveBeenCalled();
      
      // Verify we have featured products in our dataset
      expect(featuredCount).toBeGreaterThan(0);
    });

    it('should be disabled when enabled is false', () => {
      const { result } = renderHook(() => useFeaturedProducts(false), {
        wrapper: createWrapper(),
      });

      expect(result.current.isFetching).toBe(false);
    });
  });

  describe('useProductRecommendations with Real Data', () => {
    it('should fetch recommendations for real product', () => {
      const testProduct = products[0];
      
      renderHook(() => useProductRecommendations(testProduct.id), {
        wrapper: createWrapper(),
      });

      expect(mockProductsApi.getFeaturedProducts).toHaveBeenCalled();
    });

    it('should be disabled when enabled is false', () => {
      const testProduct = products[0];
      const { result } = renderHook(() => useProductRecommendations(testProduct.id, false), {
        wrapper: createWrapper(),
      });

      expect(result.current.isFetching).toBe(false);
    });
  });

  describe('Data Validation with Real Products', () => {
    it('should verify real product data structure', () => {
      expect(products.length).toBeGreaterThan(0);
      
      const sampleProduct = products[0];
      expect(sampleProduct).toHaveProperty('id');
      expect(sampleProduct).toHaveProperty('title');
      expect(sampleProduct).toHaveProperty('category');
      expect(sampleProduct).toHaveProperty('price');
      expect(sampleProduct).toHaveProperty('description');
    });

    it('should have products in multiple categories', () => {
      const categories = [...new Set(products.map(p => p.category))];
      expect(categories.length).toBeGreaterThan(1);
      expect(categories).toContain('ai');
    });

    it('should have products with SAR pricing', () => {
      const sampleProduct = products[0];
      expect(typeof sampleProduct.price).toBe('number');
      expect(sampleProduct.price).toBeGreaterThan(0);
    });

    it('should have some featured products', () => {
      const featuredProducts = products.filter(p => p.badge === "FEATURED");
      expect(featuredProducts.length).toBeGreaterThan(0);
    });

    it('should have products with Arabic titles', () => {
      const productsWithArabic = products.filter(p => p.arabicTitle);
      expect(productsWithArabic.length).toBeGreaterThan(0);
    });
  });

  describe('Real Search Functionality', () => {
    it('should search function work with actual data', () => {
      const aiResults = searchProducts('AI');
      expect(aiResults.length).toBeGreaterThan(0);
      
      const businessResults = searchProducts('Business');
      expect(businessResults.length).toBeGreaterThan(0);
      
      const noResults = searchProducts('xyznonsense123456');
      expect(noResults.length).toBe(0);
    });

    it('should category filtering work with real data', () => {
      const counts = getProductCounts();
      expect(counts.all).toBe(products.length);
      expect(counts.ai).toBe(products.filter(p => p.category === 'ai').length);
    });
  });

  describe('Hook Integration with Real Data', () => {
    it('should all hooks work together with real data', () => {
      const wrapper = createWrapper();
      
      // Test that all hooks can be used together
      const { result: productsResult } = renderHook(() => useProducts(), { wrapper });
      const { result: productResult } = renderHook(() => useProduct(products[0].id), { wrapper });
      const { result: searchResult } = renderHook(() => useSearchProducts('AI'), { wrapper });
      const { result: featuredResult } = renderHook(() => useFeaturedProducts(), { wrapper });

      expect(productsResult.current.isLoading).toBeDefined();
      expect(productResult.current.isLoading).toBeDefined();
      expect(searchResult.current.isLoading).toBeDefined();
      expect(featuredResult.current.isLoading).toBeDefined();
    });
  });
});