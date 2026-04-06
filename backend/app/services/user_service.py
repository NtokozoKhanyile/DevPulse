import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.core.exceptions import NotFoundException
from app.schemas.user import UpdateProfileRequest


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundException("User")

    return user


async def get_user_by_username(db: AsyncSession, username: str) -> User:
    result = await db.execute(
        select(User).where(User.username == username.lower(), User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundException("User")

    return user


async def update_profile(
    db: AsyncSession,
    user: User,
    data: UpdateProfileRequest,
) -> User:
    # Only update fields that were explicitly provided
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)

    return user


async def update_avatar_url(db: AsyncSession, user: User, url: str) -> User:
    user.avatar_url = url
    await db.flush()
    await db.refresh(user)
    return user