import redis.asyncio as aioredis

from app.core.config import settings

_redis: aioredis.Redis | None = None


async def init_redis() -> None:
    global _redis
    _redis = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


async def close_redis() -> None:
    if _redis:
        await _redis.aclose()


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialised — call init_redis() first")
    return _redis


async def publish(channel: str, message: str) -> None:
    await get_redis().publish(channel, message)


async def get_redis_value(key: str) -> str | None:
    """Generic GET helper for cache / blacklist lookups."""
    return await get_redis().get(key)


async def set_redis_value(key: str, value: str, ex: int | None = None) -> None:
    """Generic SET helper. ex = TTL in seconds."""
    await get_redis().set(key, value, ex=ex)


async def delete_redis_value(key: str) -> None:
    """Generic DEL helper."""
    await get_redis().delete(key)


async def increment_redis_counter(key: str, ex: int | None = None) -> int:
    """
    Atomically increments a counter and optionally sets TTL on first write.
    Used for rate limiting auth endpoints.
    """
    redis = get_redis()
    count = await redis.incr(key)
    if count == 1 and ex is not None:
        await redis.expire(key, ex)
    return count


# Channel constants
FEED_CHANNEL = "devpulse:feed"