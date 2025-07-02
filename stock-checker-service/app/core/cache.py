import json
from typing import Any, Optional, TypeVar, Generic, Type
import redis
from uuid import UUID

from app.core.config import settings

T = TypeVar('T')


class RedisCache:
    """Redis cache implementation"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            if settings.USE_REDIS_CACHE and settings.REDIS_URI:
                try:
                    cls._client = redis.from_url(str(settings.REDIS_URI))
                except Exception as e:
                    print(f"Error connecting to Redis: {e}")
                    cls._client = None
        return cls._instance
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self._client:
            return None
        
        try:
            value = self._client.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            print(f"Error getting value from Redis: {e}")
            return None
    
    def set(self, key: str, value: str, expiry: int = None) -> bool:
        """Set value in cache with optional expiry in seconds"""
        if not self._client:
            return False
        
        try:
            expiry = expiry or settings.REDIS_CACHE_EXPIRY
            return self._client.set(key, value, ex=expiry)
        except Exception as e:
            print(f"Error setting value in Redis: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self._client:
            return False
        
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            print(f"Error deleting value from Redis: {e}")
            return False
    
    def flush(self) -> bool:
        """Flush all cache"""
        if not self._client:
            return False
        
        try:
            return bool(self._client.flushdb())
        except Exception as e:
            print(f"Error flushing Redis: {e}")
            return False


class JsonCache(Generic[T]):
    """JSON object cache using Redis"""
    
    def __init__(self, model_class: Type[T], prefix: str = ""):
        self.cache = RedisCache()
        self.model_class = model_class
        self.prefix = prefix
    
    def _get_key(self, key: Any) -> str:
        """Format cache key with prefix"""
        if isinstance(key, UUID):
            key = str(key)
        return f"{self.prefix}:{key}" if self.prefix else key
    
    def get(self, key: Any) -> Optional[T]:
        """Get object from cache"""
        cache_key = self._get_key(key)
        data = self.cache.get(cache_key)
        
        if data:
            try:
                return self.model_class.model_validate_json(data)
            except Exception as e:
                print(f"Error deserializing object from cache: {e}")
        
        return None
    
    def set(self, key: Any, value: T, expiry: int = None) -> bool:
        """Set object in cache"""
        cache_key = self._get_key(key)
        try:
            json_data = value.model_dump_json()
            return self.cache.set(cache_key, json_data, expiry)
        except Exception as e:
            print(f"Error serializing object to cache: {e}")
            return False
    
    def delete(self, key: Any) -> bool:
        """Delete object from cache"""
        cache_key = self._get_key(key)
        return self.cache.delete(cache_key)
