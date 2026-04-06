import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipient_id: uuid.UUID
    actor_id: uuid.UUID | None
    type: NotificationType
    entity_type: str
    entity_id: uuid.UUID
    message: str
    is_read: bool
    created_at: datetime