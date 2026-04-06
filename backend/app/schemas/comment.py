import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CreateCommentRequest(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: uuid.UUID | None = None


class UpdateCommentRequest(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    author_id: uuid.UUID
    parent_id: uuid.UUID | None
    body: str | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime