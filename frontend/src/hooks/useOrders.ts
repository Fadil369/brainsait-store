import { ordersApi, paymentsApi, Order, CreateOrderRequest } from '@/lib/api/orders';
import { CheckoutData } from '@/types';
import { 
  createQueryHook, 
  createMutationHook, 
  createQueryManagerHook,
  QueryKeyFactory 
} from './factories';

// Query keys for orders
const orderKeys = new QueryKeyFactory('orders');

export const ORDER_QUERY_KEYS = {
  ...orderKeys,
  user: (params?: any) => orderKeys.custom('user', params),
  payment: (paymentId: string) => orderKeys.custom('payment', paymentId),
};

// Type definitions
interface UserOrderParams {
  page?: number;
  limit?: number;
  status?: Order['orderStatus'];
}

// Order query hooks using factories
export const useOrder = createQueryHook(
  (orderId?: string) => orderId ? ORDER_QUERY_KEYS.detail(orderId) : ['orders', 'detail', null],
  (orderId?: string) => {
    if (!orderId) throw new Error('Order ID is required');
    return ordersApi.getOrder(orderId);
  },
  {
    staleTime: 2 * 60 * 1000, // 2 minutes - orders change more frequently
    gcTime: 5 * 60 * 1000,
  }
);

export const useUserOrders = createQueryHook(
  (params?: UserOrderParams) => ORDER_QUERY_KEYS.user(params),
  (params?: UserOrderParams) => ordersApi.getUserOrders(params),
  {
    staleTime: 1 * 60 * 1000, // 1 minute
    gcTime: 3 * 60 * 1000,
  }
);

// Payment status hook
export const usePaymentStatus = createQueryHook(
  (paymentIntentId?: string) => 
    paymentIntentId ? ORDER_QUERY_KEYS.payment(paymentIntentId) : ['orders', 'payment', null],
  (paymentIntentId?: string) => {
    if (!paymentIntentId) throw new Error('Payment intent ID is required');
    return paymentsApi.getPaymentStatus(paymentIntentId);
  },
  {
    staleTime: 30 * 1000, // 30 seconds - payment status changes quickly
    gcTime: 2 * 60 * 1000,
    refetchInterval: 5000, // Poll every 5 seconds for payment status
  }
);

// Order mutation hooks using factories
export const useCreateOrder = createMutationHook(
  (orderData: CreateOrderRequest) => ordersApi.createOrder(orderData),
  {
    onSuccess: (data, variables, context) => {
      // Invalidate and refetch orders
      const manager = useOrdersManager();
      manager.invalidateAll();
    },
  }
);

export const useUpdateOrderStatus = createMutationHook(
  ({ orderId, status }: { orderId: string; status: Order['orderStatus'] }) =>
    ordersApi.updateOrderStatus(orderId, status),
  {
    onSuccess: (data, variables) => {
      const manager = useOrdersManager();
      // Update the specific order in cache
      manager.setDetailData(variables.orderId, data);
      // Invalidate user orders list
      manager.invalidateLists();
    },
  }
);

export const useCancelOrder = createMutationHook(
  ({ orderId, reason }: { orderId: string; reason?: string }) =>
    ordersApi.cancelOrder(orderId, reason),
  {
    onSuccess: (data, variables) => {
      const manager = useOrdersManager();
      manager.setDetailData(variables.orderId, data);
      manager.invalidateLists();
    },
  }
);

// Payment mutation hooks
export const useCreatePaymentIntent = createMutationHook(
  (checkoutData: CheckoutData) => paymentsApi.createPaymentIntent(checkoutData)
);

export const useConfirmPayment = createMutationHook(
  (paymentIntentId: string) => paymentsApi.confirmPayment(paymentIntentId),
  {
    onSuccess: (data, variables) => {
      // If payment successful and orderId returned, invalidate that order
      if (data.data.success && data.data.orderId) {
        const manager = useOrdersManager();
        manager.invalidateDetail(data.data.orderId);
        manager.invalidateLists();
      }
    },
  }
);

export const useProcessRefund = createMutationHook(
  ({ orderId, amount, reason }: { orderId: string; amount?: number; reason?: string }) =>
    paymentsApi.processRefund(orderId, amount, reason),
  {
    onSuccess: (data, variables) => {
      const manager = useOrdersManager();
      manager.invalidateDetail(variables.orderId);
      manager.invalidateLists();
    },
  }
);

// Order management hook
export const useOrdersManager = createQueryManagerHook('orders');

// Convenience hooks for common order operations
export const useOrderOperations = () => {
  const manager = useOrdersManager();
  const createOrder = useCreateOrder();
  const updateStatus = useUpdateOrderStatus();
  const cancelOrder = useCancelOrder();

  return {
    // Order CRUD operations
    createOrder: createOrder.mutate,
    updateOrderStatus: updateStatus.mutate,
    cancelOrder: cancelOrder.mutate,
    
    // Loading states
    isCreatingOrder: createOrder.isPending,
    isUpdatingOrder: updateStatus.isPending,
    isCancellingOrder: cancelOrder.isPending,
    
    // Error states
    createOrderError: createOrder.error,
    updateOrderError: updateStatus.error,
    cancelOrderError: cancelOrder.error,
    
    // Cache management
    refreshOrder: (orderId: string) => manager.refetchDetail(orderId),
    refreshUserOrders: (params?: UserOrderParams) => manager.refetchList(params),
    clearOrderCache: () => manager.removeAll(),
    
    // Optimistic updates
    optimisticallyUpdateOrderStatus: (orderId: string, status: Order['orderStatus']) => {
      const currentOrder = manager.getDetailData(orderId) as any;
      if (currentOrder) {
        manager.setDetailData(orderId, {
          ...currentOrder,
          data: { ...currentOrder.data, orderStatus: status }
        });
      }
    },
  };
};

// Payment operations hook
export const usePaymentOperations = () => {
  const createPaymentIntent = useCreatePaymentIntent();
  const confirmPayment = useConfirmPayment();
  const processRefund = useProcessRefund();

  return {
    // Payment operations
    createPaymentIntent: createPaymentIntent.mutate,
    confirmPayment: confirmPayment.mutate,
    processRefund: processRefund.mutate,
    
    // Loading states
    isCreatingPayment: createPaymentIntent.isPending,
    isConfirmingPayment: confirmPayment.isPending,
    isProcessingRefund: processRefund.isPending,
    
    // Error states
    paymentError: createPaymentIntent.error || confirmPayment.error || processRefund.error,
    
    // Success states
    paymentIntentCreated: createPaymentIntent.isSuccess,
    paymentConfirmed: confirmPayment.isSuccess,
    refundProcessed: processRefund.isSuccess,
    
    // Data
    paymentIntentData: createPaymentIntent.data,
    paymentConfirmData: confirmPayment.data,
    refundData: processRefund.data,
  };
};