# redis.py
import redis.asyncio as redis
from src.config import settings
from typing import Optional

JTI_EXPIRY = 3600  # 1 hour in seconds


class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Establish Redis connection"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            password=(
                settings.REDIS_PASSWORD if hasattr(settings, "REDIS_PASSWORD") else None
            ),
            decode_responses=False,  # Keep as bytes for performance
            max_connections=10,  # Connection pool size
        )
        # Test connection
        await self.client.ping()

    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.aclose()

    async def add_jti_to_BlockList(self, jti: str, ttl: int = None) -> None:
        if not self.client:
            await self.connect()
        await self.client.setex(
            name=jti, time=ttl or JTI_EXPIRY, value="1"  # Use meaningful value
        )

    async def token_in_BlockList(self, jti: str) -> bool:
        if not self.client:
            await self.connect()
        return await self.client.exists(jti) == 1

    async def get_token_info(self, jti: str) -> dict:
        """Get token metadata if needed"""
        if not self.client:
            await self.connect()
        ttl = await self.client.ttl(jti)
        return {"jti": jti, "ttl": ttl}


# Singleton instance
redis_client = RedisClient()

#!!!!!!!!!!!!!!7. Important Security Fix
# Legacy functions for backward compatibility
async def add_jti_to_BlockList(jti: str, ttl: int = None) -> None:
    await redis_client.add_jti_to_BlockList(jti, ttl)


async def token_in_BlockList(jti: str) -> bool:
    return await redis_client.token_in_BlockList(jti)


async def get_redis() -> RedisClient:
    """Dependency for FastAPI"""
    await redis_client.connect()
    return redis_client
