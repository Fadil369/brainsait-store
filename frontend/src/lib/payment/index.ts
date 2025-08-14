/**
 * BrainSAIT Payment Integration Service
 * Supports Stripe, PayPal, Apple Pay, and Saudi local gateways
 */

import { loadStripe, Stripe } from '@stripe/stripe-js';
import { loadScript } from '@paypal/paypal-js';

// Types
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

// Environment Configuration
const config = {
  stripe: {
    publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!,
  },
  paypal: {
    clientId: process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID!,
    environment: process.env.NEXT_PUBLIC_PAYPAL_ENVIRONMENT as 'live' | 'sandbox',
    currency: process.env.NEXT_PUBLIC_PAYPAL_CURRENCY || 'SAR',
  },
  applePay: {
    merchantId: process.env.NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID!,
    displayName: process.env.NEXT_PUBLIC_APPLE_PAY_DISPLAY_NAME || 'BrainSAIT Solutions',
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
};

// Stripe Integration
let stripePromise: Promise<Stripe | null>;

export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(config.stripe.publishableKey);
  }
  return stripePromise;
};

export class PaymentService {
  private static instance: PaymentService;
  private stripe: Stripe | null = null;
  private paypal: any = null;

  private constructor() {}

  public static getInstance(): PaymentService {
    if (!PaymentService.instance) {
      PaymentService.instance = new PaymentService();
    }
    return PaymentService.instance;
  }

  // Initialize payment services
  async initialize() {
    try {
      // Initialize Stripe
      this.stripe = await getStripe();
      
      // Initialize PayPal
      this.paypal = await loadScript({
        'client-id': config.paypal.clientId,
        currency: config.paypal.currency,
        intent: 'capture',
        'enable-funding': 'venmo,paylater',
        'disable-funding': 'card',
        'data-client-token': undefined,
      });

      // Payment services initialized successfully
    } catch (error) {
      // Failed to initialize payment services
      throw error;
    }
  }

  // Get available payment methods
  async getPaymentMethods(): Promise<Record<string, PaymentMethod>> {
    try {
      const response = await fetch(`${config.api.baseUrl}/payments/methods`);
      if (!response.ok) throw new Error('Failed to fetch payment methods');
      return await response.json();
    } catch (error) {
      // console.error('Error fetching payment methods:', error);
      // Return default methods if API fails
      return this.getDefaultPaymentMethods();
    }
  }

  private getDefaultPaymentMethods(): Record<string, PaymentMethod> {
    return {
      stripe: {
        id: 'stripe',
        name: 'Credit/Debit Cards',
        name_ar: 'البطاقات الائتمانية/المدينة',
        description: 'Visa, Mastercard, American Express, Apple Pay',
        description_ar: 'فيزا، ماستركارد، أمريكان إكسبريس، أبل باي',
        supported_currencies: ['SAR', 'USD', 'EUR'],
        fees: { percentage: 2.9, fixed: 0 },
        enabled: true,
        logo_url: '/payment-logos/stripe.svg',
      },
      paypal: {
        id: 'paypal',
        name: 'PayPal',
        name_ar: 'باي بال',
        description: 'PayPal, Credit Cards, Bank Transfer',
        description_ar: 'باي بال، البطاقات الائتمانية، تحويل بنكي',
        supported_currencies: ['SAR', 'USD', 'EUR'],
        fees: { percentage: 3.4, fixed: 0 },
        enabled: true,
        logo_url: '/payment-logos/paypal.svg',
      },
      apple_pay: {
        id: 'apple_pay',
        name: 'Apple Pay',
        name_ar: 'أبل باي',
        description: 'Touch ID, Face ID, Apple Watch',
        description_ar: 'بصمة الإصبع، التعرف على الوجه، ساعة أبل',
        supported_currencies: ['SAR', 'USD', 'EUR'],
        fees: { percentage: 2.9, fixed: 0 },
        enabled: true,
        logo_url: '/payment-logos/apple-pay.svg',
      },
      mada: {
        id: 'mada',
        name: 'Mada Cards',
        name_ar: 'بطاقات مدى',
        description: 'Saudi domestic debit cards',
        description_ar: 'البطاقات المدينة السعودية المحلية',
        supported_currencies: ['SAR'],
        fees: { percentage: 1.5, fixed: 0 },
        enabled: true,
        logo_url: '/payment-logos/mada.svg',
      },
      stc_pay: {
        id: 'stc_pay',
        name: 'STC Pay',
        name_ar: 'STC Pay',
        description: 'Mobile wallet payment',
        description_ar: 'دفع عبر المحفظة الرقمية',
        supported_currencies: ['SAR'],
        fees: { percentage: 1.0, fixed: 0 },
        enabled: true,
        logo_url: '/payment-logos/stc-pay.svg',
      },
    };
  }

