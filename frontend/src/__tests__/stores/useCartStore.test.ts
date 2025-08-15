/**
 * @jest-environment jsdom
 */

import { renderHook, act } from '@testing-library/react';
import { useCartStore, formatPrice, formatPriceEnglish } from '@/stores/useCartStore';
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
  title: 'Test Product',
  arabicTitle: 'منتج تجريبي',
  description: 'Test product description',
  arabicDescription: 'وصف المنتج التجريبي',
  price: 1000,
  category: 'ai',
  status: 'active',
  features: ['Feature 1', 'Feature 2'],
  arabicFeatures: ['خاصية 1', 'خاصية 2'],
  icon: 'test-icon',
};

const mockProduct2: Product = {
  id: 2,
  title: 'Test Product 2',
  arabicTitle: 'منتج تجريبي 2',
  description: 'Test product 2 description',
  arabicDescription: 'وصف المنتج التجريبي 2',
  price: 500,
  category: 'courses',
  status: 'active',
  features: ['Feature A', 'Feature B'],
  arabicFeatures: ['خاصية أ', 'خاصية ب'],
  icon: 'test-icon-2',
};

describe('useCartStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useCartStore.getState().clearCart();
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have empty cart initially', () => {
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
        result.current.addItem(mockProduct);
      });
      
      expect(result.current.items).toHaveLength(1);
      expect(result.current.items[0]).toMatchObject({
        productId: mockProduct.id,
        title: mockProduct.title,
        arabicTitle: mockProduct.arabicTitle,
        price: mockProduct.price,
        quantity: 1,
        icon: mockProduct.icon,
      });
    });

    it('should add item with custom quantity', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 3);
      });
      
      expect(result.current.items[0].quantity).toBe(3);
    });

    it('should update quantity when adding existing item', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 2);
        result.current.addItem(mockProduct, 1);
      });
      
      expect(result.current.items).toHaveLength(1);
      expect(result.current.items[0].quantity).toBe(3);
    });

    it('should remove item from cart', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct);
        result.current.addItem(mockProduct2);
      });
      
      expect(result.current.items).toHaveLength(2);
      
      act(() => {
        result.current.removeItem(mockProduct.id);
      });
      
      expect(result.current.items).toHaveLength(1);
      expect(result.current.items[0].productId).toBe(mockProduct2.id);
    });

    it('should update item quantity', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 2);
      });
      
      act(() => {
        result.current.updateQuantity(mockProduct.id, 5);
      });
      
      expect(result.current.items[0].quantity).toBe(5);
    });

    it('should remove item when quantity is set to 0 or negative', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct);
      });
      
      expect(result.current.items).toHaveLength(1);
      
      act(() => {
        result.current.updateQuantity(mockProduct.id, 0);
      });
      
      expect(result.current.items).toHaveLength(0);
    });

    it('should clear entire cart', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct);
        result.current.addItem(mockProduct2);
      });
      
      expect(result.current.items).toHaveLength(2);
      
      act(() => {
        result.current.clearCart();
      });
      
      expect(result.current.items).toHaveLength(0);
      expect(result.current.totals).toEqual({
        subtotal: 0,
        tax: 0,
        total: 0,
        itemCount: 0,
      });
    });
  });

  describe('Cart State Management', () => {
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
      });
      
      expect(result.current.isOpen).toBe(true);
      
      act(() => {
        result.current.closeCart();
      });
      
      expect(result.current.isOpen).toBe(false);
    });
  });

  describe('Totals Calculation', () => {
    it('should calculate subtotal correctly', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 2); // 1000 * 2 = 2000
        result.current.addItem(mockProduct2, 1); // 500 * 1 = 500
      });
      
      expect(result.current.totals.subtotal).toBe(2500);
    });

    it('should calculate VAT (15%) correctly', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1); // 1000 * 1 = 1000
      });
      
      const expectedTax = 1000 * 0.15; // 150
      expect(result.current.totals.tax).toBe(expectedTax);
    });

    it('should calculate total with VAT correctly', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 1); // 1000
      });
      
      const subtotal = 1000;
      const tax = subtotal * 0.15; // 150
      const total = subtotal + tax; // 1150
      
      expect(result.current.totals.total).toBe(total);
    });

    it('should calculate item count correctly', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 3);
        result.current.addItem(mockProduct2, 2);
      });
      
      expect(result.current.totals.itemCount).toBe(5);
    });

    it('should recalculate totals when items change', () => {
      const { result } = renderHook(() => useCartStore());
      
      act(() => {
        result.current.addItem(mockProduct, 2);
      });
      
      const initialTotal = result.current.totals.total;
      
      act(() => {
        result.current.updateQuantity(mockProduct.id, 4);
      });
      
      expect(result.current.totals.total).toBe(initialTotal * 2);
    });
  });

  describe('Error Handling', () => {
    it('should clear error when performing operations', () => {
      const { result } = renderHook(() => useCartStore());
      
      // Manually set an error
      act(() => {
        useCartStore.setState({ error: 'Test error' });
      });
      
      expect(result.current.error).toBe('Test error');
      
      act(() => {
        result.current.addItem(mockProduct);
      });
      
      expect(result.current.error).toBeUndefined();
    });
  });

  describe('Selector Hooks', () => {
    it('should provide correct selector values', () => {
      const { result: cartStore } = renderHook(() => useCartStore());
      const { result: cartItems } = renderHook(() => useCartStore((state) => state.items));
      const { result: cartTotals } = renderHook(() => useCartStore((state) => state.totals));
      const { result: isCartOpen } = renderHook(() => useCartStore((state) => state.isOpen));
      
      act(() => {
        cartStore.current.addItem(mockProduct);
        cartStore.current.openCart();
      });
      
      expect(cartItems.current).toHaveLength(1);
      expect(cartTotals.current.itemCount).toBe(1);
      expect(isCartOpen.current).toBe(true);
    });
  });
});

describe('Price Formatting Functions', () => {
  it('should format price in Arabic locale', () => {
    const formatted = formatPrice(1500);
    expect(formatted).toMatch(/1[٬,]?500|١[٬,]?٥٠٠/); // Handle both Arabic and English numerals
    expect(formatted).toMatch(/SAR|ر\.س/);
  });

  it('should format price in English locale', () => {
    const formatted = formatPriceEnglish(1500);
    expect(formatted).toBe('1,500 SAR');
  });

  it('should handle zero price', () => {
    const arabicFormatted = formatPrice(0);
    const englishFormatted = formatPriceEnglish(0);
    
    expect(arabicFormatted).toMatch(/0|٠/); // Handle both Arabic and English zero
    expect(englishFormatted).toBe('0 SAR');
  });

  it('should handle large numbers', () => {
    const formatted = formatPriceEnglish(1234567);
    expect(formatted).toBe('1,234,567 SAR');
  });
});