import { cn, formatPrice, formatNumber, generateId, debounce, throttle, isMobile, isTouchDevice, getBrowserLanguage } from '@/lib/utils';

describe('Utils Library', () => {
  describe('cn (classname utility)', () => {
    it('should merge classnames correctly', () => {
      expect(cn('base', 'additional')).toBe('base additional');
    });

    it('should handle conditional classnames', () => {
      expect(cn('base', { active: true, disabled: false })).toBe('base active');
    });

    it('should handle undefined and null values', () => {
      expect(cn('base', null, undefined, 'valid')).toBe('base valid');
    });

    it('should merge tailwind classes correctly', () => {
      expect(cn('p-2 text-red-500', 'p-4 text-blue-500')).toBe('p-4 text-blue-500');
    });
  });

  describe('formatPrice', () => {
    it('should format SAR price in Arabic', () => {
      const result = formatPrice(1000, 'ar');
      expect(result).toContain('ر.س');
      expect(result).toContain('١');
    });

    it('should format SAR price in English', () => {
      const result = formatPrice(1000, 'en');
      expect(result).toContain('SAR');
      expect(result).toContain('1,000');
    });

    it('should handle zero values', () => {
      const result = formatPrice(0, 'en');
      expect(result).toContain('0');
      expect(result).toContain('SAR');
    });

    it('should handle negative values', () => {
      const result = formatPrice(-1000, 'en');
      expect(result).toContain('-');
      expect(result).toContain('SAR');
    });

    it('should default to English locale', () => {
      const result = formatPrice(1000);
      expect(result).toContain('SAR');
    });
  });

  describe('formatNumber', () => {
    it('should format numbers in Arabic', () => {
      const result = formatNumber(1000, 'ar');
      expect(result).toContain('١');
    });

    it('should format numbers in English', () => {
      const result = formatNumber(1000, 'en');
      expect(result).toBe('1,000');
    });

    it('should handle decimal numbers', () => {
      const result = formatNumber(1000.99, 'en');
      expect(result).toBe('1,000.99');
    });

    it('should default to English locale', () => {
      const result = formatNumber(1000);
      expect(result).toBe('1,000');
    });
  });

  describe('generateId', () => {
    it('should generate a string ID', () => {
      const id = generateId();
      expect(typeof id).toBe('string');
      expect(id.length).toBeGreaterThan(0);
    });

    it('should generate unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
    });

    it('should generate ID with specified prefix', () => {
      const id = generateId('test');
      expect(id).toMatch(/^test_/);
    });

    it('should generate ID without prefix', () => {
      const id = generateId();
      expect(id).not.toMatch(/^_/);
    });
  });

  describe('debounce', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should debounce function calls', () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 300);

      debouncedFn();
      debouncedFn();
      debouncedFn();

      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(300);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should pass arguments correctly', () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 300);

      debouncedFn('test', 123);
      jest.advanceTimersByTime(300);

      expect(mockFn).toHaveBeenCalledWith('test', 123);
    });

    it('should reset timer on subsequent calls', () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 300);

      debouncedFn();
      jest.advanceTimersByTime(200);
      debouncedFn(); // Should reset timer
      jest.advanceTimersByTime(200);

      expect(mockFn).not.toHaveBeenCalled();
      
      jest.advanceTimersByTime(100);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });
  });

  describe('throttle', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should throttle function calls', () => {
      const mockFn = jest.fn();
      const throttledFn = throttle(mockFn, 300);

      throttledFn();
      throttledFn();
      throttledFn();

      expect(mockFn).toHaveBeenCalledTimes(1);

      jest.advanceTimersByTime(300);
      throttledFn();
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('should pass arguments from first call', () => {
      const mockFn = jest.fn();
      const throttledFn = throttle(mockFn, 300);

      throttledFn('first', 1);
      throttledFn('second', 2);

      expect(mockFn).toHaveBeenCalledWith('first', 1);
    });
  });

  describe('isMobile', () => {
    it('should return true for mobile width', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 500,
      });
      
      expect(isMobile()).toBe(true);
    });

    it('should return false for desktop width', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1024,
      });
      
      expect(isMobile()).toBe(false);
    });
  });

  describe('isTouchDevice', () => {
    it('should detect touch support', () => {
      Object.defineProperty(window, 'ontouchstart', {
        value: true,
        configurable: true,
      });
      
      expect(isTouchDevice()).toBe(true);
    });

    it('should detect no touch support', () => {
      delete (window as any).ontouchstart;
      Object.defineProperty(navigator, 'maxTouchPoints', {
        writable: true,
        configurable: true,
        value: 0,
      });
      
      expect(isTouchDevice()).toBe(false);
    });
  });

  describe('getBrowserLanguage', () => {
    it('should return ar for Arabic languages', () => {
      Object.defineProperty(navigator, 'language', {
        writable: true,
        configurable: true,
        value: 'ar-SA',
      });
      
      expect(getBrowserLanguage()).toBe('ar');
    });

    it('should return en for English languages', () => {
      Object.defineProperty(navigator, 'language', {
        writable: true,
        configurable: true,
        value: 'en-US',
      });
      
      expect(getBrowserLanguage()).toBe('en');
    });

    it('should default to en for unknown languages', () => {
      Object.defineProperty(navigator, 'language', {
        writable: true,
        configurable: true,
        value: 'fr-FR',
      });
      
      expect(getBrowserLanguage()).toBe('en');
    });
  });
});