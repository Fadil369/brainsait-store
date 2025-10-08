import '@testing-library/jest-dom'

// Setup for modal portal container
beforeEach(() => {
  // Create a div with id 'root' if it doesn't exist for modal portals
  if (!document.getElementById('root')) {
    const div = document.createElement('div');
    div.setAttribute('id', 'root');
    document.body.appendChild(div);
  }
});

// Mock i18next for translations
jest.mock('@/hooks/useTranslation', () => ({
  useTranslation: () => ({
    t: (key) => {
      const translations = {
        'cart.empty': 'Your cart is empty',
        'cart.title': 'Shopping Cart',
        'cart.subtotal': 'Subtotal',
        'cart.vat': 'VAT (15%)',
        'cart.total': 'Total',
        'cart.remove': 'Remove',
        'cart.checkout': 'Proceed to Checkout',
        'cart.itemAdded': 'Added to cart!',
        'cart.itemRemoved': 'Removed from cart',
        'common.continueShopping': 'Continue Shopping',
        'products.addToCart': 'Add to Cart',
        'products.viewDetails': 'View Details',
      };
      return translations[key] || key;
    },
    language: 'en',
  }),
}));

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});