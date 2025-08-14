'use client';

import { Badge } from '@/components/ui/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { RealTimeMetrics as RealTimeMetricsType } from '@/lib/analytics';
import { analyticsService } from '@/lib/analytics';
import { Activity, DollarSign, ShoppingCart, TrendingDown, TrendingUp, Users } from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  description?: string;
}

function MetricCard({ title, value, change, icon, trend = 'neutral', description }: MetricCardProps) {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-3 w-3" />;
      case 'down': return <TrendingDown className="h-3 w-3" />;
      default: return null;
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change !== undefined && (
          <div className={`flex items-center text-xs ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="ml-1">
              {change > 0 ? '+' : ''}{typeof change === 'number' ? change.toFixed(2) : change}
              {typeof change === 'number' && change !== 0 ? '%' : ''}
            </span>
          </div>
        )}
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}

export default function RealTimeMetrics() {
  const [metrics, setMetrics] = useState<RealTimeMetricsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    // Initial fetch
    fetchMetrics();

    // Subscribe to real-time updates
    const unsubscribe = analyticsService.subscribeToRealTimeUpdates((data) => {
      setMetrics(data);
      setLastUpdated(new Date().toLocaleTimeString());
    });

    return unsubscribe;
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await analyticsService.getRealTimeMetrics();
      setMetrics(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      // Error will be handled by the analytics service or shown in UI
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="space-y-0 pb-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-4">
        <p className="text-muted-foreground">Failed to load real-time metrics</p>
      </div>
    );
  }

  const revenueChange = ((metrics.today_revenue - metrics.yesterday_revenue) / metrics.yesterday_revenue) * 100;
  const revenueTrend = revenueChange > 0 ? 'up' : revenueChange < 0 ? 'down' : 'neutral';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Real-Time Metrics</h2>
          <p className="text-sm text-muted-foreground">Live performance indicators</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="animate-pulse">
            <Activity className="h-3 w-3 mr-1" />
            Live
          </Badge>
          {lastUpdated && (
            <span className="text-xs text-muted-foreground">
              Last updated: {lastUpdated}
            </span>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Today's Revenue"
          value={`$${metrics.today_revenue.toLocaleString()}`}
          change={revenueChange}
          trend={revenueTrend}
          icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
          description={`vs $${metrics.yesterday_revenue.toLocaleString()} yesterday`}
        />

        <MetricCard
          title="Active Sessions"
          value={metrics.active_sessions.toLocaleString()}
          icon={<Users className="h-4 w-4 text-muted-foreground" />}
          description="Current online users"
        />

        <MetricCard
          title="Current Hour Orders"
          value={metrics.current_hour_orders.toLocaleString()}
          icon={<ShoppingCart className="h-4 w-4 text-muted-foreground" />}
          description="Orders in the last hour"
        />

        <MetricCard
          title="Conversion Rate"
          value={`${metrics.conversion_rate.toFixed(2)}%`}
          icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
          description="Visitors to customers"
        />
      </div>

      {/* Additional Real-Time Info */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Revenue Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">Today</span>
                <span className="font-medium">${metrics.today_revenue.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Yesterday</span>
                <span className="font-medium">${metrics.yesterday_revenue.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t">
                <span className="text-sm font-medium">Difference</span>
                <span className={`font-medium ${revenueChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {revenueChange > 0 ? '+' : ''}${metrics.revenue_change.toLocaleString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">API Status</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Operational
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Payment Gateway</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Online
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Last Update</span>
                <span className="text-sm text-muted-foreground">
                  {new Date(metrics.last_updated).toLocaleTimeString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
