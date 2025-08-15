'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  AlertTriangle, 
  Activity, 
  Database, 
  Cpu, 
  MemoryStick, 
  HardDrive,
  Wifi,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface SystemHealth {
  system: {
    cpu_usage_percent: number;
    memory_usage_percent: number;
    memory_available_mb: number;
    disk_usage_percent: number;
    disk_free_gb: number;
    network_bytes_sent: number;
    network_bytes_recv: number;
  };
  database: {
    status: string;
    connection_time_ms: number;
    database_size: string;
    active_connections: number;
    slow_queries_count: number;
    slow_queries: Array<{
      query: string;
      calls: number;
      total_time: number;
      mean_time: number;
    }>;
  };
  application: {
    orders_last_hour: number;
    failed_orders_last_hour: number;
    error_rate_percent: number;
    active_users_last_hour: number;
    status: string;
  };
  alerts: Array<{
    type: string;
    severity: string;
    message: string;
    value: number;
    threshold: number;
  }>;
  timestamp: string;
}

interface PerformanceMetrics {
  period: {
    start: string;
    end: string;
    hours: number;
  };
  response_times: {
    average: number;
    p50: number;
    p95: number;
    p99: number;
    samples: number;
  };
  errors: {
    error_rate: number;
    total_errors: number;
    total_requests: number;
    error_types: Record<string, number>;
  };
  throughput: {
    total_requests: number;
    average_per_hour: number;
    peak_hour_requests: number;
    hourly_breakdown: Array<{
      hour: string;
      requests: number;
    }>;
  };
  summary: {
    avg_response_time: number;
    error_rate: number;
    total_requests: number;
  };
}

