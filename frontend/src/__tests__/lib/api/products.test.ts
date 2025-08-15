import { productsApi, mockProductsApi } from '@/lib/api/products';
import { api } from '@/lib/api/client';
import { products } from '@/data/products';

// Mock the client API
jest.mock('@/lib/api/client', () => ({
  api: {
    get: jest.fn(),
  },
  createQueryString: jest.fn(),
}));

// Mock the products data
jest.mock('@/data/products', () => ({
  products: [
    {
      id: 1,
      category: 'ai',
      title: 'AI Business Assistant',
      arabicTitle: 'مساعد الأعمال الذكي',
      description: 'AI-powered business assistant',
      price: 74996,
      badge: 'BESTSELLER',
      icon: '🤖',
      features: ['GPT-4 Integration']
    },
    {
      id: 2,
      category: 'apps',
      title: 'Task Management App',
      description: 'Manage your tasks efficiently',
      price: 29999,
      badge: 'FEATURED',
      icon: '📱',
      features: ['Real-time sync']
    },
    {
      id: 3,
      category: 'tools',
      title: 'Analytics Dashboard',
      description: 'Business analytics tool',
      price: 19999,
      icon: '📊',
      features: ['Charts', 'Reports']
    }
  ],
  searchProducts: jest.fn(),
  getProductCounts: jest.fn()
}));

const mockApi = api as jest.Mocked<typeof api>;
const mockCreateQueryString = require('@/lib/api/client').createQueryString as jest.Mock;
const mockSearchProducts = require('@/data/products').searchProducts as jest.Mock;

