/**
 * @jest-environment jsdom
 */

import { renderHook, act } from '@testing-library/react';
import { useCartStore } from '@/stores/useCartStore';
import { useAppStore } from '@/stores/useAppStore';
import { useProductStore } from '@/stores/useProductStore';
import { Product } from '@/types';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock product data
const mockProduct: Product = {
  id: 1,
  title: 'Integration Test Product',
  arabicTitle: 'منتج تجريبي للتكامل',
  description: 'Product for integration testing',
  arabicDescription: 'منتج لاختبار التكامل',
  price: 1000,
  category: 'ai',
  status: 'active',
  features: ['AI Integration', 'Multi-language'],
  arabicFeatures: ['تكامل الذكاء الاصطناعي', 'متعدد اللغات'],
  icon: 'test-icon',
  source: 'existing',
};

describe('Store Integration Tests', () => {
  beforeEach(() => {
    // Reset all stores
    useCartStore.getState().clearCart();
    useAppStore.setState({
      language: 'en',
      isRTL: false,
      isMobileMenuOpen: false,
      theme: 'dark',
      notifications: [],
      isLoading: false,
      loadingMessage: undefined,
    });
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
    
    jest.clearAllMocks();
  });

  describe('E2E User Journey: Product Discovery to Cart', () => {
    it('should handle complete user journey from product search to cart', () => {
      const { result: productStore } = renderHook(() => useProductStore());
      const { result: cartStore } = renderHook(() => useCartStore());

      // Step 1: Set up products
      act(() => {
        productStore.current.setProducts([mockProduct]);
      });

      expect(productStore.current.filteredProducts).toHaveLength(1);

      // Step 2: Search for product
      act(() => {
        productStore.current.setSearchQuery('Integration');
      });

      expect(productStore.current.searchQuery).toBe('Integration');
      expect(productStore.current.filteredProducts).toHaveLength(1);

      // Step 3: Add product to cart
      act(() => {
        cartStore.current.addItem(mockProduct, 2);
      });

      expect(cartStore.current.items).toHaveLength(1);
      expect(cartStore.current.items[0].quantity).toBe(2);
      expect(cartStore.current.totals.subtotal).toBe(2000); // 1000 * 2

      // Step 4: Open cart
      act(() => {
        cartStore.current.openCart();
      });

      expect(cartStore.current.isOpen).toBe(true);

      // Step 5: Update quantity
      act(() => {
        cartStore.current.updateQuantity(mockProduct.id, 3);
      });

      expect(cartStore.current.items[0].quantity).toBe(3);
      expect(cartStore.current.totals.subtotal).toBe(3000); // 1000 * 3
      expect(cartStore.current.totals.tax).toBe(450); // 15% of 3000
      expect(cartStore.current.totals.total).toBe(3450); // 3000 + 450
    });

    it('should handle language switching during shopping flow', () => {
      const { result: cartStore } = renderHook(() => useCartStore());
      const { result: appStore } = renderHook(() => useAppStore());

      // Start in English
      expect(appStore.current.language).toBe('en');
      expect(appStore.current.isRTL).toBe(false);

      // Add product to cart
      act(() => {
        cartStore.current.addItem(mockProduct);
      });

      expect(cartStore.current.items[0].title).toBe('Integration Test Product');

      // Switch to Arabic
      act(() => {
        appStore.current.setLanguage('ar');
      });

      expect(appStore.current.language).toBe('ar');
      expect(appStore.current.isRTL).toBe(true);

      // Product should still be in cart with both languages available
      expect(cartStore.current.items[0].arabicTitle).toBe('منتج تجريبي للتكامل');

      // Switch back to English
      act(() => {
        appStore.current.setLanguage('en');
      });

      expect(appStore.current.language).toBe('en');
      expect(appStore.current.isRTL).toBe(false);
    });

    it('should handle notifications during shopping flow', () => {
      const { result: cartStore } = renderHook(() => useCartStore());
      const { result: appStore } = renderHook(() => useAppStore());

      // Simulate adding product and showing notification
      act(() => {
        cartStore.current.addItem(mockProduct);
        appStore.current.addNotification({
          message: 'Product added to cart',
          type: 'success',
        });
      });

      expect(cartStore.current.items).toHaveLength(1);
      expect(appStore.current.notifications).toHaveLength(1);
      expect(appStore.current.notifications[0].type).toBe('success');
      expect(appStore.current.notifications[0].message).toBe('Product added to cart');

      // Clear notification
      const notificationId = appStore.current.notifications[0].id;
      act(() => {
        appStore.current.removeNotification(notificationId);
      });

      expect(appStore.current.notifications).toHaveLength(0);
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle errors gracefully across stores', () => {
      const { result: productStore } = renderHook(() => useProductStore());
      const { result: appStore } = renderHook(() => useAppStore());

      // Simulate error in product loading
      act(() => {
        productStore.current.setError('Failed to load products');
        appStore.current.addNotification({
          message: 'Error loading products',
          type: 'error',
        });
      });

      expect(productStore.current.error).toBe('Failed to load products');
      expect(appStore.current.notifications).toHaveLength(1);
      expect(appStore.current.notifications[0].type).toBe('error');

      // Clear error
      act(() => {
        productStore.current.setError();
      });

      expect(productStore.current.error).toBeUndefined();
    });
  });
});