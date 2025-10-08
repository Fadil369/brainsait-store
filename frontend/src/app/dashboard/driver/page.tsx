"use client";

import React, { useState, useEffect } from 'react';

interface DriverStats {
  today_deliveries: number;
  week_deliveries: number;
  month_deliveries: number;
  today_earnings: number;
  week_earnings: number;
  month_earnings: number;
  current_rating: number;
  active_routes: number;
  completion_rate: number;
}

interface ActiveRoute {
  id: string;
  route_number: string;
  total_stops: number;
  completed_stops: number;
  status: string;
}

interface SafetyAlert {
  id: string;
  alert_type: string;
  severity: string;
  message: string;
  triggered_at: string;
  acknowledged: boolean;
}

export default function DriverDashboard() {
  const [stats, setStats] = useState<DriverStats | null>(null);
  const [activeRoutes, setActiveRoutes] = useState<ActiveRoute[]>([]);
  const [safetyAlerts, setSafetyAlerts] = useState<SafetyAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data for demonstration
    // In production, fetch from API
    setStats({
      today_deliveries: 12,
      week_deliveries: 68,
      month_deliveries: 287,
      today_earnings: 450.0,
      week_earnings: 3200.0,
      month_earnings: 12800.0,
      current_rating: 4.8,
      active_routes: 1,
      completion_rate: 96.5,
    });

    setActiveRoutes([
      {
        id: '1',
        route_number: 'RT-20240115-A1B2',
        total_stops: 15,
        completed_stops: 8,
        status: 'in_progress',
      },
    ]);

    setSafetyAlerts([
      {
        id: '1',
        alert_type: 'fatigue',
        severity: 'medium',
        message: 'Consider taking a break after next delivery',
        triggered_at: new Date().toISOString(),
        acknowledged: false,
      },
    ]);

    setLoading(false);
  }, []);

  const getStatusBadge = (status: string) => {
    const statusColors = {
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      planned: 'bg-gray-100 text-gray-800',
    };
    return statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityBadge = (severity: string) => {
    const severityColors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };
    return severityColors[severity as keyof typeof severityColors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6" dir="ltr">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Driver Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's your performance overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Today's Deliveries */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Deliveries</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.today_deliveries}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
          </div>
        </div>

        {/* Today's Earnings */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Earnings</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {stats?.today_earnings.toFixed(2)} SAR
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Rating */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Current Rating</p>
              <div className="flex items-center mt-2">
                <p className="text-3xl font-bold text-yellow-600">{stats?.current_rating}</p>
                <span className="ml-2 text-yellow-500">★</span>
              </div>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Completion Rate */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completion Rate</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">{stats?.completion_rate}%</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Active Routes & Safety Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Active Routes */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Active Routes</h2>
          </div>
          <div className="p-6">
            {activeRoutes.length > 0 ? (
              <div className="space-y-4">
                {activeRoutes.map((route) => (
                  <div key={route.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-gray-900">{route.route_number}</span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(route.status)}`}>
                        {route.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>Progress: {route.completed_stops}/{route.total_stops} stops</span>
                      <span>{Math.round((route.completed_stops / route.total_stops) * 100)}%</span>
                    </div>
                    <div className="mt-2 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${(route.completed_stops / route.total_stops) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No active routes</p>
            )}
          </div>
        </div>

        {/* Safety Alerts */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Safety Alerts</h2>
          </div>
          <div className="p-6">
            {safetyAlerts.length > 0 ? (
              <div className="space-y-4">
                {safetyAlerts.map((alert) => (
                  <div key={alert.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityBadge(alert.severity)}`}>
                            {alert.severity}
                          </span>
                          <span className="text-xs text-gray-500">{alert.alert_type}</span>
                        </div>
                        <p className="text-sm text-gray-700">{alert.message}</p>
                      </div>
                    </div>
                    {!alert.acknowledged && (
                      <button className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition">
                        Acknowledge
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No safety alerts</p>
            )}
          </div>
        </div>
      </div>

      {/* Monthly Overview */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Monthly Overview</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Total Deliveries</p>
              <p className="text-4xl font-bold text-gray-900">{stats?.month_deliveries}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Total Earnings</p>
              <p className="text-4xl font-bold text-green-600">{stats?.month_earnings.toFixed(2)} SAR</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Active Routes</p>
              <p className="text-4xl font-bold text-blue-600">{stats?.active_routes}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="bg-blue-600 text-white rounded-lg p-4 hover:bg-blue-700 transition flex items-center justify-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          View Routes
        </button>
        <button className="bg-green-600 text-white rounded-lg p-4 hover:bg-green-700 transition flex items-center justify-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Report Incident
        </button>
        <button className="bg-purple-600 text-white rounded-lg p-4 hover:bg-purple-700 transition flex items-center justify-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          View Profile
        </button>
      </div>
    </div>
  );
}