describe('Products API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCreateQueryString.mockImplementation((params) => {
      const searchParams = new URLSearchParams();
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          searchParams.append(key, String(params[key]));
        }
      });
      return searchParams.toString();
    });
  });

  describe('productsApi', () => {
    describe('getProducts', () => {
      it('should fetch products without parameters', async () => {
        const mockResponse = { data: { products: [], pagination: {} } };
        mockApi.get.mockResolvedValue(mockResponse);

        const result = await productsApi.getProducts();

        expect(mockApi.get).toHaveBeenCalledWith('/products');
        expect(result).toBe(mockResponse);
      });

      it('should fetch products with parameters', async () => {
        const mockResponse = { data: { products: [], pagination: {} } };
        mockApi.get.mockResolvedValue(mockResponse);
        mockCreateQueryString.mockReturnValue('page=1&limit=10&category=ai');

        const params = {
          page: 1,
          limit: 10,
          category: 'ai' as const,
          search: 'assistant',
          sortBy: 'price',
          sortDirection: 'asc' as const
        };

        await productsApi.getProducts(params);

        expect(mockCreateQueryString).toHaveBeenCalledWith(params);
        expect(mockApi.get).toHaveBeenCalledWith('/products?page=1&limit=10&category=ai');
      });

      it('should handle empty parameters', async () => {
        const mockResponse = { data: { products: [], pagination: {} } };
        mockApi.get.mockResolvedValue(mockResponse);
        mockCreateQueryString.mockReturnValue('');

        await productsApi.getProducts({});

        expect(mockCreateQueryString).toHaveBeenCalledWith({});
        expect(mockApi.get).toHaveBeenCalledWith('/products');
      });
    });

    describe('getProduct', () => {
      it('should fetch single product by ID', async () => {
        const mockProduct = { id: 1, title: 'Test Product' };
        mockApi.get.mockResolvedValue(mockProduct);

        const result = await productsApi.getProduct(1);

        expect(mockApi.get).toHaveBeenCalledWith('/products/1');
        expect(result).toBe(mockProduct);
      });

      it('should handle different product IDs', async () => {
        const mockProduct = { id: 999, title: 'Another Product' };
        mockApi.get.mockResolvedValue(mockProduct);

        await productsApi.getProduct(999);

        expect(mockApi.get).toHaveBeenCalledWith('/products/999');
      });
    });

    describe('searchProducts', () => {
      it('should search products with query only', async () => {
        const mockResults = { data: { products: [], totalCount: 0 } };
        mockApi.get.mockResolvedValue(mockResults);
        mockCreateQueryString.mockReturnValue('search=assistant');

        const result = await productsApi.searchProducts('assistant');

        expect(mockCreateQueryString).toHaveBeenCalledWith({ search: 'assistant' });
        expect(mockApi.get).toHaveBeenCalledWith('/products/search?search=assistant');
        expect(result).toBe(mockResults);
      });

      it('should search products with filters', async () => {
        const mockResults = { data: { products: [], totalCount: 0 } };
        mockApi.get.mockResolvedValue(mockResults);
        mockCreateQueryString.mockReturnValue('search=assistant&category=ai&minPrice=100');

        const filters = { category: 'ai', minPrice: 100 };
        await productsApi.searchProducts('assistant', filters);

        expect(mockCreateQueryString).toHaveBeenCalledWith({
          search: 'assistant',
          category: 'ai',
          minPrice: 100
        });
        expect(mockApi.get).toHaveBeenCalledWith('/products/search?search=assistant&category=ai&minPrice=100');
      });

      it('should handle empty filters', async () => {
        const mockResults = { data: { products: [], totalCount: 0 } };
        mockApi.get.mockResolvedValue(mockResults);
        mockCreateQueryString.mockReturnValue('search=test');

        await productsApi.searchProducts('test', {});

        expect(mockCreateQueryString).toHaveBeenCalledWith({ search: 'test' });
      });
    });

    describe('getProductsByCategory', () => {
      it('should fetch products by category without parameters', async () => {
        const mockResponse = { data: { products: [], pagination: {} } };
        mockApi.get.mockResolvedValue(mockResponse);

        await productsApi.getProductsByCategory('ai');

        expect(mockApi.get).toHaveBeenCalledWith('/products/category/ai');
      });

      it('should fetch products by category with parameters', async () => {
        const mockResponse = { data: { products: [], pagination: {} } };
        mockApi.get.mockResolvedValue(mockResponse);
        mockCreateQueryString.mockReturnValue('page=1&limit=5');

        const params = { page: 1, limit: 5, sortBy: 'price', sortDirection: 'desc' as const };
        await productsApi.getProductsByCategory('tools', params);

        expect(mockCreateQueryString).toHaveBeenCalledWith(params);
        expect(mockApi.get).toHaveBeenCalledWith('/products/category/tools?page=1&limit=5');
      });

      it('should handle all product categories', async () => {
        const categories = ['ai', 'apps', 'websites', 'templates', 'tools', 'courses'] as const;
        const mockResponse = { data: { products: [], pagination: {} } };
        mockApi.get.mockResolvedValue(mockResponse);

        for (const category of categories) {
          await productsApi.getProductsByCategory(category);
          expect(mockApi.get).toHaveBeenCalledWith(`/products/category/${category}`);
        }

        expect(mockApi.get).toHaveBeenCalledTimes(categories.length);
      });
    });

    describe('getFeaturedProducts', () => {
      it('should fetch featured products', async () => {
        const mockFeatured = { data: [{ id: 1, title: 'Featured Product' }] };
        mockApi.get.mockResolvedValue(mockFeatured);

        const result = await productsApi.getFeaturedProducts();

        expect(mockApi.get).toHaveBeenCalledWith('/products/featured');
        expect(result).toBe(mockFeatured);
      });
    });

    describe('getRecommendations', () => {
      it('should fetch product recommendations', async () => {
        const mockRecommendations = { data: [{ id: 2, title: 'Recommended Product' }] };
        mockApi.get.mockResolvedValue(mockRecommendations);

        const result = await productsApi.getRecommendations(1);

        expect(mockApi.get).toHaveBeenCalledWith('/products/1/recommendations');
        expect(result).toBe(mockRecommendations);
      });
    });

    describe('getProductStats', () => {
      it('should fetch product statistics', async () => {
        const mockStats = {
          data: {
            totalProducts: 100,
            categoryCounts: { ai: 20, apps: 15, tools: 30 },
            averagePrice: 50000,
            averageRating: 4.5
          }
        };
        mockApi.get.mockResolvedValue(mockStats);

        const result = await productsApi.getProductStats();

        expect(mockApi.get).toHaveBeenCalledWith('/products/stats');
        expect(result).toBe(mockStats);
      });
    });
  });

  describe('mockProductsApi', () => {
    beforeEach(() => {
      // Reset the mocked search function
      mockSearchProducts.mockImplementation((query: string, category?: string) => {
        const mockProducts = [
          { id: 1, title: 'AI Business Assistant', category: 'ai' },
          { id: 2, title: 'Task Management App', category: 'apps' }
        ];
        
        let filtered = mockProducts;
        if (category) {
          filtered = mockProducts.filter(p => p.category === category);
        }
        
        if (query) {
          filtered = filtered.filter(p => 
            p.title.toLowerCase().includes(query.toLowerCase())
          );
        }
        
        return filtered;
      });
    });

    describe('getProducts', () => {
      it('should return paginated products with default parameters', async () => {
        const result = await mockProductsApi.getProducts();

        expect(result.data.data).toHaveLength(3); // All mock products
        expect(result.data.pagination).toEqual({
          page: 1,
          limit: 12,
          total: 3,
          totalPages: 1
        });
      });

      it('should filter products by category', async () => {
        const result = await mockProductsApi.getProducts({ category: 'ai' });

        expect(result.data.data).toHaveLength(1);
        expect(result.data.data[0].category).toBe('ai');
      });

      it('should filter products by search term', async () => {
        const result = await mockProductsApi.getProducts({ search: 'AI' });

        const hasAI = result.data.data.some(p => 
          p.title.toLowerCase().includes('ai') || 
          p.description.toLowerCase().includes('ai')
        );
        expect(hasAI).toBe(true);
      });

      it('should apply sorting by price ascending', async () => {
        const result = await mockProductsApi.getProducts({ 
          sortBy: 'price', 
          sortDirection: 'asc' 
        });

        const prices = result.data.data.map(p => p.price);
        const sortedPrices = [...prices].sort((a, b) => a - b);
        expect(prices).toEqual(sortedPrices);
      });

      it('should apply sorting by price descending', async () => {
        const result = await mockProductsApi.getProducts({ 
          sortBy: 'price', 
          sortDirection: 'desc' 
        });

        const prices = result.data.data.map(p => p.price);
        const sortedPrices = [...prices].sort((a, b) => b - a);
        expect(prices).toEqual(sortedPrices);
      });

      it('should apply pagination correctly', async () => {
        const result = await mockProductsApi.getProducts({ 
          page: 1, 
          limit: 2 
        });

        expect(result.data.data).toHaveLength(2);
        expect(result.data.pagination).toEqual({
          page: 1,
          limit: 2,
          total: 3,
          totalPages: 2
        });
      });

      it('should handle second page pagination', async () => {
        const result = await mockProductsApi.getProducts({ 
          page: 2, 
          limit: 2 
        });

        expect(result.data.data).toHaveLength(1); // Last product
        expect(result.data.pagination.page).toBe(2);
      });

      it('should apply multiple filters together', async () => {
        const result = await mockProductsApi.getProducts({ 
          category: 'ai',
          search: 'assistant',
          sortBy: 'price',
          sortDirection: 'asc',
          page: 1,
          limit: 10
        });

        expect(result.data.data.length).toBeGreaterThanOrEqual(0);
        expect(result.data.pagination.page).toBe(1);
        expect(result.data.pagination.limit).toBe(10);
      });

      it('should simulate API delay', async () => {
        const startTime = Date.now();
        await mockProductsApi.getProducts();
        const endTime = Date.now();
        
        // Should take at least 500ms due to setTimeout
        expect(endTime - startTime).toBeGreaterThanOrEqual(400);
      });
    });

    describe('getProduct', () => {
      it('should return specific product by ID', async () => {
        const result = await mockProductsApi.getProduct(1);

        expect(result.data).toEqual(expect.objectContaining({
          id: 1,
          title: 'AI Business Assistant'
        }));
      });

      it('should throw error for non-existent product', async () => {
        await expect(mockProductsApi.getProduct(999))
          .rejects.toThrow('Product not found');
      });

      it('should simulate API delay', async () => {
        const startTime = Date.now();
        await mockProductsApi.getProduct(1);
        const endTime = Date.now();
        
        expect(endTime - startTime).toBeGreaterThanOrEqual(250);
      });
    });

    describe('searchProducts', () => {
      it('should search products using real search function', async () => {
        mockSearchProducts.mockReturnValue([
          { id: 1, title: 'AI Business Assistant', category: 'ai' }
        ]);

        const result = await mockProductsApi.searchProducts('AI');

        expect(mockSearchProducts).toHaveBeenCalledWith('AI', undefined);
        expect(result.data.products).toHaveLength(1);
        expect(result.data.totalCount).toBe(1);
      });

      it('should search products with category filter', async () => {
        mockSearchProducts.mockReturnValue([]);

        await mockProductsApi.searchProducts('test', { category: 'apps' });

        expect(mockSearchProducts).toHaveBeenCalledWith('test', 'apps');
      });

      it('should return proper facets structure', async () => {
        mockSearchProducts.mockReturnValue([]);

        const result = await mockProductsApi.searchProducts('test');

        expect(result.data.facets).toEqual({
          categories: [],
          priceRanges: []
        });
      });

      it('should simulate API delay', async () => {
        const startTime = Date.now();
        await mockProductsApi.searchProducts('test');
        const endTime = Date.now();
        
        expect(endTime - startTime).toBeGreaterThanOrEqual(350);
      });
    });

    describe('getFeaturedProducts', () => {
      it('should return products with badges', async () => {
        const result = await mockProductsApi.getFeaturedProducts();

        // Should return products that have badges
        result.data.forEach(product => {
          expect(product.badge).toBeDefined();
        });
        
        // Should limit to 6 products
        expect(result.data.length).toBeLessThanOrEqual(6);
      });

      it('should simulate API delay', async () => {
        const startTime = Date.now();
        await mockProductsApi.getFeaturedProducts();
        const endTime = Date.now();
        
        expect(endTime - startTime).toBeGreaterThanOrEqual(250);
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors in getProducts', async () => {
      const error = new Error('Network error');
      mockApi.get.mockRejectedValue(error);

      await expect(productsApi.getProducts()).rejects.toThrow('Network error');
    });

    it('should handle API errors in getProduct', async () => {
      const error = new Error('Product not found');
      mockApi.get.mockRejectedValue(error);

      await expect(productsApi.getProduct(1)).rejects.toThrow('Product not found');
    });

    it('should handle API errors in searchProducts', async () => {
      const error = new Error('Search failed');
      mockApi.get.mockRejectedValue(error);

      await expect(productsApi.searchProducts('test')).rejects.toThrow('Search failed');
    });
  });

  describe('Edge Cases', () => {
    it('should handle null/undefined parameters gracefully', async () => {
      const mockResponse = { data: { products: [], pagination: {} } };
      mockApi.get.mockResolvedValue(mockResponse);

      // These should not throw errors
      await productsApi.getProducts(undefined);
      await productsApi.searchProducts('test', undefined);
      await productsApi.getProductsByCategory('ai', undefined);

      expect(mockApi.get).toHaveBeenCalledTimes(3);
    });

    it('should handle empty search query', async () => {
      const mockResults = { data: { products: [], totalCount: 0 } };
      mockApi.get.mockResolvedValue(mockResults);
      mockCreateQueryString.mockReturnValue('search=');

      await productsApi.searchProducts('');

      expect(mockApi.get).toHaveBeenCalledWith('/products/search?search=');
    });

    it('should handle zero product ID', async () => {
      const mockProduct = { id: 0, title: 'Zero Product' };
      mockApi.get.mockResolvedValue(mockProduct);

      await productsApi.getProduct(0);

      expect(mockApi.get).toHaveBeenCalledWith('/products/0');
    });
  });
});