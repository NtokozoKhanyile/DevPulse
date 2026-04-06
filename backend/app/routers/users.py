from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import PageParams
from app.models import User
from app.schemas.user import UserPublic, UserPrivate, UpdateProfileRequest
from app.schemas.project import ProjectResponse
from app.services import user_service, project_service, storage_service

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserPrivate)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserPrivate)
async def update_me(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await user_service.update_profile(db, current_user, data)
    await db.commit()
    return user


@router.post("/me/avatar", response_model=UserPrivate)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    url = await storage_service.upload_avatar(current_user.id, file)
    user = await user_service.update_avatar_url(db, current_user, url)
    await db.commit()
    return user


@router.get("/{username}", response_model=UserPublic)
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await user_service.get_user_by_username(db, username)


@router.get("/{username}/projects", response_model=list[ProjectResponse])
async def get_user_projects(
    username: str,
    pagination: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list:
    user = await user_service.get_user_by_username(db, username)
    return await project_service.get_user_projects(db, user.id, pagination)