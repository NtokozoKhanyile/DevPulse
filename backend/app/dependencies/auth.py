import uuid

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import CredentialsException, ForbiddenException
from app.models import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise CredentialsException
        user_id = uuid.UUID(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise CredentialsException

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise CredentialsException

    return user


async def get_current_active_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Use this dependency for actions that require email verification."""
    if not current_user.is_verified:
        raise ForbiddenException
    return current_user