import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
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
    db: AsyncSession = Depends(get_db),
) -> list:
    project = await project_service.get_project_by_id(db, project_id)
    # Milestones are already eagerly loaded and ordered by created_at ASC
    # via the relationship definition on the Project model
    return project.milestones