'use client';

import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';
import {
  ChartBarIcon,
  MapPinIcon,
  CreditCardIcon,
  MicrophoneIcon,
  TrophyIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import type { SalesRepDashboard as DashboardData } from '@/types/field-sales';
import { fieldSalesApi } from '@/lib/api/field-sales';

interface SalesRepDashboardProps {
  repId: string;
}

export default function SalesRepDashboard({ repId }: SalesRepDashboardProps) {
  const { t, i18n } = useTranslation();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isRTL = i18n.language === 'ar';

  useEffect(() => {
    loadDashboard();
  }, [repId]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await fieldSalesApi.getDashboard(repId);
      setDashboard(data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Dashboard not available'}</p>
          <button
            onClick={loadDashboard}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            {t('retry', 'Retry')}
          </button>
        </div>
      </div>
    );
  }

  const { rep_info, target_progress, recent_check_ins, pending_credits, leaderboard_position, route_summary } = dashboard;

  return (
    <div className={`min-h-screen bg-gray-50 p-4 ${isRTL ? 'rtl' : 'ltr'}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('field_sales.welcome', 'Welcome')}, {rep_info.rep_code}
            </h1>
            <p className="text-gray-600">
              {t('field_sales.level', 'Level')} {rep_info.level} • {rep_info.points} {t('field_sales.points', 'Points')}
            </p>
          </div>
          <div className="text-right">
            {rep_info.csat_score && (
              <div className="text-lg font-semibold text-green-600">
                ⭐ {rep_info.csat_score.toFixed(1)}
              </div>
            )}
            <p className="text-sm text-gray-500">
              {t('field_sales.csat_score', 'CSAT Score')}
            </p>
          </div>
        </div>
      </div>

      {/* Target Progress */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-400 rounded-lg shadow-sm p-6 mb-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">{t('field_sales.monthly_target', 'Monthly Target')}</h2>
          <ChartBarIcon className="w-8 h-8" />
        </div>
        <div className="mb-4">
          <div className="flex justify-between mb-2">
            <span className="text-sm">{t('field_sales.progress', 'Progress')}</span>
            <span className="text-sm font-bold">{target_progress.progress_percentage}%</span>
          </div>
          <div className="w-full bg-blue-300 rounded-full h-3">
            <div
              className="bg-white rounded-full h-3 transition-all duration-300"
              style={{ width: `${Math.min(target_progress.progress_percentage, 100)}%` }}
            ></div>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold">
              {target_progress.current_sales.toLocaleString()}
            </div>
            <div className="text-xs opacity-90">{t('field_sales.current_sales', 'Current')}</div>
          </div>
          <div>
            <div className="text-2xl font-bold">
              {target_progress.monthly_target.toLocaleString()}
            </div>
            <div className="text-xs opacity-90">{t('field_sales.target', 'Target')}</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{target_progress.days_remaining}</div>
            <div className="text-xs opacity-90">{t('field_sales.days_left', 'Days Left')}</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <Link
          href="/field-sales/check-in"
          className="bg-green-600 hover:bg-green-700 text-white rounded-lg p-6 flex items-center justify-center shadow-sm transition-colors"
        >
          <MapPinIcon className="w-8 h-8 mr-3" />
          <div>
            <div className="font-bold text-lg">{t('field_sales.check_in', 'Check In')}</div>
            <div className="text-xs opacity-90">{t('field_sales.start_visit', 'Start Visit')}</div>
          </div>
        </Link>

        <Link
          href="/field-sales/voice-order"
          className="bg-purple-600 hover:bg-purple-700 text-white rounded-lg p-6 flex items-center justify-center shadow-sm transition-colors"
        >
          <MicrophoneIcon className="w-8 h-8 mr-3" />
          <div>
            <div className="font-bold text-lg">{t('field_sales.voice_order', 'Voice Order')}</div>
            <div className="text-xs opacity-90">{t('field_sales.speak_order', 'Speak Order')}</div>
          </div>
        </Link>

        <Link
          href="/field-sales/credit"
          className="bg-orange-600 hover:bg-orange-700 text-white rounded-lg p-6 flex items-center justify-center shadow-sm transition-colors"
        >
          <CreditCardIcon className="w-8 h-8 mr-3" />
          <div>
            <div className="font-bold text-lg">{t('field_sales.credit_request', 'Credit')}</div>
            <div className="text-xs opacity-90">{t('field_sales.request_credit', 'Request Credit')}</div>
          </div>
        </Link>

        <Link
          href="/field-sales/leaderboard"
          className="bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg p-6 flex items-center justify-center shadow-sm transition-colors"
        >
          <TrophyIcon className="w-8 h-8 mr-3" />
          <div>
            <div className="font-bold text-lg">{t('field_sales.leaderboard', 'Leaderboard')}</div>
            <div className="text-xs opacity-90">#{leaderboard_position.rank}</div>
          </div>
        </Link>
      </div>

      {/* Today's Route Summary */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          {t('field_sales.todays_route', "Today's Route")}
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {route_summary.total_visits_today}
            </div>
            <div className="text-sm text-gray-600">{t('field_sales.total_visits', 'Total Visits')}</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {route_summary.completed_visits}
            </div>
            <div className="text-sm text-gray-600">{t('field_sales.completed', 'Completed')}</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {route_summary.in_progress}
            </div>
            <div className="text-sm text-gray-600">{t('field_sales.in_progress', 'In Progress')}</div>
          </div>
        </div>
      </div>

      {/* Recent Check-ins */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          {t('field_sales.recent_visits', 'Recent Visits')}
        </h3>
        {recent_check_ins.length === 0 ? (
          <p className="text-gray-500 text-center py-4">
            {t('field_sales.no_recent_visits', 'No recent visits')}
          </p>
        ) : (
          <div className="space-y-3">
            {recent_check_ins.slice(0, 5).map((checkIn) => (
              <div
                key={checkIn.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center">
                  <MapPinIcon className="w-5 h-5 text-blue-600 mr-3" />
                  <div>
                    <div className="font-medium text-gray-900">{checkIn.outlet_name}</div>
                    <div className="text-sm text-gray-500">
                      {new Date(checkIn.check_in_time).toLocaleString()}
                    </div>
                  </div>
                </div>
                {checkIn.check_out_time ? (
                  <CheckCircleIcon className="w-6 h-6 text-green-600" />
                ) : (
                  <ClockIcon className="w-6 h-6 text-orange-600" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pending Credit Requests */}
      {pending_credits.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            {t('field_sales.pending_credits', 'Pending Credit Requests')}
          </h3>
          <div className="space-y-3">
            {pending_credits.slice(0, 3).map((credit) => (
              <div key={credit.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">{credit.customer_name}</div>
                  <div className="text-sm text-gray-500">
                    {credit.requested_amount.toLocaleString()} SAR
                  </div>
                </div>
                <div className="text-right">
                  {credit.ai_score && (
                    <div className="text-sm font-semibold text-blue-600">
                      AI Score: {credit.ai_score.toFixed(0)}
                    </div>
                  )}
                  <div className="text-xs text-gray-500">{credit.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
