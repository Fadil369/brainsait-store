'use client';

import React, { useState } from 'react';
import { useAppStore } from '@/stores';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  CubeIcon, 
  ClockIcon,
  FireIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export function InventoryInsights() {
  const { language } = useAppStore();
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = ['all', 'Electronics', 'Food', 'Beverages'];
  
  const inventoryData = [
    { 
      id: 'P001', 
      name: 'Product A', 
      nameAr: 'منتج أ',
      category: 'Electronics',
      stock: 45,
      reorderLevel: 50,
      expiryDate: '2025-06-15',
      velocity: 'fast',
      lastRestocked: '2025-01-10'
    },
    { 
      id: 'P002', 
      name: 'Product B', 
      nameAr: 'منتج ب',
      category: 'Food',
      stock: 15,
      reorderLevel: 30,
      expiryDate: '2025-02-28',
      velocity: 'medium',
      lastRestocked: '2025-01-12'
    },
    { 
      id: 'P003', 
      name: 'Product C', 
      nameAr: 'منتج ج',
      category: 'Beverages',
      stock: 120,
      reorderLevel: 100,
      expiryDate: '2025-08-20',
      velocity: 'fast',
      lastRestocked: '2025-01-05'
    },
    { 
      id: 'P004', 
      name: 'Product D', 
      nameAr: 'منتج د',
      category: 'Electronics',
      stock: 5,
      reorderLevel: 20,
      expiryDate: null,
      velocity: 'slow',
      lastRestocked: '2024-12-20'
    },
  ];

  const filteredInventory = selectedCategory === 'all' 
    ? inventoryData 
    : inventoryData.filter(item => item.category === selectedCategory);

  const lowStockItems = inventoryData.filter(item => item.stock < item.reorderLevel);
  const expiringItems = inventoryData.filter(item => {
    if (!item.expiryDate) return false;
    const daysUntilExpiry = Math.floor((new Date(item.expiryDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry < 60;
  });
  const fastMovingItems = inventoryData.filter(item => item.velocity === 'fast');

  const getStockStatus = (stock: number, reorderLevel: number) => {
    const percentage = (stock / reorderLevel) * 100;
    if (percentage < 50) return { color: 'text-red-400', bg: 'bg-red-400' };
    if (percentage < 80) return { color: 'text-yellow-400', bg: 'bg-yellow-400' };
    return { color: 'text-green-400', bg: 'bg-green-400' };
  };

  const getDaysUntilExpiry = (expiryDate: string | null) => {
    if (!expiryDate) return null;
    return Math.floor((new Date(expiryDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
              <ExclamationTriangleIcon className="h-4 w-4 text-red-400" />
              {language === 'ar' ? 'مخزون منخفض' : 'Low Stock'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-400">{lowStockItems.length}</div>
            <p className="text-xs text-gray-400">
              {language === 'ar' ? 'منتجات تحتاج إلى إعادة طلب' : 'products need reordering'}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
              <ClockIcon className="h-4 w-4 text-yellow-400" />
              {language === 'ar' ? 'قريب من الانتهاء' : 'Expiring Soon'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-400">{expiringItems.length}</div>
            <p className="text-xs text-gray-400">
              {language === 'ar' ? 'منتجات تنتهي خلال 60 يوم' : 'products expiring in 60 days'}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
              <FireIcon className="h-4 w-4 text-orange-400" />
              {language === 'ar' ? 'سريع الحركة' : 'Fast Moving'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-400">{fastMovingItems.length}</div>
            <p className="text-xs text-gray-400">
              {language === 'ar' ? 'منتجات عالية الطلب' : 'high demand products'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Inventory Table */}
      <Card className="bg-glass-bg border-white/10">
        <CardHeader>
          <CardTitle className="text-white">
            {language === 'ar' ? 'حالة المخزون' : 'Inventory Status'}
          </CardTitle>
          <CardDescription className="text-gray-300">
            {language === 'ar' 
              ? 'تتبع مستويات المخزون والمنتجات القريبة من الانتهاء' 
              : 'Track stock levels and expiring products'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Category Filter */}
          <div className="flex gap-2 mb-6 flex-wrap">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedCategory === cat
                    ? 'bg-vision-green text-black'
                    : 'bg-white/5 text-gray-300 hover:bg-white/10'
                }`}
              >
                {cat === 'all' 
                  ? (language === 'ar' ? 'الكل' : 'All')
                  : cat}
              </button>
            ))}
          </div>

          {/* Inventory Items */}
          <div className="space-y-3">
            {filteredInventory.map((item) => {
              const status = getStockStatus(item.stock, item.reorderLevel);
              const daysUntilExpiry = getDaysUntilExpiry(item.expiryDate);
              
              return (
                <div 
                  key={item.id} 
                  className="p-4 bg-white/5 border border-white/10 rounded-lg hover:border-vision-green/50 transition-all"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-white flex items-center gap-2">
                        {language === 'ar' ? item.nameAr : item.name}
                        {item.velocity === 'fast' && (
                          <FireIcon className="h-4 w-4 text-orange-400" />
                        )}
                      </h3>
                      <p className="text-xs text-gray-400">{item.category} • ID: {item.id}</p>
                    </div>
                    <span className={`text-sm ${status.color} font-semibold`}>
                      {item.stock} / {item.reorderLevel}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-white/10 rounded-full h-2 mb-3">
                    <div 
                      className={`${status.bg} h-2 rounded-full transition-all`}
                      style={{ width: `${Math.min((item.stock / item.reorderLevel) * 100, 100)}%` }}
                    />
                  </div>

                  {/* Additional Info */}
                  <div className="flex flex-wrap gap-4 text-xs text-gray-400">
                    <span>
                      {language === 'ar' ? 'آخر تجديد:' : 'Last restocked:'} {item.lastRestocked}
                    </span>
                    {daysUntilExpiry !== null && (
                      <span className={daysUntilExpiry < 30 ? 'text-yellow-400' : ''}>
                        {language === 'ar' ? 'ينتهي في:' : 'Expires in:'} {daysUntilExpiry} {language === 'ar' ? 'يوم' : 'days'}
                      </span>
                    )}
                    <span className="capitalize">
                      {language === 'ar' ? 'السرعة:' : 'Velocity:'} {item.velocity}
                    </span>
                  </div>

                  {/* Alerts */}
                  {(item.stock < item.reorderLevel || (daysUntilExpiry && daysUntilExpiry < 30)) && (
                    <div className="mt-3 p-2 bg-yellow-400/10 border border-yellow-400/30 rounded text-xs text-yellow-400">
                      {item.stock < item.reorderLevel && (
                        <div>⚠️ {language === 'ar' ? 'مخزون منخفض - يحتاج إلى إعادة طلب' : 'Low stock - needs reordering'}</div>
                      )}
                      {daysUntilExpiry && daysUntilExpiry < 30 && (
                        <div>⏰ {language === 'ar' ? 'قريب من الانتهاء' : 'Expiring soon'}</div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
