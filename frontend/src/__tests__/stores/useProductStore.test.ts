/**
 * @jest-environment jsdom
 */

import { renderHook, act } from '@testing-library/react';
import { useProductStore, getCategoryCount } from '@/stores/useProductStore';
import { Product } from '@/types';

// Mock product data
const mockProducts: Product[] = [
  {
    id: 1,
    title: 'AI Business Assistant',
    arabicTitle: 'مساعد الأعمال الذكي',
    description: 'Advanced AI-powered business automation platform',
    arabicDescription: 'منصة أتمتة الأعمال المدعومة بالذكاء الاصطناعي المتقدمة',
    price: 1499,
    category: 'ai',
    status: 'active',
    features: ['GPT-4 Integration', 'Multi-language Support'],
    arabicFeatures: ['تكامل GPT-4', 'دعم متعدد اللغات'],
    icon: 'ai-icon',
    rating: 4.8,
    reviewCount: 125,
    tags: ['ai', 'business', 'automation'],
  },
  {
    id: 2,
    title: 'Digital Marketing Course',
    arabicTitle: 'دورة التسويق الرقمي',
    description: 'Complete digital marketing course with case studies',
    arabicDescription: 'دورة التسويق الرقمي الكاملة مع دراسات الحالة',
    price: 2999,
    category: 'courses',
    status: 'active',
    features: ['60+ Hours Content', 'Certificate'],
    arabicFeatures: ['أكثر من 60 ساعة محتوى', 'شهادة'],
    icon: 'course-icon',
    rating: 4.5,
    reviewCount: 87,
    tags: ['marketing', 'course', 'digital'],
  },
  {
    id: 3,
    title: 'Data Analytics Tool',
    arabicTitle: 'أداة تحليل البيانات',
    description: 'Professional data analytics and visualization tool',
    arabicDescription: 'أداة تحليل البيانات والتصور المهنية',
    price: 899,
    category: 'tools',
    status: 'active',
    features: ['Real-time Analytics', 'Custom Dashboards'],
    arabicFeatures: ['تحليلات في الوقت الفعلي', 'لوحات مخصصة'],
    icon: 'analytics-icon',
    rating: 4.2,
    reviewCount: 45,
    tags: ['analytics', 'data', 'visualization'],
  },
  {
    id: 4,
    title: 'Premium AI Course',
    arabicTitle: 'دورة الذكاء الاصطناعي المتقدمة',
    description: 'Advanced AI course for professionals',
    arabicDescription: 'دورة الذكاء الاصطناعي المتقدمة للمحترفين',
    price: 3500,
    category: 'courses',
    status: 'active',
    features: ['Advanced Topics', 'Hands-on Projects'],
    arabicFeatures: ['مواضيع متقدمة', 'مشاريع عملية'],
    icon: 'ai-course-icon',
    rating: 4.9,
    reviewCount: 203,
    tags: ['ai', 'course', 'advanced'],
  },
];

