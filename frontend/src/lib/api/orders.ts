import { randomBytes } from 'crypto';
import { api } from './client';
import { CartItem, CustomerInfo, PaymentMethod, CheckoutData } from '@/types';

// Order-related types
export interface Order {
  id: string;
  userId?: string;
  customerInfo: CustomerInfo;
  items: CartItem[];
  subtotal: number;
  tax: number;
  total: number;
  currency: string;
  paymentMethod: PaymentMethod;
  paymentStatus: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
  orderStatus: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  createdAt: string;
  updatedAt: string;
  paymentIntentId?: string;
  trackingNumber?: string;
}

export interface CreateOrderRequest {
  customerInfo: CustomerInfo;
  items: CartItem[];
  paymentMethod: PaymentMethod;
  paymentIntentId?: string;
}

export interface PaymentIntent {
  id: string;
  clientSecret: string;
  amount: number;
  currency: string;
  status: string;
}

// Orders API endpoints
export const ordersApi = {
  // Create a new order
  createOrder: async (orderData: CreateOrderRequest) => {
    return api.post<Order>('/orders', orderData);
  },

  // Get order by ID
  getOrder: async (orderId: string) => {
    return api.get<Order>(`/orders/${orderId}`);
  },

  // Get user orders
  getUserOrders: async (params?: {
    page?: number;
    limit?: number;
    status?: Order['orderStatus'];
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.status) queryParams.set('status', params.status);
    
    const url = `/orders/user${queryParams.toString() ? `?${queryParams}` : ''}`;
    return api.get<{
      orders: Order[];
      pagination: {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
      };
    }>(url);
  },

  // Update order status
  updateOrderStatus: async (orderId: string, status: Order['orderStatus']) => {
    return api.patch<Order>(`/orders/${orderId}/status`, { status });
  },

  // Cancel order
  cancelOrder: async (orderId: string, reason?: string) => {
    return api.patch<Order>(`/orders/${orderId}/cancel`, { reason });
  },
};

// Payment API endpoints
export const paymentsApi = {
  // Create payment intent
  createPaymentIntent: async (checkoutData: CheckoutData) => {
    return api.post<PaymentIntent>('/payments/intent', {
      amount: Math.round(checkoutData.totals.total * 100), // Convert to cents
      currency: 'SAR',
      items: checkoutData.items,
      customerInfo: checkoutData.customerInfo,
    });
  },

  // Confirm payment
  confirmPayment: async (paymentIntentId: string) => {
    return api.post<{ success: boolean; orderId?: string }>(`/payments/${paymentIntentId}/confirm`);
  },

  // Get payment status
  getPaymentStatus: async (paymentIntentId: string) => {
    return api.get<{
      id: string;
      status: 'requires_payment_method' | 'requires_confirmation' | 'processing' | 'succeeded' | 'canceled';
      orderId?: string;
    }>(`/payments/${paymentIntentId}/status`);
  },

  // Process refund
  processRefund: async (orderId: string, amount?: number, reason?: string) => {
    return api.post<{ success: boolean; refundId: string }>(`/payments/refund`, {
      orderId,
      amount,
      reason,
    });
  },
};

// Mock implementation for development
// Helper to generate a secure random string
function secureRandomString(length: number) {
  return randomBytes(length).toString('hex').substr(0, length);
}

export const mockOrdersApi = {
  createOrder: async (orderData: CreateOrderRequest) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const orderId = `order_${Date.now()}_${secureRandomString(18)}`;
    const now = new Date().toISOString();
    
    const order: Order = {
      id: orderId,
      customerInfo: orderData.customerInfo,
      items: orderData.items,
      subtotal: orderData.items.reduce((sum, item) => sum + (item.price * item.quantity), 0),
      tax: orderData.items.reduce((sum, item) => sum + (item.price * item.quantity), 0) * 0.15,
      total: orderData.items.reduce((sum, item) => sum + (item.price * item.quantity), 0) * 1.15,
      currency: 'SAR',
      paymentMethod: orderData.paymentMethod,
      paymentStatus: 'completed',
      orderStatus: 'processing',
      createdAt: now,
      updatedAt: now,
      paymentIntentId: orderData.paymentIntentId,
    };
    
    return { data: order };
  },

  getOrder: async (orderId: string) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Mock order data
    const order: Order = {
      id: orderId,
      customerInfo: {
        email: 'customer@example.com',
        firstName: 'John',
        lastName: 'Doe',
        phone: '+966501234567',
        country: 'SA',
        city: 'Riyadh',
        isCompany: false,
      },
      items: [],
      subtotal: 1000,
      tax: 150,
      total: 1150,
      currency: 'SAR',
      paymentMethod: 'mada',
      paymentStatus: 'completed',
      orderStatus: 'processing',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    return { data: order };
  },
};

export const mockPaymentsApi = {
  createPaymentIntent: async (checkoutData: CheckoutData) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const paymentIntent: PaymentIntent = {
      id: `pi_${Date.now()}_${secureRandomString(18)}`,
      clientSecret: `pi_${Date.now()}_secret_${secureRandomString(18)}`,
      amount: Math.round(checkoutData.totals.total * 100),
      currency: 'SAR',
      status: 'requires_payment_method',
    };
    
    return { data: paymentIntent };
  },

  confirmPayment: async (_paymentIntentId: string) => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      data: {
        success: true,
        orderId: `order_${Date.now()}_${secureRandomString(18)}`,
      }
    };
  },
};

// Choose API based on environment
const shouldUseMockApi = process.env.NODE_ENV === 'development' && 
                        process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

export const orders = shouldUseMockApi ? mockOrdersApi : ordersApi;
export const payments = shouldUseMockApi ? mockPaymentsApi : paymentsApi;