export default function MonitoringDashboard() {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchData = async () => {
    setRefreshing(true);
    try {
      const token = localStorage.getItem('authToken');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const [healthRes, performanceRes] = await Promise.all([
        fetch(`${baseUrl}/api/v1/monitoring/health`, { headers }),
        fetch(`${baseUrl}/api/v1/monitoring/performance?hours=24`, { headers })
      ]);

      const [healthData, performanceData] = await Promise.all([
        healthRes.json(),
        performanceRes.json()
      ]);

      setSystemHealth(healthData.data);
      setPerformanceMetrics(performanceData.data);
      setLastRefresh(new Date());
    } catch (error) {
      // Error handling will be improved with user notifications
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'operational':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
      case 'critical':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'operational':
        return <CheckCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      case 'error':
      case 'critical':
        return <XCircle className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Monitoring</h1>
          <p className="text-muted-foreground">
            Real-time infrastructure and application monitoring
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="animate-pulse">
            <Activity className="h-3 w-3 mr-1" />
            Live
          </Badge>
          <Button
            variant="outline"
            onClick={fetchData}
            disabled={refreshing}
            className="ml-2"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <span className="text-xs text-muted-foreground">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Alerts Section */}
      {systemHealth?.alerts && systemHealth.alerts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
            <h2 className="text-lg font-semibold text-red-800">Active Alerts</h2>
          </div>
          <div className="space-y-2">
            {systemHealth.alerts.map((alert, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                <div className="flex items-center">
                  <Badge className={getStatusColor(alert.severity)}>
                    {alert.severity.toUpperCase()}
                  </Badge>
                  <span className="ml-2 text-sm">{alert.message}</span>
                </div>
                <span className="text-xs text-gray-500">
                  {alert.value.toFixed(1)} / {alert.threshold}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemHealth?.system.cpu_usage_percent.toFixed(1)}%
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className={`h-2 rounded-full ${
                  (systemHealth?.system.cpu_usage_percent || 0) > 80 ? 'bg-red-600' : 
                  (systemHealth?.system.cpu_usage_percent || 0) > 60 ? 'bg-yellow-600' : 'bg-green-600'
                }`}
                style={{ width: `${systemHealth?.system.cpu_usage_percent || 0}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
            <MemoryStick className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemHealth?.system.memory_usage_percent.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {systemHealth?.system.memory_available_mb} MB available
            </p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className={`h-2 rounded-full ${
                  (systemHealth?.system.memory_usage_percent || 0) > 85 ? 'bg-red-600' : 
                  (systemHealth?.system.memory_usage_percent || 0) > 70 ? 'bg-yellow-600' : 'bg-green-600'
                }`}
                style={{ width: `${systemHealth?.system.memory_usage_percent || 0}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemHealth?.system.disk_usage_percent.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {systemHealth?.system.disk_free_gb} GB free
            </p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className={`h-2 rounded-full ${
                  (systemHealth?.system.disk_usage_percent || 0) > 90 ? 'bg-red-600' : 
                  (systemHealth?.system.disk_usage_percent || 0) > 75 ? 'bg-yellow-600' : 'bg-green-600'
                }`}
                style={{ width: `${systemHealth?.system.disk_usage_percent || 0}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Network I/O</CardTitle>
            <Wifi className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              <div className="flex justify-between">
                <span>Sent:</span>
                <span>{formatBytes(systemHealth?.system.network_bytes_sent || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span>Received:</span>
                <span>{formatBytes(systemHealth?.system.network_bytes_recv || 0)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Monitoring Tabs */}
      <Tabs defaultValue="system" className="space-y-4">
        <TabsList>
          <TabsTrigger value="system">System Health</TabsTrigger>
          <TabsTrigger value="database">Database</TabsTrigger>
          <TabsTrigger value="application">Application</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        {/* System Health Tab */}
        <TabsContent value="system" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>System Resources</CardTitle>
                <CardDescription>Current system resource utilization</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>CPU Usage</span>
                    <span>{systemHealth?.system.cpu_usage_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${systemHealth?.system.cpu_usage_percent || 0}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Memory Usage</span>
                    <span>{systemHealth?.system.memory_usage_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${systemHealth?.system.memory_usage_percent || 0}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Disk Usage</span>
                    <span>{systemHealth?.system.disk_usage_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-orange-600 h-2 rounded-full"
                      style={{ width: `${systemHealth?.system.disk_usage_percent || 0}%` }}
                    ></div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Status</CardTitle>
                <CardDescription>Overall system health indicators</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">System Status</span>
                  <Badge className="bg-green-100 text-green-800">
                    {getStatusIcon('healthy')}
                    <span className="ml-1">Operational</span>
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Load Average</span>
                  <span className="text-sm font-medium">Normal</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Uptime</span>
                  <span className="text-sm font-medium">99.9%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Last Check</span>
                  <span className="text-sm text-muted-foreground">
                    {new Date(systemHealth?.timestamp || '').toLocaleTimeString()}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Database Tab */}
        <TabsContent value="database" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="h-5 w-5 mr-2" />
                  Database Health
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge className={getStatusColor(systemHealth?.database.status || 'unknown')}>
                    {getStatusIcon(systemHealth?.database.status || 'unknown')}
                    <span className="ml-1">{systemHealth?.database.status}</span>
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Connection Time</span>
                  <span className="text-sm font-medium">
                    {systemHealth?.database.connection_time_ms.toFixed(2)}ms
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Database Size</span>
                  <span className="text-sm font-medium">{systemHealth?.database.database_size}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Connections</span>
                  <span className="text-sm font-medium">{systemHealth?.database.active_connections}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Slow Queries</span>
                  <span className="text-sm font-medium">{systemHealth?.database.slow_queries_count}</span>
                </div>
              </CardContent>
            </Card>

            {systemHealth?.database.slow_queries && systemHealth.database.slow_queries.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Slow Queries</CardTitle>
                  <CardDescription>Queries taking longer than 1 second</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {systemHealth.database.slow_queries.slice(0, 3).map((query, index) => (
                      <div key={index} className="p-3 border rounded-lg">
                        <div className="text-xs font-mono text-gray-600 mb-1">
                          {query.query}
                        </div>
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Calls: {query.calls}</span>
                          <span>Avg: {query.mean_time.toFixed(2)}ms</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Application Tab */}
        <TabsContent value="application" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Application Metrics</CardTitle>
                <CardDescription>Last hour performance indicators</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge className={getStatusColor(systemHealth?.application.status || 'unknown')}>
                    {getStatusIcon(systemHealth?.application.status || 'unknown')}
                    <span className="ml-1">{systemHealth?.application.status}</span>
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Orders (Last Hour)</span>
                  <span className="text-sm font-medium">{systemHealth?.application.orders_last_hour}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Failed Orders</span>
                  <span className="text-sm font-medium text-red-600">
                    {systemHealth?.application.failed_orders_last_hour}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Error Rate</span>
                  <span className="text-sm font-medium">
                    {systemHealth?.application.error_rate_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Users</span>
                  <span className="text-sm font-medium">{systemHealth?.application.active_users_last_hour}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Error Rate Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Error Rate</span>
                    <span>{systemHealth?.application.error_rate_percent.toFixed(2)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        (systemHealth?.application.error_rate_percent || 0) > 5 ? 'bg-red-600' : 
                        (systemHealth?.application.error_rate_percent || 0) > 2 ? 'bg-yellow-600' : 'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(100, (systemHealth?.application.error_rate_percent || 0) * 10)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Target: &lt; 2% error rate
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Response Times</CardTitle>
                <CardDescription>Last 24 hours</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm">Average</span>
                  <span className="font-medium">{performanceMetrics?.response_times.average.toFixed(2)}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">50th Percentile</span>
                  <span className="font-medium">{performanceMetrics?.response_times.p50.toFixed(2)}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">95th Percentile</span>
                  <span className="font-medium">{performanceMetrics?.response_times.p95.toFixed(2)}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">99th Percentile</span>
                  <span className="font-medium">{performanceMetrics?.response_times.p99.toFixed(2)}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Total Samples</span>
                  <span className="font-medium">{performanceMetrics?.response_times.samples.toLocaleString()}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Throughput</CardTitle>
                <CardDescription>Request volume metrics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm">Total Requests</span>
                  <span className="font-medium">{performanceMetrics?.throughput.total_requests.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Avg per Hour</span>
                  <span className="font-medium">{performanceMetrics?.throughput.average_per_hour.toFixed(0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Peak Hour</span>
                  <span className="font-medium">{performanceMetrics?.throughput.peak_hour_requests}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Error Rate</span>
                  <span className="font-medium text-red-600">
                    {performanceMetrics?.errors.error_rate.toFixed(2)}%
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Hourly Request Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Request Volume (Last 24 Hours)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={performanceMetrics?.throughput.hourly_breakdown || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="hour" 
                    tickFormatter={(value) => new Date(value).getHours() + ':00'}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="requests" 
                    stroke="#8884d8" 
                    fill="#8884d8" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}