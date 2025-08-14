// Re-export all stores and their hooks for easy importing
export * from './useAppStore';
export * from './useCartStore';
export * from './useProductStore';

// Store initialization and hydration utilities
export const initializeStores = () => {
  // Any store initialization logic can go here
  // This is useful for SSR/SSG where you need to sync state
};

// Helper function to get all store states (useful for debugging)
export const getStoreStates = () => {
  if (typeof window === 'undefined') return null;
  
  const stores = {
    app: JSON.parse(localStorage.getItem('brainsait-app-store') || '{}'),
    cart: JSON.parse(localStorage.getItem('brainsait-cart-store') || '{}'),
  };
  
  return stores;
};

// Clear all persisted store data (useful for logout or reset)
export const clearAllStores = () => {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem('brainsait-app-store');
  localStorage.removeItem('brainsait-cart-store');
  
  // Force reload to reset all store states
  window.location.reload();
};