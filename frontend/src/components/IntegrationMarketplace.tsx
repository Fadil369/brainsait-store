'use client';

import React, { useEffect, useState } from 'react';
import { 
  Cog6ToothIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  XCircleIcon,
  PlayIcon,
  TrashIcon,
  ChartBarIcon,
  DocumentIcon
} from '@heroicons/react/24/outline';

interface Integration {
  id: string;
  name: string;
  description: string;
  category: string;
  vendor: string;
  icon: string;
  pricing: string;
  features: string[];
  supported_events: string[];
  setup_complexity: string;
  status: string;
  rating: number;
  installs: number;
  documentation_url: string;
  webhook_url: string;
  oauth_required: boolean;
  configuration_fields?: ConfigField[];
}

interface ConfigField {
  name: string;
  label: string;
  type: string;
  required: boolean;
}

interface InstalledIntegration {
  id: string;
  name: string;
  status: string;
  installed_at: string;
  last_sync?: string;
  sync_count: number;
  health_status: string;
}

interface IntegrationMarketplaceProps {
  apiEndpoint?: string;
  onIntegrationInstall?: (integration: Integration) => void;
  onIntegrationUninstall?: (integrationId: string) => void;
  className?: string;
}

const IntegrationMarketplace: React.FC<IntegrationMarketplaceProps> = ({
  apiEndpoint = '/api/v1/integrations/marketplace',
  onIntegrationInstall,
  onIntegrationUninstall,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'marketplace' | 'installed' | 'analytics'>('marketplace');
  const [availableIntegrations, setAvailableIntegrations] = useState<Integration[]>([]);
  const [installedIntegrations, setInstalledIntegrations] = useState<InstalledIntegration[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [installLoading, setInstallLoading] = useState<Set<string>>(new Set());
  const [showConfigModal, setShowConfigModal] = useState<Integration | null>(null);
  const [configuration, setConfiguration] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchAvailableIntegrations(),
        fetchInstalledIntegrations(),
        fetchCategories()
      ]);
    } catch (error) {
      console.error('Error fetching marketplace data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableIntegrations = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/marketplace`);
      if (response.ok) {
        const data = await response.json();
        setAvailableIntegrations(data);
      }
    } catch (error) {
      console.error('Error fetching available integrations:', error);
    }
  };

  const fetchInstalledIntegrations = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/installed`);
      if (response.ok) {
        const data = await response.json();
        setInstalledIntegrations(data);
      }
    } catch (error) {
      console.error('Error fetching installed integrations:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/categories`);
      if (response.ok) {
        const result = await response.json();
        setCategories(result.data || []);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const isInstalled = (integrationId: string) => {
    return installedIntegrations.some(i => i.id === integrationId);
  };

  const handleInstallClick = (integration: Integration) => {
    if (integration.configuration_fields && integration.configuration_fields.length > 0) {
      setShowConfigModal(integration);
      // Initialize configuration with empty values
      const initialConfig = integration.configuration_fields.reduce((acc, field) => {
        acc[field.name] = '';
        return acc;
      }, {} as Record<string, string>);
      setConfiguration(initialConfig);
    } else {
      installIntegration(integration.id, {});
    }
  };

  const installIntegration = async (integrationId: string, config: Record<string, string>) => {
    setInstallLoading(prev => new Set(prev).add(integrationId));
    
    try {
      const response = await fetch(`${apiEndpoint}/install/${integrationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          configuration: config
        })
      });

      if (response.ok) {
        const result = await response.json();
        await fetchInstalledIntegrations();
        setShowConfigModal(null);
        setConfiguration({});
        
        const integration = availableIntegrations.find(i => i.id === integrationId);
        if (integration && onIntegrationInstall) {
          onIntegrationInstall(integration);
        }
      } else {
        const error = await response.json();
        alert(`Failed to install integration: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error installing integration:', error);
      alert('Failed to install integration');
    } finally {
      setInstallLoading(prev => {
        const newSet = new Set(prev);
        newSet.delete(integrationId);
        return newSet;
      });
    }
  };

  const uninstallIntegration = async (integrationId: string) => {
    if (!confirm('Are you sure you want to uninstall this integration?')) {
      return;
    }

    try {
      const response = await fetch(`${apiEndpoint}/uninstall/${integrationId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchInstalledIntegrations();
        if (onIntegrationUninstall) {
          onIntegrationUninstall(integrationId);
        }
      } else {
        const error = await response.json();
        alert(`Failed to uninstall integration: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error uninstalling integration:', error);
      alert('Failed to uninstall integration');
    }
  };

  const testWebhook = async (integrationId: string) => {
    try {
      const response = await fetch(`${apiEndpoint}/test-webhook/${integrationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: 'test'
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message || 'Webhook test completed successfully');
      } else {
        const error = await response.json();
        alert(`Webhook test failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error testing webhook:', error);
      alert('Failed to test webhook');
    }
  };

  const filteredIntegrations = availableIntegrations.filter(integration => {
    const matchesCategory = selectedCategory === 'all' || integration.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      integration.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      integration.vendor.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesCategory && matchesSearch;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <Cog6ToothIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPricingBadge = (pricing: string) => {
    const colors = {
      free: 'bg-green-100 text-green-800',
      freemium: 'bg-blue-100 text-blue-800',
      premium: 'bg-purple-100 text-purple-800',
      transaction_fee: 'bg-orange-100 text-orange-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[pricing as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {pricing.charAt(0).toUpperCase() + pricing.slice(1).replace('_', ' ')}
      </span>
    );
  };

  const getComplexityBadge = (complexity: string) => {
    const colors = {
      easy: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      advanced: 'bg-red-100 text-red-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[complexity as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {complexity.charAt(0).toUpperCase() + complexity.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className={`integration-marketplace ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-300 h-64 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`integration-marketplace ${className}`}>
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('marketplace')}
          className={`px-4 py-2 rounded-md transition-all ${
            activeTab === 'marketplace'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Marketplace
        </button>
        <button
          onClick={() => setActiveTab('installed')}
          className={`px-4 py-2 rounded-md transition-all ${
            activeTab === 'installed'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Installed ({installedIntegrations.length})
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`px-4 py-2 rounded-md transition-all ${
            activeTab === 'analytics'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Analytics
        </button>
      </div>

      {/* Marketplace Tab */}
      {activeTab === 'marketplace' && (
        <div>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search integrations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Categories</option>
                {categories.map((category) => (
                  <option key={category.name} value={category.name}>
                    {category.name.charAt(0).toUpperCase() + category.name.slice(1)} ({category.count})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Integration Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredIntegrations.map((integration) => (
              <div key={integration.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <img
                        src={integration.icon}
                        alt={integration.name}
                        className="w-12 h-12 rounded-lg"
                        onError={(e) => {
                          e.currentTarget.src = 'https://via.placeholder.com/48';
                        }}
                      />
                      <div>
                        <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                        <p className="text-sm text-gray-500">{integration.vendor}</p>
                      </div>
                    </div>
                    {isInstalled(integration.id) && (
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {integration.description}
                  </p>

                  {/* Badges */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {getPricingBadge(integration.pricing)}
                    {getComplexityBadge(integration.setup_complexity)}
                  </div>

                  {/* Features */}
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Key Features:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {integration.features.slice(0, 3).map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>⭐ {integration.rating}</span>
                    <span>{integration.installs.toLocaleString()} installs</span>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    {isInstalled(integration.id) ? (
                      <button
                        onClick={() => uninstallIntegration(integration.id)}
                        className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center"
                      >
                        <TrashIcon className="h-4 w-4 mr-2" />
                        Uninstall
                      </button>
                    ) : (
                      <button
                        onClick={() => handleInstallClick(integration)}
                        disabled={installLoading.has(integration.id)}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {installLoading.has(integration.id) ? 'Installing...' : 'Install'}
                      </button>
                    )}
                    <a
                      href={integration.documentation_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      📖
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Installed Tab */}
      {activeTab === 'installed' && (
        <div>
          {installedIntegrations.length === 0 ? (
            <div className="text-center py-12">
              <Cog6ToothIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">No integrations installed</h3>
              <p className="text-gray-500 mb-6">Browse the marketplace to install your first integration</p>
              <button
                onClick={() => setActiveTab('marketplace')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Browse Marketplace
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {installedIntegrations.map((integration) => (
                <div key={integration.id} className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(integration.health_status)}
                        <div>
                          <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                          <p className="text-sm text-gray-500">
                            Installed {new Date(integration.installed_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-sm text-gray-600">
                        <p>{integration.sync_count} syncs</p>
                        {integration.last_sync && (
                          <p>Last sync: {new Date(integration.last_sync).toLocaleString()}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => testWebhook(integration.id)}
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center"
                      >
                        <PlayIcon className="h-4 w-4 mr-1" />
                        Test
                      </button>
                      <button
                        onClick={() => uninstallIntegration(integration.id)}
                        className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center"
                      >
                        <TrashIcon className="h-4 w-4 mr-1" />
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="text-center py-12">
          <ChartBarIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-medium text-gray-900 mb-2">Integration Analytics</h3>
          <p className="text-gray-500">Coming soon - Detailed analytics for your integrations</p>
        </div>
      )}

      {/* Configuration Modal */}
      {showConfigModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Configure {showConfigModal.name}</h3>
            <div className="space-y-4">
              {showConfigModal.configuration_fields?.map((field) => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {field.label} {field.required && <span className="text-red-500">*</span>}
                  </label>
                  <input
                    type={field.type === 'password' ? 'password' : 'text'}
                    value={configuration[field.name] || ''}
                    onChange={(e) => setConfiguration(prev => ({
                      ...prev,
                      [field.name]: e.target.value
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required={field.required}
                  />
                </div>
              ))}
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowConfigModal(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => installIntegration(showConfigModal.id, configuration)}
                disabled={installLoading.has(showConfigModal.id)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {installLoading.has(showConfigModal.id) ? 'Installing...' : 'Install'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrationMarketplace;