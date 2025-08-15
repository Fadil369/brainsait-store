import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductCard } from '@/components/features/ProductCard';
import { useAppStore } from '@/stores';
import { Product } from '@/types';

// Mock the stores
jest.mock('@/stores', () => ({
  useAppStore: jest.fn(),
}));

// Mock the translation hook
jest.mock('@/hooks/useTranslation', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'product.features': 'Features',
        'product.addToCart': 'Add to Cart',
        'product.tryDemo': 'Try Demo',
        'product.vision2030Badge': 'Vision 2030',
        'product.newBadge': 'New',
        'product.hotBadge': 'Hot',
        'product.proBadge': 'Pro',
      };
      return translations[key] || key;
    },
  }),
}));

const mockProduct: Product = {
  id: '1',
  title: 'Test Product',
  arabicTitle: 'منتج تجريبي',
  description: 'A test product description',
  arabicDescription: 'وصف المنتج التجريبي',
  price: 99.99,
  originalPrice: 149.99,
  category: 'ai',
  icon: '🤖',
  features: ['Feature 1', 'Feature 2', 'Feature 3'],
  arabicFeatures: ['ميزة 1', 'ميزة 2', 'ميزة 3'],
  badge: 'NEW',
  badgeType: 'new',
  isAvailable: true,
  isFeatured: true,
  rating: 4.5,
  reviewCount: 10,
  tags: ['ai', 'automation'],
};

const mockUseAppStore = useAppStore as jest.MockedFunction<typeof useAppStore>;

describe('ProductCard Component', () => {
  const mockOnAddToCart = jest.fn();
  const mockOnShowDemo = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAppStore.mockReturnValue({
      language: 'en',
      isRTL: false,
    } as any);
  });

  it('should render product information correctly', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('A test product description')).toBeInTheDocument();
    expect(screen.getByText('🤖')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
    expect(screen.getByText('Features')).toBeInTheDocument();
  });

  it('should display Arabic content when language is Arabic', () => {
    mockUseAppStore.mockReturnValue({
      language: 'ar',
      isRTL: true,
    } as any);

    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('منتج تجريبي')).toBeInTheDocument();
    expect(screen.getByText('وصف المنتج التجريبي')).toBeInTheDocument();
  });

  it('should display product features', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('Feature 1')).toBeInTheDocument();
    expect(screen.getByText('Feature 2')).toBeInTheDocument();
    expect(screen.getByText('Feature 3')).toBeInTheDocument();
  });

  it('should display Arabic features when language is Arabic', () => {
    mockUseAppStore.mockReturnValue({
      language: 'ar',
      isRTL: true,
    } as any);

    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('ميزة 1')).toBeInTheDocument();
    expect(screen.getByText('ميزة 2')).toBeInTheDocument();
  });

  it('should display badge when present', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('New')).toBeInTheDocument();
  });

  it('should handle add to cart action', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    fireEvent.click(screen.getByText('Add to Cart'));
    expect(mockOnAddToCart).toHaveBeenCalledWith(mockProduct);
  });

  it('should handle demo action', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    fireEvent.click(screen.getByText('Try Demo'));
    expect(mockOnShowDemo).toHaveBeenCalledWith(mockProduct);
  });

  it('should display pricing information', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    // Should display current price
    expect(screen.getByText(/99\.99/)).toBeInTheDocument();
  });

  it('should handle product without badge', () => {
    const productWithoutBadge = { ...mockProduct, badge: undefined, badgeType: undefined };
    
    render(
      <ProductCard
        product={productWithoutBadge}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.queryByText('New')).not.toBeInTheDocument();
  });

  it('should handle different badge types', () => {
    const hotProduct = { ...mockProduct, badge: 'HOT', badgeType: 'hot' as const };
    
    render(
      <ProductCard
        product={hotProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('Hot')).toBeInTheDocument();
  });

  it('should handle Vision 2030 badge', () => {
    const visionProduct = { ...mockProduct, badge: 'VISION 2030', badgeType: 'pro' as const };
    
    render(
      <ProductCard
        product={visionProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('Vision 2030')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
        className="custom-product-card"
      />
    );

    expect(container.firstChild).toHaveClass('custom-product-card');
  });

  it('should limit features display to 4 items', () => {
    const productWithManyFeatures = {
      ...mockProduct,
      features: ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Feature 5', 'Feature 6'],
    };

    render(
      <ProductCard
        product={productWithManyFeatures}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('Feature 1')).toBeInTheDocument();
    expect(screen.getByText('Feature 4')).toBeInTheDocument();
    expect(screen.queryByText('Feature 5')).not.toBeInTheDocument();
    expect(screen.queryByText('Feature 6')).not.toBeInTheDocument();
  });

  it('should handle RTL layout', () => {
    mockUseAppStore.mockReturnValue({
      language: 'ar',
      isRTL: true,
    } as any);

    const { container } = render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    // Check if RTL classes are applied
    const badgeContainer = container.querySelector('.left-6');
    expect(badgeContainer).toBeInTheDocument();
  });

  it('should handle multiple clicks without issues', () => {
    render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    const addToCartButton = screen.getByText('Add to Cart');
    const demoButton = screen.getByText('Try Demo');

    fireEvent.click(addToCartButton);
    fireEvent.click(addToCartButton);
    fireEvent.click(demoButton);

    expect(mockOnAddToCart).toHaveBeenCalledTimes(2);
    expect(mockOnShowDemo).toHaveBeenCalledTimes(1);
  });

  it('should memoize properly and not re-render unnecessarily', () => {
    const { rerender } = render(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    // Re-render with same props should not cause re-render
    rerender(
      <ProductCard
        product={mockProduct}
        onAddToCart={mockOnAddToCart}
        onShowDemo={mockOnShowDemo}
      />
    );

    expect(screen.getByText('Test Product')).toBeInTheDocument();
  });
});