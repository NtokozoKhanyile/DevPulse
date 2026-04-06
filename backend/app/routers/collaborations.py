import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ForbiddenException, ConflictException, UnprocessableException
from app.dependencies.auth import get_current_user
from app.models import User
from app.models.collaboration_request import CollaborationRequest, CollabStatus
from app.schemas.collaboration_request import (
    CreateCollaborationRequest,
    UpdateCollaborationRequest,
    CollaborationRequestResponse,
)
from app.services import project_service

router = APIRouter(tags=["collaborations"])


@router.post("/{project_id}/collaborate", response_model=CollaborationRequestResponse, status_code=201)
async def raise_hand(
    project_id: uuid.UUID,
    data: CreateCollaborationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CollaborationRequestResponse:
    project = await project_service.get_project_by_id(db, project_id)

    # Cannot request to collaborate on your own project
    if project.owner_id == current_user.id:
        raise UnprocessableException("You cannot collaborate on your own project")

    # Check for duplicate request
    existing = await db.execute(
        select(CollaborationRequest).where(
            CollaborationRequest.project_id == project_id,
            CollaborationRequest.requester_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictException("You have already sent a collaboration request for this project")

    collab_request = CollaborationRequest(
        project_id=project_id,
        requester_id=current_user.id,
        message=data.message,
    )
    db.add(collab_request)
    await db.flush()
    await db.refresh(collab_request)
    await db.commit()
    return collab_request


@router.get("/{project_id}/collaborate", response_model=list[CollaborationRequestResponse])
async def list_requests(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    project = await project_service.get_project_by_id(db, project_id)
    project_service.assert_owner(project, current_user.id)

    result = await db.execute(
        select(CollaborationRequest)
        .where(CollaborationRequest.project_id == project_id)
        .order_by(CollaborationRequest.created_at.asc())
    )
    return list(result.scalars().all())


@router.patch("/{project_id}/collaborate/{request_id}", response_model=CollaborationRequestResponse)
async def respond_to_request(
    project_id: uuid.UUID,
    request_id: uuid.UUID,
    data: UpdateCollaborationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CollaborationRequestResponse:
    project = await project_service.get_project_by_id(db, project_id)
    project_service.assert_owner(project, current_user.id)

    result = await db.execute(
        select(CollaborationRequest).where(
            CollaborationRequest.id == request_id,
            CollaborationRequest.project_id == project_id,
        )
    )
    collab_request = result.scalar_one_or_none()

    if collab_request is None:
        raise NotFoundException("Collaboration request")

    if collab_request.status != CollabStatus.PENDING:
        raise ConflictException("This request has already been responded to")

    collab_request.status = data.status
    collab_request.responded_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(collab_request)
    await db.commit()
    return collab_request