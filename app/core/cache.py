import json
import logging
from typing import Any, Optional, List, Dict

from redis.asyncio import Redis as AsyncRedis
from upstash_redis import Redis as UpstashRedis

from app.core.config import Settings


logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._async_client: Optional[AsyncRedis] = None
        self._upstash_client: Optional[UpstashRedis] = None
        self._mode: Optional[str] = None # "upstash" or "redis"

    async def connect(self) -> None:
        # 1. Try Upstash First (if credentials exist)
        url = self._settings.upstash_redis_rest_url
        token = self._settings.upstash_redis_rest_token
        
        if url and token:
            try:
                url = url.strip('"').strip("'")
                token = token.strip('"').strip("'")
                self._upstash_client = UpstashRedis(url=url, token=token)
                self._mode = "upstash"
                logger.info(f"Redis cache connected via Upstash REST ({url[:20]}...)")
                return
            except Exception as e:
                logger.warning(f"Upstash Redis initialization failed: {e}")

        # 2. Try Standard Redis
        if self._settings.redis_url:
            try:
                self._async_client = AsyncRedis.from_url(
                    self._settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                await self._async_client.ping()
                self._mode = "redis"
                logger.info("Redis cache connected via TCP")
            except Exception as exc:
                logger.warning("Local Redis unavailable, continuing without cache.")
                self._async_client = None
                self._mode = None

    async def close(self) -> None:
        if self._async_client is not None:
            await self._async_client.aclose()

    async def get_json(self, key: str) -> dict[str, Any] | None:
        try:
            if self._mode == "upstash" and self._upstash_client:
                result = self._upstash_client.get(key)
                if result:
                    return json.loads(result) if isinstance(result, str) else result
            elif self._mode == "redis" and self._async_client:
                payload = await self._async_client.get(key)
                return json.loads(payload) if payload else None
        except Exception as e:
            logger.error(f"Cache GET error for {key}: {e}")
        return None

    async def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        try:
            if self._mode == "upstash" and self._upstash_client:
                self._upstash_client.set(key, json.dumps(value), ex=ttl_seconds)
                logger.info(f"Upstash Cache SET: {key}")
            elif self._mode == "redis" and self._async_client:
                await self._async_client.set(key, json.dumps(value), ex=ttl_seconds)
                logger.info(f"Redis Cache SET: {key}")
        except Exception as e:
            logger.error(f"Cache SET error for {key}: {e}")

    # Unified helpers for chat history
    async def add_message_to_history(self, user_id: str, message: list[str]) -> None:
        key = f"chat_history:{user_id}"
        serialized_msg = json.dumps(message)
        try:
            if self._mode == "upstash" and self._upstash_client:
                self._upstash_client.rpush(key, serialized_msg)
                self._upstash_client.ltrim(key, -10, -1)
                self._upstash_client.expire(key, 3600)
            elif self._mode == "redis" and self._async_client:
                await self._async_client.rpush(key, serialized_msg)
                await self._async_client.ltrim(key, -10, -1)
                await self._async_client.expire(key, 3600)
        except Exception as e:
            logger.error(f"Failed to add message to history: {e}")

    async def get_message_history(self, user_id: str) -> list:
        key = f"chat_history:{user_id}"
        try:
            history = []
            if self._mode == "upstash" and self._upstash_client:
                history = self._upstash_client.lrange(key, 0, -1)
            elif self._mode == "redis" and self._async_client:
                history = await self._async_client.lrange(key, 0, -1)
            
            if not history: return []
            
            parsed = []
            for msg in history:
                try:
                    parsed.append(json.loads(msg) if isinstance(msg, str) else msg)
                except: continue
            return parsed
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []

    # Standalone utilities migrated from services/cache.py
    def generate_cache_key(self, user_id: str, messages: list[str]) -> str:
        import hashlib
        input_str = "v3" + str(user_id) + "".join(messages)
        return hashlib.md5(input_str.encode("utf-8")).hexdigest()

    async def check_rate_limit(self, user_id: str, limit: int = 20) -> None:
        from fastapi import HTTPException
        key = f"usage:{user_id}"
        try:
            count = 0
            if self._mode == "upstash" and self._upstash_client:
                count = self._upstash_client.incr(key)
                if count == 1:
                    self._upstash_client.expire(key, 86400)
            elif self._mode == "redis" and self._async_client:
                count = await self._async_client.incr(key)
                if count == 1:
                    await self._async_client.expire(key, 86400)
            
            if count > limit:
                logger.warning(f"Rate limit exceeded for user: {user_id}")
                raise HTTPException(status_code=429, detail="Daily rate limit exceeded. Gain more credits to continue.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")

    async def delete(self, key: str) -> None:
        try:
            if self._mode == "upstash" and self._upstash_client:
                self._upstash_client.delete(key)
            elif self._mode == "redis" and self._async_client:
                await self._async_client.delete(key)
        except Exception as e:
            logger.error(f"Cache DELETE error for {key}: {e}")
