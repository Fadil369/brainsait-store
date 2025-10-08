'use client';

import React, { useState } from 'react';
import { useAppStore } from '@/stores';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { 
  BellIcon, 
  GiftIcon,
  TagIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

export function PromotionsNotifications() {
  const { language } = useAppStore();
  const [selectedTab, setSelectedTab] = useState('promotions');

  const promotions = [
    {
      id: 'PROMO-001',
      title: 'New Year Special',
      titleAr: 'عرض رأس السنة الخاص',
      discount: '20%',
      validUntil: '2025-01-31',
      description: 'Get 20% off on all electronics',
      descriptionAr: 'احصل على خصم 20٪ على جميع الإلكترونيات',
      code: 'NEWYEAR2025',
      status: 'active'
    },
    {
      id: 'PROMO-002',
      title: 'Bulk Order Discount',
      titleAr: 'خصم الطلبات الكبيرة',
      discount: '15%',
      validUntil: '2025-02-28',
      description: 'Order 100+ items and save 15%',
      descriptionAr: 'اطلب أكثر من 100 عنصر واحفظ 15٪',
      code: 'BULK15',
      status: 'active'
    },
    {
      id: 'PROMO-003',
      title: 'Loyalty Reward',
      titleAr: 'مكافأة الولاء',
      discount: '10%',
      validUntil: '2025-03-31',
      description: 'Exclusive discount for loyal customers',
      descriptionAr: 'خصم حصري للعملاء المخلصين',
      code: 'LOYAL10',
      status: 'active'
    }
  ];

  const notifications = [
    {
      id: 'NOTIF-001',
      type: 'order',
      title: 'Order Shipped',
      titleAr: 'تم شحن الطلب',
      message: 'Your order ORD-12345 has been shipped',
      messageAr: 'تم شحن طلبك ORD-12345',
      timestamp: '2 hours ago',
      read: false
    },
    {
      id: 'NOTIF-002',
      type: 'promotion',
      title: 'New Promotion Available',
      titleAr: 'عرض ترويجي جديد متاح',
      message: 'Check out our latest 20% discount on electronics',
      messageAr: 'تحقق من أحدث خصم 20٪ على الإلكترونيات',
      timestamp: '5 hours ago',
      read: false
    },
    {
      id: 'NOTIF-003',
      type: 'payment',
      title: 'Payment Received',
      titleAr: 'تم استلام الدفعة',
      message: 'Payment of 15,000 SAR has been processed',
      messageAr: 'تمت معالجة دفعة 15,000 ريال',
      timestamp: '1 day ago',
      read: true
    },
    {
      id: 'NOTIF-004',
      type: 'inventory',
      title: 'Low Stock Alert',
      titleAr: 'تنبيه مخزون منخفض',
      message: 'Product A is running low on stock',
      messageAr: 'المنتج أ ينخفض في المخزون',
      timestamp: '2 days ago',
      read: true
    }
  ];

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'order':
        return <TagIcon className="h-5 w-5" />;
      case 'promotion':
        return <GiftIcon className="h-5 w-5" />;
      case 'payment':
        return <SparklesIcon className="h-5 w-5" />;
      default:
        return <BellIcon className="h-5 w-5" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'order':
        return 'bg-blue-400/20 text-blue-400';
      case 'promotion':
        return 'bg-purple-400/20 text-purple-400';
      case 'payment':
        return 'bg-green-400/20 text-green-400';
      default:
        return 'bg-yellow-400/20 text-yellow-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Tab Selection */}
      <div className="flex gap-4">
        <button
          onClick={() => setSelectedTab('promotions')}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
            selectedTab === 'promotions'
              ? 'bg-vision-green text-black'
              : 'bg-white/5 text-gray-300 hover:bg-white/10'
          }`}
        >
          <GiftIcon className="h-5 w-5" />
          {language === 'ar' ? 'العروض الترويجية' : 'Promotions'}
        </button>
        <button
          onClick={() => setSelectedTab('notifications')}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
            selectedTab === 'notifications'
              ? 'bg-vision-green text-black'
              : 'bg-white/5 text-gray-300 hover:bg-white/10'
          }`}
        >
          <BellIcon className="h-5 w-5" />
          {language === 'ar' ? 'الإشعارات' : 'Notifications'}
          {notifications.filter(n => !n.read).length > 0 && (
            <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
              {notifications.filter(n => !n.read).length}
            </span>
          )}
        </button>
      </div>

      {/* Promotions Tab */}
      {selectedTab === 'promotions' && (
        <div className="space-y-4">
          <Card className="bg-glass-bg border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <GiftIcon className="h-6 w-6" />
                {language === 'ar' ? 'العروض الترويجية النشطة' : 'Active Promotions'}
              </CardTitle>
              <CardDescription className="text-gray-300">
                {language === 'ar' 
                  ? 'استفد من عروضنا الحصرية ووفر المال' 
                  : 'Take advantage of our exclusive offers and save money'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {promotions.map((promo) => (
                  <div 
                    key={promo.id}
                    className="relative p-6 bg-gradient-to-br from-vision-green/20 to-purple-500/20 border border-vision-green/30 rounded-lg overflow-hidden"
                  >
                    <div className="absolute top-2 right-2">
                      <span className="bg-vision-green text-black text-xs font-bold px-3 py-1 rounded-full">
                        {promo.discount} OFF
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">
                      {language === 'ar' ? promo.titleAr : promo.title}
                    </h3>
                    <p className="text-gray-300 text-sm mb-4">
                      {language === 'ar' ? promo.descriptionAr : promo.description}
                    </p>
                    <div className="mb-4">
                      <p className="text-xs text-gray-400 mb-2">
                        {language === 'ar' ? 'كود الخصم:' : 'Promo Code:'}
                      </p>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 px-3 py-2 bg-black/30 border border-white/20 rounded text-vision-green font-mono">
                          {promo.code}
                        </code>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => navigator.clipboard.writeText(promo.code)}
                          className="text-white hover:bg-white/10"
                        >
                          {language === 'ar' ? 'نسخ' : 'Copy'}
                        </Button>
                      </div>
                    </div>
                    <p className="text-xs text-gray-400">
                      {language === 'ar' ? 'صالح حتى:' : 'Valid until:'} {promo.validUntil}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Notifications Tab */}
      {selectedTab === 'notifications' && (
        <Card className="bg-glass-bg border-white/10">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-white flex items-center gap-2">
                  <BellIcon className="h-6 w-6" />
                  {language === 'ar' ? 'الإشعارات' : 'Notifications'}
                </CardTitle>
                <CardDescription className="text-gray-300">
                  {language === 'ar' 
                    ? 'ابق على اطلاع بآخر التحديثات' 
                    : 'Stay updated with the latest updates'}
                </CardDescription>
              </div>
              <Button variant="ghost" size="sm" className="text-vision-green">
                {language === 'ar' ? 'وضع علامة كمقروء للكل' : 'Mark all as read'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {notifications.map((notif) => (
                <div 
                  key={notif.id}
                  className={`p-4 rounded-lg border transition-all ${
                    notif.read 
                      ? 'bg-white/5 border-white/10' 
                      : 'bg-vision-green/10 border-vision-green/30'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-lg ${getNotificationColor(notif.type)}`}>
                      {getNotificationIcon(notif.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="font-semibold text-white">
                          {language === 'ar' ? notif.titleAr : notif.title}
                        </h4>
                        {!notif.read && (
                          <span className="w-2 h-2 bg-vision-green rounded-full"></span>
                        )}
                      </div>
                      <p className="text-sm text-gray-300 mb-2">
                        {language === 'ar' ? notif.messageAr : notif.message}
                      </p>
                      <p className="text-xs text-gray-400">{notif.timestamp}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
