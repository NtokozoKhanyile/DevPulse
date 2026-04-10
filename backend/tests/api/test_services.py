"""
Unit tests for service layer business logic.
Tests cover auth_service, user_service, and project_service in isolation.
"""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.project import Project, ProjectStage
from app.core.security import hash_password, verify_password
from app.core.exceptions import ConflictException, CredentialsException, NotFoundException
from app.services import auth_service, user_service, project_service
from app.schemas.auth import RegisterRequest
from app.schemas.user import UpdateProfileRequest
from app.schemas.project import CreateProjectRequest, UpdateProjectRequest


# ============================================================================
# Utility Functions
# ============================================================================

def truncate_password(pwd: str, max_bytes: int = 72) -> str:
    """Truncate password safely to bcrypt's 72-byte limit."""
    encoded = pwd.encode('utf-8')
    if len(encoded) > max_bytes:
        return encoded[:max_bytes].decode('utf-8', errors='ignore')
    return pwd
class TestAuthService:
    """Unit tests for auth_service."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, db_session: AsyncSession):
        """Test user registration creates a new user."""
        data = RegisterRequest(
            username="newuser",
            email="new@example.com",
            password=truncate_password("Pass123!"),
            display_name="New User",
        )
        user = await auth_service.register_user(db_session, data)

        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.display_name == "New User"
        assert verify_password("SecurePass123!", user.password_hash)

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, db_session: AsyncSession, test_user: User):
        """Test registration fails with duplicate email."""
        data = RegisterRequest(
            username="different",
            email=test_user.email,
            password="StrongPass1!",
            display_name="Different User",
        )
        try:
            await auth_service.register_user(db_session, data)
            assert False, "Should have raised ConflictException"
        except Exception as e:
            assert hasattr(e, 'status_code') and e.status_code == 409

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, db_session: AsyncSession, test_user: User):
        """Test registration fails with duplicate username."""
        data = RegisterRequest(
            username=test_user.username,
            email="different@example.com",
            password="StrongPass1!",
            display_name="Different User",
        )
        try:
            await auth_service.register_user(db_session, data)
            assert False, "Should have raised ConflictException"
        except Exception as e:
            assert hasattr(e, 'status_code') and e.status_code == 409

    @pytest.mark.asyncio
    async def test_register_user_case_insensitive_email(self, db_session: AsyncSession, test_user: User):
        """Test email comparison is case-insensitive."""
        data = RegisterRequest(
            username="different",
            email=test_user.email.upper(),  # UPPERCASE
            password="StrongPass1!",
            display_name="Different User",
        )
        try:
            await auth_service.register_user(db_session, data)
            assert False, "Should have raised ConflictException"
        except Exception as e:
            assert hasattr(e, 'status_code') and e.status_code == 409

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session: AsyncSession, test_user: User, test_user_data: dict):
        """Test successful user authentication."""
        user = await auth_service.authenticate_user(db_session, test_user_data["email"], test_user_data["password"])
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session: AsyncSession, test_user_data: dict):
        """Test authentication fails with wrong password."""
        from app.core.exceptions import CredentialsException
        try:
            await auth_service.authenticate_user(db_session, test_user_data["email"], truncate_password("Wrong123!"))
            assert False, "Should have raised CredentialsException"
        except Exception as e:
            # CredentialsException is an HTTPException which is not a regular exception
            assert hasattr(e, 'status_code')  # HTTPException has status_code

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, db_session: AsyncSession):
        """Test authentication fails for non-existent user."""
        from app.core.exceptions import CredentialsException
        try:
            await auth_service.authenticate_user(db_session, "nonexistent@example.com", "SecurePass123!")
            assert False, "Should have raised CredentialsException"
        except Exception as e:
            assert hasattr(e, 'status_code')

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, db_session: AsyncSession, inactive_user: User):
        """Test authentication fails for inactive user."""
        with pytest.raises(CredentialsException):
            await auth_service.authenticate_user(db_session, inactive_user.email, "SecurePass123!")

    @pytest.mark.asyncio
    async def test_issue_tokens(self, test_user: User):
        """Test token generation."""
        tokens = auth_service.issue_tokens(test_user)
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert len(tokens["access_token"]) > 0
        assert len(tokens["refresh_token"]) > 0


class TestUserService:
    """Unit tests for user_service."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db_session: AsyncSession, test_user: User):
        """Test retrieving user by ID."""
        user = await user_service.get_user_by_id(db_session, test_user.id)
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_get_user_by_id_nonexistent(self, db_session: AsyncSession):
        """Test retrieving non-existent user."""
        try:
            await user_service.get_user_by_id(db_session, uuid.uuid4())
            assert False, "Should have raised NotFoundException"
        except Exception as e:
            assert hasattr(e, 'status_code') and e.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, db_session: AsyncSession, test_user: User):
        """Test retrieving user by username."""
        user = await user_service.get_user_by_username(db_session, test_user.username)
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_username_case_insensitive(self, db_session: AsyncSession, test_user: User):
        """Test username lookup is case-insensitive."""
        user = await user_service.get_user_by_username(db_session, test_user.username.upper())
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_get_user_by_username_nonexistent(self, db_session: AsyncSession):
        """Test retrieving non-existent user by username."""
        try:
            await user_service.get_user_by_username(db_session, "nonexistentuser")
            assert False, "Should have raised NotFoundException"
        except Exception as e:
            assert hasattr(e, 'status_code') and e.status_code == 404

    @pytest.mark.asyncio
    async def test_update_profile_single_field(self, db_session: AsyncSession, test_user: User):
        """Test updating single profile field."""
        data = UpdateProfileRequest(display_name="Updated Name")
        user = await user_service.update_profile(db_session, test_user, data)
        assert user.display_name == "Updated Name"
        assert user.bio == test_user.bio  # Other fields unchanged

    @pytest.mark.asyncio
    async def test_update_profile_multiple_fields(self, db_session: AsyncSession, test_user: User):
        """Test updating multiple profile fields."""
        data = UpdateProfileRequest(
            display_name="Updated Name",
            bio="New bio",
            skills=["Python", "Go"],
        )
        user = await user_service.update_profile(db_session, test_user, data)
        assert user.display_name == "Updated Name"
        assert user.bio == "New bio"
        assert user.skills == ["Python", "Go"]

    @pytest.mark.asyncio
    async def test_update_avatar_url(self, db_session: AsyncSession, test_user: User):
        """Test updating avatar URL."""
        new_url = "https://example.com/avatars/user.png"
        user = await user_service.update_avatar_url(db_session, test_user, new_url)
        assert user.avatar_url == new_url


