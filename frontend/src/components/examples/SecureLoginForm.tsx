/**
 * Example React component demonstrating secure form validation
 */

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, type LoginFormData } from '../../lib/validation';
import SecurityUtils from '../../lib/security';

const { XSSProtection, APISecurity, SessionSecurity } = SecurityUtils;

export const SecureLoginForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      // Check rate limiting
      if (!APISecurity.checkRateLimit('/api/v1/auth/login')) {
        throw new Error('Too many requests. Please try again later.');
      }

      // Update session activity
      SessionSecurity.updateActivity();

      // Make secure API call
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: APISecurity.getSecureHeaders(false),
        body: JSON.stringify(data),
      });

      // Validate response
      APISecurity.validateResponse(response);

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const result = await response.json();
      
      // Handle successful login
      console.log('Login successful:', result);
      
    } catch (error) {
      console.error('Login error:', error);
      // Handle error appropriately
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          placeholder="Enter your email"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          type="password"
          {...register('password')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          placeholder="Enter your password"
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            {...register('rememberMe')}
            className="rounded"
          />
          <span className="ml-2 text-sm">Remember me</span>
        </label>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isSubmitting ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  );
};

export default SecureLoginForm;