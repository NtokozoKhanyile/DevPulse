import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import PageParams
from app.models import User, Milestone
from app.schemas.milestone import CreateMilestoneRequest, MilestoneResponse
from app.services import project_service

router = APIRouter(tags=["milestones"])


@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=201)
async def post_milestone(
    project_id: uuid.UUID,
    data: CreateMilestoneRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MilestoneResponse:
    project = await project_service.get_project_by_id(db, project_id)
    project_service.assert_owner(project, current_user.id)
    milestone = await project_service.post_milestone(db, project, data.title, data.body)
    await db.commit()
    return milestone


@router.get("/{project_id}/milestones", response_model=list[MilestoneResponse])
async def list_milestones(
    project_id: uuid.UUID,
    pagination: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list:
    # Confirm project exists
    await project_service.get_project_by_id(db, project_id)

    result = await db.execute(
        select(Milestone)
        .where(Milestone.project_id == project_id)
        .order_by(Milestone.created_at.asc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    return list(result.scalars().all())