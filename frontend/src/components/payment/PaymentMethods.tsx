'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAppStore } from '@/stores';
import { paymentService, PaymentMethod } from '@/lib/payment';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

interface PaymentMethodsProps {
  orderId: string;
  totalAmount: number;
  currency: string;
  onPaymentSuccess: (_paymentId: string) => void;
  onPaymentError: (_error: string) => void;
}

export const PaymentMethods: React.FC<PaymentMethodsProps> = ({
  orderId,
  totalAmount,
  currency,
  onPaymentSuccess,
  onPaymentError
}) => {
  const [paymentMethods, setPaymentMethods] = useState<Record<string, PaymentMethod>>({});
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [showApplePay, setShowApplePay] = useState(false);
  const [customerData, setCustomerData] = useState({
    name: '',
    phone: '',
    email: ''
  });
  const { language } = useAppStore();

  const initializePaymentMethods = useCallback(async () => {
    try {
      await paymentService.initialize();
      const methods = await paymentService.getPaymentMethods();
      setPaymentMethods(methods);
    } catch (error) {
      // Failed to initialize payment methods
      onPaymentError('Failed to load payment methods');
    }
  }, [onPaymentError]);

  useEffect(() => {
    initializePaymentMethods();
    checkApplePayAvailability();
  }, [initializePaymentMethods]);

  const checkApplePayAvailability = async () => {
    try {
      const available = await paymentService.isApplePayAvailable();
      setShowApplePay(available);
    } catch (error) {
      // Apple Pay check failed
    }
  };

  const handlePaymentMethodSelect = (methodId: string) => {
    setSelectedMethod(methodId);
  };

  const processPayment = async () => {
    if (!selectedMethod) {
      onPaymentError('Please select a payment method');
      return;
    }

    setLoading(true);

    try {
      switch (selectedMethod) {
        case 'stripe':
          await processStripePayment();
          break;
        case 'paypal':
          await processPayPalPayment();
          break;
        case 'apple_pay':
          await processApplePayPayment();
          break;
        case 'mada':
          await processMadaPayment();
          break;
        case 'stc_pay':
          await processSTCPayPayment();
          break;
        default:
          throw new Error('Unsupported payment method');
      }
    } catch (error) {
      // Payment processing failed
      onPaymentError(error instanceof Error ? error.message : 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  const processStripePayment = async () => {
    const paymentIntent = await paymentService.createStripePayment(orderId);
    
    // For Stripe, we'll use the StripeCheckout component
    window.location.href = `/payment/stripe?client_secret=${paymentIntent.client_secret}&order_id=${orderId}`;
  };

  const processPayPalPayment = async () => {
    const paymentIntent = await paymentService.createPayPalOrder(orderId);
    
    if (paymentIntent.redirect_url) {
      window.location.href = paymentIntent.redirect_url;
    } else {
      throw new Error('PayPal redirect URL not provided');
    }
  };

  const processApplePayPayment = async () => {
    await paymentService.processApplePayPayment(orderId);
  };

  const processMadaPayment = async () => {
    if (!customerData.name || !customerData.phone) {
      onPaymentError('Please provide customer name and phone for Mada payment');
      return;
    }

    const paymentIntent = await paymentService.createMadaPayment(orderId, customerData);
    
    if (paymentIntent.redirect_url) {
      window.location.href = paymentIntent.redirect_url;
    } else {
      throw new Error('Mada redirect URL not provided');
    }
  };

  const processSTCPayPayment = async () => {
    if (!customerData.phone || !paymentService.validatePaymentData('stc_pay', { mobile_number: customerData.phone })) {
      onPaymentError('Please provide a valid Saudi mobile number (+966XXXXXXXXX)');
      return;
    }

    const paymentIntent = await paymentService.createSTCPayPayment(orderId, customerData.phone);
    
    if (paymentIntent.mobile_verification) {
      // Show success message for mobile verification
      onPaymentSuccess(paymentIntent.payment_intent_id);
    }
  };

  const formatCurrency = (amount: number) => {
    return paymentService.formatCurrency(amount, currency);
  };

  const renderPaymentMethodCard = (method: PaymentMethod) => {
    const isSelected = selectedMethod === method.id;
    const isDisabled = !method.enabled;

    return (
      <div
        key={method.id}
        onClick={() => !isDisabled && handlePaymentMethodSelect(method.id)}
        className={`
          payment-method-card p-4 border-2 rounded-lg cursor-pointer transition-all duration-200
          ${isSelected ? 'border-vision-green bg-vision-green/10' : 'border-glass-border hover:border-vision-green/50'}
          ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-glass-bg rounded-lg flex items-center justify-center">
            <Image 
              src={method.logo_url} 
              alt={method.name}
              width={32}
              height={32}
              className="w-8 h-8 object-contain"
              onError={(e) => {
                e.currentTarget.src = '/payment-logos/default.svg';
              }}
            />
          </div>
          
          <div className="flex-1">
            <h3 className="font-semibold text-text-primary">
              {language === 'ar' ? method.name_ar : method.name}
            </h3>
            <p className="text-sm text-text-secondary">
              {language === 'ar' ? method.description_ar : method.description}
            </p>
            <p className="text-xs text-vision-green mt-1">
              {method.fees.percentage}% fee
            </p>
          </div>
          
          <div className="text-right">
            <div className="flex flex-wrap gap-1">
              {method.supported_currencies.map(curr => (
                <span 
                  key={curr}
                  className="text-xs bg-glass-border px-2 py-1 rounded"
                >
                  {curr}
                </span>
              ))}
            </div>
          </div>
          
          {isSelected && (
            <div className="w-5 h-5 bg-vision-green rounded-full flex items-center justify-center">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderCustomerDataForm = () => {
    if (!selectedMethod || !['mada', 'stc_pay'].includes(selectedMethod)) {
      return null;
    }

    return (
      <div className="mt-6 p-4 bg-glass-bg rounded-lg">
        <h4 className="font-semibold text-text-primary mb-4">
          {language === 'ar' ? 'معلومات العميل' : 'Customer Information'}
        </h4>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              {language === 'ar' ? 'الاسم الكامل' : 'Full Name'}
            </label>
            <Input
              value={customerData.name}
              onChange={(e) => setCustomerData({...customerData, name: e.target.value})}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              {language === 'ar' ? 'رقم الجوال' : 'Mobile Number'}
            </label>
            <Input
              value={customerData.phone}
              onChange={(e) => setCustomerData({...customerData, phone: e.target.value})}
              placeholder="+966501234567"
              required
            />
          </div>
          
          {selectedMethod === 'mada' && (
            <div>
              <label className="block text-sm font-medium mb-2">
                {language === 'ar' ? 'البريد الإلكتروني' : 'Email Address'}
              </label>
              <Input
                type="email"
                value={customerData.email}
                onChange={(e) => setCustomerData({...customerData, email: e.target.value})}
              />
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="payment-methods">
      {/* Payment Summary */}
      <div className="payment-summary mb-6 p-4 bg-glass-bg rounded-lg">
        <div className="flex justify-between items-center">
          <span className="text-text-secondary">
            {language === 'ar' ? 'المجموع:' : 'Total:'}
          </span>
          <span className="text-2xl font-bold text-vision-green">
            {formatCurrency(totalAmount)}
          </span>
        </div>
      </div>

      {/* Payment Methods Grid */}
      <div className="space-y-3 mb-6">
        <h3 className="text-lg font-semibold text-text-primary">
          {language === 'ar' ? 'اختر طريقة الدفع' : 'Choose Payment Method'}
        </h3>
        
        {Object.values(paymentMethods).map(method => (
          renderPaymentMethodCard(method)
        ))}
        
        {/* Apple Pay Special Button */}
        {showApplePay && (
          <button
            onClick={() => handlePaymentMethodSelect('apple_pay')}
            className={`
              w-full h-14 bg-black text-white rounded-lg flex items-center justify-center space-x-2
              hover:bg-gray-800 transition-colors duration-200
              ${selectedMethod === 'apple_pay' ? 'ring-2 ring-vision-green' : ''}
            `}
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
            </svg>
            <span>Pay with Apple Pay</span>
          </button>
        )}
      </div>

      {/* Customer Data Form */}
      {renderCustomerDataForm()}

      {/* Payment Action Button */}
      <div className="mt-6">
        <Button
          onClick={processPayment}
          disabled={!selectedMethod || loading}
          className="w-full btn-primary-enhanced h-12"
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="loading-enhanced" />
              <span>
                {language === 'ar' ? 'جاري المعالجة...' : 'Processing...'}
              </span>
            </div>
          ) : (
            <span>
              {language === 'ar' 
                ? `ادفع ${formatCurrency(totalAmount)}`
                : `Pay ${formatCurrency(totalAmount)}`
              }
            </span>
          )}
        </Button>
      </div>

      {/* Security Notice */}
      <div className="mt-4 text-center text-sm text-text-secondary">
        <div className="flex items-center justify-center space-x-2">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
          </svg>
          <span>
            {language === 'ar' 
              ? 'معاملاتك محمية بتشفير SSL 256-bit'
              : 'Your transactions are secured with 256-bit SSL encryption'
            }
          </span>
        </div>
      </div>
    </div>
  );
};

// Stripe Checkout Component
export const StripeCheckout: React.FC<{
  clientSecret: string;
  orderId: string;
  onSuccess: (_paymentId: string) => void;
  onError: (_error: string) => void;
}> = ({ clientSecret, orderId, onSuccess, onError }) => {
  return (
    <Elements stripe={stripePromise}>
      <StripePaymentForm 
        clientSecret={clientSecret}
        orderId={orderId}
        onSuccess={onSuccess}
        onError={onError}
      />
    </Elements>
  );
};

const StripePaymentForm: React.FC<{
  clientSecret: string;
  orderId: string;
  onSuccess: (_paymentId: string) => void;
  onError: (_error: string) => void;
}> = ({ clientSecret: _clientSecret, orderId, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const { language } = useAppStore();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!stripe || !elements) return;

    setLoading(true);

    try {
      const cardElement = elements.getElement(CardElement);
      if (!cardElement) throw new Error('Card element not found');

      const result = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment/success?orderId=${orderId}`,
        },
      });

      if (result.error) {
        onError(result.error.message || 'Payment failed');
      } else if ('paymentIntent' in result && result.paymentIntent) {
        onSuccess((result.paymentIntent as any).id);
      } else {
        onError('Payment failed - no payment intent');
      }
    } catch (error) {
      // Stripe payment error
      onError(error instanceof Error ? error.message : 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="stripe-payment-form">
      <div className="mb-6">
        <label className="block text-sm font-medium text-text-primary mb-2">
          {language === 'ar' ? 'معلومات البطاقة' : 'Card Information'}
        </label>
        <div className="p-3 border border-glass-border rounded-lg">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#ffffff',
                  '::placeholder': {
                    color: '#aab7c4',
                  },
                },
                invalid: {
                  color: '#fa755a',
                  iconColor: '#fa755a',
                },
              },
            }}
          />
        </div>
      </div>

      <Button
        type="submit"
        disabled={!stripe || loading}
        className="w-full btn-primary-enhanced h-12"
      >
        {loading ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="loading-enhanced" />
            <span>
              {language === 'ar' ? 'جاري المعالجة...' : 'Processing...'}
            </span>
          </div>
        ) : (
          <span>
            {language === 'ar' ? 'تأكيد الدفع' : 'Confirm Payment'}
          </span>
        )}
      </Button>
    </form>
  );
};

export default PaymentMethods;