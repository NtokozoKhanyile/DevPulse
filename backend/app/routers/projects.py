from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import PageParams
from app.models import User
from app.schemas.project import CreateProjectRequest, UpdateProjectRequest, ProjectResponse
from app.services import project_service, storage_service, feed_service

router = APIRouter(tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    project = await project_service.create_project(db, current_user.id, data)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    pagination: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list:
    return await feed_service.get_feed(db, pagination)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    import uuid
    project = await project_service.get_public_project_by_id(db, uuid.UUID(project_id))
    await db.commit()
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: UpdateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    import uuid
    project = await project_service.get_project_by_id(db, uuid.UUID(project_id))
    project_service.assert_owner(project, current_user.id)
    project = await project_service.update_project(db, project, data)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    import uuid
    project = await project_service.get_project_by_id(db, uuid.UUID(project_id))
    project_service.assert_owner(project, current_user.id)
    await project_service.delete_project(db, project)
    await db.commit()


@router.post("/{project_id}/complete", response_model=ProjectResponse, status_code=201)
async def complete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    import uuid
    project = await project_service.get_project_by_id(db, uuid.UUID(project_id))
    project_service.assert_owner(project, current_user.id)
    project = await project_service.complete_project(db, project)
    await db.commit()
    await db.refresh(project)
    return project


@router.post("/{project_id}/cover", response_model=ProjectResponse)
async def upload_cover(
    project_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    import uuid
    project = await project_service.get_project_by_id(db, uuid.UUID(project_id))
    project_service.assert_owner(project, current_user.id)
    url = await storage_service.upload_cover(project.id, file)
    project = await project_service.update_cover_image_url(db, project, url)
    await db.commit()
    await db.refresh(project)
    return project