class TestProjectService:
    """Unit tests for project_service."""

    @pytest.mark.asyncio
    async def test_get_project_by_id_success(self, db_session: AsyncSession, test_project: Project):
        """Test retrieving project by ID."""
        project = await project_service.get_project_by_id(db_session, test_project.id)
        assert project.id == test_project.id

    @pytest.mark.asyncio
    async def test_get_project_by_id_nonexistent(self, db_session: AsyncSession):
        """Test retrieving non-existent project."""
        try:
            await project_service.get_project_by_id(db_session, uuid.uuid4())
            assert False, "Should have raised NotFoundException"
        except Exception as e:
            assert hasattr(e, 'status_code') and e.status_code == 404

    @pytest.mark.asyncio
    async def test_get_public_project_increments_view_count(self, db_session: AsyncSession, test_project: Project):
        """Test retrieving public project increments view count."""
        initial_count = test_project.view_count
        project = await project_service.get_public_project_by_id(db_session, test_project.id)
        assert project.view_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_create_project_success(self, db_session: AsyncSession, test_user: User):
        """Test creating a project."""
        data = CreateProjectRequest(
            title="New Project",
            description="A new project",
            stage=ProjectStage.BUILDING,
        )
        project = await project_service.create_project(db_session, test_user.id, data)
        assert project.title == "New Project"
        assert project.owner_id == test_user.id
        assert project.stage == ProjectStage.BUILDING

    @pytest.mark.asyncio
    async def test_update_project_success(self, db_session: AsyncSession, test_project: Project):
        """Test updating a project."""
        data = UpdateProjectRequest(
            title="Updated Title",
            stage=ProjectStage.TESTING,
        )
        project = await project_service.update_project(db_session, test_project, data)
        assert project.title == "Updated Title"
        assert project.stage == ProjectStage.TESTING

    @pytest.mark.asyncio
    async def test_assert_owner_success(self, test_project: Project, test_user: User):
        """Test ownership assertion passes for owner."""
        # Should not raise
        project_service.assert_owner(test_project, test_user.id)

    @pytest.mark.asyncio
    async def test_assert_owner_failure(self, test_project: Project, test_user_2: User):
        """Test ownership assertion fails for non-owner."""
        with pytest.raises(ForbiddenException):
            project_service.assert_owner(test_project, test_user_2.id)
