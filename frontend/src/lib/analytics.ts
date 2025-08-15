/**
 * Analytics Service
 * Handles data fetching and processing for analytics dashboard
 */

export interface DateRange {
  start_date?: string;
  end_date?: string;
}

export interface RevenueAnalytics {
  total_revenue: number;
  average_order_value: number;
  revenue_growth_percentage: number;
  revenue_by_payment_method: Array<{
    payment_method: string;
    revenue: number;
    order_count: number;
  }>;
  daily_revenue_trend: Array<{
    date: string;
    revenue: number;
    orders: number;
  }>;
  period: {
    start_date: string;
    end_date: string;
  };
}

export interface CustomerAnalytics {
  total_customers: number;
  new_customers: number;
  active_customers: number;
  customer_lifetime_value: number;
  top_customers: Array<{
    id: number;
    email: string;
    full_name: string;
    total_spent: number;
    order_count: number;
  }>;
  customer_acquisition_trend: Array<{
    year: number;
    month: number;
    new_customers: number;
  }>;
}

export interface ProductAnalytics {
  top_selling_products: Array<{
    id: number;
    name: string;
    price: number;
    total_sold: number;
    total_revenue: number;
    order_count: number;
  }>;
  category_performance: Array<{
    category: string;
    total_sold: number;
    total_revenue: number;
    product_count: number;
  }>;
  conversion_rates: any[];
}

export interface PaymentAnalytics {
  payment_method_distribution: Array<{
    payment_method: string;
    transaction_count: number;
    total_amount: number;
    average_amount: number;
  }>;
  success_rates: Array<{
    payment_method: string;
    successful_transactions: number;
    failed_transactions: number;
    total_transactions: number;
    success_rate: number;
  }>;
  daily_transaction_volume: Array<{
    date: string;
    transaction_count: number;
    total_amount: number;
  }>;
}

export interface ExecutiveSummary {
  summary: {
    total_revenue: number;
    total_customers: number;
    new_customers: number;
    average_order_value: number;
    revenue_growth: number;
  };
  top_metrics: {
    best_selling_product: any;
    preferred_payment_method: any;
    top_customer: any;
  };
  trends: {
    revenue_trend: any[];
    customer_acquisition: any[];
  };
  period: {
    start_date: string;
    end_date: string;
  };
}

export interface RealTimeMetrics {
  today_revenue: number;
  yesterday_revenue: number;
  revenue_change: number;
  current_hour_orders: number;
  active_sessions: number;
  conversion_rate: number;
  last_updated: string;
}

export class AnalyticsService {
  private baseUrl: string;
  private getAuthHeaders: () => Record<string, string>;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.getAuthHeaders = () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : '';
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
    };
  }

  private async fetchWithAuth(endpoint: string, options?: any) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'API request failed');
    }

    return data.data;
  }

  private buildQueryParams(params: DateRange): string {
    const searchParams = new URLSearchParams();
    
    if (params.start_date) {
      searchParams.append('start_date', params.start_date);
    }
    
    if (params.end_date) {
      searchParams.append('end_date', params.end_date);
    }

    const queryString = searchParams.toString();
    return queryString ? `?${queryString}` : '';
  }

  // Revenue Analytics
  async getRevenueAnalytics(dateRange?: DateRange): Promise<RevenueAnalytics> {
    const queryParams = this.buildQueryParams(dateRange || {});
    return this.fetchWithAuth(`/api/v1/analytics/revenue${queryParams}`);
  }

  // Customer Analytics
  async getCustomerAnalytics(dateRange?: DateRange): Promise<CustomerAnalytics> {
    const queryParams = this.buildQueryParams(dateRange || {});
    return this.fetchWithAuth(`/api/v1/analytics/customers${queryParams}`);
  }

  // Product Analytics
  async getProductAnalytics(dateRange?: DateRange): Promise<ProductAnalytics> {
    const queryParams = this.buildQueryParams(dateRange || {});
    return this.fetchWithAuth(`/api/v1/analytics/products${queryParams}`);
  }

  // Payment Analytics
  async getPaymentAnalytics(dateRange?: DateRange): Promise<PaymentAnalytics> {
    const queryParams = this.buildQueryParams(dateRange || {});
    return this.fetchWithAuth(`/api/v1/analytics/payments${queryParams}`);
  }

  // Executive Dashboard
  async getExecutiveDashboard(dateRange?: DateRange): Promise<ExecutiveSummary> {
    const queryParams = this.buildQueryParams(dateRange || {});
    return this.fetchWithAuth(`/api/v1/analytics/dashboard${queryParams}`);
  }

  // Real-time Metrics
  async getRealTimeMetrics(): Promise<RealTimeMetrics> {
    return this.fetchWithAuth('/api/v1/analytics/real-time');
  }

  // Export Report
  async exportReport(
    reportType: 'revenue' | 'customers' | 'products' | 'payments',
    format: 'json' | 'csv' = 'json',
    dateRange?: DateRange
  ): Promise<any> {
    const queryParams = new URLSearchParams({
      report_type: reportType,
      format,
      ...(dateRange?.start_date && { start_date: dateRange.start_date }),
      ...(dateRange?.end_date && { end_date: dateRange.end_date }),
    });

    return this.fetchWithAuth(`/api/v1/analytics/export?${queryParams}`);
  }

  // Get All Analytics Data
  async getAllAnalytics(dateRange?: DateRange) {
    const [revenue, customers, products, payments, dashboard] = await Promise.all([
      this.getRevenueAnalytics(dateRange),
      this.getCustomerAnalytics(dateRange),
      this.getProductAnalytics(dateRange),
      this.getPaymentAnalytics(dateRange),
      this.getExecutiveDashboard(dateRange),
    ]);

    return {
      revenue,
      customers,
      products,
      payments,
      dashboard,
    };
  }

  // Helper method to format currency
  static formatCurrency(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount);
  }

  // Helper method to format percentage
  static formatPercentage(value: number, decimals: number = 1): string {
    return `${value.toFixed(decimals)}%`;
  }

  // Helper method to calculate growth rate
  static calculateGrowthRate(current: number, previous: number): number {
    if (previous === 0) return current > 0 ? 100 : 0;
    return ((current - previous) / previous) * 100;
  }

  // Helper method to get period comparison
  static getPeriodComparison(current: any, previous: any) {
    return {
      revenue_growth: this.calculateGrowthRate(current.total_revenue, previous.total_revenue),
      customer_growth: this.calculateGrowthRate(current.total_customers, previous.total_customers),
      order_growth: this.calculateGrowthRate(current.total_orders, previous.total_orders),
    };
  }

  // Real-time data subscription (placeholder for WebSocket implementation)
  subscribeToRealTimeUpdates(callback: (_data: RealTimeMetrics) => void): () => void {
    // This would implement WebSocket connection for real-time updates
    const interval = setInterval(async () => {
      try {
        const data = await this.getRealTimeMetrics();
        callback(data);
      } catch (error) {
        // Failed to fetch real-time metrics
      }
    }, 30000); // Update every 30 seconds

    // Return unsubscribe function
    return () => clearInterval(interval);
  }
}

// Export singleton instance
export const analyticsService = new AnalyticsService();

// Export utility functions
export const AnalyticsUtils = {
  formatCurrency: AnalyticsService.formatCurrency,
  formatPercentage: AnalyticsService.formatPercentage,
  calculateGrowthRate: AnalyticsService.calculateGrowthRate,
  getPeriodComparison: AnalyticsService.getPeriodComparison,
};