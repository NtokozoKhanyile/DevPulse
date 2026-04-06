from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, create_access_token
from app.core.redis import set_redis_value, get_redis_value, increment_redis_counter
from app.core.exceptions import CredentialsException, RateLimitException
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.services import auth_service

from jose import JWTError

router = APIRouter(tags=["auth"])

# Rate limit: 10 attempts per IP per 15 minutes
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 15 * 60  # seconds


async def _check_rate_limit(request: Request) -> None:
    """Raises RateLimitException if the IP has exceeded the auth attempt limit."""
    ip = request.client.host
    key = f"rate_limit:auth:{ip}"
    count = await increment_redis_counter(key, ex=RATE_LIMIT_WINDOW)
    if count > RATE_LIMIT_MAX:
        raise RateLimitException


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    await _check_rate_limit(request)
    user = await auth_service.register_user(db, data)
    await db.commit()
    return TokenResponse(**auth_service.issue_tokens(user))


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    await _check_rate_limit(request)
    user = await auth_service.authenticate_user(db, data.email, data.password)
    return TokenResponse(**auth_service.issue_tokens(user))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest) -> TokenResponse:
    try:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise CredentialsException

        # Check if token has been blacklisted via logout
        blacklisted = await get_redis_value(f"blacklist:{data.refresh_token}")
        if blacklisted:
            raise CredentialsException

        user_id: str = payload["sub"]

    except (JWTError, KeyError):
        raise CredentialsException

    new_access_token = create_access_token(user_id)
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=data.refresh_token,
    )


@router.post("/logout", status_code=204)
async def logout(
    data: RefreshRequest,
    current_user: User = Depends(get_current_user),
) -> None:
    # Blacklist the refresh token in Redis until it naturally expires
    try:
        payload = decode_token(data.refresh_token)
        exp: int = payload["exp"]
        import time
        ttl = int(exp - time.time())
        if ttl > 0:
            await set_redis_value(f"blacklist:{data.refresh_token}", "1", ex=ttl)
    except (JWTError, KeyError):
        # Token is already invalid — nothing to blacklist
        pass