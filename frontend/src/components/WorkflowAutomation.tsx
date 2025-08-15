'use client';

import React, { useEffect, useState } from 'react';
import { 
  Cog6ToothIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  XCircleIcon,
  PlayIcon,
  PauseIcon,
  TrashIcon,
  ChartBarIcon,
  ClockIcon,
  BoltIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  trigger_events: string[];
  actions: string[];
  complexity: string;
  estimated_time_saved: string;
  status: string;
  usage_count: number;
  success_rate: number;
  configuration?: any;
}

interface ActiveWorkflow {
  id: string;
  template_id: string;
  name: string;
  status: string;
  created_at: string;
  last_run?: string;
  runs_count: number;
  success_rate: number;
  performance?: {
    avg_execution_time: number;
    errors_last_week: number;
    time_saved_hours: number;
  };
}

interface WorkflowAutomationProps {
  apiEndpoint?: string;
  onWorkflowCreate?: (workflow: ActiveWorkflow) => void;
  onWorkflowDelete?: (workflowId: string) => void;
  className?: string;
}

const WorkflowAutomation: React.FC<WorkflowAutomationProps> = ({
  apiEndpoint = '/api/v1/workflows',
  onWorkflowCreate,
  onWorkflowDelete,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'templates' | 'active' | 'analytics'>('active');
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [activeWorkflows, setActiveWorkflows] = useState<ActiveWorkflow[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [createLoading, setCreateLoading] = useState<Set<string>>(new Set());
  const [showConfigModal, setShowConfigModal] = useState<WorkflowTemplate | null>(null);
  const [configuration, setConfiguration] = useState<Record<string, any>>({});
  const [workflowName, setWorkflowName] = useState<string>('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchTemplates(),
        fetchActiveWorkflows(),
        fetchCategories()
      ]);
    } catch (error) {
      console.error('Error fetching workflow data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchActiveWorkflows = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/active`);
      if (response.ok) {
        const data = await response.json();
        setActiveWorkflows(data);
      }
    } catch (error) {
      console.error('Error fetching active workflows:', error);
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

  const handleCreateClick = (template: WorkflowTemplate) => {
    setShowConfigModal(template);
    setWorkflowName(`${template.name} - ${new Date().toLocaleDateString()}`);
    
    // Initialize configuration with default values
    const initialConfig = template.configuration || {};
    setConfiguration(initialConfig);
  };

  const createWorkflow = async () => {
    if (!showConfigModal || !workflowName.trim()) {
      alert('Please provide a workflow name');
      return;
    }

    setCreateLoading(prev => new Set(prev).add(showConfigModal.id));
    
    try {
      const response = await fetch(`${apiEndpoint}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: showConfigModal.id,
          name: workflowName,
          configuration: configuration
        })
      });

      if (response.ok) {
        const result = await response.json();
        await fetchActiveWorkflows();
        setShowConfigModal(null);
        setConfiguration({});
        setWorkflowName('');
        
        if (onWorkflowCreate) {
          // Would get the created workflow data from the response
          onWorkflowCreate(result.data as ActiveWorkflow);
        }
      } else {
        const error = await response.json();
        alert(`Failed to create workflow: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
      alert('Failed to create workflow');
    } finally {
      setCreateLoading(prev => {
        const newSet = new Set(prev);
        newSet.delete(showConfigModal.id);
        return newSet;
      });
    }
  };

  const deleteWorkflow = async (workflowId: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) {
      return;
    }

    try {
      const response = await fetch(`${apiEndpoint}/${workflowId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchActiveWorkflows();
        if (onWorkflowDelete) {
          onWorkflowDelete(workflowId);
        }
      } else {
        const error = await response.json();
        alert(`Failed to delete workflow: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error deleting workflow:', error);
      alert('Failed to delete workflow');
    }
  };

  const triggerWorkflow = async (workflowId: string) => {
    try {
      const response = await fetch(`${apiEndpoint}/${workflowId}/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: 'manual_trigger',
          event_data: {
            triggered_by: 'user',
            timestamp: new Date().toISOString()
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert('Workflow triggered successfully!');
        await fetchActiveWorkflows();
      } else {
        const error = await response.json();
        alert(`Failed to trigger workflow: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error triggering workflow:', error);
      alert('Failed to trigger workflow');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'paused':
        return <PauseIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <Cog6ToothIcon className="h-5 w-5 text-gray-500" />;
    }
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

  const getCategoryBadge = (category: string) => {
    const colors = {
      customer_management: 'bg-blue-100 text-blue-800',
      order_management: 'bg-purple-100 text-purple-800',
      marketing: 'bg-pink-100 text-pink-800',
      customer_support: 'bg-indigo-100 text-indigo-800',
      inventory: 'bg-orange-100 text-orange-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {category.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
      </span>
    );
  };

  const filteredTemplates = templates.filter(template => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesCategory && matchesSearch;
  });

  if (loading) {
    return (
      <div className={`workflow-automation ${className}`}>
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
    <div className={`workflow-automation ${className}`}>
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('active')}
          className={`px-4 py-2 rounded-md transition-all ${
            activeTab === 'active'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Active Workflows ({activeWorkflows.length})
        </button>
        <button
          onClick={() => setActiveTab('templates')}
          className={`px-4 py-2 rounded-md transition-all ${
            activeTab === 'templates'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Templates ({templates.length})
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

      {/* Active Workflows Tab */}
      {activeTab === 'active' && (
        <div>
          {activeWorkflows.length === 0 ? (
            <div className="text-center py-12">
              <BoltIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">No active workflows</h3>
              <p className="text-gray-500 mb-6">Create your first workflow from our templates</p>
              <button
                onClick={() => setActiveTab('templates')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Browse Templates
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {activeWorkflows.map((workflow) => (
                <div key={workflow.id} className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(workflow.status)}
                        <div>
                          <h3 className="font-semibold text-gray-900">{workflow.name}</h3>
                          <p className="text-sm text-gray-500">
                            Created {new Date(workflow.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-sm text-gray-600">
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center">
                            <ArrowPathIcon className="h-4 w-4 mr-1" />
                            <span>{workflow.runs_count} runs</span>
                          </div>
                          <div className="flex items-center">
                            <ChartBarIcon className="h-4 w-4 mr-1" />
                            <span>{workflow.success_rate.toFixed(1)}% success</span>
                          </div>
                          {workflow.last_run && (
                            <div className="flex items-center">
                              <ClockIcon className="h-4 w-4 mr-1" />
                              <span>Last: {new Date(workflow.last_run).toLocaleString()}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => triggerWorkflow(workflow.id)}
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center"
                      >
                        <PlayIcon className="h-4 w-4 mr-1" />
                        Trigger
                      </button>
                      <button
                        onClick={() => deleteWorkflow(workflow.id)}
                        className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center"
                      >
                        <TrashIcon className="h-4 w-4 mr-1" />
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search templates..."
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
                    {category.name.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())} ({category.count})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Template Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <div key={template.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">{template.name}</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">{template.description}</p>
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {getCategoryBadge(template.category)}
                    {getComplexityBadge(template.complexity)}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      <span>{template.estimated_time_saved}</span>
                    </div>
                    <div className="flex items-center">
                      <ChartBarIcon className="h-4 w-4 mr-1" />
                      <span>{template.success_rate}% success</span>
                    </div>
                  </div>

                  {/* Trigger Events */}
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Triggers:</h4>
                    <div className="flex flex-wrap gap-1">
                      {template.trigger_events.slice(0, 3).map((event, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          {event}
                        </span>
                      ))}
                      {template.trigger_events.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          +{template.trigger_events.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Usage Stats */}
                  <div className="text-sm text-gray-500 mb-4">
                    {template.usage_count} organizations using this template
                  </div>

                  {/* Action Button */}
                  <button
                    onClick={() => handleCreateClick(template)}
                    disabled={createLoading.has(template.id)}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createLoading.has(template.id) ? 'Creating...' : 'Create Workflow'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="text-center py-12">
          <ChartBarIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-medium text-gray-900 mb-2">Workflow Analytics</h3>
          <p className="text-gray-500">
            {activeWorkflows.length > 0 
              ? `Monitoring ${activeWorkflows.length} active workflows`
              : 'Create workflows to see analytics'
            }
          </p>
          {activeWorkflows.length > 0 && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Total Runs</h4>
                <p className="text-3xl font-bold text-blue-600">
                  {activeWorkflows.reduce((sum, w) => sum + w.runs_count, 0)}
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Average Success Rate</h4>
                <p className="text-3xl font-bold text-green-600">
                  {(activeWorkflows.reduce((sum, w) => sum + w.success_rate, 0) / activeWorkflows.length).toFixed(1)}%
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Time Saved</h4>
                <p className="text-3xl font-bold text-purple-600">
                  {Math.round(activeWorkflows.reduce((sum, w) => sum + (w.performance?.time_saved_hours || 0), 0))}h
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Configuration Modal */}
      {showConfigModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create Workflow: {showConfigModal.name}</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Workflow Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={workflowName}
                  onChange={(e) => setWorkflowName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter workflow name"
                />
              </div>
              
              <div className="text-sm text-gray-600">
                <p><strong>Category:</strong> {showConfigModal.category.replace('_', ' ')}</p>
                <p><strong>Complexity:</strong> {showConfigModal.complexity}</p>
                <p><strong>Expected Time Saved:</strong> {showConfigModal.estimated_time_saved}</p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowConfigModal(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createWorkflow}
                disabled={createLoading.has(showConfigModal.id) || !workflowName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {createLoading.has(showConfigModal.id) ? 'Creating...' : 'Create Workflow'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowAutomation;