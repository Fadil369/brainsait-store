import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Extend the axios interface to include metadata
/* eslint-disable no-unused-vars */
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: {
      startTime?: number;
      [key: string]: any;
    };
  }
}
/* eslint-enable no-unused-vars */

import { ApiResponse } from '@/types';

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const API_TIMEOUT = 10000; // 10 seconds

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = typeof window !== 'undefined' 
      ? localStorage.getItem('brainsait-auth-token') 
      : null;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add language header
    const language = typeof window !== 'undefined'
      ? localStorage.getItem('brainsait-language') || 'en'
      : 'en';
    
    config.headers['Accept-Language'] = language;

    // Add request timestamp
    config.metadata = { ...config.metadata, startTime: Date.now() };

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time in development
    if (process.env.NODE_ENV === 'development') {
      const _endTime = Date.now();
      const _startTime = response.config.metadata?.startTime || _endTime;
      // API Request timing debug info removed for production
    }

    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - clear auth token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('brainsait-auth-token');
        // You might want to redirect to login page here
      }
    }

    if (error.response?.status >= 500) {
      // Server error - you might want to show a notification
      // Server error occurred
    }

    return Promise.reject(error);
  }
);

// Generic API methods
export const api = {
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    try {
      const response = await apiClient.get(url, config);
      return response.data;
    } catch (error: any) {
      throw handleApiError(error);
    }
  },

  post: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    try {
      const response = await apiClient.post(url, data, config);
      return response.data;
    } catch (error: any) {
      throw handleApiError(error);
    }
  },

  put: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    try {
      const response = await apiClient.put(url, data, config);
      return response.data;
    } catch (error: any) {
      throw handleApiError(error);
    }
  },

  patch: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    try {
      const response = await apiClient.patch(url, data, config);
      return response.data;
    } catch (error: any) {
      throw handleApiError(error);
    }
  },

  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    try {
      const response = await apiClient.delete(url, config);
      return response.data;
    } catch (error: any) {
      throw handleApiError(error);
    }
  },
};

// Error handler
function handleApiError(error: any): Error {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.message || error.response.statusText || 'An error occurred';
    const apiError = new Error(message);
    (apiError as any).status = error.response.status;
    (apiError as any).data = error.response.data;
    return apiError;
  } else if (error.request) {
    // Network error
    return new Error('Network error. Please check your internet connection.');
  } else {
    // Other error
    return new Error(error.message || 'An unexpected error occurred');
  }
}

// Export the axios instance for direct use if needed
export { apiClient };

// Request configuration helpers
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