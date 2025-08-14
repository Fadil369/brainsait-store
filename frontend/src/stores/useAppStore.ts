import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Language } from '@/types';

interface AppState {
  // Language and localization
  language: Language;
  isRTL: boolean;
  
  // UI state
  isMobileMenuOpen: boolean;
  theme: 'dark' | 'light';
  
  // Notification system
  notifications: Array<{
    id: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
  }>;
  
  // Loading states
  isLoading: boolean;
  loadingMessage?: string;
  
  // Actions
  setLanguage: (language: Language) => void;
  toggleMobileMenu: () => void;
  closeMobileMenu: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
  addNotification: (notification: Omit<AppState['notifications'][0], 'id'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  setLoading: (isLoading: boolean, message?: string) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      language: 'en',
      isRTL: false,
      isMobileMenuOpen: false,
      theme: 'dark',
      notifications: [],
      isLoading: false,
      loadingMessage: undefined,
      
      // Actions
      setLanguage: (language: Language) => {
        const isRTL = language === 'ar';
        
        set({ language, isRTL });
        
        // Update document attributes for proper RTL support
        if (typeof document !== 'undefined') {
          document.documentElement.setAttribute('lang', language);
          document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
          
          // Update font family for Arabic
          if (isRTL) {
            document.body.style.fontFamily = "'Noto Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
          } else {
            document.body.style.fontFamily = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', 'Noto Sans Arabic', Roboto, Oxygen, Ubuntu, sans-serif";
          }
        }
      },
      
      toggleMobileMenu: () => {
        set((state) => ({ isMobileMenuOpen: !state.isMobileMenuOpen }));
      },
      
      closeMobileMenu: () => {
        set({ isMobileMenuOpen: false });
      },
      
      setTheme: (theme: 'dark' | 'light') => {
        set({ theme });
        
        // Update document class for theme switching
        if (typeof document !== 'undefined') {
          if (theme === 'dark') {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
        }
      },
      
      addNotification: (notification) => {
        const id = Math.random().toString(36).substr(2, 9);
        const newNotification = { ...notification, id };
        
        set((state) => ({
          notifications: [...state.notifications, newNotification]
        }));
        
        // Auto-remove notification after duration (default 5 seconds)
        const duration = notification.duration || 5000;
        setTimeout(() => {
          get().removeNotification(id);
        }, duration);
      },
      
      removeNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }));
      },
      
      clearNotifications: () => {
        set({ notifications: [] });
      },
      
      setLoading: (isLoading: boolean, message?: string) => {
        set({ isLoading, loadingMessage: message });
      },
    }),
    {
      name: 'brainsait-app-store',
      partialize: (state) => ({
        language: state.language,
        isRTL: state.isRTL,
        theme: state.theme,
      }),
    }
  )
);

// Selector hooks for optimized re-renders
export const useLanguage = () => useAppStore((state) => state.language);
export const useIsRTL = () => useAppStore((state) => state.isRTL);
export const useTheme = () => useAppStore((state) => state.theme);
export const useIsMobileMenuOpen = () => useAppStore((state) => state.isMobileMenuOpen);
export const useNotifications = () => useAppStore((state) => state.notifications);
export const useIsLoading = () => useAppStore((state) => ({ 
  isLoading: state.isLoading, 
  message: state.loadingMessage 
}));