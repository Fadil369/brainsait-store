"""
Test cases for the Product Recommendation Engine
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.services.recommendation_engine import RecommendationEngine


class TestRecommendationEngine:
    """Test the recommendation engine functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection"""
        return AsyncMock()

    @pytest.fixture
    def recommendation_engine(self, mock_db):
        """Create recommendation engine instance"""
        engine = RecommendationEngine(mock_db, "test-tenant")
        return engine

    @pytest.mark.asyncio
    async def test_get_personalized_recommendations(self, recommendation_engine, mock_db):
        """Test personalized recommendations"""
        user_id = uuid4()
        
        # Mock user interactions
        recommendation_engine._get_user_interactions = AsyncMock(return_value={
            uuid4(): 4.5,
            uuid4(): 3.8
        })
        
        # Mock collaborative filtering
        recommendation_engine._collaborative_filtering = AsyncMock(return_value=[
            {
                'id': str(uuid4()),
                'name': 'Test Product 1',
                'price': 100.0,
                'score': 0.8
            }
        ])
        
        # Mock content-based filtering
        recommendation_engine._content_based_filtering = AsyncMock(return_value=[
            {
                'id': str(uuid4()),
                'name': 'Test Product 2',
                'price': 150.0,
                'score': 0.7
            }
        ])
        
        # Mock trending products
        recommendation_engine._get_trending_products = AsyncMock(return_value=[
            {
                'id': str(uuid4()),
                'name': 'Test Product 3',
                'price': 200.0,
                'score': 0.6
            }
        ])
        
        recommendations = await recommendation_engine.get_personalized_recommendations(user_id, 5)
        
        assert len(recommendations) <= 5
        assert all('score' in rec for rec in recommendations)
        assert all('reason' in rec for rec in recommendations)

    @pytest.mark.asyncio
    async def test_get_trending_products(self, recommendation_engine, mock_db):
        """Test trending products functionality"""
        # Mock database query result
        mock_result = MagicMock()
        mock_product = MagicMock()
        mock_product.id = uuid4()
        mock_product.name = "Trending Product"
        mock_product.price = 99.99
        mock_product.purchase_count = 50
        mock_product.view_count = 1000
        mock_product.category_id = uuid4()
        mock_product.image_url = "https://example.com/image.jpg"
        
        mock_result.scalars.return_value.all.return_value = [mock_product]
        mock_db.execute.return_value = mock_result
        
        trending = await recommendation_engine._get_trending_products(10)
        
        assert len(trending) == 1
        assert trending[0]['name'] == "Trending Product"
        assert trending[0]['price'] == 99.99
        assert 'score' in trending[0]

    @pytest.mark.asyncio
    async def test_track_user_behavior(self, recommendation_engine):
        """Test user behavior tracking"""
        user_id = uuid4()
        product_id = uuid4()
        
        # Mock Redis
        recommendation_engine.redis = AsyncMock()
        recommendation_engine.redis.lpush = AsyncMock()
        recommendation_engine.redis.expire = AsyncMock()
        
        await recommendation_engine.track_user_behavior(
            user_id, 'view', product_id, {'source': 'test'}
        )
        
        recommendation_engine.redis.lpush.assert_called_once()
        recommendation_engine.redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_seasonal_recommendations(self, recommendation_engine, mock_db):
        """Test seasonal recommendations"""
        # Mock database query result
        mock_result = MagicMock()
        mock_product = MagicMock()
        mock_product.id = uuid4()
        mock_product.name = "Spring Product"
        mock_product.price = 75.0
        mock_product.purchase_count = 25
        mock_product.category_id = uuid4()
        mock_product.image_url = "https://example.com/spring.jpg"
        
        mock_result.scalars.return_value.all.return_value = [mock_product]
        mock_db.execute.return_value = mock_result
        
        seasonal = await recommendation_engine.get_seasonal_recommendations('spring', 5)
        
        assert len(seasonal) == 1
        assert seasonal[0]['name'] == "Spring Product"
        assert seasonal[0]['seasonal_relevance'] == 'spring'

    def test_calculate_cosine_similarity(self, recommendation_engine):
        """Test cosine similarity calculation"""
        ratings1 = {uuid4(): 4.0, uuid4(): 3.5, uuid4(): 5.0}
        ratings2 = {list(ratings1.keys())[0]: 4.5, list(ratings1.keys())[1]: 3.0, list(ratings1.keys())[2]: 5.0}
        
        similarity = recommendation_engine._calculate_cosine_similarity(ratings1, ratings2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.8  # Should be high similarity

    def test_calculate_cosine_similarity_no_common_products(self, recommendation_engine):
        """Test cosine similarity with no common products"""
        ratings1 = {uuid4(): 4.0, uuid4(): 3.5}
        ratings2 = {uuid4(): 4.5, uuid4(): 3.0}
        
        similarity = recommendation_engine._calculate_cosine_similarity(ratings1, ratings2)
        
        assert similarity == 0.0

    @pytest.mark.asyncio
    async def test_fallback_to_trending_on_error(self, recommendation_engine):
        """Test fallback behavior when personalized recommendations fail"""
        user_id = uuid4()
        
        # Mock methods to raise exceptions
        recommendation_engine._get_user_interactions = AsyncMock(side_effect=Exception("DB error"))
        recommendation_engine._get_trending_products = AsyncMock(return_value=[
            {
                'id': str(uuid4()),
                'name': 'Fallback Product',
                'price': 50.0,
                'score': 0.5
            }
        ])
        
        recommendations = await recommendation_engine.get_personalized_recommendations(user_id, 5)
        
        assert len(recommendations) == 1
        assert recommendations[0]['name'] == 'Fallback Product'

    @pytest.mark.asyncio 
    async def test_empty_user_interactions(self, recommendation_engine):
        """Test behavior with users who have no interaction history"""
        user_id = uuid4()
        
        # Mock empty user interactions
        recommendation_engine._get_user_interactions = AsyncMock(return_value={})
        recommendation_engine._get_trending_products = AsyncMock(return_value=[
            {
                'id': str(uuid4()),
                'name': 'Default Product',
                'price': 25.0,
                'score': 0.3
            }
        ])
        
        recommendations = await recommendation_engine.get_personalized_recommendations(user_id, 5)
        
        # Should fallback to trending products for new users
        assert len(recommendations) == 1
        assert recommendations[0]['name'] == 'Default Product'


if __name__ == "__main__":
    pytest.main([__file__])