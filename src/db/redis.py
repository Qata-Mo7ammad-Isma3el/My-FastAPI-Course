import redis.asyncio as redis
from src.config import settings
JTI_EXPIRY= 3600  # 1 hour in seconds

token_BlockList = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db = 0 
)


async def add_jti_to_BlockList(jti: str) -> None:
    await token_BlockList.set(
        name= jti,
        value="",
        ex= JTI_EXPIRY
        )

async def token_in_BlockList(jti: str) -> bool:
    token = await token_BlockList.get(name= jti)
    return True if token is not None else False