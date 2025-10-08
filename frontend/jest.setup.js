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