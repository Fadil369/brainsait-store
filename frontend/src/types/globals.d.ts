// Global type definitions for the BrainSAIT Store frontend
/* eslint-disable no-unused-vars */

declare global {
  // Window object extensions
  interface Window {
    StoreKit?: {
      initialize: (_config: { storefront: string; language: string }) => Promise<void>;
      requestReview: () => Promise<void>;
      showProductPage: (_config: { productIdentifier: string }) => Promise<void>;
    };
    ApplePaySession?: {
      new (_version: number, _paymentRequest: any): any;
      canMakePaymentsWithActiveCard: (_merchantId: string) => Promise<boolean>;
      STATUS_SUCCESS: number;
      STATUS_FAILURE: number;
    };
  }

  // Fetch API types
  interface RequestInit {
    method?: string;
    headers?: Record<string, string> | Headers;
    body?: string | FormData | Blob;
    credentials?: 'omit' | 'same-origin' | 'include';
    cache?: 'default' | 'no-store' | 'reload' | 'no-cache' | 'force-cache' | 'only-if-cached';
    redirect?: 'follow' | 'error' | 'manual';
    referrer?: string;
    referrerPolicy?: 'no-referrer' | 'no-referrer-when-downgrade' | 'origin' | 'origin-when-cross-origin' | 'same-origin' | 'strict-origin' | 'strict-origin-when-cross-origin' | 'unsafe-url';
    integrity?: string;
    keepalive?: boolean;
    signal?: AbortSignal;
  }

  interface HeadersInit {
    [key: string]: string;
  }

  // Node.js types for browser environment
  namespace NodeJS {
    interface Timeout extends ReturnType<typeof setTimeout> {}
  }
}

export {};