'use client';

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CreditCardIcon } from '@heroicons/react/24/outline';
import { fieldSalesApi } from '@/lib/api/field-sales';
import { offlineStorage } from '@/lib/offline-storage';
import type { CreditRequestFormData } from '@/types/field-sales';

interface CreditRequestFormProps {
  repId: string;
  onSuccess?: () => void;
}

export default function CreditRequestForm({ repId, onSuccess }: CreditRequestFormProps) {
  const { t, i18n } = useTranslation();
  const [formData, setFormData] = useState<CreditRequestFormData>({
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    customer_business: '',
    requested_amount: 0,
    credit_term_days: 30,
    purpose: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiAssessment, setAiAssessment] = useState<any>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  const isRTL = i18n.language === 'ar';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isOnline) {
        const result = await fieldSalesApi.createCreditRequest(repId, formData);
        setAiAssessment(result);
        setTimeout(() => {
          if (onSuccess) onSuccess();
        }, 3000);
      } else {
        await offlineStorage.saveCreditRequest(formData);
        alert(t('field_sales.credit_saved_offline', 'Credit request saved offline. Will sync when online.'));
        if (onSuccess) onSuccess();
      }
    } catch (err) {
      setError(t('field_sales.credit_request_error', 'Failed to submit credit request'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`max-w-2xl mx-auto p-4 ${isRTL ? 'rtl' : 'ltr'}`}>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center mb-6">
          <CreditCardIcon className="w-8 h-8 text-orange-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">
            {t('field_sales.credit_request', 'Credit Request')}
          </h2>
        </div>

        {!isOnline && (
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800 text-sm">
              📱 {t('field_sales.offline_mode', 'Offline Mode - Data will be synced when online')}
            </p>
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {aiAssessment ? (
          <div className="space-y-4">
            <div className="p-6 bg-blue-50 border-2 border-blue-200 rounded-lg">
              <h3 className="text-lg font-bold text-blue-900 mb-4">
                🤖 {t('field_sales.ai_assessment', 'AI Credit Assessment')}
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-blue-700">{t('field_sales.ai_score', 'AI Score')}</div>
                  <div className="text-3xl font-bold text-blue-900">
                    {aiAssessment.ai_score?.toFixed(0) || 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-blue-700">{t('field_sales.recommendation', 'Recommendation')}</div>
                  <div className="text-xl font-bold text-blue-900 capitalize">
                    {aiAssessment.ai_recommendation || 'Pending'}
                  </div>
                </div>
              </div>
              {aiAssessment.risk_factors && aiAssessment.risk_factors.length > 0 && (
                <div className="mt-4">
                  <div className="text-sm text-blue-700 mb-2">{t('field_sales.risk_factors', 'Risk Factors')}:</div>
                  <ul className="list-disc list-inside text-sm text-blue-900">
                    {aiAssessment.risk_factors.map((factor: string, idx: number) => (
                      <li key={idx}>{factor}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <button
              onClick={() => {
                setAiAssessment(null);
                setFormData({
                  customer_name: '',
                  customer_email: '',
                  customer_phone: '',
                  customer_business: '',
                  requested_amount: 0,
                  credit_term_days: 30,
                  purpose: '',
                });
              }}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              {t('field_sales.new_request', 'New Request')}
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('field_sales.customer_name', 'Customer Name')} *
              </label>
              <input
                type="text"
                value={formData.customer_name}
                onChange={(e) => setFormData(prev => ({ ...prev, customer_name: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('field_sales.customer_phone', 'Customer Phone')} *
              </label>
              <input
                type="tel"
                value={formData.customer_phone}
                onChange={(e) => setFormData(prev => ({ ...prev, customer_phone: e.target.value }))}
                placeholder="+966XXXXXXXXX"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('field_sales.customer_email', 'Customer Email')} ({t('optional', 'Optional')})
              </label>
              <input
                type="email"
                value={formData.customer_email}
                onChange={(e) => setFormData(prev => ({ ...prev, customer_email: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('field_sales.customer_business', 'Business Name')} ({t('optional', 'Optional')})
              </label>
              <input
                type="text"
                value={formData.customer_business}
                onChange={(e) => setFormData(prev => ({ ...prev, customer_business: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('field_sales.requested_amount', 'Requested Amount (SAR)')} *
              </label>
              <input
                type="number"
                value={formData.requested_amount}
                onChange={(e) => setFormData(prev => ({ ...prev, requested_amount: parseFloat(e.target.value) }))}
                min="0"
                step="100"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('field_sales.credit_term_days', 'Credit Term (Days)')} *
              </label>
              <select
                value={formData.credit_term_days}
                onChange={(e) => setFormData(prev => ({ ...prev, credit_term_days: parseInt(e.target.value) }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value={30}>30 Days</option>
                <option value={60}>60 Days</option>
                <option value={90}>90 Days</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('field_sales.purpose', 'Purpose')} ({t('optional', 'Optional')})
              </label>
              <textarea
                value={formData.purpose}
                onChange={(e) => setFormData(prev => ({ ...prev, purpose: e.target.value }))}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium text-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  {t('field_sales.submitting', 'Submitting...')}
                </span>
              ) : (
                t('field_sales.submit_request', 'Submit Request')
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
