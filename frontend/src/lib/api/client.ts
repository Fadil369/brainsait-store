import { BaseApiClient, createQueryString, createFormData, ApiError } from './base';
import { ApiResponse } from '@/types';

// Main API client instance extending the base
class BrainSAITApiClient extends BaseApiClient {
  constructor() {
    super({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      retryAttempts: 3,
      retryDelay: 1000,
    });
  }

  // Public API methods using the protected base methods
  async get<T>(url: string, config?: any): Promise<ApiResponse<T>> {
    return super.get<T>(url, config);
  }

  async post<T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    return super.post<T>(url, data, config);
  }

  async put<T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    return super.put<T>(url, data, config);
  }

  async patch<T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> {
    return super.patch<T>(url, data, config);
  }

  async delete<T>(url: string, config?: any): Promise<ApiResponse<T>> {
    return super.delete<T>(url, config);
  }
}

// Create singleton instance
const apiClient = new BrainSAITApiClient();

// Export the singleton for backward compatibility
export const api = apiClient;

// Export the axios instance for direct use if needed (for backward compatibility)
export { apiClient };

// Re-export utilities
export { createFormData, createQueryString, ApiError };