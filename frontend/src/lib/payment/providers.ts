import { BaseHttpPaymentProvider, IPaymentProvider, PaymentIntent, PaymentResult, PaymentUtils } from './interfaces';
import { loadStripe, Stripe } from '@stripe/stripe-js';

// Stripe provider implementation
export class StripePaymentProvider extends BaseHttpPaymentProvider {
  readonly id = 'stripe';
  readonly name = 'Stripe';
  
  private stripe: Stripe | null = null;

  async initialize(config?: any): Promise<void> {
    const publishableKey = config?.publishableKey || process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
    if (!publishableKey) {
      throw new Error('Stripe publishable key is required');
    }
    
    this.stripe = await loadStripe(publishableKey);
    if (!this.stripe) {
      throw new Error('Failed to load Stripe');
    }
  }

  async isAvailable(): Promise<boolean> {
    return this.stripe !== null;
  }

  async confirmPayment(clientSecret: string, paymentMethod?: any): Promise<PaymentResult> {
    if (!this.stripe) {
      throw new Error('Stripe not initialized');
    }

    const result = await this.stripe.confirmPayment({
      clientSecret,
      confirmParams: {
        return_url: PaymentUtils.generateReturnUrl(),
      },
      ...(paymentMethod && { payment_method: paymentMethod }),
    });

    return {
      success: !result.error,
      payment_intent_id: result.paymentIntent?.id,
      error: result.error?.message,
    };
  }

  validatePaymentData(data: any): boolean {
    // Basic validation for Stripe payments
    return true; // Stripe handles most validation
  }
}

// PayPal provider implementation  
export class PayPalPaymentProvider extends BaseHttpPaymentProvider {
  readonly id = 'paypal';
  readonly name = 'PayPal';
  
  private paypal: any = null;

  async initialize(config?: any): Promise<void> {
    const { loadScript } = await import('@paypal/paypal-js');
    
    this.paypal = await loadScript({
      clientId: config?.clientId || process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID!,
      currency: config?.currency || 'SAR',
      intent: 'capture',
      enableFunding: 'venmo,paylater',
      disableFunding: 'card',
    });
  }

  async isAvailable(): Promise<boolean> {
    return this.paypal !== null;
  }

