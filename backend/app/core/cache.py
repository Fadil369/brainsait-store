"""
Enhanced caching system with multiple strategies and performance monitoring
"""

import json
import hashlib
import time
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Enhanced cache manager with multiple strategies"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.default_ttl = settings.CACHE_TTL
        
    async def get(self, key: str) -> Optional[Any]:
        """Get data from cache with error handling"""
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None
    
    async def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set data in cache with error handling"""
        try:
            ttl = ttl or self.default_ttl
            json_data = json.dumps(data, default=str)
            await self.redis_client.setex(key, ttl, json_data)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, pattern: str) -> bool:
        """Delete cache keys by pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for pattern {pattern}: {e}")
            return False
    
    async def get_or_set(self, key: str, fetch_func, ttl: Optional[int] = None) -> Any:
        """Get from cache or fetch and set if not exists"""
        # Try to get from cache first
        cached_data = await self.get(key)
        if cached_data is not None:
            return cached_data
        
        # Fetch data if not in cache
        try:
            fresh_data = await fetch_func()
            await self.set(key, fresh_data, ttl)
            return fresh_data
        except Exception as e:
            logger.error(f"Error fetching data for key {key}: {e}")
            raise
    
    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple keys at once"""
        try:
            values = await self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        logger.error(f"JSON decode error for key {key}")
            return result
        except Exception as e:
            logger.error(f"Cache mget error: {e}")
            return {}
    
    async def mset(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple keys at once"""
        try:
            ttl = ttl or self.default_ttl
            pipeline = self.redis_client.pipeline()
            
            for key, value in data.items():
                json_data = json.dumps(value, default=str)
                pipeline.setex(key, ttl, json_data)
            
            await pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Cache mset error: {e}")
            return False
    
    def generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    def generate_hash_key(self, prefix: str, data: Dict) -> str:
        """Generate cache key with hash for complex data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
        return f"{prefix}:hash:{data_hash}"

# Global cache manager instance
cache_manager = CacheManager()

def cache_result(prefix: str, ttl: Optional[int] = None, key_func=None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation from function name and arguments
                key_parts = [prefix, func.__name__]
                for arg in args:
                    if hasattr(arg, 'id'):
                        key_parts.append(str(arg.id))
                    elif isinstance(arg, (str, int, float)):
                        key_parts.append(str(arg))
                for k, v in kwargs.items():
                    key_parts.append(f"{k}:{v}")
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def cache_invalidate(pattern: str):
    """Decorator for invalidating cache on function execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await cache_manager.delete(pattern)
            return result
        return wrapper
    return decorator

class CacheStats:
    """Cache statistics tracking"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
    
    def hit(self):
        self.hits += 1
    
    def miss(self):
        self.misses += 1
    
    def set(self):
        self.sets += 1
    
    def delete(self):
        self.deletes += 1
    
    def error(self):
        self.errors += 1
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "hit_rate": round(self.hit_rate, 2),
        }

# Global cache stats instance
cache_stats = CacheStats()

# Product-specific cache functions
async def cache_product_list(
    tenant_id: str,
    language: str,
    filters: Dict[str, Any],
    page: int = 1,
    per_page: int = 20
) -> str:
    """Generate cache key for product listings"""
    return cache_manager.generate_hash_key(
        f"products:{tenant_id}:{language}:{page}:{per_page}",
        filters
    )

async def cache_category_tree(tenant_id: str, language: str) -> str:
    """Generate cache key for category tree"""
    return f"categories:tree:{tenant_id}:{language}"

async def cache_user_permissions(user_id: str, tenant_id: str) -> str:
    """Generate cache key for user permissions"""
    return f"permissions:{tenant_id}:{user_id}"

# Warming cache functions
async def warm_cache():
    """Warm up frequently accessed cache"""
    logger.info("Warming up cache...")
    
    # Here you would pre-populate cache with frequently accessed data
    # For example:
    # - Popular products
    # - Category trees
    # - Common search results
    
    logger.info("Cache warming completed")

# Cache monitoring
async def get_cache_health() -> Dict[str, Any]:
    """Get cache health and statistics"""
    try:
        # Test Redis connection
        await cache_manager.redis_client.ping()
        redis_status = "healthy"
        
        # Get Redis info
        redis_info = await cache_manager.redis_client.info()
        memory_usage = redis_info.get('used_memory_human', 'unknown')
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}", exc_info=True)
        redis_status = "error"
        memory_usage = "unknown"
    
    return {
        "status": redis_status,
        "memory_usage": memory_usage,
        "stats": cache_stats.get_stats(),
    }