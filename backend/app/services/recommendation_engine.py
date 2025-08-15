"""
Advanced Product Recommendation Engine
Implements collaborative filtering, behavioral analytics, and intelligent product suggestions
"""

import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_redis
from app.models.products import Product, ProductReview
from app.models.users import User

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Advanced recommendation engine with multiple algorithms"""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.redis = get_redis()

    async def get_personalized_recommendations(
        self, user_id: UUID, limit: int = 10
    ) -> List[Dict]:
        """Get personalized product recommendations for a user"""
        try:
            # Combine multiple recommendation strategies
            collaborative_recs = await self._collaborative_filtering(user_id, limit // 2)
            content_based_recs = await self._content_based_filtering(user_id, limit // 2)
            trending_recs = await self._get_trending_products(limit // 4)

            # Merge and deduplicate recommendations
            all_recs = {}
            
            # Add collaborative filtering results (highest weight)
            for i, rec in enumerate(collaborative_recs):
                all_recs[rec['id']] = {
                    **rec,
                    'score': rec.get('score', 0) + 0.6,
                    'reason': 'Users with similar preferences also liked this'
                }

            # Add content-based results (medium weight)
            for i, rec in enumerate(content_based_recs):
                if rec['id'] in all_recs:
                    all_recs[rec['id']]['score'] += 0.4
                    all_recs[rec['id']]['reason'] += ', Similar to your interests'
                else:
                    all_recs[rec['id']] = {
                        **rec,
                        'score': rec.get('score', 0) + 0.4,
                        'reason': 'Similar to your interests'
                    }

            # Add trending products (lower weight)
            for i, rec in enumerate(trending_recs):
                if rec['id'] in all_recs:
                    all_recs[rec['id']]['score'] += 0.2
                else:
                    all_recs[rec['id']] = {
                        **rec,
                        'score': rec.get('score', 0) + 0.2,
                        'reason': 'Trending now'
                    }

            # Sort by score and return top recommendations
            sorted_recs = sorted(all_recs.values(), key=lambda x: x['score'], reverse=True)
            return sorted_recs[:limit]

        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            # Fallback to trending products
            return await self._get_trending_products(limit)

    async def _collaborative_filtering(self, user_id: UUID, limit: int) -> List[Dict]:
        """Implement collaborative filtering recommendation"""
        try:
            # Get user's purchase/review history
            user_products = await self._get_user_interactions(user_id)
            if not user_products:
                return []

            # Find similar users based on common products
            similar_users = await self._find_similar_users(user_id, user_products)
            
            # Get products liked by similar users
            recommendations = []
            for similar_user_id, similarity_score in similar_users[:10]:
                similar_user_products = await self._get_user_interactions(similar_user_id)
                
                for product_id, rating in similar_user_products.items():
                    if product_id not in user_products:  # User hasn't interacted with this product
                        recommendations.append({
                            'product_id': product_id,
                            'score': rating * similarity_score
                        })

            # Group by product and calculate average score
            product_scores = {}
            for rec in recommendations:
                pid = rec['product_id']
                if pid not in product_scores:
                    product_scores[pid] = []
                product_scores[pid].append(rec['score'])

            # Calculate final scores
            final_recs = []
            for product_id, scores in product_scores.items():
                avg_score = sum(scores) / len(scores)
                final_recs.append({
                    'product_id': product_id,
                    'score': avg_score
                })

            # Sort by score and get product details
            final_recs.sort(key=lambda x: x['score'], reverse=True)
            return await self._get_product_details(final_recs[:limit])

        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []

    async def _content_based_filtering(self, user_id: UUID, limit: int) -> List[Dict]:
        """Implement content-based filtering recommendation"""
        try:
            # Get user's interaction history
            user_products = await self._get_user_interactions(user_id)
            if not user_products:
                return []

            # Get user's preferred categories and tags
            preferred_categories, preferred_tags = await self._analyze_user_preferences(user_products.keys())

            # Find products with similar characteristics
            query = (
                select(Product)
                .where(
                    and_(
                        Product.tenant_id == self.tenant_id,
                        Product.is_active == True,
                        Product.status == "active",
                        ~Product.id.in_(user_products.keys())
                    )
                )
                .order_by(desc(Product.created_at))
                .limit(50)  # Get more products to score
            )

            result = await self.db.execute(query)
            products = result.scalars().all()

            # Score products based on user preferences
            scored_products = []
            for product in products:
                score = 0
                
                # Category preference score
                if product.category_id in preferred_categories:
                    score += preferred_categories[product.category_id] * 0.4
                
                # Tag preference score
                product_tags = (product.tags or []) + (product.tags_ar or [])
                for tag in product_tags:
                    if tag in preferred_tags:
                        score += preferred_tags[tag] * 0.3
                
                # Popularity score
                score += min(product.purchase_count / 100, 0.3)  # Normalize and cap at 0.3
                
                if score > 0:
                    scored_products.append({
                        'id': str(product.id),
                        'name': product.name,
                        'price': float(product.price),
                        'score': score,
                        'category_id': str(product.category_id) if product.category_id else None,
                        'image_url': product.image_url
                    })

            # Sort by score and return top results
            scored_products.sort(key=lambda x: x['score'], reverse=True)
            return scored_products[:limit]

        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []

    async def _get_trending_products(self, limit: int) -> List[Dict]:
        """Get trending products based on recent activity"""
        try:
            # Calculate trending score based on recent purchases and views
            query = (
                select(Product)
                .where(
                    and_(
                        Product.tenant_id == self.tenant_id,
                        Product.is_active == True,
                        Product.status == "active"
                    )
                )
                .order_by(
                    desc(Product.purchase_count + Product.view_count / 10)
                )
                .limit(limit)
            )

            result = await self.db.execute(query)
            products = result.scalars().all()

            return [
                {
                    'id': str(product.id),
                    'name': product.name,
                    'price': float(product.price),
                    'score': product.purchase_count + product.view_count / 10,
                    'category_id': str(product.category_id) if product.category_id else None,
                    'image_url': product.image_url,
                    'purchase_count': product.purchase_count,
                    'view_count': product.view_count
                }
                for product in products
            ]

        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []

    async def _get_user_interactions(self, user_id: UUID) -> Dict[UUID, float]:
        """Get user's interaction history with products"""
        try:
            interactions = {}
            
            # Get user's reviews (explicit ratings)
            review_query = (
                select(ProductReview)
                .where(ProductReview.user_id == user_id)
            )
            review_result = await self.db.execute(review_query)
            reviews = review_result.scalars().all()
            
            for review in reviews:
                interactions[review.product_id] = review.rating

            # Note: In a real implementation, you'd also track:
            # - Purchase history
            # - View history
            # - Add to cart events
            # - Time spent viewing products
            
            return interactions

        except Exception as e:
            logger.error(f"Error getting user interactions: {e}")
            return {}

    async def _find_similar_users(self, user_id: UUID, user_products: Dict[UUID, float]) -> List[Tuple[UUID, float]]:
        """Find users with similar preferences using cosine similarity"""
        try:
            if not user_products:
                return []

            # Get all users who have reviewed the same products
            product_ids = list(user_products.keys())
            query = (
                select(ProductReview)
                .where(
                    and_(
                        ProductReview.product_id.in_(product_ids),
                        ProductReview.user_id != user_id
                    )
                )
            )
            
            result = await self.db.execute(query)
            all_reviews = result.scalars().all()

            # Group reviews by user
            user_ratings = {}
            for review in all_reviews:
                if review.user_id not in user_ratings:
                    user_ratings[review.user_id] = {}
                user_ratings[review.user_id][review.product_id] = review.rating

            # Calculate similarity scores
            similarities = []
            for other_user_id, other_ratings in user_ratings.items():
                similarity = self._calculate_cosine_similarity(user_products, other_ratings)
                if similarity > 0.1:  # Only include users with significant similarity
                    similarities.append((other_user_id, similarity))

            # Sort by similarity and return top users
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:20]

        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []

    def _calculate_cosine_similarity(self, ratings1: Dict[UUID, float], ratings2: Dict[UUID, float]) -> float:
        """Calculate cosine similarity between two rating vectors"""
        try:
            # Find common products
            common_products = set(ratings1.keys()) & set(ratings2.keys())
            if not common_products:
                return 0.0

            # Create vectors for common products
            vector1 = [ratings1[pid] for pid in common_products]
            vector2 = [ratings2[pid] for pid in common_products]

            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(vector1, vector2))
            norm1 = sum(a * a for a in vector1) ** 0.5
            norm2 = sum(b * b for b in vector2) ** 0.5

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    async def _analyze_user_preferences(self, product_ids: List[UUID]) -> Tuple[Dict[UUID, float], Dict[str, float]]:
        """Analyze user preferences from their interaction history"""
        try:
            # Get product details
            query = (
                select(Product)
                .where(Product.id.in_(product_ids))
            )
            result = await self.db.execute(query)
            products = result.scalars().all()

            # Count category preferences
            category_counts = {}
            tag_counts = {}
            
            for product in products:
                # Category preferences
                if product.category_id:
                    category_counts[product.category_id] = category_counts.get(product.category_id, 0) + 1
                
                # Tag preferences
                all_tags = (product.tags or []) + (product.tags_ar or [])
                for tag in all_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Normalize to preferences (0-1 scale)
            total_products = len(products)
            if total_products == 0:
                return {}, {}

            category_prefs = {k: v / total_products for k, v in category_counts.items()}
            tag_prefs = {k: v / total_products for k, v in tag_counts.items()}

            return category_prefs, tag_prefs

        except Exception as e:
            logger.error(f"Error analyzing user preferences: {e}")
            return {}, {}

    async def _get_product_details(self, product_recommendations: List[Dict]) -> List[Dict]:
        """Get detailed product information for recommendations"""
        try:
            product_ids = [UUID(rec['product_id']) for rec in product_recommendations]
            
            query = (
                select(Product)
                .where(Product.id.in_(product_ids))
            )
            result = await self.db.execute(query)
            products = result.scalars().all()

            # Create product lookup
            product_lookup = {str(p.id): p for p in products}

            # Combine recommendation scores with product details
            detailed_recs = []
            for rec in product_recommendations:
                product = product_lookup.get(rec['product_id'])
                if product:
                    detailed_recs.append({
                        'id': str(product.id),
                        'name': product.name,
                        'price': float(product.price),
                        'score': rec['score'],
                        'category_id': str(product.category_id) if product.category_id else None,
                        'image_url': product.image_url,
                        'description': product.description
                    })

            return detailed_recs

        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return []

    async def track_user_behavior(self, user_id: UUID, action: str, product_id: UUID, metadata: Dict = None):
        """Track user behavior for improving recommendations"""
        try:
            behavior_data = {
                'user_id': str(user_id),
                'action': action,  # 'view', 'add_to_cart', 'purchase', 'review'
                'product_id': str(product_id),
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }

            # Store in Redis for real-time tracking
            key = f"user_behavior:{self.tenant_id}:{user_id}:{action}"
            await self.redis.lpush(key, json.dumps(behavior_data))
            await self.redis.expire(key, 86400 * 30)  # Keep for 30 days

            # Update product view count if it's a view action
            if action == 'view':
                update_query = (
                    select(Product)
                    .where(Product.id == product_id)
                )
                result = await self.db.execute(update_query)
                product = result.scalar_one_or_none()
                if product:
                    product.view_count += 1
                    await self.db.commit()

        except Exception as e:
            logger.error(f"Error tracking user behavior: {e}")

    async def get_seasonal_recommendations(self, season: str, limit: int = 10) -> List[Dict]:
        """Get seasonal product recommendations"""
        try:
            # Define seasonal keywords
            seasonal_keywords = {
                'spring': ['spring', 'fresh', 'new', 'renewal'],
                'summer': ['summer', 'vacation', 'outdoor', 'hot'],
                'autumn': ['autumn', 'fall', 'harvest', 'cozy'],
                'winter': ['winter', 'holiday', 'warm', 'celebration']
            }

            keywords = seasonal_keywords.get(season.lower(), [])
            if not keywords:
                return await self._get_trending_products(limit)

            # Search for products with seasonal keywords
            products = []
            for keyword in keywords:
                query = (
                    select(Product)
                    .where(
                        and_(
                            Product.tenant_id == self.tenant_id,
                            Product.is_active == True,
                            Product.status == "active",
                            func.lower(Product.name).contains(keyword.lower()) |
                            Product.name.ilike(f"%{keyword}%") |
                            Product.description.ilike(f"%{keyword}%") |
                            Product.tags.contains([keyword]) |
                            Product.tags_ar.contains([keyword])
                        )
                    )
                    .order_by(desc(Product.purchase_count))
                    .limit(limit)
                )
                
                result = await self.db.execute(query)
                seasonal_products = result.scalars().all()
                products.extend(seasonal_products)

            # Remove duplicates and format
            seen_ids = set()
            unique_products = []
            for product in products:
                if product.id not in seen_ids:
                    unique_products.append({
                        'id': str(product.id),
                        'name': product.name,
                        'price': float(product.price),
                        'score': product.purchase_count,
                        'category_id': str(product.category_id) if product.category_id else None,
                        'image_url': product.image_url,
                        'seasonal_relevance': season
                    })
                    seen_ids.add(product.id)

            return unique_products[:limit]

        except Exception as e:
            logger.error(f"Error getting seasonal recommendations: {e}")
            return []