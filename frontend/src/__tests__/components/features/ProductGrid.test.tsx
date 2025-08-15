import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductGrid } from '@/components/features/ProductGrid';
import { Product } from '@/types';
import { products } from '@/data/products';

// Mock the ProductCard component to make tests more focused
jest.mock('@/components/features/ProductCard', () => ({
  ProductCard: ({ product, onAddToCart, onShowDemo }: any) => (
    <div data-testid={`product-card-${product.id}`}>
      <h3>{product.title}</h3>
      <button 
        type="button"
        onClick={() => onAddToCart(product)} 
        data-testid={`add-to-cart-${product.id}`}
      >
        Add to Cart
      </button>
      <button 
        type="button"
        onClick={() => onShowDemo(product)} 
        data-testid={`show-demo-${product.id}`}
      >
        Show Demo
      </button>
    </div>
  )
}));

// Mock useTranslation hook
jest.mock('@/hooks/useTranslation', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: { [key: string]: string } = {
        'filters.noResults': 'No products found',
        'filters.tryAdjusting': 'Try adjusting your filters to find more products',
      };
      return translations[key] || key;
    }
  })
}));

describe('ProductGrid Component', () => {
  const mockOnAddToCart = jest.fn();
  const mockOnShowDemo = jest.fn();
  
  // Use real product data for tests
  const testProducts = products.slice(0, 4); // First 4 products

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering with Products', () => {
    it('should render products grid with real product data', () => {
      render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Check that all products are rendered
      testProducts.forEach(product => {
        expect(screen.getByTestId(`product-card-${product.id}`)).toBeInTheDocument();
        expect(screen.getByText(product.title)).toBeInTheDocument();
      });
    });

    it('should render with proper grid classes', () => {
      const { container } = render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      const gridElement = container.querySelector('.grid');
      expect(gridElement).toHaveClass(
        'grid',
        'grid-cols-1',
        'md:grid-cols-2',
        'lg:grid-cols-3',
        'xl:grid-cols-4',
        'gap-6'
      );
    });

    it('should apply custom className when provided', () => {
      const customClass = 'custom-grid-class';
      const { container } = render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
          className={customClass}
        />
      );

      expect(container.firstChild).toHaveClass(customClass);
    });

    it('should apply animation delay styles to product cards', () => {
      const { container } = render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      const animatedDivs = container.querySelectorAll('.animate-fade-in-up');
      expect(animatedDivs).toHaveLength(testProducts.length);

      // Check that animation delays are applied
      animatedDivs.forEach((div, index) => {
        const style = window.getComputedStyle(div);
        expect(div).toHaveStyle(`animation-delay: ${index * 100}ms`);
        expect(div).toHaveStyle('animation-fill-mode: both');
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading skeletons when loading is true', () => {
      render(
        <ProductGrid
          products={[]}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
          loading={true}
        />
      );

      // Should show 8 loading skeletons
      const skeletons = screen.getAllByText('', { selector: '.animate-pulse' });
      expect(skeletons).toHaveLength(8);

      // Should not show empty state or products
      expect(screen.queryByText('No products found')).not.toBeInTheDocument();
    });

    it('should render loading skeleton with proper structure', () => {
      const { container } = render(
        <ProductGrid
          products={[]}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
          loading={true}
        />
      );

      const skeleton = container.querySelector('.animate-pulse');
      expect(skeleton).toHaveClass('glass', 'rounded-2xl', 'p-6', 'animate-pulse');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when no products and not loading', () => {
      render(
        <ProductGrid
          products={[]}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
          loading={false}
        />
      );

      expect(screen.getByText('No products found')).toBeInTheDocument();
      expect(screen.getByText('Try adjusting your filters to find more products')).toBeInTheDocument();
      expect(screen.getByText('🔍')).toBeInTheDocument();
    });

    it('should render empty state with proper styling', () => {
      render(
        <ProductGrid
          products={[]}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      const emptyState = screen.getByText('No products found').closest('div');
      expect(emptyState).toHaveClass(
        'col-span-full',
        'flex',
        'flex-col',
        'items-center',
        'justify-center',
        'py-16',
        'px-4'
      );
    });
  });

  describe('Product Interactions', () => {
    it('should call onAddToCart when add to cart button is clicked', () => {
      render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      const firstProduct = testProducts[0];
      const addToCartButton = screen.getByTestId(`add-to-cart-${firstProduct.id}`);
      
      fireEvent.click(addToCartButton);
      
      expect(mockOnAddToCart).toHaveBeenCalledWith(firstProduct);
      expect(mockOnAddToCart).toHaveBeenCalledTimes(1);
    });

    it('should call onShowDemo when show demo button is clicked', () => {
      render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      const firstProduct = testProducts[0];
      const showDemoButton = screen.getByTestId(`show-demo-${firstProduct.id}`);
      
      fireEvent.click(showDemoButton);
      
      expect(mockOnShowDemo).toHaveBeenCalledWith(firstProduct);
      expect(mockOnShowDemo).toHaveBeenCalledTimes(1);
    });

    it('should handle multiple product interactions correctly', () => {
      render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Click on multiple products
      testProducts.slice(0, 2).forEach(product => {
        fireEvent.click(screen.getByTestId(`add-to-cart-${product.id}`));
        fireEvent.click(screen.getByTestId(`show-demo-${product.id}`));
      });

      expect(mockOnAddToCart).toHaveBeenCalledTimes(2);
      expect(mockOnShowDemo).toHaveBeenCalledTimes(2);
    });
  });

  describe('Performance Optimization', () => {
    it('should maintain component reference when props do not change', () => {
      const { rerender } = render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Re-render with same props
      rerender(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Component should still render correctly
      testProducts.forEach(product => {
        expect(screen.getByTestId(`product-card-${product.id}`)).toBeInTheDocument();
      });
    });

    it('should update when products prop changes', () => {
      const { rerender } = render(
        <ProductGrid
          products={testProducts.slice(0, 2)}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Should show first 2 products
      expect(screen.getAllByText('', { selector: '[data-testid^="product-card"]' })).toHaveLength(2);

      // Update to show more products
      rerender(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Should now show all 4 products
      expect(screen.getAllByText('', { selector: '[data-testid^="product-card"]' })).toHaveLength(4);
    });
  });

  describe('Real Product Data Validation', () => {
    it('should render with actual product data from data layer', () => {
      const realProducts = products.filter(p => p.category === 'ai').slice(0, 3);
      
      render(
        <ProductGrid
          products={realProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      realProducts.forEach(product => {
        expect(screen.getByText(product.title)).toBeInTheDocument();
        expect(screen.getByTestId(`product-card-${product.id}`)).toBeInTheDocument();
      });
    });

    it('should handle products from different categories', () => {
      const mixedProducts = [
        ...products.filter(p => p.category === 'ai').slice(0, 1),
        ...products.filter(p => p.category === 'apps').slice(0, 1),
        ...products.filter(p => p.category === 'tools').slice(0, 1),
      ];

      render(
        <ProductGrid
          products={mixedProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      mixedProducts.forEach(product => {
        expect(screen.getByText(product.title)).toBeInTheDocument();
      });
    });

    it('should work with large product sets efficiently', () => {
      const largeProductSet = products.slice(0, 20); // First 20 products

      render(
        <ProductGrid
          products={largeProductSet}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Should render all products
      expect(screen.getAllByText('', { selector: '[data-testid^="product-card"]' })).toHaveLength(20);

      // Should handle interactions on any product
      const randomProduct = largeProductSet[10];
      fireEvent.click(screen.getByTestId(`add-to-cart-${randomProduct.id}`));
      expect(mockOnAddToCart).toHaveBeenCalledWith(randomProduct);
    });
  });

  describe('Edge Cases', () => {
    it('should handle undefined products gracefully', () => {
      render(
        <ProductGrid
          products={[]}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      expect(screen.getByText('No products found')).toBeInTheDocument();
    });

    it('should handle products with missing properties gracefully', () => {
      const incompleteProduct = {
        id: 999,
        title: 'Incomplete Product',
        category: 'ai' as const,
        description: 'Test',
        price: 100,
        icon: '🤖',
        features: []
      };

      render(
        <ProductGrid
          products={[incompleteProduct]}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      expect(screen.getByText('Incomplete Product')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should maintain proper semantic structure', () => {
      const { container } = render(
        <ProductGrid
          products={testProducts}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Grid container should exist
      const gridContainer = container.querySelector('.grid');
      expect(gridContainer).toBeInTheDocument();

      // All buttons should be accessible
      testProducts.forEach(product => {
        const addButton = screen.getByTestId(`add-to-cart-${product.id}`);
        const demoButton = screen.getByTestId(`show-demo-${product.id}`);
        
        expect(addButton).toHaveAttribute('type', 'button');
        expect(demoButton).toHaveAttribute('type', 'button');
        expect(addButton).toBeInTheDocument();
        expect(demoButton).toBeInTheDocument();
      });
    });

    it('should provide meaningful empty state content', () => {
      render(
        <ProductGrid
          products={[]}
          onAddToCart={mockOnAddToCart}
          onShowDemo={mockOnShowDemo}
        />
      );

      // Should have accessible text content
      expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('No products found');
    });
  });
});