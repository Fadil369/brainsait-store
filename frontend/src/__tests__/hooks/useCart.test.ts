import { renderHook, act } from '@testing-library/react';
import { useCart } from '@/hooks/useCart';
import { Product } from '@/types';

// Mock the stores
const mockUseCartStore = jest.fn();
const mockUseAppStore = jest.fn();

jest.mock('@/stores', () => ({
  useCartStore: () => mockUseCartStore(),
  useAppStore: () => mockUseAppStore(),
}));

// Mock window.confirm
global.confirm = jest.fn();

describe('useCart Hook', () => {
  const mockAddItem = jest.fn();
  const mockRemoveItem = jest.fn();
  const mockUpdateQuantity = jest.fn();
  const mockClearCart = jest.fn();
  const mockToggleCart = jest.fn();
  const mockCloseCart = jest.fn();
  const mockOpenCart = jest.fn();
  const mockAddNotification = jest.fn();

  const mockProduct: Product = {
    id: 1,
    title: 'Test Product',
    description: 'Test Description',
    price: 100,
    category: 'ai',
    imageUrl: '/test-image.jpg',
    features: [],
    demoUrl: 'https://demo.example.com',
    tags: ['test'],
    isNew: false,
    isFeatured: false,
    rating: 4.5,
    reviewCount: 10,
    availability: 'available'
  };

  const mockCartItems = [
    {
      productId: 1,
      title: 'Test Product',
      price: 100,
      quantity: 2,
      imageUrl: '/test-image.jpg',
      subtotal: 200,
    }
  ];

  const mockTotals = {
    itemCount: 2,
    subtotal: 200,
    tax: 20,
    total: 220,
  };

  beforeEach(() => {
    jest.clearAllMocks();

    mockUseCartStore.mockReturnValue({
      items: mockCartItems,
      totals: mockTotals,
      isOpen: false,
      isLoading: false,
      error: null,
      addItem: mockAddItem,
      removeItem: mockRemoveItem,
      updateQuantity: mockUpdateQuantity,
      clearCart: mockClearCart,
      toggleCart: mockToggleCart,
      closeCart: mockCloseCart,
      openCart: mockOpenCart,
    });

    mockUseAppStore.mockReturnValue({
      addNotification: mockAddNotification,
    });
  });

  describe('addToCart', () => {
    it('should add product to cart and show success notification', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.addToCart(mockProduct, 1);
      });

      expect(mockAddItem).toHaveBeenCalledWith(mockProduct, 1);
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'success',
        message: 'Test Product added to cart!',
        duration: 3000,
      });
    });

    it('should handle add to cart error', () => {
      mockAddItem.mockImplementation(() => {
        throw new Error('Add failed');
      });

      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.addToCart(mockProduct, 1);
      });

      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        message: 'Failed to add item to cart',
        duration: 3000,
      });
    });

    it('should use default quantity of 1', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.addToCart(mockProduct);
      });

      expect(mockAddItem).toHaveBeenCalledWith(mockProduct, 1);
    });
  });

  describe('removeFromCart', () => {
    it('should remove product from cart and show notification', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.removeFromCart(1);
      });

      expect(mockRemoveItem).toHaveBeenCalledWith(1);
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'info',
        message: 'Test Product removed from cart',
        duration: 3000,
      });
    });

    it('should handle remove from cart error', () => {
      mockRemoveItem.mockImplementation(() => {
        throw new Error('Remove failed');
      });

      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.removeFromCart(1);
      });

      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        message: 'Failed to remove item from cart',
        duration: 3000,
      });
    });

    it('should handle removing non-existent item gracefully', () => {
      const emptyCartState = {
        items: [],
        totals: { itemCount: 0, subtotal: 0, tax: 0, total: 0 },
        isOpen: false,
        isLoading: false,
        error: null,
        addItem: mockAddItem,
        removeItem: mockRemoveItem,
        updateQuantity: mockUpdateQuantity,
        clearCart: mockClearCart,
        toggleCart: mockToggleCart,
        closeCart: mockCloseCart,
        openCart: mockOpenCart,
      };

      mockUseCartStore.mockReturnValue(emptyCartState);

      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.removeFromCart(999);
      });

      expect(mockRemoveItem).toHaveBeenCalledWith(999);
      // Since item is not found in empty cart, no info notification should be shown
    });
  });

  describe('updateItemQuantity', () => {
    it('should update quantity for valid values', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.updateItemQuantity(1, 5);
      });

      expect(mockUpdateQuantity).toHaveBeenCalledWith(1, 5);
    });

    it('should remove item when quantity is less than 1', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.updateItemQuantity(1, 0);
      });

      expect(mockRemoveItem).toHaveBeenCalledWith(1);
      expect(mockUpdateQuantity).not.toHaveBeenCalled();
    });

    it('should show warning for quantity above 99', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.updateItemQuantity(1, 100);
      });

      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'warning',
        message: 'Maximum quantity is 99',
        duration: 3000,
      });
      expect(mockUpdateQuantity).not.toHaveBeenCalled();
    });

    it('should handle update quantity error', () => {
      mockUpdateQuantity.mockImplementation(() => {
        throw new Error('Update failed');
      });

      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.updateItemQuantity(1, 5);
      });

      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        message: 'Failed to update quantity',
        duration: 3000,
      });
    });
  });

  describe('clearCartWithConfirmation', () => {
    it('should clear cart when confirmed', () => {
      (global.confirm as jest.Mock).mockReturnValue(true);

      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.clearCartWithConfirmation();
      });

      expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to clear your cart?');
      expect(mockClearCart).toHaveBeenCalled();
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'info',
        message: 'Cart cleared',
        duration: 3000,
      });
    });

    it('should not clear cart when cancelled', () => {
      (global.confirm as jest.Mock).mockReturnValue(false);

      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.clearCartWithConfirmation();
      });

      expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to clear your cart?');
      expect(mockClearCart).not.toHaveBeenCalled();
      expect(mockAddNotification).not.toHaveBeenCalled();
    });

    it('should not prompt when cart is empty', () => {
      mockUseCartStore.mockReturnValue({
        ...mockUseCartStore(),
        items: [],
      });

      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.clearCartWithConfirmation();
      });

      expect(global.confirm).not.toHaveBeenCalled();
      expect(mockClearCart).not.toHaveBeenCalled();
    });
  });

  describe('isInCart', () => {
    it('should return true for product in cart', () => {
      const { result } = renderHook(() => useCart());

      const isProductInCart = result.current.isInCart(1);

      expect(isProductInCart).toBe(true);
    });

    it('should return false for product not in cart', () => {
      const { result } = renderHook(() => useCart());

      const isProductInCart = result.current.isInCart(999);

      expect(isProductInCart).toBe(false);
    });
  });

  describe('getItemQuantity', () => {
    it('should return correct quantity for product in cart', () => {
      const { result } = renderHook(() => useCart());

      const quantity = result.current.getItemQuantity(1);

      expect(quantity).toBe(2);
    });

    it('should return 0 for product not in cart', () => {
      const { result } = renderHook(() => useCart());

      const quantity = result.current.getItemQuantity(999);

      expect(quantity).toBe(0);
    });
  });

  describe('getCartSummary', () => {
    it('should return correct cart summary', () => {
      const { result } = renderHook(() => useCart());

      const summary = result.current.getCartSummary();

      expect(summary).toEqual({
        itemCount: 2,
        uniqueItems: 1,
        subtotal: 200,
        tax: 20,
        total: 220,
        isEmpty: false,
      });
    });

    it('should indicate empty cart', () => {
      mockUseCartStore.mockReturnValue({
        ...mockUseCartStore(),
        items: [],
        totals: { itemCount: 0, subtotal: 0, tax: 0, total: 0 },
      });

      const { result } = renderHook(() => useCart());

      const summary = result.current.getCartSummary();

      expect(summary.isEmpty).toBe(true);
      expect(summary.uniqueItems).toBe(0);
    });
  });

  describe('getSavings', () => {
    it('should calculate savings correctly', () => {
      const { result } = renderHook(() => useCart());

      const savings = result.current.getSavings();

      expect(savings).toEqual({
        amount: 0,
        percentage: 0,
      });
    });

    it('should handle empty cart', () => {
      mockUseCartStore.mockReturnValue({
        ...mockUseCartStore(),
        items: [],
      });

      const { result } = renderHook(() => useCart());

      const savings = result.current.getSavings();

      expect(savings).toEqual({
        amount: 0,
        percentage: 0,
      });
    });
  });

  describe('prepareCheckoutData', () => {
    it('should prepare checkout data correctly', () => {
      const { result } = renderHook(() => useCart());

      const customerInfo = {
        name: 'John Doe',
        email: 'john@example.com',
      };

      const checkoutData = result.current.prepareCheckoutData(customerInfo);

      expect(checkoutData).toEqual({
        customerInfo: customerInfo,
        items: mockCartItems,
        totals: mockTotals,
      });
    });
  });

  describe('Cart State Exposure', () => {
    it('should expose cart state properties', () => {
      const { result } = renderHook(() => useCart());

      expect(result.current.items).toEqual(mockCartItems);
      expect(result.current.totals).toEqual(mockTotals);
      expect(result.current.isOpen).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('should expose cart action methods', () => {
      const { result } = renderHook(() => useCart());

      expect(typeof result.current.toggleCart).toBe('function');
      expect(typeof result.current.closeCart).toBe('function');
      expect(typeof result.current.openCart).toBe('function');
    });
  });

  describe('Edge Cases', () => {
    it('should handle negative quantity in updateItemQuantity', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.updateItemQuantity(1, -1);
      });

      expect(mockRemoveItem).toHaveBeenCalledWith(1);
    });

    it('should handle boundary quantity value 99', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.updateItemQuantity(1, 99);
      });

      expect(mockUpdateQuantity).toHaveBeenCalledWith(1, 99);
      // No warning should be shown for quantity 99 as it's the limit
    });

    it('should handle boundary quantity value 1', () => {
      const { result } = renderHook(() => useCart());

      act(() => {
        result.current.updateItemQuantity(1, 1);
      });

      expect(mockUpdateQuantity).toHaveBeenCalledWith(1, 1);
      expect(mockRemoveItem).not.toHaveBeenCalled();
    });
  });

  describe('Hook Stability', () => {
    it('should maintain function references across re-renders', () => {
      const { result, rerender } = renderHook(() => useCart());

      const firstRenderFunctions = {
        addToCart: result.current.addToCart,
        removeFromCart: result.current.removeFromCart,
        updateItemQuantity: result.current.updateItemQuantity,
      };

      rerender();

      expect(result.current.addToCart).toBe(firstRenderFunctions.addToCart);
      expect(result.current.removeFromCart).toBe(firstRenderFunctions.removeFromCart);
      expect(result.current.updateItemQuantity).toBe(firstRenderFunctions.updateItemQuantity);
    });
  });
});