import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { CartItem, CartTotals, Product } from '@/types';

interface CartState {
  // Cart data
  items: CartItem[];
  totals: CartTotals;
  isOpen: boolean;
  
  // UI states
  isLoading: boolean;
  error?: string;
  
  // Actions
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  clearCart: () => void;
  toggleCart: () => void;
  closeCart: () => void;
  openCart: () => void;
  
  // Private methods
  calculateTotals: () => void;
}

// VAT rate for Saudi Arabia
const VAT_RATE = 0.15;

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      // Initial state
      items: [],
      totals: {
        subtotal: 0,
        tax: 0,
        total: 0,
        itemCount: 0,
      },
      isOpen: false,
      isLoading: false,
      error: undefined,
      
      // Actions
      addItem: (product: Product, quantity = 1) => {
        const { items } = get();
        const existingItem = items.find(item => item.productId === product.id);
        
        if (existingItem) {
          // Update quantity if item already exists
          get().updateQuantity(product.id, existingItem.quantity + quantity);
        } else {
          // Add new item
          const newItem: CartItem = {
            id: Math.random(), // Generate unique cart item ID
            productId: product.id,
            title: product.title,
            arabicTitle: product.arabicTitle,
            price: product.price,
            quantity,
            icon: product.icon,
          };
          
          set((state) => ({
            items: [...state.items, newItem],
            error: undefined,
          }));
        }
        
        get().calculateTotals();
      },
      
      removeItem: (productId: number) => {
        set((state) => ({
          items: state.items.filter(item => item.productId !== productId),
          error: undefined,
        }));
        
        get().calculateTotals();
      },
      
      updateQuantity: (productId: number, quantity: number) => {
        if (quantity <= 0) {
          get().removeItem(productId);
          return;
        }
        
        set((state) => ({
          items: state.items.map(item =>
            item.productId === productId
              ? { ...item, quantity }
              : item
          ),
          error: undefined,
        }));
        
        get().calculateTotals();
      },
      
      clearCart: () => {
        set({
          items: [],
          totals: {
            subtotal: 0,
            tax: 0,
            total: 0,
            itemCount: 0,
          },
          error: undefined,
        });
      },
      
      toggleCart: () => {
        set((state) => ({ isOpen: !state.isOpen }));
      },
      
      closeCart: () => {
        set({ isOpen: false });
      },
      
      openCart: () => {
        set({ isOpen: true });
      },
      
      calculateTotals: () => {
        const { items } = get();
        
        const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const tax = subtotal * VAT_RATE;
        const total = subtotal + tax;
        const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
        
        set({
          totals: {
            subtotal,
            tax,
            total,
            itemCount,
          }
        });
      },
    }),
    {
      name: 'brainsait-cart-store',
      partialize: (state) => ({
        items: state.items,
        totals: state.totals,
      }),
      onRehydrateStorage: () => (state) => {
        // Recalculate totals after rehydration
        if (state) {
          state.calculateTotals();
        }
      },
    }
  )
);

// Selector hooks for optimized re-renders
export const useCartItems = () => useCartStore((state) => state.items);
export const useCartTotals = () => useCartStore((state) => state.totals);
export const useCartItemCount = () => useCartStore((state) => state.totals.itemCount);
export const useIsCartOpen = () => useCartStore((state) => state.isOpen);
export const useCartLoading = () => useCartStore((state) => state.isLoading);
export const useCartError = () => useCartStore((state) => state.error);

// Computed selectors
export const useIsCartEmpty = () => useCartStore((state) => state.items.length === 0);
export const useCartTotal = () => useCartStore((state) => state.totals.total);

// Helper functions for cart operations
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency: 'SAR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
};

export const formatPriceEnglish = (price: number): string => {
  return `${price.toLocaleString()} SAR`;
};