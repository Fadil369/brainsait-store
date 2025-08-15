/**
 * BrainSAIT Payment Integration Service - Refactored with DRY principles
 * Supports Stripe, PayPal, Apple Pay, and Saudi local gateways
 */

import { PaymentMethodFactory, PaymentMethod, PaymentIntent, IPaymentProvider, PaymentUtils } from './interfaces';
import { PaymentProviderFactory } from './providers';

// Re-export types for backward compatibility
export type { PaymentMethod, PaymentIntent };

// Order and item interfaces
export interface Order {
  id: string;
  total_amount: number;
  currency: string;
  customer_email: string;
  items: OrderItem[];
}

export interface OrderItem {
  product_id: number;
  product_name: string;
  license_type: 'app_only' | 'app_with_source' | 'enterprise';
  quantity: number;
  price: number;
  includes_source_code: boolean;
  support_months: number;
}

// Main payment service with improved abstraction
export class PaymentService {
  private static instance: PaymentService;
  private providers: Map<string, IPaymentProvider> = new Map();
  private availableProviders: Set<string> = new Set();

  private constructor() {}

  public static getInstance(): PaymentService {
    if (!PaymentService.instance) {
      PaymentService.instance = new PaymentService();
    }
    return PaymentService.instance;
  }

  // Initialize all payment providers
  async initialize(): Promise<void> {
    const allProviders = PaymentProviderFactory.getAllProviders();
    
    for (const provider of allProviders) {
      try {
        await provider.initialize();
        if (await provider.isAvailable()) {
          this.providers.set(provider.id, provider);
          this.availableProviders.add(provider.id);
        }
      } catch (error) {
        console.warn(`Failed to initialize ${provider.name} provider:`, error);
      }
    }
  }

  // Get available payment methods with consistent structure
  async getPaymentMethods(): Promise<Record<string, PaymentMethod>> {
    try {
      // Try to fetch from API first
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/payments/methods`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to fetch payment methods from API:', error);
    }

    // Fallback to default methods, filtered by available providers
    const allMethods = PaymentMethodFactory.getAllDefaultMethods();
    const availableMethods: Record<string, PaymentMethod> = {};

    for (const [id, method] of Object.entries(allMethods)) {
      if (this.availableProviders.has(id)) {
        availableMethods[id] = method;
      }
    }

    return availableMethods;
  }

  // Generic payment creation using provider pattern
  async createPayment(
    providerId: string,
    orderId: string,
    amount: number,
    options?: any
  ): Promise<PaymentIntent> {
    const provider = this.providers.get(providerId);
    if (!provider) {
      throw new Error(`Payment provider ${providerId} not available`);
    }

    if (!provider.validatePaymentData(options || {})) {
      throw new Error(`Invalid payment data for ${provider.name}`);
    }

    return provider.createPayment(orderId, amount, options);
  }

  // Generic payment confirmation
  async confirmPayment(
    providerId: string,
    paymentIntentId: string,
    paymentData?: any
  ): Promise<any> {
    const provider = this.providers.get(providerId);
    if (!provider) {
      throw new Error(`Payment provider ${providerId} not available`);
    }

    return provider.confirmPayment(paymentIntentId, paymentData);
  }

  // Get payment status
  async getPaymentStatus(providerId: string, paymentIntentId: string): Promise<any> {
    const provider = this.providers.get(providerId);
    if (!provider) {
      throw new Error(`Payment provider ${providerId} not available`);
    }

    return provider.getPaymentStatus(paymentIntentId);
  }

  // Convenience methods for backward compatibility
  async createStripePayment(orderId: string, returnUrl?: string): Promise<PaymentIntent> {
    return this.createPayment('stripe', orderId, 0, {
      return_url: returnUrl || PaymentUtils.generateReturnUrl(),
      cancel_url: PaymentUtils.generateCancelUrl(),
    });
  }

  async confirmStripePayment(clientSecret: string, paymentMethod?: any): Promise<any> {
    return this.confirmPayment('stripe', clientSecret, paymentMethod);
  }

  async createPayPalOrder(orderId: string): Promise<PaymentIntent> {
    return this.createPayment('paypal', orderId, 0);
  }

  async renderPayPalButtons(containerId: string, orderId: string): Promise<void> {
    const provider = this.providers.get('paypal') as any;
    if (provider && provider.renderButtons) {
      await provider.renderButtons(containerId, orderId);
    } else {
      throw new Error('PayPal provider not available or does not support button rendering');
    }
  }

  async isApplePayAvailable(): Promise<boolean> {
    const provider = this.providers.get('apple_pay');
    return provider ? provider.isAvailable() : false;
  }

  async processApplePayPayment(orderId: string): Promise<void> {
    const result = await this.confirmPayment('apple_pay', orderId);
    if (result.success) {
      window.location.href = `/payment/success?orderId=${orderId}`;
    } else {
      throw new Error(result.error || 'Apple Pay payment failed');
    }
  }

  async createMadaPayment(orderId: string, customerData: any): Promise<PaymentIntent> {
    return this.createPayment('mada', orderId, 0, {
      customer_name: customerData.name,
      customer_phone: customerData.phone,
      return_url: PaymentUtils.generateReturnUrl(),
    });
  }

  async createSTCPayPayment(orderId: string, mobileNumber: string): Promise<PaymentIntent> {
    return this.createPayment('stc_pay', orderId, 0, {
      mobile_number: mobileNumber,
    });
  }

  // Product management methods (could be moved to separate service)
  async syncProductsToStripe(): Promise<any> {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/payments/stripe/products/sync`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('access_token') : ''}`,
      },
    });

    if (!response.ok) throw new Error('Failed to sync products to Stripe');
    return response.json();
  }

  async createStripePaymentLink(productIds: number[], metadata?: any): Promise<any> {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/payments/stripe/payment-link`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('access_token') : ''}`,
      },
      body: JSON.stringify({
        product_ids: productIds,
        metadata: metadata || {},
      }),
    });

    if (!response.ok) throw new Error('Failed to create payment link');
    return response.json();
  }

  // Utility methods using the new PaymentUtils
  formatCurrency(amount: number, currency: string = 'SAR', locale: string = 'en'): string {
    return PaymentUtils.formatCurrency(amount, currency, locale);
  }

  validatePaymentData(paymentMethod: string, data: any): boolean {
    const provider = this.providers.get(paymentMethod);
    return provider ? provider.validatePaymentData(data) : false;
  }

  // Provider management
  getAvailableProviders(): string[] {
    return Array.from(this.availableProviders);
  }

  isProviderAvailable(providerId: string): boolean {
    return this.availableProviders.has(providerId);
  }
}

// Global payment service instance
export const paymentService = PaymentService.getInstance();

// Export for React components
export default paymentService;
