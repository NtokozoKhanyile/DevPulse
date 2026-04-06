from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import ConflictException, CredentialsException
from app.schemas.auth import RegisterRequest


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    # Check email and username uniqueness in a single query
    existing = await db.execute(
        select(User).where(
            (User.email == data.email.lower()) | (User.username == data.username.lower())
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictException("Email or username already registered")

    user = User(
        username=data.username.lower(),
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        display_name=data.display_name,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(
        select(User).where(User.email == email.lower())
    )
    user = result.scalar_one_or_none()

    # Deliberate: same exception for wrong email or wrong password — no enumeration
    if not user or not verify_password(password, user.password_hash):
        raise CredentialsException

    if not user.is_active:
        raise CredentialsException

    return user


def issue_tokens(user: User) -> dict:
    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
    }