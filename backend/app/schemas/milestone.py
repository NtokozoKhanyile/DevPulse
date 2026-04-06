import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CreateMilestoneRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    body: str | None = Field(default=None)


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    body: str | None
    created_at: datetime