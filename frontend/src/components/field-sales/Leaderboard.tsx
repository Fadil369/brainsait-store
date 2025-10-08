'use client';

import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TrophyIcon } from '@heroicons/react/24/outline';
import { fieldSalesApi } from '@/lib/api/field-sales';
import type { LeaderboardEntry } from '@/types/field-sales';

export default function Leaderboard() {
  const { t, i18n } = useTranslation();
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const isRTL = i18n.language === 'ar';

  useEffect(() => {
    loadLeaderboard();
  }, [period]);

  const loadLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await fieldSalesApi.getLeaderboard(period);
      setEntries(data.entries);
    } catch (err) {
      console.error('Failed to load leaderboard', err);
    } finally {
      setLoading(false);
    }
  };

  const getMedalEmoji = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  return (
    <div className={`max-w-4xl mx-auto p-4 ${isRTL ? 'rtl' : 'ltr'}`}>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <TrophyIcon className="w-8 h-8 text-yellow-500 mr-3" />
            {t('field_sales.leaderboard', 'Leaderboard')}
          </h2>
        </div>

        {/* Period Selector */}
        <div className="flex space-x-2 mb-6">
          {(['daily', 'weekly', 'monthly'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === p
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {t(`field_sales.${p}`, p.charAt(0).toUpperCase() + p.slice(1))}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
          </div>
        ) : entries.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            {t('field_sales.no_leaderboard_data', 'No leaderboard data available')}
          </p>
        ) : (
          <div className="space-y-3">
            {entries.map((entry) => (
              <div
                key={entry.sales_rep_id}
                className={`flex items-center justify-between p-4 rounded-lg ${
                  entry.rank <= 3
                    ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-2 border-yellow-300'
                    : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className="text-3xl font-bold w-12 text-center">
                    {getMedalEmoji(entry.rank)}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{entry.rep_name}</div>
                    {entry.territory && (
                      <div className="text-sm text-gray-500">{entry.territory}</div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">
                    {entry.total_sales.toLocaleString()} SAR
                  </div>
                  <div className="text-sm text-gray-600">
                    {entry.total_orders} {t('field_sales.orders', 'orders')} • {entry.points_earned} {t('field_sales.pts', 'pts')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
