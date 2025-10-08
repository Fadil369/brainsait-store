'use client';

import React from 'react';
import { useAppStore } from '@/stores';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { 
  SparklesIcon, 
  ArrowTrendingUpIcon,
  LightBulbIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

export function AIRecommendations() {
  const { language } = useAppStore();

  const recommendations = [
    {
      id: 'REC-001',
      type: 'reorder',
      title: 'Reorder Suggestion',
      titleAr: 'اقتراح إعادة الطلب',
      description: 'Based on your ordering patterns, you may run out of Product A in 5 days',
      descriptionAr: 'بناءً على أنماط الطلب الخاصة بك، قد تنفد من المنتج أ في 5 أيام',
      action: 'Order Now',
      actionAr: 'اطلب الآن',
      priority: 'high',
      products: ['Product A', 'Product B'],
      estimatedSavings: 450
    },
    {
      id: 'REC-002',
      type: 'bundle',
      title: 'Bundle Opportunity',
      titleAr: 'فرصة حزمة',
      description: 'Customers who bought Product C also bought Product D. Save 12% by ordering together',
      descriptionAr: 'العملاء الذين اشتروا المنتج ج اشتروا أيضًا المنتج د. وفر 12٪ من خلال الطلب معًا',
      action: 'View Bundle',
      actionAr: 'عرض الحزمة',
      priority: 'medium',
      products: ['Product C', 'Product D'],
      estimatedSavings: 280
    },
    {
      id: 'REC-003',
      type: 'timing',
      title: 'Best Time to Order',
      titleAr: 'أفضل وقت للطلب',
      description: 'Historical data shows ordering on Tuesdays gives you 3-day faster delivery',
      descriptionAr: 'تظهر البيانات التاريخية أن الطلب يوم الثلاثاء يمنحك تسليمًا أسرع بـ 3 أيام',
      action: 'Schedule Order',
      actionAr: 'جدولة الطلب',
      priority: 'low',
      products: [],
      estimatedSavings: 0
    },
    {
      id: 'REC-004',
      type: 'seasonal',
      title: 'Seasonal Demand Forecast',
      titleAr: 'توقعات الطلب الموسمي',
      description: 'Demand for beverages typically increases 40% next month. Consider stocking up',
      descriptionAr: 'يزداد الطلب على المشروبات عادةً بنسبة 40٪ في الشهر المقبل. فكر في تخزينها',
      action: 'Plan Ahead',
      actionAr: 'خطط مسبقًا',
      priority: 'medium',
      products: ['Beverages Category'],
      estimatedSavings: 680
    }
  ];

  const insights = [
    {
      title: 'Top Performing Products',
      titleAr: 'المنتجات الأكثر أداءً',
      value: 'Product C, Product A',
      change: '+25%',
      icon: ArrowTrendingUpIcon,
      color: 'text-green-400'
    },
    {
      title: 'Predicted Next Order',
      titleAr: 'الطلب التالي المتوقع',
      value: 'In 7 days',
      change: null,
      icon: LightBulbIcon,
      color: 'text-blue-400'
    },
    {
      title: 'Optimization Potential',
      titleAr: 'إمكانات التحسين',
      value: '1,450 SAR/month',
      change: null,
      icon: ChartBarIcon,
      color: 'text-purple-400'
    }
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-400/50 bg-red-400/10';
      case 'medium':
        return 'border-yellow-400/50 bg-yellow-400/10';
      case 'low':
        return 'border-blue-400/50 bg-blue-400/10';
      default:
        return 'border-white/10 bg-white/5';
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      high: 'bg-red-400/20 text-red-400',
      medium: 'bg-yellow-400/20 text-yellow-400',
      low: 'bg-blue-400/20 text-blue-400'
    };
    return colors[priority as keyof typeof colors] || colors.low;
  };

  return (
    <div className="space-y-6">
      {/* AI Insights Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {insights.map((insight, index) => {
          const Icon = insight.icon;
          return (
            <Card key={index} className="bg-glass-bg border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
                  <Icon className={`h-4 w-4 ${insight.color}`} />
                  {language === 'ar' ? insight.titleAr : insight.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{insight.value}</div>
                {insight.change && (
                  <p className="text-xs text-green-400 mt-1">{insight.change}</p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* AI Recommendations */}
      <Card className="bg-glass-bg border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <SparklesIcon className="h-6 w-6 text-vision-green" />
            {language === 'ar' ? 'توصيات الذكاء الاصطناعي' : 'AI-Powered Recommendations'}
          </CardTitle>
          <CardDescription className="text-gray-300">
            {language === 'ar' 
              ? 'رؤى مخصصة لتحسين عمليات الطلب والمخزون الخاصة بك' 
              : 'Personalized insights to optimize your ordering and inventory operations'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recommendations.map((rec) => (
              <div 
                key={rec.id}
                className={`p-5 border rounded-lg transition-all hover:border-vision-green/50 ${getPriorityColor(rec.priority)}`}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-start gap-3">
                    <SparklesIcon className="h-6 w-6 text-vision-green mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">
                        {language === 'ar' ? rec.titleAr : rec.title}
                      </h3>
                      <p className="text-gray-300 text-sm">
                        {language === 'ar' ? rec.descriptionAr : rec.description}
                      </p>
                    </div>
                  </div>
                  <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getPriorityBadge(rec.priority)}`}>
                    {rec.priority.toUpperCase()}
                  </span>
                </div>

                {rec.products.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-400 mb-2">
                      {language === 'ar' ? 'المنتجات:' : 'Products:'}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {rec.products.map((product, idx) => (
                        <span 
                          key={idx}
                          className="px-3 py-1 bg-white/10 rounded-full text-xs text-gray-300"
                        >
                          {product}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-between items-center pt-3 border-t border-white/10">
                  {rec.estimatedSavings > 0 && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">
                        {language === 'ar' ? 'التوفير المتوقع:' : 'Est. Savings:'}
                      </span>
                      <span className="text-vision-green font-bold">
                        {rec.estimatedSavings} SAR
                      </span>
                    </div>
                  )}
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="text-vision-green hover:bg-vision-green/20 ml-auto"
                  >
                    {language === 'ar' ? rec.actionAr : rec.action}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Learning Section */}
      <Card className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 border-purple-400/30">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <LightBulbIcon className="h-6 w-6 text-yellow-400" />
            {language === 'ar' ? 'كيف يعمل الذكاء الاصطناعي لك' : 'How AI Works for You'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300">
            <div>
              <div className="text-white font-semibold mb-2">📊 {language === 'ar' ? 'تحليل البيانات' : 'Data Analysis'}</div>
              <p>{language === 'ar' 
                ? 'نحلل أنماط الطلب التاريخية واتجاهات المخزون' 
                : 'We analyze your historical ordering patterns and inventory trends'}</p>
            </div>
            <div>
              <div className="text-white font-semibold mb-2">🎯 {language === 'ar' ? 'توصيات مخصصة' : 'Personalized Recommendations'}</div>
              <p>{language === 'ar' 
                ? 'احصل على اقتراحات مصممة خصيصًا لاحتياجات عملك' 
                : 'Get suggestions tailored specifically to your business needs'}</p>
            </div>
            <div>
              <div className="text-white font-semibold mb-2">💰 {language === 'ar' ? 'توفير التكاليف' : 'Cost Savings'}</div>
              <p>{language === 'ar' 
                ? 'قم بتحسين عملياتك وتوفير ما يصل إلى 15٪ على التكاليف' 
                : 'Optimize your operations and save up to 15% on costs'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
