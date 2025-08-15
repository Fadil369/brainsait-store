/**
 * App Store Connect Integration
 * Handles receipt validation and subscription management
 */

interface AppStoreProduct {
  product_id: string;
  name: string;
  description: string;
  price: string;
  type: 'subscription' | 'consumable' | 'non_consumable';
  duration?: string;
}

interface ReceiptValidationRequest {
  receipt_data: string;
  is_sandbox?: boolean;
}

interface ReceiptValidationResponse {
  verified: boolean;
  user_id: number;
  purchases: Array<{
    product_id: string;
    transaction_id: string;
    purchase_date: number;
    verified: boolean;
  }>;
  receipt_info: any;
}

interface PurchaseCompletionRequest {
  receipt_data: string;
  transaction_id: string;
  product_id: string;
}

export class AppStoreService {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000', apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey || '';
  }

  /**
   * Get available App Store products
   */
  async getProducts(): Promise<AppStoreProduct[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/app-store/products`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch products: ${response.statusText}`);
    }

    const result = await response.json();
    return result.data || [];
  }

  /**
   * Validate App Store receipt
   */
  async validateReceipt(request: ReceiptValidationRequest): Promise<ReceiptValidationResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/app-store/validate-receipt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Receipt validation failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result.data;
  }

  /**
   * Complete App Store purchase
   */
  async completePurchase(request: PurchaseCompletionRequest): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/app-store/purchase/complete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Purchase completion failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result.data;
  }

  /**
   * Get transaction information
   */
  async getTransactionInfo(transactionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/app-store/transaction-info`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({ transaction_id: transactionId }),
    });

    if (!response.ok) {
      throw new Error(`Transaction lookup failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result.data;
  }

  /**
   * Get subscription status
   */
  async getSubscriptionStatus(originalTransactionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/app-store/subscription-status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({ original_transaction_id: originalTransactionId }),
    });

    if (!response.ok) {
      throw new Error(`Subscription lookup failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result.data;
  }

  /**
   * Initialize App Store Kit (for iOS Safari)
   */
  async initializeStoreKit(): Promise<void> {
    if (typeof window === 'undefined') return;

    try {
      // Check if StoreKit is available
      if ('StoreKit' in window) {
        // Initialize StoreKit for web
        await (window as any).StoreKit.initialize({
          storefront: 'SAU', // Saudi Arabia storefront
          language: 'en-US',
        });
      }
    } catch (error) {
      // StoreKit not available or failed to initialize
    }
  }

  /**
   * Request App Store review (for iOS Safari)
   */
  async requestReview(): Promise<void> {
    if (typeof window === 'undefined') return;

    try {
      if ('StoreKit' in window) {
        await (window as any).StoreKit.requestReview();
      }
    } catch (error) {
      // Failed to request review
    }
  }

  /**
   * Show App Store product page (for iOS Safari)
   */
  async showProductPage(productId: string): Promise<void> {
    if (typeof window === 'undefined') return;

    try {
      if ('StoreKit' in window) {
        await (window as any).StoreKit.showProductPage({
          productIdentifier: productId,
        });
      } else {
        // Fallback to App Store URL
        const appStoreUrl = `https://apps.apple.com/sa/app/id${productId}`;
        window.open(appStoreUrl, '_blank');
      }
    } catch (error) {
      // Failed to show product page
    }
  }

  /**
   * Validate receipt from iOS app
   */
  async validateiOSReceipt(receiptData: string): Promise<ReceiptValidationResponse> {
    // Detect if running in sandbox mode
    const isSandbox = process.env.NODE_ENV === 'development' || 
                     window.location.hostname === 'localhost';

    return this.validateReceipt({
      receipt_data: receiptData,
      is_sandbox: isSandbox,
    });
  }

  /**
   * Handle purchase result from iOS
   */
  async handlePurchaseResult(transaction: any): Promise<any> {
    const receiptData = transaction.transactionReceipt;
    const transactionId = transaction.transactionIdentifier;
    const productId = transaction.productIdentifier;

    // First validate the receipt
    const validation = await this.validateiOSReceipt(receiptData);

    if (!validation.verified) {
      throw new Error('Receipt validation failed');
    }

    // Complete the purchase
    const completion = await this.completePurchase({
      receipt_data: receiptData,
      transaction_id: transactionId,
      product_id: productId,
    });

    return completion;
  }
}

// Export singleton instance
export const appStoreService = new AppStoreService();

// Add types to window for StoreKit
/* eslint-disable no-unused-vars */
declare global {
  interface Window {
    StoreKit?: any;
  }
}
/* eslint-enable no-unused-vars */