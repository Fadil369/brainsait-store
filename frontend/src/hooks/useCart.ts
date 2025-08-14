import { useCallback } from 'react';
import { useCartStore, useAppStore } from '@/stores';
import { Product } from '@/types';

// Custom hook for cart operations with enhanced functionality
export const useCart = () => {
  const {
    items,
    totals,
    isOpen,
    isLoading,
    error,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    toggleCart,
    closeCart,
    openCart,
  } = useCartStore();

  const { addNotification } = useAppStore();

  // Enhanced add to cart with notification
  const addToCart = useCallback((product: Product, quantity = 1) => {
    try {
      addItem(product, quantity);
      addNotification({
        type: 'success',
        message: `${product.title} added to cart!`,
        duration: 3000,
      });
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to add item to cart',
        duration: 3000,
      });
    }
  }, [addItem, addNotification]);

  // Enhanced remove from cart with notification
  const removeFromCart = useCallback((productId: number) => {
    try {
      const item = items.find(item => item.productId === productId);
      removeItem(productId);
      
      if (item) {
        addNotification({
          type: 'info',
          message: `${item.title} removed from cart`,
          duration: 3000,
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to remove item from cart',
        duration: 3000,
      });
    }
  }, [items, removeItem, addNotification]);

  // Enhanced update quantity with validation
  const updateItemQuantity = useCallback((productId: number, quantity: number) => {
    if (quantity < 1) {
      removeFromCart(productId);
      return;
    }

    if (quantity > 99) {
      addNotification({
        type: 'warning',
        message: 'Maximum quantity is 99',
        duration: 3000,
      });
      return;
    }

    try {
      updateQuantity(productId, quantity);
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to update quantity',
        duration: 3000,
      });
    }
  }, [updateQuantity, removeFromCart, addNotification]);

  // Clear cart with confirmation
  const clearCartWithConfirmation = useCallback(() => {
    if (items.length === 0) return;

    const confirmed = window.confirm('Are you sure you want to clear your cart?');
    if (confirmed) {
      clearCart();
      addNotification({
        type: 'info',
        message: 'Cart cleared',
        duration: 3000,
      });
    }
  }, [items.length, clearCart, addNotification]);

  // Check if product is in cart
  const isInCart = useCallback((productId: number) => {
    return items.some(item => item.productId === productId);
  }, [items]);

  // Get quantity of specific product in cart
  const getItemQuantity = useCallback((productId: number) => {
    const item = items.find(item => item.productId === productId);
    return item?.quantity || 0;
  }, [items]);

  // Get cart summary
  const getCartSummary = useCallback(() => {
    return {
      itemCount: totals.itemCount,
      uniqueItems: items.length,
      subtotal: totals.subtotal,
      tax: totals.tax,
      total: totals.total,
      isEmpty: items.length === 0,
    };
  }, [items.length, totals]);

  // Calculate savings (if any original prices exist)
  const getSavings = useCallback(() => {
    const totalSavings = 0;
    
    // Calculate current total from cart items
    const originalTotal = items.reduce((total, item) => total + (item.price * item.quantity), 0);

    return {
      amount: totalSavings,
      percentage: originalTotal > 0 ? (totalSavings / originalTotal) * 100 : 0,
    };
  }, [items]);

  // Format cart for checkout
  const prepareCheckoutData = useCallback((customerInfo: any) => {
    return {
      items: items,
      totals: totals,
      customerInfo: customerInfo,
    };
  }, [items, totals]);

  return {
    // State
    items,
    totals,
    isOpen,
    isLoading,
    error,
    
    // Enhanced actions
    addToCart,
    removeFromCart,
    updateItemQuantity,
    clearCartWithConfirmation,
    
    // Cart controls
    toggleCart,
    closeCart,
    openCart,
    
    // Utility functions
    isInCart,
    getItemQuantity,
    getCartSummary,
    getSavings,
    prepareCheckoutData,
  };
};