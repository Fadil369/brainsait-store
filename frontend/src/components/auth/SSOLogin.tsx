'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/stores';
import { cn } from '@/lib/utils';

interface SSOProvider {
  provider: string;
  sso_type: string;
  display_name: string;
  login_url: string;
}

interface SSOLoginProps {
  tenantId?: string;
  onSuccess?: (_token: string) => void;
  onError?: (_error: string) => void;
  className?: string;
}

export const SSOLogin: React.FC<SSOLoginProps> = ({
  tenantId,
  onSuccess,
  onError,
  className
}) => {
  const [providers, setProviders] = useState<SSOProvider[]>([]);
  const [loading, setLoading] = useState(false);
  const { language } = useAppStore();

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const response = await fetch('/api/v1/auth/sso/providers', {
          headers: {
            'X-Tenant-ID': tenantId || 'default',
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          setProviders(data);
        }
      } catch (error) {
        if (onError) {
          onError(error instanceof Error ? error.message : 'Failed to fetch SSO providers');
        }
      }
    };

    fetchProviders();
  }, [tenantId, onError]);

  const handleSSOLogin = (provider: SSOProvider) => {
    setLoading(true);
    
    // Store callback handlers in sessionStorage for after redirect
    if (onSuccess) {
      sessionStorage.setItem('sso_success_callback', 'true');
    }
    
    // Redirect to SSO provider
    window.location.href = provider.login_url;
  };

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      'azure_ad': '🏢',
      'google': '🔍',
      'okta': '🔐',
      'active_directory': '🏢',
      'onelogin': '🔑',
      'ping_identity': '🏓',
      'custom': '🔒',
    };
    return icons[provider] || '🔐';
  };

  const getProviderColor = (provider: string) => {
    const colors: Record<string, string> = {
      'azure_ad': 'from-blue-600 to-blue-700',
      'google': 'from-red-500 to-red-600',
      'okta': 'from-blue-500 to-blue-600',
      'active_directory': 'from-gray-600 to-gray-700',
      'onelogin': 'from-purple-600 to-purple-700',
      'ping_identity': 'from-green-600 to-green-700',
      'custom': 'from-gray-600 to-gray-800',
    };
    return colors[provider] || 'from-gray-600 to-gray-700';
  };

  if (providers.length === 0) {
    return null;
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          {language === 'ar' ? 'تسجيل الدخول المؤسسي' : 'Enterprise Login'}
        </h3>
        <p className="text-sm text-text-secondary">
          {language === 'ar' 
            ? 'استخدم حساب شركتك للدخول'
            : 'Use your organization account to sign in'
          }
        </p>
      </div>

      <div className="space-y-3">
        {providers.map((provider) => (
          <Button
            key={provider.provider}
            onClick={() => handleSSOLogin(provider)}
            disabled={loading}
            className={cn(
              'w-full h-12 text-left justify-start relative overflow-hidden',
              'bg-gradient-to-r text-white border-0',
              getProviderColor(provider.provider),
              'hover:shadow-lg hover:scale-105 transition-all duration-200',
              'group'
            )}
          >
            {/* Background animation */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
            
            {/* Content */}
            <div className="flex items-center space-x-3 relative z-10">
              <span className="text-2xl">
                {getProviderIcon(provider.provider)}
              </span>
              <div>
                <div className="font-semibold">
                  {language === 'ar' 
                    ? `الدخول عبر ${provider.display_name}`
                    : `Sign in with ${provider.display_name}`
                  }
                </div>
                <div className="text-xs opacity-90">
                  {provider.sso_type.toUpperCase()} 
                  {language === 'ar' ? ' مصادقة' : ' Authentication'}
                </div>
              </div>
            </div>
            
            {/* Loading indicator */}
            {loading && (
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              </div>
            )}
          </Button>
        ))}
      </div>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-glass-border" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-dark text-text-secondary">
            {language === 'ar' ? 'أو' : 'or'}
          </span>
        </div>
      </div>
    </div>
  );
};

// SSO Callback Handler Component
export const SSOCallbackHandler: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    handleSSOCallback();
  }, []);

  const handleSSOCallback = async () => {
    try {
      // Get token from URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      const error = urlParams.get('error');

      if (error) {
        setStatus('error');
        setMessage(decodeURIComponent(error));
        return;
      }

      if (token) {
        // Store token
        localStorage.setItem('access_token', token);
        
        // Trigger success callback if stored
        const hasCallback = sessionStorage.getItem('sso_success_callback');
        if (hasCallback) {
          sessionStorage.removeItem('sso_success_callback');
        }

        setStatus('success');
        setMessage('Successfully authenticated');
        
        // Redirect to dashboard after delay
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
      } else {
        setStatus('error');
        setMessage('No authentication token received');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Authentication failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark">
      <div className="max-w-md w-full mx-auto p-6">
        <div className="text-center">
          {status === 'loading' && (
            <>
              <div className="w-16 h-16 border-4 border-vision-green/30 border-t-vision-green rounded-full animate-spin mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-text-primary mb-2">
                Processing Authentication
              </h2>
              <p className="text-text-secondary">
                Please wait while we complete your login...
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-16 h-16 bg-success rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-text-primary mb-2">
                Authentication Successful
              </h2>
              <p className="text-text-secondary">
                {message}. Redirecting to dashboard...
              </p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 bg-error rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-text-primary mb-2">
                Authentication Failed
              </h2>
              <p className="text-text-secondary mb-4">
                {message}
              </p>
              <Button
                onClick={() => window.location.href = '/login'}
                className="btn-primary-enhanced"
              >
                Try Again
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};