describe('useProductStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useProductStore.setState({
      products: [],
      filteredProducts: [],
      searchResults: undefined,
      currentProduct: undefined,
      filters: {
        category: 'all',
        searchQuery: '',
        sortBy: 'newest',
        sortDirection: 'desc',
        priceRange: { min: 0, max: 10000 },
      },
      searchQuery: '',
      isLoading: false,
      error: undefined,
      hasMore: true,
      page: 1,
      isDemoOpen: false,
      demoProduct: undefined,
    });
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useProductStore());
      
      expect(result.current.products).toEqual([]);
      expect(result.current.filteredProducts).toEqual([]);
      expect(result.current.searchResults).toBeUndefined();
      expect(result.current.currentProduct).toBeUndefined();
      expect(result.current.filters).toEqual({
        category: 'all',
        searchQuery: '',
        sortBy: 'newest',
        sortDirection: 'desc',
        priceRange: { min: 0, max: 10000 },
      });
      expect(result.current.searchQuery).toBe('');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeUndefined();
      expect(result.current.hasMore).toBe(true);
      expect(result.current.page).toBe(1);
      expect(result.current.isDemoOpen).toBe(false);
      expect(result.current.demoProduct).toBeUndefined();
    });
  });

  describe('Product Management', () => {
    it('should set products and apply filters', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setProducts(mockProducts);
      });
      
      expect(result.current.products).toEqual(mockProducts);
      expect(result.current.filteredProducts).toHaveLength(mockProducts.length);
    });

    it('should add products and apply filters', () => {
      const { result } = renderHook(() => useProductStore());
      
      // First set some products
      act(() => {
        result.current.setProducts([mockProducts[0], mockProducts[1]]);
      });
      
      expect(result.current.products).toHaveLength(2);
      
      // Then add more products
      act(() => {
        result.current.addProducts([mockProducts[2], mockProducts[3]]);
      });
      
      expect(result.current.products).toHaveLength(4);
      expect(result.current.filteredProducts).toHaveLength(4);
    });

    it('should set current product', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setCurrentProduct(mockProducts[0]);
      });
      
      expect(result.current.currentProduct).toEqual(mockProducts[0]);
    });

    it('should clear current product', () => {
      const { result } = renderHook(() => useProductStore());
      
      // First set a product
      act(() => {
        result.current.setCurrentProduct(mockProducts[0]);
      });
      
      expect(result.current.currentProduct).toEqual(mockProducts[0]);
      
      // Then clear it
      act(() => {
        result.current.clearCurrentProduct();
      });
      
      expect(result.current.currentProduct).toBeUndefined();
    });
  });

  describe('Search and Filtering', () => {
    beforeEach(() => {
      const { result } = renderHook(() => useProductStore());
      act(() => {
        result.current.setProducts(mockProducts);
      });
    });

    it('should filter by search query', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSearchQuery('AI');
      });
      
      expect(result.current.searchQuery).toBe('AI');
      expect(result.current.filteredProducts).toHaveLength(2); // AI Business Assistant and Premium AI Course
      expect(result.current.filteredProducts[0].title).toContain('AI');
    });

    it('should filter by Arabic search query', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSearchQuery('ذكي');
      });
      
      // Should find products with Arabic titles/descriptions containing 'ذكي'
      expect(result.current.filteredProducts.length).toBeGreaterThan(0);
    });

    it('should filter by category', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setCategoryFilter('courses');
      });
      
      expect(result.current.filters.category).toBe('courses');
      expect(result.current.filteredProducts).toHaveLength(2); // Two course products
      expect(result.current.filteredProducts.every(p => p.category === 'courses')).toBe(true);
    });

    it('should filter by price range', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setPriceRange(1000, 2000);
      });
      
      expect(result.current.filters.priceRange).toEqual({ min: 1000, max: 2000 });
      const filteredProducts = result.current.filteredProducts;
      expect(filteredProducts.every(p => p.price >= 1000 && p.price <= 2000)).toBe(true);
    });

    it('should sort by price ascending', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSortBy('price', 'asc');
      });
      
      expect(result.current.filters.sortBy).toBe('price');
      expect(result.current.filters.sortDirection).toBe('asc');
      
      const prices = result.current.filteredProducts.map(p => p.price);
      expect(prices).toEqual([...prices].sort((a, b) => a - b));
    });

    it('should sort by price descending', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSortBy('price', 'desc');
      });
      
      const prices = result.current.filteredProducts.map(p => p.price);
      expect(prices).toEqual([...prices].sort((a, b) => b - a));
    });

    it('should sort by rating', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSortBy('rating', 'desc');
      });
      
      const ratings = result.current.filteredProducts.map(p => p.rating || 0);
      expect(ratings).toEqual([...ratings].sort((a, b) => b - a));
    });

    it('should sort by popularity (review count)', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSortBy('popular', 'desc');
      });
      
      const reviewCounts = result.current.filteredProducts.map(p => p.reviewCount || 0);
      expect(reviewCounts).toEqual([...reviewCounts].sort((a, b) => b - a));
    });

    it('should reset filters', () => {
      const { result } = renderHook(() => useProductStore());
      
      // Apply some filters
      act(() => {
        result.current.setSearchQuery('test');
        result.current.setCategoryFilter('ai');
        result.current.setPriceRange(500, 1500);
        result.current.setSortBy('price', 'asc');
      });
      
      // Verify filters are applied
      expect(result.current.filters.category).toBe('ai');
      expect(result.current.searchQuery).toBe('test');
      
      // Reset filters
      act(() => {
        result.current.resetFilters();
      });
      
      expect(result.current.filters).toEqual({
        category: 'all',
        searchQuery: '',
        sortBy: 'newest',
        sortDirection: 'desc',
        priceRange: { min: 0, max: 10000 },
      });
      expect(result.current.searchQuery).toBe('');
    });

    it('should search in product features', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSearchQuery('GPT-4');
      });
      
      expect(result.current.filteredProducts).toHaveLength(1);
      expect(result.current.filteredProducts[0].features).toContain('GPT-4 Integration');
    });

    it('should search in tags', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSearchQuery('automation');
      });
      
      expect(result.current.filteredProducts.length).toBeGreaterThan(0);
      expect(result.current.filteredProducts[0].tags).toContain('automation');
    });
  });

  describe('Demo Modal Management', () => {
    it('should open demo modal', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.openDemo(mockProducts[0]);
      });
      
      expect(result.current.isDemoOpen).toBe(true);
      expect(result.current.demoProduct).toEqual(mockProducts[0]);
    });

    it('should close demo modal', () => {
      const { result } = renderHook(() => useProductStore());
      
      // First open the modal
      act(() => {
        result.current.openDemo(mockProducts[0]);
      });
      
      expect(result.current.isDemoOpen).toBe(true);
      
      // Then close it
      act(() => {
        result.current.closeDemo();
      });
      
      expect(result.current.isDemoOpen).toBe(false);
      expect(result.current.demoProduct).toBeUndefined();
    });
  });

  describe('Loading and Error States', () => {
    it('should set loading state', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setLoading(true);
      });
      
      expect(result.current.isLoading).toBe(true);
      
      act(() => {
        result.current.setLoading(false);
      });
      
      expect(result.current.isLoading).toBe(false);
    });

    it('should set error state', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setError('Test error message');
      });
      
      expect(result.current.error).toBe('Test error message');
      
      act(() => {
        result.current.setError();
      });
      
      expect(result.current.error).toBeUndefined();
    });
  });

  describe('Pagination', () => {
    it('should simulate load more functionality', async () => {
      const { result } = renderHook(() => useProductStore());
      
      expect(result.current.page).toBe(1);
      expect(result.current.hasMore).toBe(true);
      
      await act(async () => {
        await result.current.loadMore();
      });
      
      expect(result.current.page).toBe(2);
      expect(result.current.hasMore).toBe(false);
    });

    it('should not load more when hasMore is false', async () => {
      const { result } = renderHook(() => useProductStore());
      
      // First load more to set hasMore to false
      await act(async () => {
        await result.current.loadMore();
      });
      
      const pageAfterFirst = result.current.page;
      
      // Try to load more again
      await act(async () => {
        await result.current.loadMore();
      });
      
      expect(result.current.page).toBe(pageAfterFirst); // Should not increment
    });

    it('should reset pagination', () => {
      const { result } = renderHook(() => useProductStore());
      
      // Modify pagination state
      act(() => {
        useProductStore.setState({ page: 5, hasMore: false });
      });
      
      expect(result.current.page).toBe(5);
      expect(result.current.hasMore).toBe(false);
      
      act(() => {
        result.current.resetPagination();
      });
      
      expect(result.current.page).toBe(1);
      expect(result.current.hasMore).toBe(true);
    });
  });

  describe('Selector Hooks', () => {
    it('should provide correct selector values', () => {
      const { result: productStore } = renderHook(() => useProductStore());
      const { result: products } = renderHook(() => useProductStore((state) => state.products));
      const { result: filteredProducts } = renderHook(() => useProductStore((state) => state.filteredProducts));
      const { result: currentProduct } = renderHook(() => useProductStore((state) => state.currentProduct));
      const { result: filters } = renderHook(() => useProductStore((state) => state.filters));
      
      act(() => {
        productStore.current.setProducts(mockProducts);
        productStore.current.setCurrentProduct(mockProducts[0]);
        productStore.current.setCategoryFilter('ai');
      });
      
      expect(products.current).toEqual(mockProducts);
      expect(filteredProducts.current.length).toBeGreaterThan(0);
      expect(currentProduct.current).toEqual(mockProducts[0]);
      expect(filters.current.category).toBe('ai');
    });
  });

  describe('Complex Filtering Scenarios', () => {
    beforeEach(() => {
      const { result } = renderHook(() => useProductStore());
      act(() => {
        result.current.setProducts(mockProducts);
      });
    });

    it('should apply multiple filters simultaneously', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setCategoryFilter('courses');
        result.current.setPriceRange(2000, 4000);
        result.current.setSearchQuery('Digital');
      });
      
      const filtered = result.current.filteredProducts;
      expect(filtered.every(p => 
        p.category === 'courses' && 
        p.price >= 2000 && 
        p.price <= 4000 &&
        (p.title.toLowerCase().includes('digital') || 
         p.description.toLowerCase().includes('digital'))
      )).toBe(true);
    });

    it('should handle empty search results', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSearchQuery('nonexistent product');
      });
      
      expect(result.current.filteredProducts).toHaveLength(0);
    });

    it('should handle case-insensitive search', () => {
      const { result } = renderHook(() => useProductStore());
      
      act(() => {
        result.current.setSearchQuery('AI');
      });
      
      const upperCaseResults = result.current.filteredProducts.length;
      
      act(() => {
        result.current.setSearchQuery('ai');
      });
      
      const lowerCaseResults = result.current.filteredProducts.length;
      
      expect(upperCaseResults).toBe(lowerCaseResults);
    });
  });
});

describe('getCategoryCount Helper Function', () => {
  beforeEach(() => {
    useProductStore.setState({ products: mockProducts });
  });

  it('should return total count for "all" category', () => {
    const count = getCategoryCount('all');
    expect(count).toBe(mockProducts.length);
  });

  it('should return correct count for specific category', () => {
    const coursesCount = getCategoryCount('courses');
    const coursesInMock = mockProducts.filter(p => p.category === 'courses').length;
    expect(coursesCount).toBe(coursesInMock);
  });

  it('should return 0 for non-existent category', () => {
    const count = getCategoryCount('nonexistent' as any);
    expect(count).toBe(0);
  });
});