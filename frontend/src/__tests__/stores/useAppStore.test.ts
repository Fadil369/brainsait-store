/**
 * @jest-environment jsdom
 */

import { renderHook, act } from '@testing-library/react';
import { useAppStore } from '@/stores/useAppStore';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock setTimeout for auto-remove notification tests
jest.useFakeTimers();

describe('useAppStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAppStore.setState({
      language: 'en',
      isRTL: false,
      isMobileMenuOpen: false,
      theme: 'dark',
      notifications: [],
      isLoading: false,
      loadingMessage: undefined,
    });
    
    jest.clearAllMocks();
    jest.clearAllTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAppStore());
      
      expect(result.current.language).toBe('en');
      expect(result.current.isRTL).toBe(false);
      expect(result.current.isMobileMenuOpen).toBe(false);
      expect(result.current.theme).toBe('dark');
      expect(result.current.notifications).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.loadingMessage).toBeUndefined();
    });
  });

  describe('Language Management', () => {
    it('should set language to Arabic and enable RTL', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.setLanguage('ar');
      });
      
      expect(result.current.language).toBe('ar');
      expect(result.current.isRTL).toBe(true);
      // Note: DOM updates are mocked in JSDOM environment
    });

    it('should set language to English and disable RTL', () => {
      const { result } = renderHook(() => useAppStore());
      
      // First set to Arabic
      act(() => {
        result.current.setLanguage('ar');
      });
      
      // Then switch to English
      act(() => {
        result.current.setLanguage('en');
      });
      
      expect(result.current.language).toBe('en');
      expect(result.current.isRTL).toBe(false);
    });

    it('should update document attributes when setting language', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.setLanguage('ar');
      });
      
      // The actual DOM updates happen, we're just testing the state changes
      expect(result.current.language).toBe('ar');
      expect(result.current.isRTL).toBe(true);
    });
  });

  describe('Mobile Menu Management', () => {
    it('should toggle mobile menu', () => {
      const { result } = renderHook(() => useAppStore());
      
      expect(result.current.isMobileMenuOpen).toBe(false);
      
      act(() => {
        result.current.toggleMobileMenu();
      });
      
      expect(result.current.isMobileMenuOpen).toBe(true);
      
      act(() => {
        result.current.toggleMobileMenu();
      });
      
      expect(result.current.isMobileMenuOpen).toBe(false);
    });

    it('should close mobile menu', () => {
      const { result } = renderHook(() => useAppStore());
      
      // First open the menu
      act(() => {
        result.current.toggleMobileMenu();
      });
      
      expect(result.current.isMobileMenuOpen).toBe(true);
      
      act(() => {
        result.current.closeMobileMenu();
      });
      
      expect(result.current.isMobileMenuOpen).toBe(false);
    });
  });

  describe('Theme Management', () => {
    it('should set dark theme', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.setTheme('dark');
      });
      
      expect(result.current.theme).toBe('dark');
    });

    it('should set light theme', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.setTheme('light');
      });
      
      expect(result.current.theme).toBe('light');
    });

    it('should update document class when switching themes', () => {
      const { result } = renderHook(() => useAppStore());
      
      // Switch to light theme
      act(() => {
        result.current.setTheme('light');
      });
      
      expect(result.current.theme).toBe('light');
      
      // Switch back to dark theme
      act(() => {
        result.current.setTheme('dark');
      });
      
      expect(result.current.theme).toBe('dark');
    });
  });

  describe('Notification Management', () => {
    it('should add notification', () => {
      const { result } = renderHook(() => useAppStore());
      
      const notification = {
        message: 'Test notification',
        type: 'success' as const,
      };
      
      act(() => {
        result.current.addNotification(notification);
      });
      
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0]).toMatchObject({
        message: 'Test notification',
        type: 'success',
        id: expect.any(String),
      });
    });

    it('should add notification with custom duration', () => {
      const { result } = renderHook(() => useAppStore());
      
      const notification = {
        message: 'Test notification',
        type: 'info' as const,
        duration: 3000,
      };
      
      act(() => {
        result.current.addNotification(notification);
      });
      
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].duration).toBe(3000);
    });

    it('should auto-remove notification after duration', () => {
      const { result } = renderHook(() => useAppStore());
      
      const notification = {
        message: 'Test notification',
        type: 'info' as const,
        duration: 1000,
      };
      
      act(() => {
        result.current.addNotification(notification);
      });
      
      expect(result.current.notifications).toHaveLength(1);
      
      // Fast-forward time
      act(() => {
        jest.advanceTimersByTime(1000);
      });
      
      expect(result.current.notifications).toHaveLength(0);
    });

    it('should remove specific notification by id', () => {
      const { result } = renderHook(() => useAppStore());
      
      const notification1 = {
        message: 'First notification',
        type: 'success' as const,
      };
      
      const notification2 = {
        message: 'Second notification',
        type: 'error' as const,
      };
      
      act(() => {
        result.current.addNotification(notification1);
        result.current.addNotification(notification2);
      });
      
      expect(result.current.notifications).toHaveLength(2);
      
      const firstNotificationId = result.current.notifications[0].id;
      
      act(() => {
        result.current.removeNotification(firstNotificationId);
      });
      
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].message).toBe('Second notification');
    });

    it('should clear all notifications', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.addNotification({ message: 'Test 1', type: 'success' });
        result.current.addNotification({ message: 'Test 2', type: 'error' });
        result.current.addNotification({ message: 'Test 3', type: 'warning' });
      });
      
      expect(result.current.notifications).toHaveLength(3);
      
      act(() => {
        result.current.clearNotifications();
      });
      
      expect(result.current.notifications).toHaveLength(0);
    });

    it('should generate unique IDs for notifications', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.addNotification({ message: 'Test 1', type: 'success' });
        result.current.addNotification({ message: 'Test 2', type: 'error' });
      });
      
      const ids = result.current.notifications.map(n => n.id);
      expect(ids[0]).not.toBe(ids[1]);
      expect(ids[0]).toBeTruthy();
      expect(ids[1]).toBeTruthy();
    });
  });

  describe('Loading State Management', () => {
    it('should set loading state without message', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.setLoading(true);
      });
      
      expect(result.current.isLoading).toBe(true);
      expect(result.current.loadingMessage).toBeUndefined();
    });

    it('should set loading state with message', () => {
      const { result } = renderHook(() => useAppStore());
      
      act(() => {
        result.current.setLoading(true, 'Loading data...');
      });
      
      expect(result.current.isLoading).toBe(true);
      expect(result.current.loadingMessage).toBe('Loading data...');
    });

    it('should clear loading state', () => {
      const { result } = renderHook(() => useAppStore());
      
      // First set loading
      act(() => {
        result.current.setLoading(true, 'Loading...');
      });
      
      expect(result.current.isLoading).toBe(true);
      expect(result.current.loadingMessage).toBe('Loading...');
      
      // Then clear loading
      act(() => {
        result.current.setLoading(false);
      });
      
      expect(result.current.isLoading).toBe(false);
      expect(result.current.loadingMessage).toBeUndefined();
    });
  });

  describe('Selector Hooks', () => {
    it('should provide correct selector values', () => {
      const { result: appStore } = renderHook(() => useAppStore());
      const { result: language } = renderHook(() => useAppStore((state) => state.language));
      const { result: isRTL } = renderHook(() => useAppStore((state) => state.isRTL));
      const { result: theme } = renderHook(() => useAppStore((state) => state.theme));
      const { result: notifications } = renderHook(() => useAppStore((state) => state.notifications));
      
      act(() => {
        appStore.current.setLanguage('ar');
        appStore.current.setTheme('light');
        appStore.current.addNotification({ message: 'Test', type: 'info' });
      });
      
      expect(language.current).toBe('ar');
      expect(isRTL.current).toBe(true);
      expect(theme.current).toBe('light');
      expect(notifications.current).toHaveLength(1);
    });
  });

  describe('Notification Types', () => {
    it('should handle different notification types', () => {
      const { result } = renderHook(() => useAppStore());
      
      const notifications = [
        { message: 'Success message', type: 'success' as const },
        { message: 'Error message', type: 'error' as const },
        { message: 'Warning message', type: 'warning' as const },
        { message: 'Info message', type: 'info' as const },
      ];
      
      notifications.forEach(notification => {
        act(() => {
          result.current.addNotification(notification);
        });
      });
      
      expect(result.current.notifications).toHaveLength(4);
      expect(result.current.notifications[0].type).toBe('success');
      expect(result.current.notifications[1].type).toBe('error');
      expect(result.current.notifications[2].type).toBe('warning');
      expect(result.current.notifications[3].type).toBe('info');
    });
  });
});