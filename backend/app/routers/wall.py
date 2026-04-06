import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ForbiddenException
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import PageParams
from app.models import User
from app.models.celebration_entry import CelebrationEntry
from app.schemas.celebration_entry import CelebrationEntryResponse, UpdateShoutoutRequest

router = APIRouter(tags=["wall"])


@router.get("/", response_model=list[CelebrationEntryResponse])
async def list_wall(
    pagination: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list:
    # Featured entries first, then by created_at DESC
    result = await db.execute(
        select(CelebrationEntry)
        .options(selectinload(CelebrationEntry.project))
        .options(selectinload(CelebrationEntry.owner))
        .order_by(CelebrationEntry.featured.desc(), CelebrationEntry.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    return list(result.scalars().all())


@router.get("/{entry_id}", response_model=CelebrationEntryResponse)
async def get_wall_entry(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CelebrationEntryResponse:
    result = await db.execute(
        select(CelebrationEntry)
        .where(CelebrationEntry.id == entry_id)
        .options(selectinload(CelebrationEntry.project))
        .options(selectinload(CelebrationEntry.owner))
    )
    entry = result.scalar_one_or_none()

    if entry is None:
        raise NotFoundException("Celebration entry")

    return entry


@router.patch("/{entry_id}/shoutout", response_model=CelebrationEntryResponse)
async def update_shoutout(
    entry_id: uuid.UUID,
    data: UpdateShoutoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CelebrationEntryResponse:
    result = await db.execute(
        select(CelebrationEntry).where(CelebrationEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if entry is None:
        raise NotFoundException("Celebration entry")

    if entry.owner_id != current_user.id:
        raise ForbiddenException

    entry.shoutout = data.shoutout
    await db.flush()
    await db.refresh(entry)
    await db.commit()
    return entry