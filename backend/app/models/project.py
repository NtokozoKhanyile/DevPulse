import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ProjectStage(str, enum.Enum):
    """Valid lifecycle stages for a DevPulse project."""

    IDEA = "idea"
    BUILDING = "building"
    TESTING = "testing"
    SHIPPED = "shipped"
    COMPLETED = "completed"


class Project(Base, TimestampMixin):
    """A developer project on the DevPulse platform."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)  # no length cap — rich content
    stage: Mapped[ProjectStage] = mapped_column(
        SAEnum(ProjectStage, name="project_stage_enum"),
        nullable=False,
    )
    support_tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)  # e.g. ["Need UX", "Co-founder"]
    tech_stack: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)   # e.g. ["Python", "React"]
    repo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)   # False = hidden from feed
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True  # set when stage → completed
    )

    # Relationships
    owner = relationship(
        "User",
        back_populates="projects",
    )
    milestones = relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Milestone.created_at",
    )
    comments = relationship(
        "Comment",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    collaboration_requests = relationship(
        "CollaborationRequest",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    celebration_entry = relationship(
        "CelebrationEntry",
        back_populates="project",
        uselist=False,  # one-to-one
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_projects_owner_id", "owner_id"),
        Index("idx_projects_stage", "stage"),
        Index("idx_projects_is_public", "is_public"),
        Index("idx_projects_completed_at", "completed_at"),
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title!r} stage={self.stage}>"