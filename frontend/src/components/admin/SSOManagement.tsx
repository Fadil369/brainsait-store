'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { useAppStore } from '@/stores';
import { cn } from '@/lib/utils';

interface SSOConfig {
  id: number;
  provider: string;
  sso_type: string;
  display_name: string;
  description?: string;
  is_active: boolean;
  auto_create_users: boolean;
  enforce_sso: boolean;
  require_group_membership: boolean;
  allowed_groups?: string[];
  created_at: string;
  updated_at: string;
  last_sync?: string;
}

interface SSOManagementProps {
  className?: string;
}

export const SSOManagement: React.FC<SSOManagementProps> = ({ className }) => {
  const [configs, setConfigs] = useState<SSOConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<SSOConfig | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const { language } = useAppStore();

  useEffect(() => {
    fetchSSOConfigs();
  }, []);

  const fetchSSOConfigs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/admin/sso/configs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setConfigs(data);
      }
    } catch (error) {
      // Error handling could be improved with user feedback
    } finally {
      setLoading(false);
    }
  };

  const toggleSSOConfig = async (configId: number, isActive: boolean) => {
    try {
      const response = await fetch(`/api/v1/admin/sso/configs/${configId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ is_active: !isActive }),
      });

      if (response.ok) {
        await fetchSSOConfigs();
      }
    } catch (error) {
      // Error handling could be improved with user feedback
    }
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

  const getSSOTypeColor = (ssoType: string) => {
    const colors: Record<string, string> = {
      'oauth': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      'saml': 'bg-green-500/20 text-green-400 border-green-500/30',
      'ldap': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      'oidc': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    };
    return colors[ssoType] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">
            {language === 'ar' ? 'إدارة تسجيل الدخول المؤسسي' : 'SSO Management'}
          </h1>
          <p className="text-text-secondary mt-2">
            {language === 'ar' 
              ? 'إدارة موفري المصادقة المؤسسية لمؤسستك'
              : 'Manage enterprise authentication providers for your organization'
            }
          </p>
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary-enhanced"
        >
          <span className="mr-2">➕</span>
          {language === 'ar' ? 'إضافة موفر جديد' : 'Add Provider'}
        </Button>
      </div>

      {/* SSO Configurations Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="enhanced-card animate-pulse">
              <div className="h-4 bg-glass-border rounded mb-3"></div>
              <div className="h-8 bg-glass-border rounded mb-2"></div>
              <div className="h-3 bg-glass-border rounded mb-4"></div>
              <div className="flex space-x-2">
                <div className="h-8 bg-glass-border rounded flex-1"></div>
                <div className="h-8 bg-glass-border rounded w-16"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {configs.map((config) => (
            <div key={config.id} className="enhanced-card">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">
                    {getProviderIcon(config.provider)}
                  </span>
                  <div>
                    <h3 className="font-semibold text-text-primary">
                      {config.display_name}
                    </h3>
                    <span className={cn(
                      'text-xs px-2 py-1 rounded-full border',
                      getSSOTypeColor(config.sso_type)
                    )}>
                      {config.sso_type.toUpperCase()}
                    </span>
                  </div>
                </div>
                
                {/* Status Toggle */}
                <button
                  onClick={() => toggleSSOConfig(config.id, config.is_active)}
                  className={cn(
                    'relative w-11 h-6 rounded-full transition-colors duration-200',
                    config.is_active ? 'bg-success' : 'bg-gray-600'
                  )}
                >
                  <div className={cn(
                    'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform duration-200',
                    config.is_active ? 'translate-x-5' : 'translate-x-0'
                  )} />
                </button>
              </div>

              {/* Description */}
              {config.description && (
                <p className="text-sm text-text-secondary mb-4">
                  {config.description}
                </p>
              )}

              {/* Configuration Details */}
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">
                    {language === 'ar' ? 'إنشاء المستخدمين تلقائياً' : 'Auto Create Users'}
                  </span>
                  <span className={config.auto_create_users ? 'text-success' : 'text-error'}>
                    {config.auto_create_users ? '✓' : '✗'}
                  </span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">
                    {language === 'ar' ? 'فرض تسجيل الدخول المؤسسي' : 'Enforce SSO'}
                  </span>
                  <span className={config.enforce_sso ? 'text-success' : 'text-error'}>
                    {config.enforce_sso ? '✓' : '✗'}
                  </span>
                </div>

                {config.allowed_groups && config.allowed_groups.length > 0 && (
                  <div className="text-sm">
                    <span className="text-text-secondary">
                      {language === 'ar' ? 'المجموعات المسموحة:' : 'Allowed Groups:'}
                    </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {config.allowed_groups.slice(0, 2).map((group, index) => (
                        <span key={index} className="text-xs bg-glass-bg px-2 py-1 rounded">
                          {group}
                        </span>
                      ))}
                      {config.allowed_groups.length > 2 && (
                        <span className="text-xs text-text-secondary">
                          +{config.allowed_groups.length - 2} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Last Sync */}
              {config.last_sync && (
                <div className="text-xs text-text-secondary mb-4">
                  {language === 'ar' ? 'آخر مزامنة:' : 'Last Sync:'} {' '}
                  {new Date(config.last_sync).toLocaleDateString()}
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-2">
                <Button
                  onClick={() => {
                    setSelectedConfig(config);
                    setIsEditModalOpen(true);
                  }}
                  variant="outline"
                  size="sm"
                  className="flex-1"
                >
                  {language === 'ar' ? 'تحرير' : 'Edit'}
                </Button>
                <Button
                  onClick={() => {/* Test SSO configuration */}}
                  variant="outline"
                  size="sm"
                  className="px-3"
                  title={language === 'ar' ? 'اختبار الاتصال' : 'Test Connection'}
                >
                  🔧
                </Button>
              </div>
            </div>
          ))}

          {/* Add New Provider Card */}
          <div 
            onClick={() => setIsCreateModalOpen(true)}
            className="enhanced-card border-dashed border-2 border-glass-border hover:border-vision-green cursor-pointer transition-colors duration-200 flex items-center justify-center min-h-[300px]"
          >
            <div className="text-center">
              <div className="text-4xl mb-4">➕</div>
              <h3 className="font-semibold text-text-primary mb-2">
                {language === 'ar' ? 'إضافة موفر SSO' : 'Add SSO Provider'}
              </h3>
              <p className="text-sm text-text-secondary">
                {language === 'ar' 
                  ? 'اضافة موفر مصادقة مؤسسي جديد'
                  : 'Configure a new enterprise authentication provider'
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Create SSO Configuration Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title={language === 'ar' ? 'إضافة موفر SSO جديد' : 'Add New SSO Provider'}
        size="lg"
      >
        <SSOConfigForm
          onSuccess={() => {
            setIsCreateModalOpen(false);
            fetchSSOConfigs();
          }}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      </Modal>

      {/* Edit SSO Configuration Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title={language === 'ar' ? 'تحرير موفر SSO' : 'Edit SSO Provider'}
        size="lg"
      >
        {selectedConfig && (
          <SSOConfigForm
            config={selectedConfig}
            onSuccess={() => {
              setIsEditModalOpen(false);
              fetchSSOConfigs();
            }}
            onCancel={() => setIsEditModalOpen(false)}
          />
        )}
      </Modal>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
        <div className="enhanced-card text-center">
          <div className="text-2xl font-bold text-vision-green">
            {configs.length}
          </div>
          <div className="text-sm text-text-secondary">
            {language === 'ar' ? 'موفرين مُكونين' : 'Configured Providers'}
          </div>
        </div>
        
        <div className="enhanced-card text-center">
          <div className="text-2xl font-bold text-success">
            {configs.filter(c => c.is_active).length}
          </div>
          <div className="text-sm text-text-secondary">
            {language === 'ar' ? 'نشط' : 'Active'}
          </div>
        </div>
        
        <div className="enhanced-card text-center">
          <div className="text-2xl font-bold text-warning">
            {configs.filter(c => c.enforce_sso).length}
          </div>
          <div className="text-sm text-text-secondary">
            {language === 'ar' ? 'مفروض' : 'Enforced'}
          </div>
        </div>
        
        <div className="enhanced-card text-center">
          <div className="text-2xl font-bold text-info">
            {configs.filter(c => c.auto_create_users).length}
          </div>
          <div className="text-sm text-text-secondary">
            {language === 'ar' ? 'إنشاء تلقائي' : 'Auto Create'}
          </div>
        </div>
      </div>
    </div>
  );
};

// SSO Configuration Form Component
interface SSOConfigFormProps {
  config?: SSOConfig;
  onSuccess: () => void;
  onCancel: () => void;
}

const SSOConfigForm: React.FC<SSOConfigFormProps> = ({ config, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    provider: config?.provider || '',
    sso_type: config?.sso_type || 'oauth',
    display_name: config?.display_name || '',
    description: config?.description || '',
    // OAuth fields
    client_id: '',
    client_secret: '',
    authorization_url: '',
    token_url: '',
    user_info_url: '',
    scopes: 'openid profile email',
    // SAML fields
    entity_id: '',
    sso_url: '',
    x509_certificate: '',
    // LDAP fields
    ldap_server: '',
    domain: '',
    base_dn: '',
    // Settings
    auto_create_users: config?.auto_create_users ?? true,
    enforce_sso: config?.enforce_sso ?? false,
    require_group_membership: config?.require_group_membership ?? false,
  });

  const [loading, setLoading] = useState(false);
  const { language } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const url = config 
        ? `/api/v1/admin/sso/configs/${config.id}`
        : '/api/v1/admin/sso/configs';
      
      const method = config ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        onSuccess();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to save SSO configuration');
      }
    } catch (error) {
      // Error handling could be improved with user feedback
      alert('Failed to save SSO configuration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Provider Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            {language === 'ar' ? 'نوع المصادقة' : 'Authentication Type'}
          </label>
          <select
            value={formData.sso_type}
            onChange={(e) => setFormData({ ...formData, sso_type: e.target.value })}
            className="input-enhanced"
            required
          >
            <option value="oauth">OAuth 2.0</option>
            <option value="saml">SAML 2.0</option>
            <option value="ldap">LDAP/Active Directory</option>
            <option value="oidc">OpenID Connect</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            {language === 'ar' ? 'موفر الخدمة' : 'Provider'}
          </label>
          <select
            value={formData.provider}
            onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
            className="input-enhanced"
            required
          >
            <option value="">Select Provider</option>
            <option value="azure_ad">Azure Active Directory</option>
            <option value="google">Google Workspace</option>
            <option value="okta">Okta</option>
            <option value="active_directory">Active Directory</option>
            <option value="onelogin">OneLogin</option>
            <option value="ping_identity">Ping Identity</option>
            <option value="custom">Custom Provider</option>
          </select>
        </div>
      </div>

      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            {language === 'ar' ? 'اسم العرض' : 'Display Name'}
          </label>
          <input
            type="text"
            value={formData.display_name}
            onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
            className="input-enhanced"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            {language === 'ar' ? 'الوصف' : 'Description'}
          </label>
          <input
            type="text"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="input-enhanced"
          />
        </div>
      </div>

      {/* OAuth Configuration */}
      {formData.sso_type === 'oauth' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">OAuth 2.0 Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Client ID</label>
              <input
                type="text"
                value={formData.client_id}
                onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                className="input-enhanced"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Client Secret</label>
              <input
                type="password"
                value={formData.client_secret}
                onChange={(e) => setFormData({ ...formData, client_secret: e.target.value })}
                className="input-enhanced"
                required={!config}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Authorization URL</label>
              <input
                type="url"
                value={formData.authorization_url}
                onChange={(e) => setFormData({ ...formData, authorization_url: e.target.value })}
                className="input-enhanced"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Token URL</label>
              <input
                type="url"
                value={formData.token_url}
                onChange={(e) => setFormData({ ...formData, token_url: e.target.value })}
                className="input-enhanced"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">User Info URL</label>
              <input
                type="url"
                value={formData.user_info_url}
                onChange={(e) => setFormData({ ...formData, user_info_url: e.target.value })}
                className="input-enhanced"
                required
              />
            </div>
          </div>
        </div>
      )}

      {/* Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-text-primary">
          {language === 'ar' ? 'إعدادات' : 'Settings'}
        </h3>
        
        <div className="space-y-3">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.auto_create_users}
              onChange={(e) => setFormData({ ...formData, auto_create_users: e.target.checked })}
              className="rounded border-glass-border"
            />
            <span className="text-text-primary">
              {language === 'ar' ? 'إنشاء المستخدمين تلقائياً' : 'Automatically create users'}
            </span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.enforce_sso}
              onChange={(e) => setFormData({ ...formData, enforce_sso: e.target.checked })}
              className="rounded border-glass-border"
            />
            <span className="text-text-primary">
              {language === 'ar' ? 'فرض تسجيل الدخول المؤسسي' : 'Enforce SSO (disable password login)'}
            </span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.require_group_membership}
              onChange={(e) => setFormData({ ...formData, require_group_membership: e.target.checked })}
              className="rounded border-glass-border"
            />
            <span className="text-text-primary">
              {language === 'ar' ? 'يتطلب عضوية المجموعة' : 'Require group membership'}
            </span>
          </label>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t border-glass-border">
        <Button
          type="button"
          onClick={onCancel}
          variant="outline"
          disabled={loading}
        >
          {language === 'ar' ? 'إلغاء' : 'Cancel'}
        </Button>
        <Button
          type="submit"
          className="btn-primary-enhanced"
          disabled={loading}
        >
          {loading ? (
            <div className="loading-enhanced mr-2" />
          ) : null}
          {config 
            ? (language === 'ar' ? 'تحديث' : 'Update')
            : (language === 'ar' ? 'إنشاء' : 'Create')
          }
        </Button>
      </div>
    </form>
  );
};