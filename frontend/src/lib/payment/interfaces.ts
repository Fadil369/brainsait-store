// Base payment provider interface for DRY abstraction
export interface PaymentMethod {
  id: string;
  name: string;
  name_ar: string;
  description: string;
  description_ar: string;
  supported_currencies: string[];
  fees: {
    percentage: number;
    fixed: number;
  };
  enabled: boolean;
  logo_url: string;
}

export interface PaymentIntent {
  payment_intent_id: string;
  client_secret?: string;
  redirect_url?: string;
  checkout_url?: string;
  amount: number;
  currency: string;
  status: string;
  mobile_verification?: boolean;
}

export interface PaymentResult {
  success: boolean;
  payment_intent_id?: string;
  error?: string;
  redirect_url?: string;
}

// Base payment provider interface
export interface IPaymentProvider {
  readonly id: string;
  readonly name: string;

  // Core payment operations
  createPayment(orderId: string, amount: number, options?: any): Promise<PaymentIntent>;
  confirmPayment(paymentIntentId: string, paymentData?: any): Promise<PaymentResult>;
  getPaymentStatus(paymentIntentId: string): Promise<{ status: string; orderId?: string }>;
  
  // Provider-specific initialization
  initialize(config?: any): Promise<void>;
  isAvailable(): Promise<boolean>;
  
  // Validation
  validatePaymentData(data: any): boolean;
}

// Payment configuration factory
export interface PaymentProviderConfig {
  apiKey?: string;
  environment?: 'live' | 'sandbox';
  webhookSecret?: string;
  returnUrl?: string;
  cancelUrl?: string;
  [key: string]: any;
}

// Factory for creating consistent payment method definitions
export class PaymentMethodFactory {
  static createPaymentMethod(
    id: string,
    name: string,
    name_ar: string,
    description: string,
    description_ar: string,
    options: Partial<Omit<PaymentMethod, 'id' | 'name' | 'name_ar' | 'description' | 'description_ar'>>
  ): PaymentMethod {
    return {
      id,
      name,
      name_ar,
      description,
      description_ar,
      supported_currencies: options.supported_currencies || ['SAR'],
      fees: options.fees || { percentage: 0, fixed: 0 },
      enabled: options.enabled ?? true,
      logo_url: options.logo_url || `/payment-logos/${id}.svg`,
    };
  }

  // Pre-defined payment methods for consistency
  static getStripeMethod(): PaymentMethod {
    return this.createPaymentMethod(
      'stripe',
      'Credit/Debit Cards',
      'البطاقات الائتمانية/المدينة',
      'Visa, Mastercard, American Express, Apple Pay',
      'فيزا، ماستركارد، أمريكان إكسبريس، أبل باي',
      {
        supported_currencies: ['SAR', 'USD', 'EUR'],
        fees: { percentage: 2.9, fixed: 0 },
      }
    );
  }

  static getPayPalMethod(): PaymentMethod {
    return this.createPaymentMethod(
      'paypal',
      'PayPal',
      'باي بال',
      'PayPal, Credit Cards, Bank Transfer',
      'باي بال، البطاقات الائتمانية، تحويل بنكي',
      {
        supported_currencies: ['SAR', 'USD', 'EUR'],
        fees: { percentage: 3.4, fixed: 0 },
      }
    );
  }

  static getApplePayMethod(): PaymentMethod {
    return this.createPaymentMethod(
      'apple_pay',
      'Apple Pay',
      'أبل باي',
      'Touch ID, Face ID, Apple Watch',
      'بصمة الإصبع، التعرف على الوجه، ساعة أبل',
      {
        supported_currencies: ['SAR', 'USD', 'EUR'],
        fees: { percentage: 2.9, fixed: 0 },
      }
    );
  }

  static getMadaMethod(): PaymentMethod {
    return this.createPaymentMethod(
      'mada',
      'Mada Cards',
      'بطاقات مدى',
      'Saudi domestic debit cards',
      'البطاقات المدينة السعودية المحلية',
      {
        supported_currencies: ['SAR'],
        fees: { percentage: 1.5, fixed: 0 },
      }
    );
  }

  static getSTCPayMethod(): PaymentMethod {
    return this.createPaymentMethod(
      'stc_pay',
      'STC Pay',
      'STC Pay',
      'Mobile wallet payment',
      'دفع عبر المحفظة الرقمية',
      {
        supported_currencies: ['SAR'],
        fees: { percentage: 1.0, fixed: 0 },
      }
    );
  }

  static getAllDefaultMethods(): Record<string, PaymentMethod> {
    return {
      stripe: this.getStripeMethod(),
      paypal: this.getPayPalMethod(),
      apple_pay: this.getApplePayMethod(),
      mada: this.getMadaMethod(),
      stc_pay: this.getSTCPayMethod(),
    };
  }
}

// Base HTTP payment provider with common fetch patterns
export abstract class BaseHttpPaymentProvider implements IPaymentProvider {
  abstract readonly id: string;
  abstract readonly name: string;
  
  protected config: PaymentProviderConfig;
  protected baseUrl: string;

  constructor(config: PaymentProviderConfig) {
    this.config = config;
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  }

  // Common HTTP request pattern
  protected async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST',
    data?: any
  ): Promise<T> {
    const url = `${this.baseUrl}/payments/${this.id}/${endpoint}`;
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      ...(data && { body: JSON.stringify(data) }),
    });

    if (!response.ok) {
      throw new Error(`${this.name} payment failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Default implementations that can be overridden
  async createPayment(orderId: string, amount: number, options?: any): Promise<PaymentIntent> {
    return this.makeRequest<PaymentIntent>('intent', 'POST', {
      order_id: orderId,
      amount,
      ...options,
    });
  }

  async getPaymentStatus(paymentIntentId: string): Promise<{ status: string; orderId?: string }> {
    return this.makeRequest(`status/${paymentIntentId}`, 'GET');
  }

  // Abstract methods that must be implemented
  abstract initialize(config?: any): Promise<void>;
  abstract isAvailable(): Promise<boolean>;
  abstract confirmPayment(paymentIntentId: string, paymentData?: any): Promise<PaymentResult>;
  abstract validatePaymentData(data: any): boolean;
}

// Utility functions for common payment operations
export class PaymentUtils {
  static formatCurrency(amount: number, currency: string = 'SAR', locale: string = 'en'): string {
    const localeCode = locale === 'ar' ? 'ar-SA' : 'en-US';
    return new Intl.NumberFormat(localeCode, {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
    }).format(amount);
  }

  static validateSaudiMobile(mobile: string): boolean {
    return /^\+966[5][0-9]{8}$/.test(mobile.replace(/\s|-/g, ''));
  }

  static generateReturnUrl(successPath: string = '/payment/success'): string {
    return `${window.location.origin}${successPath}`;
  }

  static generateCancelUrl(cancelPath: string = '/payment/cancel'): string {
    return `${window.location.origin}${cancelPath}`;
  }
}