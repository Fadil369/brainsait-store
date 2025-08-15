import axios, { AxiosResponse, AxiosError } from 'axios';
import { api, apiClient, createFormData, createQueryString } from '@/lib/api/client';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  })),
  isAxiosError: jest.fn()
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

describe('API Client', () => {
  const mockAxiosInstance = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockClear();
    mockLocalStorage.removeItem.mockClear();
  });

  describe('api.get', () => {
    it('should make GET request and return response data', async () => {
      const mockResponseData = { data: { id: 1, name: 'Test' } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await api.get('/test');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', undefined);
      expect(result).toBe(mockResponseData);
    });

    it('should pass config to axios get', async () => {
      const mockResponseData = { data: { id: 1 } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      const config = { headers: { 'Custom-Header': 'value' } };
      await api.get('/test', config);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', config);
    });

    it('should handle and transform axios errors', async () => {
      const axiosError = {
        response: {
          status: 404,
          statusText: 'Not Found',
          data: { message: 'Resource not found' }
        }
      } as AxiosError;

      mockAxiosInstance.get.mockRejectedValue(axiosError);

      await expect(api.get('/test')).rejects.toThrow('Resource not found');
    });

    it('should handle network errors', async () => {
      const networkError = {
        request: {},
        message: 'Network Error'
      } as AxiosError;

      mockAxiosInstance.get.mockRejectedValue(networkError);

      await expect(api.get('/test'))
        .rejects.toThrow('Network error. Please check your internet connection.');
    });

    it('should handle unknown errors', async () => {
      const unknownError = {
        message: 'Something went wrong'
      } as AxiosError;

      mockAxiosInstance.get.mockRejectedValue(unknownError);

      await expect(api.get('/test')).rejects.toThrow('Something went wrong');
    });
  });

  describe('api.post', () => {
    it('should make POST request with data', async () => {
      const mockResponseData = { data: { id: 1, created: true } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const postData = { name: 'New Item' };
      const result = await api.post('/test', postData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test', postData, undefined);
      expect(result).toBe(mockResponseData);
    });

    it('should make POST request without data', async () => {
      const mockResponseData = { data: { success: true } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      await api.post('/test');

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test', undefined, undefined);
    });

    it('should pass config to axios post', async () => {
      const mockResponseData = { data: { id: 1 } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.post.mockResolvedValue(mockResponse);
      
      const config = { headers: { 'Content-Type': 'multipart/form-data' } };
      const data = { file: 'test' };
      
      await api.post('/test', data, config);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test', data, config);
    });

    it('should handle POST errors', async () => {
      const axiosError = {
        response: {
          status: 400,
          data: { message: 'Bad request' }
        }
      } as AxiosError;

      mockAxiosInstance.post.mockRejectedValue(axiosError);

      await expect(api.post('/test')).rejects.toThrow('Bad request');
    });
  });

  describe('api.put', () => {
    it('should make PUT request with data', async () => {
      const mockResponseData = { data: { id: 1, updated: true } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.put.mockResolvedValue(mockResponse);

      const putData = { name: 'Updated Item' };
      const result = await api.put('/test/1', putData);

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/test/1', putData, undefined);
      expect(result).toBe(mockResponseData);
    });

    it('should handle PUT errors', async () => {
      const axiosError = {
        response: {
          status: 422,
          data: { message: 'Validation failed' }
        }
      } as AxiosError;

      mockAxiosInstance.put.mockRejectedValue(axiosError);

      await expect(api.put('/test/1')).rejects.toThrow('Validation failed');
    });
  });

  describe('api.patch', () => {
    it('should make PATCH request with data', async () => {
      const mockResponseData = { data: { id: 1, patched: true } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.patch.mockResolvedValue(mockResponse);

      const patchData = { status: 'updated' };
      const result = await api.patch('/test/1', patchData);

      expect(mockAxiosInstance.patch).toHaveBeenCalledWith('/test/1', patchData, undefined);
      expect(result).toBe(mockResponseData);
    });

    it('should handle PATCH errors', async () => {
      const axiosError = {
        response: {
          status: 403,
          data: { message: 'Forbidden' }
        }
      } as AxiosError;

      mockAxiosInstance.patch.mockRejectedValue(axiosError);

      await expect(api.patch('/test/1')).rejects.toThrow('Forbidden');
    });
  });

  describe('api.delete', () => {
    it('should make DELETE request', async () => {
      const mockResponseData = { data: { deleted: true } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.delete.mockResolvedValue(mockResponse);

      const result = await api.delete('/test/1');

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/test/1', undefined);
      expect(result).toBe(mockResponseData);
    });

    it('should pass config to axios delete', async () => {
      const mockResponseData = { data: { deleted: true } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.delete.mockResolvedValue(mockResponse);
      
      const config = { headers: { 'Authorization': 'Bearer token' } };
      
      await api.delete('/test/1', config);

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/test/1', config);
    });

    it('should handle DELETE errors', async () => {
      const axiosError = {
        response: {
          status: 404,
          data: { message: 'Not found' }
        }
      } as AxiosError;

      mockAxiosInstance.delete.mockRejectedValue(axiosError);

      await expect(api.delete('/test/1')).rejects.toThrow('Not found');
    });
  });

  describe('Error Handling', () => {
    it('should handle response errors with custom status', async () => {
      const axiosError = {
        response: {
          status: 500,
          statusText: 'Internal Server Error',
          data: { message: 'Server crashed' }
        }
      } as AxiosError;

      mockAxiosInstance.get.mockRejectedValue(axiosError);

      try {
        await api.get('/test');
      } catch (error: any) {
        expect(error.message).toBe('Server crashed');
        expect(error.status).toBe(500);
        expect(error.data).toEqual({ message: 'Server crashed' });
      }
    });

    it('should use statusText when no message in response data', async () => {
      const axiosError = {
        response: {
          status: 401,
          statusText: 'Unauthorized',
          data: {}
        }
      } as AxiosError;

      mockAxiosInstance.get.mockRejectedValue(axiosError);

      await expect(api.get('/test')).rejects.toThrow('Unauthorized');
    });

    it('should use generic message when no statusText', async () => {
      const axiosError = {
        response: {
          status: 500,
          data: {}
        }
      } as AxiosError;

      mockAxiosInstance.get.mockRejectedValue(axiosError);

      await expect(api.get('/test')).rejects.toThrow('An error occurred');
    });

    it('should handle errors with no response or request', async () => {
      const error = new Error('Random error');
      mockAxiosInstance.get.mockRejectedValue(error);

      await expect(api.get('/test')).rejects.toThrow('Random error');
    });

    it('should handle errors with no message', async () => {
      const error = {};
      mockAxiosInstance.get.mockRejectedValue(error);

      await expect(api.get('/test')).rejects.toThrow('An unexpected error occurred');
    });
  });

  describe('Helper Functions', () => {
    describe('createFormData', () => {
      it('should create FormData from object', () => {
        const data = {
          name: 'test',
          age: 25,
          active: true
        };

        const formData = createFormData(data);

        expect(formData).toBeInstanceOf(FormData);
        expect(formData.get('name')).toBe('test');
        expect(formData.get('age')).toBe('25');
        expect(formData.get('active')).toBe('true');
      });

      it('should skip null and undefined values', () => {
        const data = {
          name: 'test',
          nullValue: null,
          undefinedValue: undefined,
          emptyString: ''
        };

        const formData = createFormData(data);

        expect(formData.has('name')).toBe(true);
        expect(formData.has('nullValue')).toBe(false);
        expect(formData.has('undefinedValue')).toBe(false);
        expect(formData.has('emptyString')).toBe(true); // Empty string is valid
      });

      it('should handle nested objects by converting to string', () => {
        const data = {
          user: { id: 1, name: 'John' },
          tags: ['tag1', 'tag2']
        };

        const formData = createFormData(data);

        expect(formData.get('user')).toBe('[object Object]');
        expect(formData.get('tags')).toBe('tag1,tag2');
      });

      it('should handle empty object', () => {
        const formData = createFormData({});
        
        expect(formData).toBeInstanceOf(FormData);
        // FormData iterator isn't fully supported in jsdom, so we can't easily count entries
      });
    });

    describe('createQueryString', () => {
      it('should create query string from object', () => {
        const params = {
          page: 1,
          limit: 10,
          search: 'test query',
          active: true
        };

        const queryString = createQueryString(params);

        expect(queryString).toContain('page=1');
        expect(queryString).toContain('limit=10');
        expect(queryString).toContain('search=test+query');
        expect(queryString).toContain('active=true');
      });

      it('should skip null and undefined values', () => {
        const params = {
          page: 1,
          nullValue: null,
          undefinedValue: undefined,
          emptyString: '',
          zero: 0,
          false: false
        };

        const queryString = createQueryString(params);

        expect(queryString).toContain('page=1');
        expect(queryString).not.toContain('nullValue');
        expect(queryString).not.toContain('undefinedValue');
        expect(queryString).toContain('emptyString=');
        expect(queryString).toContain('zero=0');
        expect(queryString).toContain('false=false');
      });

      it('should handle arrays by converting to string', () => {
        const params = {
          tags: ['tag1', 'tag2', 'tag3'],
          categories: []
        };

        const queryString = createQueryString(params);

        expect(queryString).toContain('tags=tag1%2Ctag2%2Ctag3');
        expect(queryString).toContain('categories=');
      });

      it('should handle special characters', () => {
        const params = {
          search: 'test & query',
          filter: 'price>100'
        };

        const queryString = createQueryString(params);

        expect(queryString).toContain('search=test+%26+query');
        expect(queryString).toContain('filter=price%3E100');
      });

      it('should handle empty object', () => {
        const queryString = createQueryString({});
        expect(queryString).toBe('');
      });

      it('should handle numbers and booleans correctly', () => {
        const params = {
          count: 0,
          price: 99.99,
          active: true,
          disabled: false
        };

        const queryString = createQueryString(params);

        expect(queryString).toContain('count=0');
        expect(queryString).toContain('price=99.99');
        expect(queryString).toContain('active=true');
        expect(queryString).toContain('disabled=false');
      });
    });
  });

  describe('Integration', () => {
    it('should work with real-world API call patterns', async () => {
      const mockResponseData = { 
        data: { 
          products: [{ id: 1, name: 'Product 1' }],
          pagination: { page: 1, total: 1 }
        } 
      };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      // Simulate a typical products API call
      const queryParams = createQueryString({ page: 1, limit: 10, category: 'ai' });
      const result = await api.get(`/products?${queryParams}`);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/products?page=1&limit=10&category=ai', undefined);
      expect(result).toBe(mockResponseData);
    });

    it('should work with form data submission', async () => {
      const mockResponseData = { data: { success: true, id: 123 } };
      const mockResponse = { data: mockResponseData } as AxiosResponse;
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      // Simulate form submission
      const formData = createFormData({ 
        name: 'New Product',
        price: 99.99,
        category: 'tools'
      });
      
      const config = { 
        headers: { 'Content-Type': 'multipart/form-data' }
      };
      
      const result = await api.post('/products', formData, config);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/products', formData, config);
      expect(result).toBe(mockResponseData);
    });
  });

  describe('Edge Cases', () => {
    it('should handle very large query strings', () => {
      const largeParams: Record<string, any> = {};
      for (let i = 0; i < 100; i++) {
        largeParams[`param${i}`] = `value${i}`;
      }

      const queryString = createQueryString(largeParams);

      expect(queryString.length).toBeGreaterThan(1000);
      expect(queryString).toContain('param0=value0');
      expect(queryString).toContain('param99=value99');
    });

    it('should handle FormData with complex data types', () => {
      const complexData = {
        date: new Date('2024-01-01'),
        regex: /test/g,
        func: () => 'test',
        // Skip symbol as it cannot be converted to string in FormData
      };

      const formData = createFormData(complexData);

      expect(formData).toBeInstanceOf(FormData);
      // These will be converted to strings
      expect(typeof formData.get('date')).toBe('string');
      expect(typeof formData.get('regex')).toBe('string');
    });

    it('should handle concurrent API calls', async () => {
      const mockResponseData1 = { data: { id: 1 } };
      const mockResponseData2 = { data: { id: 2 } };
      const mockResponse1 = { data: mockResponseData1 } as AxiosResponse;
      const mockResponse2 = { data: mockResponseData2 } as AxiosResponse;

      mockAxiosInstance.get
        .mockResolvedValueOnce(mockResponse1)
        .mockResolvedValueOnce(mockResponse2);

      const [result1, result2] = await Promise.all([
        api.get('/test/1'),
        api.get('/test/2')
      ]);

      expect(result1).toBe(mockResponseData1);
      expect(result2).toBe(mockResponseData2);
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);
    });
  });
});