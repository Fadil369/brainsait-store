'use client';

import React, { useEffect, useState } from 'react';
import { ChevronRightIcon, StarIcon, ArrowTrendingUpIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { oidSystemService } from '@/lib/oid-integration';

interface Recommendation {
  id: string;
  name: string;
  price: number;
  score: number;
  reason?: string;
  category_id?: string;
  image_url?: string;
  seasonal_relevance?: string;
}

interface RecommendationEngineProps {
  userId?: string;
  productId?: string;
  limit?: number;
  showPersonalized?: boolean;
  showTrending?: boolean;
  showSeasonal?: boolean;
  showSimilar?: boolean;
  className?: string;
}

const RecommendationEngine: React.FC<RecommendationEngineProps> = ({
  userId,
  productId,
  limit = 10,
  showPersonalized = true,
  showTrending = true,
  showSeasonal = false,
  showSimilar = false,
  className = ''
}) => {
  const [personalizedRecs, setPersonalizedRecs] = useState<Recommendation[]>([]);
  const [trendingRecs, setTrendingRecs] = useState<Recommendation[]>([]);
  const [seasonalRecs, setSeasonalRecs] = useState<Recommendation[]>([]);
  const [similarRecs, setSimilarRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'personalized' | 'trending' | 'seasonal' | 'similar'>('personalized');

  // Get current season
  const getCurrentSeason = () => {
    const month = new Date().getMonth();
    if (month >= 2 && month <= 4) return 'spring';
    if (month >= 5 && month <= 7) return 'summer';
    if (month >= 8 && month <= 10) return 'autumn';
    return 'winter';
  };

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);

      try {
        const promises = [];

        if (showPersonalized) {
          promises.push(
            oidSystemService.getPersonalizedRecommendations(limit)
              .then(recs => setPersonalizedRecs(recs))
              .catch(err => console.error('Failed to fetch personalized recommendations:', err))
          );
        }

        if (showTrending) {
          promises.push(
            oidSystemService.getTrendingRecommendations(limit)
              .then(recs => setTrendingRecs(recs))
              .catch(err => console.error('Failed to fetch trending recommendations:', err))
          );
        }

        if (showSeasonal) {
          const currentSeason = getCurrentSeason();
          promises.push(
            oidSystemService.getSeasonalRecommendations(currentSeason, limit)
              .then(recs => setSeasonalRecs(recs))
              .catch(err => console.error('Failed to fetch seasonal recommendations:', err))
          );
        }

        if (showSimilar && productId) {
          promises.push(
            oidSystemService.getSimilarProducts(productId, limit)
              .then(recs => setSimilarRecs(recs))
              .catch(err => console.error('Failed to fetch similar products:', err))
          );
        }

        await Promise.all(promises);
      } catch (err) {
        setError('Failed to load recommendations');
        console.error('Error fetching recommendations:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [userId, productId, limit, showPersonalized, showTrending, showSeasonal, showSimilar]);

  const handleProductClick = async (recommendation: Recommendation) => {
    // Track user behavior
    await oidSystemService.trackUserBehavior('view', recommendation.id, {
      source: 'recommendations',
      recommendation_type: activeTab,
      score: recommendation.score
    });

    // Navigate to product (you'd implement this based on your routing)
    window.location.href = `/products/${recommendation.id}`;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: 'SAR'
    }).format(price);
  };

  const getTabIcon = (tab: string) => {
    switch (tab) {
      case 'personalized':
        return <SparklesIcon className="h-5 w-5" />;
      case 'trending':
        return <ArrowTrendingUpIcon className="h-5 w-5" />;
      case 'seasonal':
        return <StarIcon className="h-5 w-5" />;
      case 'similar':
        return <ChevronRightIcon className="h-5 w-5" />;
      default:
        return null;
    }
  };

  const getCurrentRecommendations = () => {
    switch (activeTab) {
      case 'personalized':
        return personalizedRecs;
      case 'trending':
        return trendingRecs;
      case 'seasonal':
        return seasonalRecs;
      case 'similar':
        return similarRecs;
      default:
        return [];
    }
  };

  const getTabTitle = (tab: string) => {
    switch (tab) {
      case 'personalized':
        return 'For You';
      case 'trending':
        return 'Trending';
      case 'seasonal':
        return `${getCurrentSeason().charAt(0).toUpperCase() + getCurrentSeason().slice(1)} Picks`;
      case 'similar':
        return 'Similar Products';
      default:
        return '';
    }
  };

  if (loading) {
    return (
      <div className={`recommendation-engine ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="bg-gray-300 h-64 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`recommendation-engine ${className}`}>
        <div className="text-center text-red-600 p-4">
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-2 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const availableTabs = [];
  if (showPersonalized && personalizedRecs.length > 0) availableTabs.push('personalized');
  if (showTrending && trendingRecs.length > 0) availableTabs.push('trending');
  if (showSeasonal && seasonalRecs.length > 0) availableTabs.push('seasonal');
  if (showSimilar && similarRecs.length > 0) availableTabs.push('similar');

  if (availableTabs.length === 0) {
    return (
      <div className={`recommendation-engine ${className}`}>
        <div className="text-center text-gray-500 p-8">
          <p>No recommendations available at the moment.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`recommendation-engine ${className}`}>
      {/* Tab Navigation */}
      {availableTabs.length > 1 && (
        <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
          {availableTabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
                activeTab === tab
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {getTabIcon(tab)}
              <span className="font-medium">{getTabTitle(tab)}</span>
            </button>
          ))}
        </div>
      )}

      {/* Recommendations Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {getCurrentRecommendations().map((recommendation) => (
          <div
            key={recommendation.id}
            onClick={() => handleProductClick(recommendation)}
            className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
          >
            {/* Product Image */}
            <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
              {recommendation.image_url ? (
                <img
                  src={recommendation.image_url}
                  alt={recommendation.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 text-sm mb-2 line-clamp-2">
                {recommendation.name}
              </h3>
              
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg font-bold text-green-600">
                  {formatPrice(recommendation.price)}
                </span>
                <div className="flex items-center text-xs text-gray-500">
                  <StarIcon className="h-3 w-3 mr-1" />
                  <span>{recommendation.score.toFixed(1)}</span>
                </div>
              </div>

              {recommendation.reason && (
                <p className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                  {recommendation.reason}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Show More Button */}
      {getCurrentRecommendations().length >= limit && (
        <div className="text-center mt-6">
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            View More Recommendations
          </button>
        </div>
      )}
    </div>
  );
};

export default RecommendationEngine;