'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  Calculator, 
  Download, 
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  Receipt
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface FinancialData {
  period: {
    start_date: string;
    end_date: string;
  };
  vat_analysis: {
    total_revenue_with_vat: number;
    revenue_before_vat: number;
    vat_amount: number;
    vat_rate_percent: number;
    zatca_compliant: boolean;
  };
  monthly_breakdown: Array<{
    year: number;
    month: number;
    total_revenue: number;
    revenue_before_vat: number;
    vat_amount: number;
    transaction_count: number;
  }>;
  payment_reconciliation: Array<{
    payment_method: string;
    total_amount: number;
    transaction_count: number;
    average_transaction: number;
  }>;
  subscription_billing: {
    monthly_recurring_revenue: number;
    annual_recurring_revenue: number;
    churn_rate: number;
    customer_lifetime_value: number;
  };
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function FinancialAnalytics() {
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const queryParams = `?start_date=${dateRange.start_date}&end_date=${dateRange.end_date}`;

      const response = await fetch(`${baseUrl}/api/v1/analytics/financial${queryParams}`, { headers });
      const data = await response.json();

      setFinancialData(data.data);
    } catch (error) {
      // Error handling will be improved with user notifications
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dateRange]); // fetchData is stable since it only depends on dateRange

  const exportVATReport = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(
        `${baseUrl}/api/v1/analytics/export?report_type=financial&format=json&start_date=${dateRange.start_date}&end_date=${dateRange.end_date}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const data = await response.json();
      
      const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vat-report-${dateRange.start_date}-to-${dateRange.end_date}.json`;
      a.click();
    } catch (error) {
      // Export error handling will be improved with user notification
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-SA', {
      style: 'currency',
      currency: 'SAR'
    }).format(amount);
  };

  const formatMonth = (year: number, month: number) => {
    return new Date(year, month - 1).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short'
    });
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
          <h1 className="text-3xl font-bold tracking-tight">Financial Analytics</h1>
          <p className="text-muted-foreground">
            Comprehensive financial reporting with ZATCA compliance
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2">
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) => setDateRange(prev => ({ ...prev, start_date: e.target.value }))}
              className="px-3 py-2 border rounded-md"
            />
            <span>to</span>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) => setDateRange(prev => ({ ...prev, end_date: e.target.value }))}
              className="px-3 py-2 border rounded-md"
            />
          </div>
          
          <Button
            variant="outline"
            onClick={exportVATReport}
            className="ml-2"
          >
            <Download className="w-4 h-4 mr-2" />
            Export VAT Report
          </Button>
        </div>
      </div>

      {/* ZATCA Compliance Status */}
      <Card className={`border-2 ${financialData?.vat_analysis.zatca_compliant ? 'border-green-200' : 'border-red-200'}`}>
        <CardHeader>
          <CardTitle className="flex items-center">
            {financialData?.vat_analysis.zatca_compliant ? (
              <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
            )}
            ZATCA Compliance Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Badge className={`${financialData?.vat_analysis.zatca_compliant ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {financialData?.vat_analysis.zatca_compliant ? 'COMPLIANT' : 'NON-COMPLIANT'}
              </Badge>
              <p className="text-sm text-muted-foreground mt-2">
                {financialData?.vat_analysis.zatca_compliant 
                  ? 'All financial records meet ZATCA requirements'
                  : 'Some financial records may not meet ZATCA requirements'
                }
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">VAT Rate</div>
              <div className="text-2xl font-bold">{financialData?.vat_analysis.vat_rate_percent}%</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Financial Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue (with VAT)</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(financialData?.vat_analysis.total_revenue_with_vat || 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue (before VAT)</CardTitle>
            <Calculator className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(financialData?.vat_analysis.revenue_before_vat || 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">VAT Collected</CardTitle>
            <Receipt className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(financialData?.vat_analysis.vat_amount || 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">MRR</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(financialData?.subscription_billing.monthly_recurring_revenue || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Monthly Recurring Revenue
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics Tabs */}
      <Tabs defaultValue="vat" className="space-y-4">
        <TabsList>
          <TabsTrigger value="vat">VAT Analysis</TabsTrigger>
          <TabsTrigger value="monthly">Monthly Breakdown</TabsTrigger>
          <TabsTrigger value="payments">Payment Reconciliation</TabsTrigger>
          <TabsTrigger value="subscription">Subscription Metrics</TabsTrigger>
        </TabsList>

        {/* VAT Analysis Tab */}
        <TabsContent value="vat" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>VAT Breakdown</CardTitle>
                <CardDescription>Tax analysis for the selected period</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={[
                        { name: 'Revenue (before VAT)', value: financialData?.vat_analysis.revenue_before_vat || 0 },
                        { name: 'VAT Amount', value: financialData?.vat_analysis.vat_amount || 0 }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      <Cell fill="#0088FE" />
                      <Cell fill="#00C49F" />
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>VAT Compliance Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm">VAT Rate Applied</span>
                  <span className="font-medium">{financialData?.vat_analysis.vat_rate_percent}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">ZATCA Compliant</span>
                  <Badge className={financialData?.vat_analysis.zatca_compliant ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                    {financialData?.vat_analysis.zatca_compliant ? 'Yes' : 'No'}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Total Revenue</span>
                  <span className="font-medium">{formatCurrency(financialData?.vat_analysis.total_revenue_with_vat || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Net Revenue</span>
                  <span className="font-medium">{formatCurrency(financialData?.vat_analysis.revenue_before_vat || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">VAT Collected</span>
                  <span className="font-medium">{formatCurrency(financialData?.vat_analysis.vat_amount || 0)}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Monthly Breakdown Tab */}
        <TabsContent value="monthly" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Monthly Revenue & VAT Trend</CardTitle>
              <CardDescription>Revenue and VAT collection over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={financialData?.monthly_breakdown || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="month" 
                    tickFormatter={(value, index) => {
                      const item = financialData?.monthly_breakdown?.[index];
                      return item ? formatMonth(item.year, item.month) : '';
                    }}
                  />
                  <YAxis tickFormatter={(value) => formatCurrency(value)} />
                  <Tooltip 
                    formatter={(value: number) => [formatCurrency(value), '']}
                    labelFormatter={(_, payload) => {
                      if (payload && payload[0]) {
                        const data = payload[0].payload;
                        return formatMonth(data.year, data.month);
                      }
                      return '';
                    }}
                  />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="revenue_before_vat" 
                    stackId="1"
                    stroke="#8884d8" 
                    fill="#8884d8" 
                    name="Revenue (before VAT)"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="vat_amount" 
                    stackId="1"
                    stroke="#82ca9d" 
                    fill="#82ca9d" 
                    name="VAT Amount"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Monthly Financial Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {financialData?.monthly_breakdown?.slice(-6).map((month) => (
                  <div key={`${month.year}-${month.month}`} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">{formatMonth(month.year, month.month)}</h4>
                      <p className="text-sm text-muted-foreground">
                        {month.transaction_count} transactions
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{formatCurrency(month.total_revenue)}</div>
                      <div className="text-sm text-muted-foreground">
                        VAT: {formatCurrency(month.vat_amount)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payment Reconciliation Tab */}
        <TabsContent value="payments" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Payment Method Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={financialData?.payment_reconciliation || []}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ payment_method, percent }) => `${payment_method} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="total_amount"
                    >
                      {(financialData?.payment_reconciliation || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Payment Reconciliation Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {financialData?.payment_reconciliation?.map((payment) => (
                    <div key={payment.payment_method} className="flex justify-between items-center p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{payment.payment_method}</h4>
                        <p className="text-sm text-muted-foreground">
                          {payment.transaction_count} transactions
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{formatCurrency(payment.total_amount)}</div>
                        <div className="text-sm text-muted-foreground">
                          Avg: {formatCurrency(payment.average_transaction)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Subscription Metrics Tab */}
        <TabsContent value="subscription" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Monthly Recurring Revenue</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(financialData?.subscription_billing.monthly_recurring_revenue || 0)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Annual Recurring Revenue</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(financialData?.subscription_billing.annual_recurring_revenue || 0)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Churn Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {financialData?.subscription_billing.churn_rate.toFixed(2)}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Customer LTV</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(financialData?.subscription_billing.customer_lifetime_value || 0)}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}