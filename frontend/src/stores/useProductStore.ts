import { create } from 'zustand';
import { Product, ProductCategory, ProductFilters, SearchResult } from '@/types';

interface ProductState {
  // Product data
  products: Product[];
  filteredProducts: Product[];
  searchResults?: SearchResult;
  
  // Current product for demo/details
  currentProduct?: Product;
  
  // Filters and search
  filters: ProductFilters;
  searchQuery: string;
  
  // UI states
  isLoading: boolean;
  error?: string;
  hasMore: boolean;
  page: number;
  
  // Demo modal state
  isDemoOpen: boolean;
  demoProduct?: Product;
  
  // Actions
  setProducts: (_products: Product[]) => void;
  addProducts: (_products: Product[]) => void;
  setCurrentProduct: (product: Product) => void;
  clearCurrentProduct: () => void;
  
  // Filtering and search
  setSearchQuery: (query: string) => void;
  setCategoryFilter: (category: ProductCategory | 'all') => void;
  setSortBy: (sortBy: ProductFilters['sortBy'], direction?: ProductFilters['sortDirection']) => void;
  setPriceRange: (min: number, max: number) => void;
  resetFilters: () => void;
  applyFilters: () => void;
  
  // Demo modal
  openDemo: (product: Product) => void;
  closeDemo: () => void;
  
  // Loading states
  setLoading: (isLoading: boolean) => void;
  setError: (error?: string) => void;
  
  // Pagination
  loadMore: () => Promise<void>;
  resetPagination: () => void;
}

const initialFilters: ProductFilters = {
  category: 'all',
  searchQuery: '',
  sortBy: 'newest',
  sortDirection: 'desc',
  priceRange: {
    min: 0,
    max: 10000,
  },
};

export const useProductStore = create<ProductState>((set, get) => ({
  // Initial state
  products: [],
  filteredProducts: [],
  searchResults: undefined,
  currentProduct: undefined,
  filters: initialFilters,
  searchQuery: '',
  isLoading: false,
  error: undefined,
  hasMore: true,
  page: 1,
  isDemoOpen: false,
  demoProduct: undefined,
  
  // Actions
  setProducts: (products: Product[]) => {
    set({ products });
    get().applyFilters();
  },
  
  addProducts: (products: Product[]) => {
    set((state) => ({
      products: [...state.products, ...products],
    }));
    get().applyFilters();
  },
  
  setCurrentProduct: (product: Product) => {
    set({ currentProduct: product });
  },
  
  clearCurrentProduct: () => {
    set({ currentProduct: undefined });
  },
  
  // Filtering and search
  setSearchQuery: (query: string) => {
    set((state) => ({
      searchQuery: query,
      filters: { ...state.filters, searchQuery: query },
    }));
    get().applyFilters();
  },
  
  setCategoryFilter: (category: ProductCategory | 'all') => {
    set((state) => ({
      filters: { ...state.filters, category },
    }));
    get().applyFilters();
  },
  
  setSortBy: (sortBy: ProductFilters['sortBy'], direction: ProductFilters['sortDirection'] = 'desc') => {
    set((state) => ({
      filters: { ...state.filters, sortBy, sortDirection: direction },
    }));
    get().applyFilters();
  },
  
  setPriceRange: (min: number, max: number) => {
    set((state) => ({
      filters: {
        ...state.filters,
        priceRange: { min, max },
      },
    }));
    get().applyFilters();
  },
  
  resetFilters: () => {
    set({
      filters: initialFilters,
      searchQuery: '',
    });
    get().applyFilters();
  },
  
  applyFilters: () => {
    const { products, filters } = get();
    let filtered = [...products];
    
    // Apply category filter
    if (filters.category !== 'all') {
      filtered = filtered.filter(product => product.category === filters.category);
    }
    
    // Apply search query
    if (filters.searchQuery.trim()) {
      const query = filters.searchQuery.toLowerCase().trim();
      filtered = filtered.filter(product => {
        return (
          product.title.toLowerCase().includes(query) ||
          product.arabicTitle?.toLowerCase().includes(query) ||
          product.description.toLowerCase().includes(query) ||
          product.arabicDescription?.toLowerCase().includes(query) ||
          product.category.toLowerCase().includes(query) ||
          product.features.some(feature => feature.toLowerCase().includes(query)) ||
          product.arabicFeatures?.some(feature => feature.toLowerCase().includes(query)) ||
          product.tags?.some(tag => tag.toLowerCase().includes(query))
        );
      });
    }
    
    // Apply price range filter
    filtered = filtered.filter(product => {
      return product.price >= filters.priceRange.min && product.price <= filters.priceRange.max;
    });
    
    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (filters.sortBy) {
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'rating':
          comparison = (a.rating || 0) - (b.rating || 0);
          break;
        case 'popular':
          comparison = (a.reviewCount || 0) - (b.reviewCount || 0);
          break;
        case 'newest':
        default:
          comparison = a.id - b.id; // Assuming higher ID means newer
          break;
      }
      
      return filters.sortDirection === 'asc' ? comparison : -comparison;
    });
    
    set({ filteredProducts: filtered });
  },
  
  // Demo modal
  openDemo: (product: Product) => {
    set({
      isDemoOpen: true,
      demoProduct: product,
    });
  },
  
  closeDemo: () => {
    set({
      isDemoOpen: false,
      demoProduct: undefined,
    });
  },
  
  // Loading states
  setLoading: (isLoading: boolean) => {
    set({ isLoading });
  },
  
  setError: (error?: string) => {
    set({ error });
  },
  
  // Pagination
  loadMore: async () => {
    // This would typically make an API call
    // For now, we'll just simulate loading more products
    const { page, hasMore } = get();
    
    if (!hasMore) return;
    
    set({ isLoading: true });
    
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, this would fetch more products from the API
      // For now, we'll just increment the page and assume no more data
      set({
        page: page + 1,
        hasMore: false,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: 'Failed to load more products',
        isLoading: false,
      });
    }
  },
  
  resetPagination: () => {
    set({
      page: 1,
      hasMore: true,
    });
  },
}));

// Selector hooks for optimized re-renders
export const useProducts = () => useProductStore((state) => state.products);
export const useFilteredProducts = () => useProductStore((state) => state.filteredProducts);
export const useCurrentProduct = () => useProductStore((state) => state.currentProduct);
export const useProductFilters = () => useProductStore((state) => state.filters);
export const useSearchQuery = () => useProductStore((state) => state.searchQuery);
export const useProductLoading = () => useProductStore((state) => state.isLoading);
export const useProductError = () => useProductStore((state) => state.error);
export const useDemoModal = () => useProductStore((state) => ({
  isOpen: state.isDemoOpen,
  product: state.demoProduct,
}));

// Computed selectors
export const useProductCount = () => useProductStore((state) => state.filteredProducts.length);
export const useHasProducts = () => useProductStore((state) => state.filteredProducts.length > 0);

// Category helpers
export const getCategoryCount = (category: ProductCategory | 'all'): number => {
  const products = useProductStore.getState().products;
  if (category === 'all') return products.length;
  return products.filter(p => p.category === category).length;
};