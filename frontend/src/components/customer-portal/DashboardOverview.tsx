'use client';

import React from 'react';
import { useAppStore } from '@/stores';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  ShoppingBagIcon, 
  CubeIcon, 
  BanknotesIcon, 
  TruckIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export function DashboardOverview() {
  const { language } = useAppStore();

  // Mock data - in production, this would come from API
  const stats = [
    {
      title: language === 'ar' ? 'إجمالي الطلبات' : 'Total Orders',
      value: '156',
      change: '+12%',
      icon: ShoppingBagIcon,
      color: 'text-blue-400',
      bgColor: 'bg-blue-400/10'
    },
    {
      title: language === 'ar' ? 'المنتجات المتاحة' : 'Available Products',
      value: '432',
      change: '+5%',
      icon: CubeIcon,
      color: 'text-green-400',
      bgColor: 'bg-green-400/10'
    },
    {
      title: language === 'ar' ? 'الرصيد الحالي' : 'Current Balance',
      value: '45,890 SAR',
      change: '-2%',
      icon: BanknotesIcon,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-400/10'
    },
    {
      title: language === 'ar' ? 'الطلبات قيد التوصيل' : 'Orders In Transit',
      value: '23',
      change: '+8%',
      icon: TruckIcon,
      color: 'text-purple-400',
      bgColor: 'bg-purple-400/10'
    }
  ];

  const recentOrders = [
    { id: 'ORD-001', date: '2025-01-15', status: 'delivered', total: 1250 },
    { id: 'ORD-002', date: '2025-01-14', status: 'processing', total: 890 },
    { id: 'ORD-003', date: '2025-01-13', status: 'shipped', total: 2100 },
  ];

  const lowStockItems = [
    { name: 'Product A', stock: 5, reorderLevel: 10 },
    { name: 'Product B', stock: 3, reorderLevel: 15 },
    { name: 'Product C', stock: 8, reorderLevel: 20 },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="bg-glass-bg border-white/10">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-300">
                  {stat.title}
                </CardTitle>
                <div className={`${stat.bgColor} p-2 rounded-lg`}>
                  <Icon className={`h-5 w-5 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <p className={`text-xs ${stat.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                  {stat.change} {language === 'ar' ? 'من الشهر الماضي' : 'from last month'}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <Card className="bg-glass-bg border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <ShoppingBagIcon className="h-5 w-5" />
              {language === 'ar' ? 'الطلبات الأخيرة' : 'Recent Orders'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentOrders.map((order) => (
                <div key={order.id} className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  <div>
                    <p className="font-semibold text-white">{order.id}</p>
                    <p className="text-sm text-gray-400">{order.date}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-vision-green">{order.total} SAR</p>
                    <span className={`text-xs px-2 py-1 rounded ${
                      order.status === 'delivered' ? 'bg-green-400/20 text-green-400' :
                      order.status === 'shipped' ? 'bg-blue-400/20 text-blue-400' :
                      'bg-yellow-400/20 text-yellow-400'
                    }`}>
                      {order.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Low Stock Alerts */}
        <Card className="bg-glass-bg border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
              {language === 'ar' ? 'تنبيهات المخزون المنخفض' : 'Low Stock Alerts'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {lowStockItems.map((item, index) => (
                <div key={index} className="p-3 bg-yellow-400/10 border border-yellow-400/20 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <p className="font-semibold text-white">{item.name}</p>
                    <span className="text-yellow-400 font-bold">{item.stock}</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div 
                      className="bg-yellow-400 h-2 rounded-full" 
                      style={{ width: `${(item.stock / item.reorderLevel) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {language === 'ar' ? 'حد إعادة الطلب:' : 'Reorder level:'} {item.reorderLevel}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
