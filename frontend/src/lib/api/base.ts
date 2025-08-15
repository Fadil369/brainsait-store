import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '@/types';

// Extend the axios interface to include metadata
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: {
      startTime?: number;
      [key: string]: any;
    };
  }
}

// Base API configuration
export interface ApiClientConfig {
  baseURL?: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
}

// Error types for better error handling
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Retry configuration
interface RetryConfig {
  attempts: number;
  delay: number;
  shouldRetry: (error: any) => boolean;
}

// Base API client class that can be extended
export class BaseApiClient {
  protected client: AxiosInstance;
  private retryConfig: RetryConfig;

  constructor(config: ApiClientConfig = {}) {
    const {
      baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      timeout = 10000,
      retryAttempts = 3,
      retryDelay = 1000,
    } = config;

    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    this.retryConfig = {
      attempts: retryAttempts,
      delay: retryDelay,
      shouldRetry: (error: any) => {
        // Don't retry on 4xx errors except 401 (unauthorized)
        if (error?.status >= 400 && error?.status < 500 && error?.status !== 401) {
          return false;
        }
        return true;
      },
    };

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add language header
        const language = this.getLanguage();
        config.headers['Accept-Language'] = language;

        // Add request timestamp
        config.metadata = { ...config.metadata, startTime: Date.now() };

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        this.logResponseTime(response);
        return response;
      },
      (error) => this.handleResponseError(error)
    );
  }

  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('brainsait-auth-token');
  }

  private getLanguage(): string {
    if (typeof window === 'undefined') return 'en';
    return localStorage.getItem('brainsait-language') || 'en';
  }

  private logResponseTime(response: AxiosResponse) {
    if (process.env.NODE_ENV === 'development') {
      const endTime = Date.now();
      const startTime = response.config.metadata?.startTime || endTime;
      const duration = endTime - startTime;
      console.debug(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
  }

  private async handleResponseError(error: any): Promise<never> {
    if (error.response?.status === 401) {
      this.handleUnauthorized();
    }

    if (error.response?.status >= 500) {
      // Server error logging could be enhanced here
      console.error('[API] Server error:', error.response);
    }

    throw this.createApiError(error);
  }

  private handleUnauthorized() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('brainsait-auth-token');
      // Could dispatch a global event or redirect here
    }
  }

  private createApiError(error: any): ApiError {
    if (error.response) {
      const message = error.response.data?.message || error.response.statusText || 'An error occurred';
      return new ApiError(message, error.response.status, error.response.data);
    } else if (error.request) {
      return new ApiError('Network error. Please check your internet connection.');
    } else {
      return new ApiError(error.message || 'An unexpected error occurred');
    }
  }

  // Generic HTTP methods with retry logic
  protected async request<T>(
    config: AxiosRequestConfig,
    customRetryConfig?: Partial<RetryConfig>
  ): Promise<ApiResponse<T>> {
    const retryConfig = { ...this.retryConfig, ...customRetryConfig };
    let lastError: any;

    for (let attempt = 1; attempt <= retryConfig.attempts; attempt++) {
      try {
        const response = await this.client.request(config);
        return response.data;
      } catch (error) {
        lastError = error;
        
        if (attempt === retryConfig.attempts || !retryConfig.shouldRetry(error)) {
          throw this.createApiError(error);
        }

        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, retryConfig.delay * attempt));
      }
    }

    throw this.createApiError(lastError);
  }

  // Convenient HTTP methods
  protected async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  protected async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  protected async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  protected async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PATCH', url, data });
  }

  protected async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }
}

// Utility functions for request building
export const createFormData = (data: Record<string, any>): FormData => {
  const formData = new FormData();
  Object.keys(data).forEach(key => {
    if (data[key] !== null && data[key] !== undefined) {
      formData.append(key, data[key]);
    }
  });
  return formData;
};

export const createQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  Object.keys(params).forEach(key => {
    if (params[key] !== null && params[key] !== undefined) {
      searchParams.append(key, String(params[key]));
    }
  });
  return searchParams.toString();
};