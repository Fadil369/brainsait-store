'use client';

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import MonitoringDashboard from '@/components/admin/MonitoringDashboard';
import AnalyticsDashboard from '@/components/analytics/AnalyticsDashboard';
import FinancialAnalytics from '@/components/analytics/FinancialAnalytics';
import { Activity, BarChart3, Calculator, Settings } from 'lucide-react';

export default function AdminPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground text-lg">
            Comprehensive system administration and analytics
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            System Operational
          </div>
        </div>
      </div>

      {/* Main Dashboard Tabs */}
      <Tabs defaultValue="monitoring" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="monitoring" className="flex items-center space-x-2">
            <Activity className="h-4 w-4" />
            <span>System Monitoring</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Business Analytics</span>
          </TabsTrigger>
          <TabsTrigger value="financial" className="flex items-center space-x-2">
            <Calculator className="h-4 w-4" />
            <span>Financial & VAT</span>
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span>System Settings</span>
          </TabsTrigger>
        </TabsList>

        {/* System Monitoring Tab */}
        <TabsContent value="monitoring">
          <MonitoringDashboard />
        </TabsContent>

        {/* Business Analytics Tab */}
        <TabsContent value="analytics">
          <AnalyticsDashboard />
        </TabsContent>

        {/* Financial Analytics Tab */}
        <TabsContent value="financial">
          <FinancialAnalytics />
        </TabsContent>

        {/* System Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Monitoring Configuration
                </CardTitle>
                <CardDescription>
                  Configure system monitoring thresholds and alerts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">CPU Alert Threshold</span>
                    <span className="text-sm">80%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Memory Alert Threshold</span>
                    <span className="text-sm">85%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Disk Alert Threshold</span>
                    <span className="text-sm">90%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Error Rate Alert</span>
                    <span className="text-sm">5%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calculator className="h-5 w-5 mr-2" />
                  Financial Settings
                </CardTitle>
                <CardDescription>
                  ZATCA compliance and VAT configuration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">VAT Rate</span>
                    <span className="text-sm">15%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">ZATCA Compliance</span>
                    <span className="text-sm text-green-600 font-medium">Enabled</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Currency</span>
                    <span className="text-sm">SAR (Saudi Riyal)</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Fiscal Year</span>
                    <span className="text-sm">2024</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Information</CardTitle>
                <CardDescription>
                  Current system configuration and status
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Platform Version</span>
                    <span className="text-sm">v1.0.0</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Environment</span>
                    <span className="text-sm">Production</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Region</span>
                    <span className="text-sm">Saudi Arabia</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Multi-tenant</span>
                    <span className="text-sm text-green-600 font-medium">Enabled</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Retention</CardTitle>
                <CardDescription>
                  Analytics and monitoring data retention policies
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Analytics Data</span>
                    <span className="text-sm">2 years</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Monitoring Metrics</span>
                    <span className="text-sm">90 days</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Error Logs</span>
                    <span className="text-sm">30 days</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Financial Records</span>
                    <span className="text-sm">7 years (ZATCA)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}