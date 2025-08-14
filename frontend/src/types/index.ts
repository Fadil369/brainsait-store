import React from 'react';

// Enhanced product types for B2B store
export interface Product {
  id: number;
  category: ProductCategory;
  title: string;
  arabicTitle?: string;
  description: string;
  arabicDescription?: string;
  price: number;
  originalPrice?: number;
  badge?: string;
  badgeType?: 'new' | 'hot' | 'pro' | 'premium';
  icon: string;
  features: string[];
  arabicFeatures?: string[];
  demo?: ProductDemo;
  tags?: string[];
  rating?: number;
  reviewCount?: number;
  isDigitalProduct?: boolean;
  
  // Enhanced B2B features
  metadata?: {
    github_url?: string;
    clone_url?: string;
    live_url?: string;
    stars?: number;
    language?: string;
    cloudflare_type?: string;
    deployment_status?: string;
    discovery_source?: string;
  };
  source: 'existing' | 'github' | 'cloudflare' | 'gp_site';
  pricingOptions?: {
    [key: string]: number;
  };
  priceRange?: string;
}

export type ProductCategory = 
  | 'ai' 
  | 'apps' 
  | 'websites' 
  | 'templates' 
  | 'ebooks' 
  | 'courses' 
  | 'tools';

export interface ProductDemo {
  title: string;
  arabicTitle?: string;
  preview: string;
  arabicPreview?: string;
  features: DemoFeature[];
  videoUrl?: string;
  images?: string[];
  
  // Enhanced demo features
  liveUrl?: string;
  githubUrl?: string;
  hasLiveDemo?: boolean;
  hasSourceCode?: boolean;
}

export interface DemoFeature {
  icon: string;
  title: string;
  arabicTitle?: string;
  desc: string;
  arabicDesc?: string;
}

// Cart and checkout types
export interface CartItem {
  id: number;
  productId: number;
  title: string;
  arabicTitle?: string;
  price: number;
  quantity: number;
  icon: string;
}

export interface CartTotals {
  subtotal: number;
  tax: number;
  total: number;
  itemCount: number;
}

export interface CheckoutData {
  items: CartItem[];
  totals: CartTotals;
  customerInfo: CustomerInfo;
  paymentMethod?: PaymentMethod;
}

export interface CustomerInfo {
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  company?: string;
  country: string;
  city: string;
  address?: string;
  isCompany: boolean;
}

export type PaymentMethod = 'mada' | 'visa' | 'mastercard' | 'stc_pay' | 'apple_pay';

// Language and localization
export type Language = 'en' | 'ar';

export interface LocalizedContent {
  en: string;
  ar: string;
}

// Filter and search types
export interface ProductFilters {
  category: ProductCategory | 'all';
  searchQuery: string;
  sortBy: 'price' | 'rating' | 'newest' | 'popular';
  sortDirection: 'asc' | 'desc';
  priceRange: {
    min: number;
    max: number;
  };
}

export interface SearchResult {
  products: Product[];
  totalCount: number;
  facets: {
    categories: Array<{
      category: ProductCategory;
      count: number;
    }>;
    priceRanges: Array<{
      range: string;
      count: number;
    }>;
  };
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Component prop types
export interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  onShowDemo: (product: Product) => void;
  className?: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

// Form types
export interface ContactFormData {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  message: string;
  preferredLanguage: Language;
}

// Navigation types
export interface NavigationItem {
  key: string;
  href: string;
  titleKey: string;
  icon?: string;
  children?: NavigationItem[];
}

// Store state types
export interface AppState {
  language: Language;
  isRTL: boolean;
  theme: 'dark' | 'light';
}

export interface CartState {
  items: CartItem[];
  isOpen: boolean;
  totals: CartTotals;
}

export interface ProductState {
  products: Product[];
  filteredProducts: Product[];
  filters: ProductFilters;
  isLoading: boolean;
  error?: string;
}

// Vision 2030 related types
export interface Vision2030Badge {
  isCompliant: boolean;
  certificationLevel?: 'bronze' | 'silver' | 'gold' | 'platinum';
  sectors: string[];
}

// Analytics and tracking
export interface AnalyticsEvent {
  event: string;
  category: string;
  action: string;
  label?: string;
  value?: number;
  properties?: Record<string, any>;
}

export interface UserActivity {
  sessionId: string;
  userId?: string;
  events: AnalyticsEvent[];
  startTime: Date;
  lastActivity: Date;
}

// Error handling
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
}

export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface ErrorState {
  error: AppError | null;
  severity: ErrorSeverity;
  isVisible: boolean;
}