  // Stripe Payment Processing
  async createStripePayment(orderId: string, returnUrl?: string): Promise<PaymentIntent> {
    try {
      const response = await fetch(`${config.api.baseUrl}/payments/stripe/intent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          order_id: orderId,
          return_url: returnUrl || `${window.location.origin}/payment/success`,
          cancel_url: `${window.location.origin}/payment/cancel`,
        }),
      });

      if (!response.ok) throw new Error('Failed to create Stripe payment');
      return await response.json();
    } catch (error) {
      // console.error('Stripe payment creation failed:', error);
      throw error;
    }
  }

  async confirmStripePayment(clientSecret: string, paymentMethod?: any): Promise<any> {
    if (!this.stripe) throw new Error('Stripe not initialized');

    try {
      const result = await this.stripe.confirmPayment({
        clientSecret,
        confirmParams: {
          return_url: `${window.location.origin}/payment/success`,
        },
        ...(paymentMethod && { payment_method: paymentMethod }),
      });

      return result;
    } catch (error) {
      // console.error('Stripe payment confirmation failed:', error);
      throw error;
    }
  }

  // PayPal Payment Processing
  async createPayPalOrder(orderId: string): Promise<PaymentIntent> {
    try {
      const response = await fetch(`${config.api.baseUrl}/payments/paypal/order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          order_id: orderId,
        }),
      });

      if (!response.ok) throw new Error('Failed to create PayPal order');
      return await response.json();
    } catch (error) {
      // console.error('PayPal order creation failed:', error);
      throw error;
    }
  }

  async renderPayPalButtons(containerId: string, orderId: string): Promise<void> {
    if (!this.paypal) {
      await this.initialize();
    }

    try {
      await this.paypal.Buttons({
        style: {
          layout: 'vertical',
          color: 'gold',
          shape: 'rect',
          label: 'paypal',
          height: 50,
        },
        createOrder: async () => {
          const payment = await this.createPayPalOrder(orderId);
          return payment.payment_intent_id;
        },
        onApprove: async (data: any) => {
          try {
            const response = await fetch(`${config.api.baseUrl}/payments/paypal/capture/${data.orderID}`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
              },
            });

            if (response.ok) {
              const result = await response.json();
              // Redirect to success page
              window.location.href = `/payment/success?orderId=${orderId}&captureId=${result.capture_id}`;
            } else {
              throw new Error('Payment capture failed');
            }
          } catch (error) {
            // console.error('PayPal capture error:', error);
            window.location.href = `/payment/error?error=${encodeURIComponent('Payment processing failed')}`;
          }
        },
        onError: (err: any) => {
          // console.error('PayPal error:', err);
          window.location.href = `/payment/error?error=${encodeURIComponent('PayPal payment failed')}`;
        },
      }).render(`#${containerId}`);
    } catch (error) {
      // console.error('PayPal button rendering failed:', error);
      throw error;
    }
  }

  // Apple Pay Processing
  async isApplePayAvailable(): Promise<boolean> {
    try {
      // Check if Apple Pay is available
      if (!window.ApplePaySession) return false;
      
      return await window.ApplePaySession.canMakePaymentsWithActiveCard(config.applePay.merchantId);
    } catch (error) {
      // console.error('Apple Pay availability check failed:', error);
      return false;
    }
  }

  async processApplePayPayment(orderId: string): Promise<void> {
    try {
      // Validate Apple Pay merchant
      const validationResponse = await fetch(`${config.api.baseUrl}/payments/apple-pay/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          validation_url: 'https://apple-pay-gateway-cert.apple.com/paymentservices/startSession',
          domain_name: window.location.hostname,
        }),
      });

      if (!validationResponse.ok) throw new Error('Apple Pay validation failed');

      // Create Apple Pay session
      const paymentRequest = {
        countryCode: 'SA',
        currencyCode: 'SAR',
        supportedNetworks: ['visa', 'masterCard', 'amex', 'mada'],
        merchantCapabilities: ['supports3DS'],
        total: {
          label: config.applePay.displayName,
          amount: '0.00', // Will be updated with actual amount
        },
      };

      const session = new window.ApplePaySession(3, paymentRequest);

      session.onvalidatemerchant = async (event: any) => {
        const validationData = await validationResponse.json();
        session.completeMerchantValidation(validationData);
      };

      session.onpaymentauthorized = async (event: any) => {
        try {
          const paymentResponse = await fetch(`${config.api.baseUrl}/payments/apple-pay/payment`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify({
              order_id: orderId,
              payment_token: event.payment.token,
            }),
          });

          if (paymentResponse.ok) {
            session.completePayment(window.ApplePaySession.STATUS_SUCCESS);
            window.location.href = `/payment/success?orderId=${orderId}`;
          } else {
            session.completePayment(window.ApplePaySession.STATUS_FAILURE);
          }
        } catch (error) {
          // console.error('Apple Pay processing error:', error);
          session.completePayment(window.ApplePaySession.STATUS_FAILURE);
        }
      };

      session.begin();
    } catch (error) {
      // console.error('Apple Pay initialization failed:', error);
      throw error;
    }
  }

  // Saudi Local Payment Methods
  async createMadaPayment(orderId: string, customerData: any): Promise<PaymentIntent> {
    try {
      const response = await fetch(`${config.api.baseUrl}/payments/mada/intent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          order_id: orderId,
          customer_name: customerData.name,
          customer_phone: customerData.phone,
          return_url: `${window.location.origin}/payment/success`,
        }),
      });

      if (!response.ok) throw new Error('Failed to create Mada payment');
      return await response.json();
    } catch (error) {
      // console.error('Mada payment creation failed:', error);
      throw error;
    }
  }

  async createSTCPayPayment(orderId: string, mobileNumber: string): Promise<PaymentIntent> {
    try {
      const response = await fetch(`${config.api.baseUrl}/payments/stc-pay/intent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          order_id: orderId,
          mobile_number: mobileNumber,
        }),
      });

      if (!response.ok) throw new Error('Failed to create STC Pay payment');
      return await response.json();
    } catch (error) {
      // console.error('STC Pay payment creation failed:', error);
      throw error;
    }
  }

  // Stripe Product Management
  async syncProductsToStripe(): Promise<any> {
    try {
      const response = await fetch(`${config.api.baseUrl}/payments/stripe/products/sync`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to sync products to Stripe');
      return await response.json();
    } catch (error) {
      // console.error('Stripe product sync failed:', error);
      throw error;
    }
  }

  async createStripePaymentLink(productIds: number[], metadata?: any): Promise<any> {
    try {
      const response = await fetch(`${config.api.baseUrl}/payments/stripe/payment-link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          product_ids: productIds,
          metadata: metadata || {},
        }),
      });

      if (!response.ok) throw new Error('Failed to create payment link');
      return await response.json();
    } catch (error) {
      // console.error('Payment link creation failed:', error);
      throw error;
    }
  }

  // Utility Methods
  formatCurrency(amount: number, currency: string = 'SAR'): string {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
    }).format(amount);
  }

  validatePaymentData(paymentMethod: string, data: any): boolean {
    switch (paymentMethod) {
      case 'stc_pay':
        return /^\+966[5][0-9]{8}$/.test(data.mobile_number);
      case 'mada':
        return data.customer_name && data.customer_phone;
      default:
        return true;
    }
  }
}

// Global payment service instance
export const paymentService = PaymentService.getInstance();

// Export for React components
export default paymentService;