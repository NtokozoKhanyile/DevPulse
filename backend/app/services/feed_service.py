from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Project
from app.core.redis import get_redis, FEED_CHANNEL
from app.dependencies.pagination import PageParams


async def get_feed(db: AsyncSession, pagination: PageParams) -> list[Project]:
    """
    Returns public projects ordered by most recently updated.
    Eagerly loads owner and milestones for each project to avoid N+1.
    """
    stmt = (
        select(Project)
        .where(Project.is_public == True)
        .options(selectinload(Project.owner))
        .options(selectinload(Project.milestones))
        .order_by(Project.updated_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def subscribe_to_feed():
    """
    Returns an async generator that yields raw feed event strings.
    Used by the WebSocket manager to broadcast to connected clients.
    """
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(FEED_CHANNEL)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
    finally:
        await pubsub.unsubscribe(FEED_CHANNEL)