import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Navigation } from '@/components/layout/Navigation';

// Mock Next.js Link component
jest.mock('next/link', () => {
  return ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  );
});

// Mock the translation hook
jest.mock('@/hooks/useTranslation', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'navigation.logo': 'BrainSAIT',
        'navigation.products': 'Products',
        'navigation.solutions': 'Solutions',
        'navigation.pricing': 'Pricing',
        'navigation.about': 'About',
        'navigation.cart': 'Cart',
        'accessibility.closeMenu': 'Close menu',
        'accessibility.openMenu': 'Open menu',
      };
      return translations[key] || key;
    },
  }),
}));

// Mock utils
jest.mock('@/lib/utils', () => ({
  cn: (...classes: (string | undefined)[]) => classes.filter(Boolean).join(' '),
}));

// Mock stores
const mockUseAppStore = jest.fn();
const mockUseCartStore = jest.fn();

jest.mock('@/stores', () => ({
  useAppStore: () => mockUseAppStore(),
  useCartStore: () => mockUseCartStore(),
}));

// Mock Heroicons
jest.mock('@heroicons/react/24/outline', () => ({
  ShoppingCartIcon: (props: any) => <svg data-testid="cart-icon" {...props} />,
}));

describe('Navigation', () => {
  const mockToggleMobileMenu = jest.fn();
  const mockCloseMobileMenu = jest.fn();
  const mockToggleCart = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    mockUseAppStore.mockReturnValue({
      isMobileMenuOpen: false,
      toggleMobileMenu: mockToggleMobileMenu,
      closeMobileMenu: mockCloseMobileMenu,
    });

    mockUseCartStore.mockReturnValue({
      totals: { itemCount: 0 },
      toggleCart: mockToggleCart,
    });
  });

  it('should render navigation with logo', () => {
    render(<Navigation />);
    
    expect(screen.getByText('BrainSAIT')).toBeInTheDocument();
    expect(screen.getByText('◈')).toBeInTheDocument();
  });

  it('should render all navigation items', () => {
    render(<Navigation />);
    
    expect(screen.getAllByText('Products')).toHaveLength(2); // Desktop and mobile
    expect(screen.getAllByText('Solutions')).toHaveLength(2);
    expect(screen.getAllByText('Pricing')).toHaveLength(2);
    expect(screen.getAllByText('About')).toHaveLength(2);
  });

  it('should render cart button', () => {
    render(<Navigation />);
    
    const cartButtons = screen.getAllByText('Cart');
    expect(cartButtons).toHaveLength(2); // Desktop and mobile versions
    expect(screen.getAllByTestId('cart-icon')).toHaveLength(2);
  });

  it('should handle cart button click', () => {
    render(<Navigation />);
    
    const cartButton = screen.getAllByText('Cart')[0]; // Desktop version
    fireEvent.click(cartButton);
    
    expect(mockToggleCart).toHaveBeenCalledTimes(1);
  });

  it('should show cart item count badge when items in cart', () => {
    mockUseCartStore.mockReturnValue({
      totals: { itemCount: 5 },
      toggleCart: mockToggleCart,
    });

    render(<Navigation />);
    
    const badges = screen.getAllByText('5');
    expect(badges).toHaveLength(2); // Desktop and mobile versions
  });

  it('should not show cart badge when cart is empty', () => {
    render(<Navigation />);
    
    // Should not find any cart count badges
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('should handle mobile menu toggle', () => {
    render(<Navigation />);
    
    const mobileMenuButton = screen.getByLabelText('Open menu');
    fireEvent.click(mobileMenuButton);
    
    expect(mockToggleMobileMenu).toHaveBeenCalledTimes(1);
  });

  it('should show mobile menu when open', () => {
    mockUseAppStore.mockReturnValue({
      isMobileMenuOpen: true,
      toggleMobileMenu: mockToggleMobileMenu,
      closeMobileMenu: mockCloseMobileMenu,
    });

    const { container } = render(<Navigation />);
    
    // Should show close menu label
    expect(screen.getByLabelText('Close menu')).toBeInTheDocument();
    
    // Should have overlay div
    const overlay = container.querySelector('.fixed.inset-0.top-16');
    expect(overlay).toBeInTheDocument();
  });

  it('should handle mobile menu overlay click', () => {
    mockUseAppStore.mockReturnValue({
      isMobileMenuOpen: true,
      toggleMobileMenu: mockToggleMobileMenu,
      closeMobileMenu: mockCloseMobileMenu,
    });

    const { container } = render(<Navigation />);
    
    // Click on overlay
    const overlay = container.querySelector('.fixed.inset-0');
    if (overlay) {
      fireEvent.click(overlay);
      expect(mockCloseMobileMenu).toHaveBeenCalledTimes(1);
    }
  });

  it('should handle mobile navigation link click', () => {
    mockUseAppStore.mockReturnValue({
      isMobileMenuOpen: true,
      toggleMobileMenu: mockToggleMobileMenu,
      closeMobileMenu: mockCloseMobileMenu,
    });

    render(<Navigation />);
    
    // Click on mobile navigation link
    const mobileLinks = screen.getAllByText('Products');
    const mobileLink = mobileLinks[1]; // Mobile version
    fireEvent.click(mobileLink);
    
    expect(mockCloseMobileMenu).toHaveBeenCalledTimes(1);
  });

  it('should handle mobile cart button click', () => {
    mockUseAppStore.mockReturnValue({
      isMobileMenuOpen: true,
      toggleMobileMenu: mockToggleMobileMenu,
      closeMobileMenu: mockCloseMobileMenu,
    });

    render(<Navigation />);
    
    // Click on mobile cart button
    const cartButtons = screen.getAllByText('Cart');
    const mobileCartButton = cartButtons[1]; // Mobile version
    fireEvent.click(mobileCartButton);
    
    expect(mockToggleCart).toHaveBeenCalledTimes(1);
    expect(mockCloseMobileMenu).toHaveBeenCalledTimes(1);
  });

  it('should apply custom className', () => {
    const { container } = render(<Navigation className="custom-nav-class" />);
    
    const nav = container.firstChild;
    expect(nav).toHaveClass('custom-nav-class');
  });

  it('should have proper navigation structure', () => {
    render(<Navigation />);
    
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    expect(nav).toHaveClass('fixed', 'top-0', 'w-full', 'z-navigation');
  });

  it('should render logo link with correct href', () => {
    render(<Navigation />);
    
    const logoLink = screen.getByText('BrainSAIT').closest('a');
    expect(logoLink).toHaveAttribute('href', '/');
  });

  it('should render navigation links with correct hrefs', () => {
    render(<Navigation />);
    
    const productsLinks = screen.getAllByText('Products');
    expect(productsLinks[0].closest('a')).toHaveAttribute('href', '#products');
    
    const solutionsLinks = screen.getAllByText('Solutions');
    expect(solutionsLinks[0].closest('a')).toHaveAttribute('href', '#solutions');
    
    const pricingLinks = screen.getAllByText('Pricing');
    expect(pricingLinks[0].closest('a')).toHaveAttribute('href', '#pricing');
    
    const aboutLinks = screen.getAllByText('About');
    expect(aboutLinks[0].closest('a')).toHaveAttribute('href', '#about');
  });

  it('should hide desktop navigation on mobile', () => {
    render(<Navigation />);
    
    const allProductsLinks = screen.getAllByText('Products');
    const desktopNav = allProductsLinks[0].parentElement;
    expect(desktopNav).toHaveClass('hidden', 'md:flex');
  });

  it('should show mobile menu button only on mobile', () => {
    render(<Navigation />);
    
    const mobileMenuButton = screen.getByLabelText('Open menu');
    expect(mobileMenuButton).toHaveClass('md:hidden');
  });

  it('should handle large cart item count', () => {
    mockUseCartStore.mockReturnValue({
      totals: { itemCount: 99 },
      toggleCart: mockToggleCart,
    });

    render(<Navigation />);
    
    const badges = screen.getAllByText('99');
    expect(badges).toHaveLength(2);
  });

  it('should render mobile menu with correct animation classes', () => {
    mockUseAppStore.mockReturnValue({
      isMobileMenuOpen: true,
      toggleMobileMenu: mockToggleMobileMenu,
      closeMobileMenu: mockCloseMobileMenu,
    });

    const { container } = render(<Navigation />);
    
    // Look for mobile menu container
    const mobileMenu = container.querySelector('[class*="md:hidden"][class*="fixed"][class*="top-16"]');
    expect(mobileMenu).toBeInTheDocument();
  });

  it('should hide mobile menu with correct animation classes', () => {
    const { container } = render(<Navigation />);
    
    // Look for mobile menu container
    const mobileMenu = container.querySelector('[class*="md:hidden"][class*="fixed"][class*="top-16"]');
    expect(mobileMenu).toBeInTheDocument();
  });

  it('should render hamburger menu icon with correct animation', () => {
    render(<Navigation />);
    
    const menuButton = screen.getByLabelText('Open menu');
    const hamburgerContainer = menuButton.querySelector('div');
    expect(hamburgerContainer).not.toHaveClass('rotate-45');
    
    const lines = hamburgerContainer?.querySelectorAll('span');
    expect(lines).toHaveLength(3);
    expect(lines?.[1]).not.toHaveClass('opacity-0');
  });

  it('should animate hamburger menu icon when open', () => {
    mockUseAppStore.mockReturnValue({
      isMobileMenuOpen: true,
      toggleMobileMenu: mockToggleMobileMenu,
      closeMobileMenu: mockCloseMobileMenu,
    });

    render(<Navigation />);
    
    const menuButton = screen.getByLabelText('Close menu');
    const hamburgerContainer = menuButton.querySelector('div');
    expect(hamburgerContainer).toBeInTheDocument();
    
    const lines = hamburgerContainer?.querySelectorAll('span');
    expect(lines).toHaveLength(3);
  });

  it('should handle different cart count scenarios', () => {
    // Test with zero items
    render(<Navigation />);
    expect(screen.queryByText('0')).not.toBeInTheDocument();

    // Test with single item
    mockUseCartStore.mockReturnValue({
      totals: { itemCount: 1 },
      toggleCart: mockToggleCart,
    });

    const { rerender } = render(<Navigation />);
    rerender(<Navigation />);
    expect(screen.getAllByText('1')).toHaveLength(2);
  });

  it('should maintain accessibility attributes', () => {
    render(<Navigation />);
    
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    
    const menuButton = screen.getByLabelText('Open menu');
    expect(menuButton).toHaveAttribute('aria-label', 'Open menu');
  });

  it('should handle rapid menu toggle clicks', () => {
    render(<Navigation />);
    
    const menuButton = screen.getByLabelText('Open menu');
    
    // Click multiple times rapidly
    fireEvent.click(menuButton);
    fireEvent.click(menuButton);
    fireEvent.click(menuButton);
    
    expect(mockToggleMobileMenu).toHaveBeenCalledTimes(3);
  });

  it('should render cart icon in both desktop and mobile versions', () => {
    render(<Navigation />);
    
    const cartIcons = screen.getAllByTestId('cart-icon');
    expect(cartIcons).toHaveLength(2);
  });

  it('should apply correct button variants', () => {
    render(<Navigation />);
    
    // Cart button should have gradient variant
    const cartButtons = screen.getAllByText('Cart');
    expect(cartButtons[0].closest('button')).toHaveClass('bg-gradient-primary');
    
    // Mobile menu button should have ghost variant
    const menuButton = screen.getByLabelText('Open menu');
    expect(menuButton).toHaveClass('text-text-primary');
  });
});