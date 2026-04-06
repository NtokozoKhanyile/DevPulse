import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    display_name: str
    bio: str | None
    avatar_url: str | None
    github_url: str | None
    website_url: str | None
    skills: list
    created_at: datetime


class UserPrivate(UserPublic):
    """Returned only to the owner of the account."""
    email: str
    is_verified: bool


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=255)
    skills: list[str] | None = None