  async confirmPayment(paymentIntentId: string): Promise<PaymentResult> {
    try {
      const result = await this.makeRequest<any>(`capture/${paymentIntentId}`, 'POST');
      return {
        success: true,
        payment_intent_id: result.capture_id,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async renderButtons(containerId: string, orderId: string): Promise<void> {
    if (!this.paypal) {
      await this.initialize();
    }

    await this.paypal.Buttons({
      style: {
        layout: 'vertical',
        color: 'gold',
        shape: 'rect',
        label: 'paypal',
        height: 50,
      },
      createOrder: async () => {
        const payment = await this.createPayment(orderId, 0); // Amount will be handled by backend
        return payment.payment_intent_id;
      },
      onApprove: async (data: any) => {
        try {
          const result = await this.confirmPayment(data.orderID);
          if (result.success) {
            window.location.href = `/payment/success?orderId=${orderId}&captureId=${result.payment_intent_id}`;
          } else {
            throw new Error('Payment capture failed');
          }
        } catch (error) {
          window.location.href = `/payment/error?error=${encodeURIComponent('Payment processing failed')}`;
        }
      },
      onError: () => {
        window.location.href = `/payment/error?error=${encodeURIComponent('PayPal payment failed')}`;
      },
    }).render(`#${containerId}`);
  }

  validatePaymentData(data: any): boolean {
    // PayPal handles validation internally
    return true;
  }
}

// Apple Pay provider implementation
export class ApplePayPaymentProvider extends BaseHttpPaymentProvider {
  readonly id = 'apple_pay';
  readonly name = 'Apple Pay';
  
  private merchantId: string;
  private displayName: string;

  constructor(config: any) {
    super(config);
    this.merchantId = config.merchantId || process.env.NEXT_PUBLIC_APPLE_PAY_MERCHANT_ID!;
    this.displayName = config.displayName || 'BrainSAIT Solutions';
  }

  async initialize(): Promise<void> {
    // Apple Pay doesn't require explicit initialization
  }

  async isAvailable(): Promise<boolean> {
    try {
      if (!(window as any).ApplePaySession) return false;
      return await (window as any).ApplePaySession.canMakePaymentsWithActiveCard(this.merchantId);
    } catch {
      return false;
    }
  }

  async confirmPayment(orderId: string): Promise<PaymentResult> {
    return new Promise((resolve, reject) => {
      // This would implement the full Apple Pay session flow
      const paymentRequest = {
        countryCode: 'SA',
        currencyCode: 'SAR',
        supportedNetworks: ['visa', 'masterCard', 'amex', 'mada'],
        merchantCapabilities: ['supports3DS'],
        total: {
          label: this.displayName,
          amount: '0.00', // Will be updated with actual amount
        },
      };

      const session = new (window as any).ApplePaySession(3, paymentRequest);

      session.onvalidatemerchant = async (event: any) => {
        try {
          const validationData = await this.makeRequest<any>('validate', 'POST', {
            validation_url: event.validationURL,
            domain_name: window.location.hostname,
          });
          session.completeMerchantValidation(validationData);
        } catch (error) {
          session.abort();
          reject(error);
        }
      };

      session.onpaymentauthorized = async (event: any) => {
        try {
          const result = await this.makeRequest<any>('payment', 'POST', {
            order_id: orderId,
            payment_token: event.payment.token,
          });

          if (result.success) {
            session.completePayment((window as any).ApplePaySession.STATUS_SUCCESS);
            resolve({
              success: true,
              payment_intent_id: result.payment_intent_id,
            });
          } else {
            session.completePayment((window as any).ApplePaySession.STATUS_FAILURE);
            resolve({
              success: false,
              error: 'Apple Pay payment failed',
            });
          }
        } catch (error: any) {
          session.completePayment((window as any).ApplePaySession.STATUS_FAILURE);
          resolve({
            success: false,
            error: error.message,
          });
        }
      };

      session.begin();
    });
  }

  validatePaymentData(data: any): boolean {
    // Apple Pay handles validation internally
    return true;
  }
}

// Saudi local payment providers
export class MadaPaymentProvider extends BaseHttpPaymentProvider {
  readonly id = 'mada';
  readonly name = 'Mada';

  async initialize(): Promise<void> {
    // Mada doesn't require client-side initialization
  }

  async isAvailable(): Promise<boolean> {
    return true; // Always available in Saudi Arabia
  }

  async confirmPayment(paymentIntentId: string): Promise<PaymentResult> {
    try {
      const result = await this.makeRequest<any>(`confirm/${paymentIntentId}`, 'POST');
      return {
        success: true,
        payment_intent_id: result.payment_intent_id,
        redirect_url: result.redirect_url,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  validatePaymentData(data: any): boolean {
    return !!(data.customer_name && data.customer_phone);
  }
}

export class STCPayPaymentProvider extends BaseHttpPaymentProvider {
  readonly id = 'stc_pay';
  readonly name = 'STC Pay';

  async initialize(): Promise<void> {
    // STC Pay doesn't require client-side initialization
  }

  async isAvailable(): Promise<boolean> {
    return true; // Available in Saudi Arabia
  }

  async createPayment(orderId: string, amount: number, options?: any): Promise<PaymentIntent> {
    return this.makeRequest<PaymentIntent>('intent', 'POST', {
      order_id: orderId,
      amount,
      mobile_number: options?.mobile_number,
    });
  }

  async confirmPayment(paymentIntentId: string): Promise<PaymentResult> {
    try {
      const result = await this.makeRequest<any>(`confirm/${paymentIntentId}`, 'POST');
      return {
        success: true,
        payment_intent_id: result.payment_intent_id,
        redirect_url: result.redirect_url,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  validatePaymentData(data: any): boolean {
    return PaymentUtils.validateSaudiMobile(data.mobile_number);
  }
}

// Provider factory for creating provider instances
export class PaymentProviderFactory {
  private static providers: Map<string, () => IPaymentProvider> = new Map();

  static registerProvider(id: string, factory: () => IPaymentProvider) {
    this.providers.set(id, factory);
  }

  static getProvider(id: string): IPaymentProvider | null {
    const factory = this.providers.get(id);
    return factory ? factory() : null;
  }

  static getAllProviders(): IPaymentProvider[] {
    return Array.from(this.providers.values()).map(factory => factory());
  }

  // Register default providers
  static initialize() {
    this.registerProvider('stripe', () => new StripePaymentProvider({}));
    this.registerProvider('paypal', () => new PayPalPaymentProvider({}));
    this.registerProvider('apple_pay', () => new ApplePayPaymentProvider({}));
    this.registerProvider('mada', () => new MadaPaymentProvider({}));
    this.registerProvider('stc_pay', () => new STCPayPaymentProvider({}));
  }
}

// Initialize providers on module load
PaymentProviderFactory.initialize();