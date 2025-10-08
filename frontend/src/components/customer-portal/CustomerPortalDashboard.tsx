'use client';

import React, { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { useAppStore } from '@/stores';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ShoppingCartIcon, 
  ChartBarIcon, 
  CreditCardIcon, 
  BellIcon,
  SparklesIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';

// Import sub-components
import { OrderingInterface } from './OrderingInterface';
import { InventoryInsights } from './InventoryInsights';
import { PaymentManagement } from './PaymentManagement';
import { PromotionsNotifications } from './PromotionsNotifications';
import { AIRecommendations } from './AIRecommendations';
import { ComplaintResolution } from './ComplaintResolution';
import { DashboardOverview } from './DashboardOverview';

export function CustomerPortalDashboard() {
  const { t } = useTranslation('common');
  const { language } = useAppStore();
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: language === 'ar' ? 'نظرة عامة' : 'Overview', icon: ChartBarIcon },
    { id: 'ordering', label: language === 'ar' ? 'الطلبات' : 'Ordering', icon: ShoppingCartIcon },
    { id: 'inventory', label: language === 'ar' ? 'المخزون' : 'Inventory', icon: ChartBarIcon },
    { id: 'payments', label: language === 'ar' ? 'المدفوعات' : 'Payments', icon: CreditCardIcon },
    { id: 'promotions', label: language === 'ar' ? 'العروض' : 'Promotions', icon: BellIcon },
    { id: 'ai-recommendations', label: language === 'ar' ? 'توصيات الذكاء الاصطناعي' : 'AI Recommendations', icon: SparklesIcon },
    { id: 'complaints', label: language === 'ar' ? 'الشكاوى' : 'Complaints', icon: ExclamationCircleIcon },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          {language === 'ar' ? 'بوابة العملاء' : 'Customer Portal'}
        </h1>
        <p className="text-gray-300">
          {language === 'ar' 
            ? 'إدارة شاملة لطلباتك ومخزونك وعملياتك التجارية' 
            : 'Comprehensive management of your orders, inventory, and business operations'}
        </p>
      </div>

      {/* Tabs Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-7 gap-2 bg-glass-bg p-2 rounded-lg mb-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <TabsTrigger 
                key={tab.id} 
                value={tab.id}
                className="flex flex-col items-center gap-1 py-3 data-[state=active]:bg-vision-green/20 data-[state=active]:text-vision-green"
              >
                <Icon className="h-5 w-5" />
                <span className="text-xs">{tab.label}</span>
              </TabsTrigger>
            );
          })}
        </TabsList>

        {/* Tab Contents */}
        <TabsContent value="overview">
          <DashboardOverview />
        </TabsContent>

        <TabsContent value="ordering">
          <OrderingInterface />
        </TabsContent>

        <TabsContent value="inventory">
          <InventoryInsights />
        </TabsContent>

        <TabsContent value="payments">
          <PaymentManagement />
        </TabsContent>

        <TabsContent value="promotions">
          <PromotionsNotifications />
        </TabsContent>

        <TabsContent value="ai-recommendations">
          <AIRecommendations />
        </TabsContent>

        <TabsContent value="complaints">
          <ComplaintResolution />
        </TabsContent>
      </Tabs>
    </div>
  );
}
