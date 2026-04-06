import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Project, CelebrationEntry, Milestone
from app.models.project import ProjectStage
from app.core.redis import publish, FEED_CHANNEL
from app.core.exceptions import NotFoundException, ForbiddenException, ConflictException
from app.schemas.project import CreateProjectRequest, UpdateProjectRequest
from app.dependencies.pagination import PageParams


async def get_project_by_id(db: AsyncSession, project_id: uuid.UUID) -> Project:
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.owner))
        .options(selectinload(Project.milestones))
    )
    project = result.scalar_one_or_none()

    if project is None:
        raise NotFoundException("Project")

    return project


async def get_public_project_by_id(db: AsyncSession, project_id: uuid.UUID) -> Project:
    """Fetches a project and increments view count. Used by the public GET endpoint."""
    project = await get_project_by_id(db, project_id)

    project.view_count += 1
    await db.flush()

    return project


async def get_user_projects(
    db: AsyncSession,
    owner_id: uuid.UUID,
    pagination: PageParams,
) -> list[Project]:
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == owner_id, Project.is_public == True)
        .options(selectinload(Project.owner))
        .order_by(Project.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    return list(result.scalars().all())


async def create_project(
    db: AsyncSession,
    owner_id: uuid.UUID,
    data: CreateProjectRequest,
) -> Project:
    project = Project(
        owner_id=owner_id,
        title=data.title,
        description=data.description,
        stage=data.stage,
        support_tags=data.support_tags,
        tech_stack=data.tech_stack,
        repo_url=data.repo_url,
        live_url=data.live_url,
    )

    db.add(project)
    await db.flush()
    await db.refresh(project)

    # Publish creation event to the live feed
    event = json.dumps({
        "type": "project_created",
        "project_id": str(project.id),
        "owner_id": str(project.owner_id),
        "title": project.title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    await publish(FEED_CHANNEL, event)

    return project


async def update_project(
    db: AsyncSession,
    project: Project,
    data: UpdateProjectRequest,
) -> Project:
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(project, field, value)

    await db.flush()
    await db.refresh(project)

    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    await db.delete(project)
    await db.flush()


async def complete_project(db: AsyncSession, project: Project) -> Project:
    """
    Atomically marks a project completed and creates its CelebrationEntry.
    Publishes completion event to the feed channel.
    Must be called within a db session — the router commits.
    """
    if project.stage == ProjectStage.COMPLETED:
        raise ConflictException("Project is already completed")

    project.stage = ProjectStage.COMPLETED
    project.completed_at = datetime.now(timezone.utc)

    entry = CelebrationEntry(
        project_id=project.id,
        owner_id=project.owner_id,
    )
    db.add(entry)
    await db.flush()

    # Publish to live feed
    event = json.dumps({
        "type": "project_completed",
        "project_id": str(project.id),
        "owner_id": str(project.owner_id),
        "title": project.title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    await publish(FEED_CHANNEL, event)

    return project


async def post_milestone(
    db: AsyncSession,
    project: Project,
    title: str,
    body: str | None,
) -> Milestone:
    """Creates a milestone and publishes it to the live feed."""
    milestone = Milestone(
        project_id=project.id,
        title=title,
        body=body,
    )
    db.add(milestone)
    await db.flush()
    await db.refresh(milestone)

    # Publish to live feed
    event = json.dumps({
        "type": "milestone_posted",
        "project_id": str(project.id),
        "owner_id": str(project.owner_id),
        "milestone_title": title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    await publish(FEED_CHANNEL, event)

    return milestone


async def update_cover_image_url(
    db: AsyncSession,
    project: Project,
    url: str,
) -> Project:
    project.cover_image_url = url
    await db.flush()
    await db.refresh(project)
    return project


def assert_owner(project: Project, user_id: uuid.UUID) -> None:
    """
    Raises ForbiddenException if the user is not the project owner.
    Call this before any mutating operation.
    """
    if project.owner_id != user_id:
        raise ForbiddenException