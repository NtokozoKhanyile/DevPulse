import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UpdateShoutoutRequest(BaseModel):
    shoutout: str | None = Field(default=None, max_length=300)


class CelebrationEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    owner_id: uuid.UUID
    shoutout: str | None
    featured: bool
    created_at: datetime