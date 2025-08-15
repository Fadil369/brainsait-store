/**
 * @jest-environment jsdom
 */

import { act, renderHook } from '@testing-library/react';
import { useCartStore } from '@/stores/useCartStore';
import { Product } from '@/types';

// Mock product for testing
const mockProduct: Product = {
  id: 1,
  category: 'ai',
  title: 'Test Product',
  arabicTitle: 'منتج تجريبي',
  description: 'Test product description',
  arabicDescription: 'وصف المنتج التجريبي',
  price: 100,
  icon: '/test-icon.svg',
  features: ['Feature 1', 'Feature 2'],
  arabicFeatures: ['الميزة 1', 'الميزة 2'],
  tags: ['tag1', 'tag2'],
  source: 'existing',
  metadata: {},
};

const mockExpensiveProduct: Product = {
  ...mockProduct,
  id: 2,
  title: 'Expensive Product',
  price: 1000,
};

describe('useCartStore', () => {
  beforeEach(() => {
    // Clear the store before each test
    useCartStore.getState().clearCart();
  });

  describe('Initial State', () => {
    it('should have empty initial state', () => {
      const { result } = renderHook(() => useCartStore());
      
      expect(result.current.items).toEqual([]);
      expect(result.current.totals).toEqual({
        subtotal: 0,
        tax: 0,
        total: 0,
        itemCount: 0,
      });
      expect(result.current.isOpen).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeUndefined();
    });
  });

  describe('Cart Operations', () => {
    it('should add item to cart', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
      });
      
      expect(result.current.items).toHaveLength(1);
      expect(result.current.items[0]).toEqual({
        id: expect.any(Number),
        productId: mockProduct.id,
        title: mockProduct.title,
        arabicTitle: mockProduct.arabicTitle,
        price: mockProduct.price,
        quantity: 1,
        icon: mockProduct.icon,
      });
    });

    it('should increase quantity when adding existing item', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.addItem(mockProduct, 2);
      });
      
      expect(result.current.items).toHaveLength(1);
      expect(result.current.items[0].quantity).toBe(3);
    });

    it('should remove item from cart', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.removeItem(mockProduct.id);
      });
      
      expect(result.current.items).toHaveLength(0);
    });

    it('should update item quantity', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.updateQuantity(mockProduct.id, 5);
      });
      
      expect(result.current.items[0].quantity).toBe(5);
    });

    it('should remove item when quantity is set to 0', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.updateQuantity(mockProduct.id, 0);
      });
      
      expect(result.current.items).toHaveLength(0);
    });

    it('should clear cart', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.addItem(mockExpensiveProduct, 2);
        result.current.clearCart();
      });
      
      expect(result.current.items).toHaveLength(0);
      expect(result.current.totals.total).toBe(0);
    });
  });

  describe('Cart UI State', () => {
    it('should toggle cart open/close', () => {
      const { result } = renderHook(() => useCartStore());
      
      expect(result.current.isOpen).toBe(false);
      
      act(() => {
        result.current.toggleCart();
      });
      
      expect(result.current.isOpen).toBe(true);
      
      act(() => {
        result.current.toggleCart();
      });
      
      expect(result.current.isOpen).toBe(false);
    });

    it('should open cart', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.openCart();
      });
      
      expect(result.current.isOpen).toBe(true);
    });

    it('should close cart', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.openCart();
        result.current.closeCart();
      });
      
      expect(result.current.isOpen).toBe(false);
    });
  });

  describe('Cart Calculations', () => {
    it('should calculate totals correctly with VAT', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 2); // 100 * 2 = 200
        result.current.addItem(mockExpensiveProduct, 1); // 1000 * 1 = 1000
      });
      
      const expectedSubtotal = 1200;
      const expectedTax = expectedSubtotal * 0.15; // 15% VAT
      const expectedTotal = expectedSubtotal + expectedTax;
      
      expect(result.current.totals.subtotal).toBe(expectedSubtotal);
      expect(result.current.totals.tax).toBe(expectedTax);
      expect(result.current.totals.total).toBe(expectedTotal);
      expect(result.current.totals.itemCount).toBe(3);
    });

    it('should recalculate totals when item is removed', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.addItem(mockExpensiveProduct, 1);
      });
      
      // Remove the expensive product
      act(() => {
        result.current.removeItem(mockExpensiveProduct.id);
      });
      
      const expectedSubtotal = 100;
      const expectedTax = expectedSubtotal * 0.15;
      const expectedTotal = expectedSubtotal + expectedTax;
      
      expect(result.current.totals.subtotal).toBe(expectedSubtotal);
      expect(result.current.totals.tax).toBe(expectedTax);
      expect(result.current.totals.total).toBe(expectedTotal);
      expect(result.current.totals.itemCount).toBe(1);
    });

    it('should handle empty cart calculations', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.clearCart();
      });
      
      expect(result.current.totals.subtotal).toBe(0);
      expect(result.current.totals.tax).toBe(0);
      expect(result.current.totals.total).toBe(0);
      expect(result.current.totals.itemCount).toBe(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle negative quantity gracefully', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.updateQuantity(mockProduct.id, -1);
      });
      
      // Should remove item when quantity becomes invalid
      expect(result.current.items).toHaveLength(0);
    });

    it('should handle removing non-existent item', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.removeItem(999); // Non-existent ID
      });
      
      // Should not affect existing items
      expect(result.current.items).toHaveLength(1);
    });

    it('should handle updating quantity of non-existent item', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1);
        result.current.updateQuantity(999, 5); // Non-existent ID
      });
      
      // Should not affect existing items
      expect(result.current.items).toHaveLength(1);
      expect(result.current.items[0].quantity).toBe(1);
    });
  });
});