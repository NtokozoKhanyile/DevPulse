import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.collaboration_request import CollabStatus


class CreateCollaborationRequest(BaseModel):
    message: str | None = Field(default=None, max_length=500)


class UpdateCollaborationRequest(BaseModel):
    status: CollabStatus


class CollaborationRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    requester_id: uuid.UUID
    message: str | None
    status: CollabStatus
    responded_at: datetime | None
    created_at: datetime