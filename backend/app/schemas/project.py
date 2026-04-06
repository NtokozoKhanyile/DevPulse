import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.project import ProjectStage


class CreateProjectRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1)
    stage: ProjectStage
    support_tags: list[str] = Field(default=[])
    tech_stack: list[str] = Field(default=[])
    repo_url: str | None = Field(default=None, max_length=255)
    live_url: str | None = Field(default=None, max_length=255)


class UpdateProjectRequest(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    description: str | None = None
    stage: ProjectStage | None = None
    support_tags: list[str] | None = None
    tech_stack: list[str] | None = None
    repo_url: str | None = None
    live_url: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: str
    stage: ProjectStage
    support_tags: list
    tech_stack: list
    repo_url: str | None
    live_url: str | None
    cover_image_url: str | None
    is_public: bool
    view_count: int
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime