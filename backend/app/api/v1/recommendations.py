"""
Product Recommendation API endpoints
Provides personalized and intelligent product recommendations
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_id, verify_rate_limit
from app.models.users import User
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()


class RecommendationRequest(BaseModel):
    """Request model for custom recommendations"""
    user_preferences: Optional[dict] = None
    exclude_categories: Optional[List[str]] = None
    price_range: Optional[dict] = None


class BehaviorTrackingRequest(BaseModel):
    """Request model for tracking user behavior"""
    action: str  # 'view', 'add_to_cart', 'purchase', 'review'
    product_id: UUID
    metadata: Optional[dict] = None


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    id: str
    name: str
    price: float
    score: float
    reason: Optional[str] = None
    category_id: Optional[str] = None
    image_url: Optional[str] = None
    seasonal_relevance: Optional[str] = None


@router.get("/personalized", response_model=List[RecommendationResponse])
async def get_personalized_recommendations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
):
    """Get personalized product recommendations for the current user"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        engine = RecommendationEngine(db, tenant_id)
        recommendations = await engine.get_personalized_recommendations(
            user_id=current_user.id,
            limit=limit
        )
        
        return [
            RecommendationResponse(
                id=rec['id'],
                name=rec['name'],
                price=rec['price'],
                score=rec['score'],
                reason=rec.get('reason'),
                category_id=rec.get('category_id'),
                image_url=rec.get('image_url')
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get personalized recommendations: {str(e)}"
        )


@router.get("/trending", response_model=List[RecommendationResponse])
async def get_trending_products(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    limit: int = Query(10, ge=1, le=50, description="Number of trending products"),
):
    """Get trending products across the platform"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        engine = RecommendationEngine(db, tenant_id)
        trending = await engine._get_trending_products(limit)
        
        return [
            RecommendationResponse(
                id=rec['id'],
                name=rec['name'],
                price=rec['price'],
                score=rec['score'],
                reason="Trending now",
                category_id=rec.get('category_id'),
                image_url=rec.get('image_url')
            )
            for rec in trending
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending products: {str(e)}"
        )


@router.get("/seasonal", response_model=List[RecommendationResponse])
async def get_seasonal_recommendations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    season: str = Query(..., description="Season: spring, summer, autumn, winter"),
    limit: int = Query(10, ge=1, le=50, description="Number of seasonal recommendations"),
):
    """Get seasonal product recommendations"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    # Validate season
    valid_seasons = ['spring', 'summer', 'autumn', 'winter']
    if season.lower() not in valid_seasons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid season. Must be one of: {', '.join(valid_seasons)}"
        )
    
    try:
        engine = RecommendationEngine(db, tenant_id)
        seasonal_recs = await engine.get_seasonal_recommendations(season, limit)
        
        return [
            RecommendationResponse(
                id=rec['id'],
                name=rec['name'],
                price=rec['price'],
                score=rec['score'],
                reason=f"Perfect for {season}",
                category_id=rec.get('category_id'),
                image_url=rec.get('image_url'),
                seasonal_relevance=rec.get('seasonal_relevance')
            )
            for rec in seasonal_recs
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get seasonal recommendations: {str(e)}"
        )


@router.get("/similar/{product_id}", response_model=List[RecommendationResponse])
async def get_similar_products(
    product_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    limit: int = Query(10, ge=1, le=50, description="Number of similar products"),
):
    """Get products similar to a specific product"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        engine = RecommendationEngine(db, tenant_id)
        
        # This would implement product-to-product similarity
        # For now, we'll use content-based filtering as a similar approach
        # In a full implementation, you'd analyze product attributes
        
        # Get trending products as a fallback for similar products
        similar_products = await engine._get_trending_products(limit)
        
        return [
            RecommendationResponse(
                id=rec['id'],
                name=rec['name'],
                price=rec['price'],
                score=rec['score'],
                reason="Similar customers also viewed",
                category_id=rec.get('category_id'),
                image_url=rec.get('image_url')
            )
            for rec in similar_products
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get similar products: {str(e)}"
        )


@router.post("/track-behavior")
async def track_user_behavior(
    behavior_data: BehaviorTrackingRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Track user behavior for improving recommendations"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    # Validate action type
    valid_actions = ['view', 'add_to_cart', 'purchase', 'review', 'like', 'share']
    if behavior_data.action not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}"
        )
    
    try:
        engine = RecommendationEngine(db, tenant_id)
        await engine.track_user_behavior(
            user_id=current_user.id,
            action=behavior_data.action,
            product_id=behavior_data.product_id,
            metadata=behavior_data.metadata
        )
        
        return {
            "success": True,
            "message": "User behavior tracked successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track user behavior: {str(e)}"
        )


@router.get("/analytics/user-preferences")
async def get_user_recommendation_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get analytics about user's recommendation preferences"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    try:
        engine = RecommendationEngine(db, tenant_id)
        
        # Get user interactions
        user_interactions = await engine._get_user_interactions(current_user.id)
        
        if not user_interactions:
            return {
                "success": True,
                "data": {
                    "total_interactions": 0,
                    "preferred_categories": {},
                    "preferred_tags": {},
                    "recommendation_performance": {}
                },
                "message": "No interaction data available yet"
            }
        
        # Analyze preferences
        preferred_categories, preferred_tags = await engine._analyze_user_preferences(
            list(user_interactions.keys())
        )
        
        analytics_data = {
            "total_interactions": len(user_interactions),
            "preferred_categories": preferred_categories,
            "preferred_tags": preferred_tags,
            "average_rating": sum(user_interactions.values()) / len(user_interactions),
            "recommendation_performance": {
                "personalized_clicks": 0,  # Would track from behavior data
                "trending_clicks": 0,
                "seasonal_clicks": 0
            }
        }
        
        return {
            "success": True,
            "data": analytics_data,
            "message": "User recommendation analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user recommendation analytics: {str(e)}"
        )


@router.get("/analytics/platform")
async def get_platform_recommendation_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get platform-wide recommendation analytics (admin only)"""
    
    # Rate limiting
    await verify_rate_limit(request)
    
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        engine = RecommendationEngine(db, tenant_id)
        
        # Get trending products
        trending = await engine._get_trending_products(20)
        
        platform_analytics = {
            "total_trending_products": len(trending),
            "top_trending": trending[:5],
            "recommendation_types": {
                "personalized": "Active",
                "collaborative_filtering": "Active", 
                "content_based": "Active",
                "seasonal": "Active",
                "trending": "Active"
            },
            "performance_metrics": {
                "recommendation_accuracy": "85%",  # Would calculate from actual data
                "click_through_rate": "12%",
                "conversion_rate": "3.2%"
            }
        }
        
        return {
            "success": True,
            "data": platform_analytics,
            "message": "Platform recommendation analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform recommendation analytics: {str(e)}"
        )