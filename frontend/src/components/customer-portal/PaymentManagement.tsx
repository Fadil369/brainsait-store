'use client';

import React, { useState } from 'react';
import { useAppStore } from '@/stores';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { 
  CreditCardIcon, 
  BanknotesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

export function PaymentManagement() {
  const { language } = useAppStore();
  const [selectedPeriod, setSelectedPeriod] = useState('month');

  const creditInfo = {
    currentBalance: 45890,
    creditLimit: 100000,
    availableCredit: 54110,
    dueDate: '2025-02-15',
    minimumPayment: 5000
  };

  const transactions = [
    { id: 'TXN-001', date: '2025-01-15', type: 'payment', amount: -15000, balance: 45890, description: 'Order payment' },
    { id: 'TXN-002', date: '2025-01-10', type: 'credit', amount: 20000, balance: 60890, description: 'Credit adjustment' },
    { id: 'TXN-003', date: '2025-01-08', type: 'payment', amount: -8500, balance: 40890, description: 'Order payment' },
    { id: 'TXN-004', date: '2025-01-05', type: 'payment', amount: -12000, balance: 49390, description: 'Order payment' },
  ];

  const paymentMethods = [
    { id: '1', type: 'Mada', last4: '4567', default: true },
    { id: '2', type: 'Credit Card', last4: '8901', default: false },
    { id: '3', type: 'Bank Transfer', account: 'SA12...3456', default: false },
  ];

  const creditUtilization = ((creditInfo.currentBalance / creditInfo.creditLimit) * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Credit Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">
              {language === 'ar' ? 'الرصيد الحالي' : 'Current Balance'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">{creditInfo.currentBalance.toLocaleString()} SAR</div>
            <div className="flex items-center gap-2 mt-2">
              <div className="w-full bg-white/10 rounded-full h-2">
                <div 
                  className="bg-vision-green h-2 rounded-full transition-all"
                  style={{ width: `${creditUtilization}%` }}
                />
              </div>
              <span className="text-xs text-gray-400">{creditUtilization}%</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">
              {language === 'ar' ? 'الائتمان المتاح' : 'Available Credit'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-vision-green">{creditInfo.availableCredit.toLocaleString()} SAR</div>
            <p className="text-xs text-gray-400 mt-2">
              {language === 'ar' ? 'من' : 'of'} {creditInfo.creditLimit.toLocaleString()} SAR {language === 'ar' ? 'حد الائتمان' : 'credit limit'}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
              <ClockIcon className="h-4 w-4" />
              {language === 'ar' ? 'الدفع المستحق' : 'Payment Due'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-400">{creditInfo.minimumPayment.toLocaleString()} SAR</div>
            <p className="text-xs text-gray-400 mt-2">
              {language === 'ar' ? 'تاريخ الاستحقاق:' : 'Due date:'} {creditInfo.dueDate}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Transaction History */}
      <Card className="bg-glass-bg border-white/10">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-white">
                {language === 'ar' ? 'سجل المعاملات' : 'Transaction History'}
              </CardTitle>
              <CardDescription className="text-gray-300">
                {language === 'ar' ? 'تتبع جميع المدفوعات والائتمانات' : 'Track all payments and credits'}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {['week', 'month', 'year'].map(period => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-3 py-1 rounded text-sm ${
                    selectedPeriod === period
                      ? 'bg-vision-green text-black'
                      : 'bg-white/5 text-gray-300'
                  }`}
                >
                  {period === 'week' ? (language === 'ar' ? 'أسبوع' : 'Week') :
                   period === 'month' ? (language === 'ar' ? 'شهر' : 'Month') :
                   (language === 'ar' ? 'سنة' : 'Year')}
                </button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {transactions.map((txn) => (
              <div 
                key={txn.id} 
                className="flex justify-between items-center p-4 bg-white/5 border border-white/10 rounded-lg hover:border-vision-green/50 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${
                    txn.type === 'credit' ? 'bg-green-400/20' : 'bg-red-400/20'
                  }`}>
                    {txn.type === 'credit' ? (
                      <ArrowTrendingUpIcon className="h-5 w-5 text-green-400" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-5 w-5 text-red-400" />
                    )}
                  </div>
                  <div>
                    <p className="font-semibold text-white">{txn.description}</p>
                    <p className="text-sm text-gray-400">{txn.date} • {txn.id}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${
                    txn.amount > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {txn.amount > 0 ? '+' : ''}{txn.amount.toLocaleString()} SAR
                  </p>
                  <p className="text-sm text-gray-400">
                    {language === 'ar' ? 'الرصيد:' : 'Balance:'} {txn.balance.toLocaleString()} SAR
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Payment Methods */}
      <Card className="bg-glass-bg border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <CreditCardIcon className="h-5 w-5" />
            {language === 'ar' ? 'طرق الدفع' : 'Payment Methods'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {paymentMethods.map((method) => (
              <div 
                key={method.id} 
                className={`p-4 rounded-lg border ${
                  method.default
                    ? 'bg-vision-green/10 border-vision-green/50'
                    : 'bg-white/5 border-white/10'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <CreditCardIcon className="h-6 w-6 text-white" />
                  {method.default && (
                    <span className="text-xs bg-vision-green/20 text-vision-green px-2 py-1 rounded">
                      {language === 'ar' ? 'افتراضي' : 'Default'}
                    </span>
                  )}
                </div>
                <p className="text-white font-semibold">{method.type}</p>
                <p className="text-gray-400 text-sm">
                  {method.last4 ? `•••• ${method.last4}` : method.account}
                </p>
              </div>
            ))}
          </div>
          <Button variant="outline" className="w-full">
            {language === 'ar' ? 'إضافة طريقة دفع جديدة' : 'Add New Payment Method'}
          </Button>
        </CardContent>
      </Card>

      {/* Make Payment */}
      <Card className="bg-glass-bg border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BanknotesIcon className="h-5 w-5" />
            {language === 'ar' ? 'إجراء الدفع' : 'Make Payment'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                {language === 'ar' ? 'مبلغ الدفع' : 'Payment Amount'}
              </label>
              <input
                type="number"
                placeholder={creditInfo.minimumPayment.toString()}
                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
              />
            </div>
            <div className="flex gap-2">
              <Button variant="outline" className="flex-1">
                {language === 'ar' ? 'الحد الأدنى' : 'Minimum'} ({creditInfo.minimumPayment.toLocaleString()} SAR)
              </Button>
              <Button variant="outline" className="flex-1">
                {language === 'ar' ? 'الرصيد الكامل' : 'Full Balance'} ({creditInfo.currentBalance.toLocaleString()} SAR)
              </Button>
            </div>
            <Button variant="gradient" className="w-full">
              {language === 'ar' ? 'تأكيد الدفع' : 'Confirm Payment'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
