import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Notification
from app.models.notification import NotificationType
from app.dependencies.pagination import PageParams


async def create_notification(
    db: AsyncSession,
    recipient_id: uuid.UUID,
    notification_type: NotificationType,
    entity_type: str,
    entity_id: uuid.UUID,
    message: str,
    actor_id: uuid.UUID | None = None,
) -> Notification:
    notification = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=notification_type,
        entity_type=entity_type,
        entity_id=entity_id,
        message=message,
    )
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification


async def get_notifications(
    db: AsyncSession,
    recipient_id: uuid.UUID,
    pagination: PageParams,
) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.recipient_id == recipient_id)
        .order_by(Notification.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    return list(result.scalars().all())


async def mark_read(
    db: AsyncSession,
    notification_id: uuid.UUID,
    recipient_id: uuid.UUID,
) -> Notification | None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.recipient_id == recipient_id,
        )
    )
    notification = result.scalar_one_or_none()

    if notification is None:
        return None

    notification.is_read = True
    await db.flush()
    return notification


async def mark_all_read(db: AsyncSession, recipient_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Notification).where(
            Notification.recipient_id == recipient_id,
            Notification.is_read == False,
        )
    )
    notifications = result.scalars().all()

    for notification in notifications:
        notification.is_read = True

    await db.flush()


async def get_unread_count(db: AsyncSession, recipient_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).where(
            Notification.recipient_id == recipient_id,
            Notification.is_read == False,
        )
    )
    return result.scalar_one()