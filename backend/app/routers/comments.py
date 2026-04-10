import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ForbiddenException, UnprocessableException
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import PageParams
from app.models import User, Comment
from app.schemas.comment import CreateCommentRequest, UpdateCommentRequest, CommentResponse
from app.services import project_service

router = APIRouter(tags=["comments"])

# Edit window: 15 minutes from creation
EDIT_WINDOW_MINUTES = 15


@router.post("/{project_id}/comments", response_model=CommentResponse, status_code=201)
async def post_comment(
    project_id: uuid.UUID,
    data: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    # Confirm project exists
    await project_service.get_project_by_id(db, project_id)

    # Validate parent comment belongs to this project
    if data.parent_id is not None:
        result = await db.execute(
            select(Comment).where(
                Comment.id == data.parent_id,
                Comment.project_id == project_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise NotFoundException("Parent comment")

    comment = Comment(
        project_id=project_id,
        author_id=current_user.id,
        parent_id=data.parent_id,
        body=data.body,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    await db.commit()
    return comment


@router.get("/{project_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    project_id: uuid.UUID,
    pagination: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list:
    # Confirm project exists
    await project_service.get_project_by_id(db, project_id)

    result = await db.execute(
        select(Comment)
        .where(Comment.project_id == project_id)
        .order_by(Comment.created_at.asc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    return list(result.scalars().all())


@router.patch("/{project_id}/comments/{comment_id}", response_model=CommentResponse)
async def edit_comment(
    project_id: uuid.UUID,
    comment_id: uuid.UUID,
    data: UpdateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    result = await db.execute(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.project_id == project_id,
        )
    )
    comment = result.scalar_one_or_none()

    if comment is None:
        raise NotFoundException("Comment")

    if comment.author_id != current_user.id:
        raise ForbiddenException()

    if comment.is_deleted:
        raise UnprocessableException("Cannot edit a deleted comment")

    # Enforce 15 minute edit window
    edit_deadline = comment.created_at + timedelta(minutes=EDIT_WINDOW_MINUTES)
    if datetime.now(timezone.utc) > edit_deadline:
        raise UnprocessableException("Edit window has expired (15 minutes)")

    comment.body = data.body
    await db.flush()
    await db.refresh(comment)
    await db.commit()
    return comment


@router.delete("/{project_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    project_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    # Load comment along with the project to check owner in one go if possible
    # But current models have project as a relationship, so selectinload works.
    result = await db.execute(
        select(Comment)
        .where(
            Comment.id == comment_id,
            Comment.project_id == project_id,
        )
        .options(selectinload(Comment.project))
    )
    comment = result.scalar_one_or_none()

    if comment is None:
        raise NotFoundException("Comment")

    # Author or project owner can soft delete
    is_author = comment.author_id == current_user.id
    is_project_owner = comment.project.owner_id == current_user.id

    if not is_author and not is_project_owner:
        raise ForbiddenException()

    # Soft delete: wipe body, flag as deleted
    comment.is_deleted = True
    comment.body = ""
    await db.flush()
    await db.commit()