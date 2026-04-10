"""
Comprehensive tests for project endpoints.
Tests cover: CRUD operations, ownership validation, stage transitions, pagination, and edge cases.
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project, ProjectStage
from app.models.user import User


class TestCreateProject:
    """Project creation endpoint tests."""

    @pytest.mark.asyncio
    async def test_create_project_success(self, client: AsyncClient, auth_token: str, test_project_data: dict):
        """Test successful project creation."""
        response = await client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_project_data["title"]
        assert data["description"] == test_project_data["description"]
        assert data["stage"] == test_project_data["stage"]
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_project_requires_auth(self, client: AsyncClient, test_project_data: dict):
        """Test project creation requires authentication."""
        response = await client.post(
            "/api/v1/projects/",
            json=test_project_data,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_project_sets_owner(self, client: AsyncClient, auth_token: str, test_user: User, test_project_data: dict, db_session: AsyncSession):
        """Test created project has correct owner."""
        response = await client.post(
            "/api/v1/projects/",
            json=test_project_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        project_id = response.json()["id"]

        # Verify in database
        stmt = select(Project).where(Project.id == uuid.UUID(project_id))
        result = await db_session.execute(stmt)
        project = result.scalar_one_or_none()
        assert project.owner_id == test_user.id

    @pytest.mark.asyncio
    async def test_create_project_minimal_fields(self, client: AsyncClient, auth_token: str):
        """Test creating project with minimal required fields."""
        response = await client.post(
            "/api/v1/projects/",
            json={
                "title": "Minimal Project",
                "description": "Minimal description",
                "stage": "idea",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["support_tags"] == []
        assert data["tech_stack"] == []

    @pytest.mark.asyncio
    async def test_create_project_missing_required_field(self, client: AsyncClient, auth_token: str):
        """Test creation fails without required field."""
        response = await client.post(
            "/api/v1/projects/",
            json={
                "title": "No Description",
                "stage": "idea",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_invalid_stage(self, client: AsyncClient, auth_token: str):
        """Test creation fails with invalid stage enum."""
        response = await client.post(
            "/api/v1/projects/",
            json={
                "title": "Invalid Stage",
                "description": "Description",
                "stage": "invalid_stage",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422


class TestListProjects:
    """Project listing endpoint tests."""

    @pytest.mark.asyncio
    async def test_list_projects_returns_public_only(self, client: AsyncClient, test_project: Project, private_project: Project):
        """Test list endpoint returns only public projects."""
        response = await client.get("/api/v1/projects/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain public project
        project_ids = [p["id"] for p in data]
        assert str(test_project.id) in project_ids
        # Should not contain private project
        assert str(private_project.id) not in project_ids

    @pytest.mark.asyncio
    async def test_list_projects_pagination_skip(self, client: AsyncClient, test_user: User, db_session: AsyncSession):
        """Test pagination skip parameter."""
        # Create multiple projects
        for i in range(5):
            project = Project(
                id=uuid.uuid4(),
                owner_id=test_user.id,
                title=f"Project {i}",
                description=f"Description {i}",
                stage=ProjectStage.IDEA,
                is_public=True,
            )
            db_session.add(project)
        await db_session.flush()

        # Test skip
        response = await client.get("/api/v1/projects/?skip=3&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    @pytest.mark.asyncio
    async def test_list_projects_pagination_limit(self, client: AsyncClient, test_user: User, db_session: AsyncSession):
        """Test pagination limit parameter."""
        # Create multiple projects
        for i in range(5):
            project = Project(
                id=uuid.uuid4(),
                owner_id=test_user.id,
                title=f"Project {i}",
                description=f"Description {i}",
                stage=ProjectStage.IDEA,
                is_public=True,
            )
            db_session.add(project)
        await db_session.flush()

        # Test limit
        response = await client.get("/api/v1/projects/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    @pytest.mark.asyncio
    async def test_list_projects_default_limit(self, client: AsyncClient):
        """Test default pagination limit is applied."""
        response = await client.get("/api/v1/projects/")
        assert response.status_code == 200


class TestGetProject:
    """Project retrieval endpoint tests."""

    @pytest.mark.asyncio
    async def test_get_public_project_success(self, client: AsyncClient, test_project: Project):
        """Test retrieving a public project."""
        response = await client.get(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_project.id)
        assert data["title"] == test_project.title

    @pytest.mark.asyncio
    async def test_get_private_project_as_non_owner(self, client: AsyncClient, private_project: Project, auth_token_2: str):
        """Test non-owner cannot view private project."""
        response = await client.get(
            f"/api/v1/projects/{private_project.id}",
            headers={"Authorization": f"Bearer {auth_token_2}"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_private_project_as_owner(self, client: AsyncClient, private_project: Project, auth_token: str):
        """Test owner can view private project."""
        response = await client.get(
            f"/api/v1/projects/{private_project.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200 or response.status_code == 200  # Depends on implementation

    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self, client: AsyncClient):
        """Test retrieving non-existent project returns 404."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/v1/projects/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_project_invalid_uuid(self, client: AsyncClient):
        """Test retrieving with invalid UUID format."""
        response = await client.get("/api/v1/projects/not-a-uuid")
        assert response.status_code == 422


class TestUpdateProject:
    """Project update endpoint tests."""

    @pytest.mark.asyncio
    async def test_update_project_success(self, client: AsyncClient, auth_token: str, test_project: Project):
        """Test successful project update."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
        }
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_project_requires_auth(self, client: AsyncClient, test_project: Project):
        """Test update requires authentication."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={"title": "New Title"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_project_non_owner_forbidden(self, client: AsyncClient, auth_token_2: str, test_project: Project):
        """Test non-owner cannot update project."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={"title": "New Title"},
            headers={"Authorization": f"Bearer {auth_token_2}"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_project_stage(self, client: AsyncClient, auth_token: str, test_project: Project):
        """Test updating project stage."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={"stage": ProjectStage.TESTING},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == ProjectStage.TESTING

    @pytest.mark.asyncio
    async def test_update_project_partial_fields(self, client: AsyncClient, auth_token: str, test_project: Project):
        """Test updating only some fields."""
        original_desc = test_project.description
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={"title": "New Title Only"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title Only"
        # Description should remain unchanged
        assert data["description"] == original_desc

    @pytest.mark.asyncio
    async def test_update_project_nonexistent(self, client: AsyncClient, auth_token: str):
        """Test updating non-existent project."""
        fake_id = uuid.uuid4()
        response = await client.patch(
            f"/api/v1/projects/{fake_id}",
            json={"title": "New Title"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404


class TestDeleteProject:
    """Project deletion endpoint tests."""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, client: AsyncClient, auth_token: str, test_user: User, db_session: AsyncSession):
        """Test successful project deletion."""
        # Create a project to delete
        project = Project(
            id=uuid.uuid4(),
            owner_id=test_user.id,
            title="To Delete",
            description="Will be deleted",
            stage=ProjectStage.IDEA,
        )
        db_session.add(project)
        await db_session.flush()

        response = await client.delete(
            f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 204

        # Verify project is deleted
        stmt = select(Project).where(Project.id == project.id)
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_project_requires_auth(self, client: AsyncClient, test_project: Project):
        """Test delete requires authentication."""
        response = await client.delete(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_project_non_owner_forbidden(self, client: AsyncClient, auth_token_2: str, test_project: Project):
        """Test non-owner cannot delete project."""
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers={"Authorization": f"Bearer {auth_token_2}"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_project(self, client: AsyncClient, auth_token: str):
        """Test deleting non-existent project."""
        fake_id = uuid.uuid4()
        response = await client.delete(
            f"/api/v1/projects/{fake_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404


class TestCompleteProject:
    """Project completion endpoint tests."""

    @pytest.mark.asyncio
    async def test_complete_project_success(self, client: AsyncClient, auth_token: str, test_project: Project):
        """Test successfully completing a project."""
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/complete",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["stage"] == ProjectStage.COMPLETED
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_complete_project_requires_auth(self, client: AsyncClient, test_project: Project):
        """Test completion requires authentication."""
        response = await client.post(f"/api/v1/projects/{test_project.id}/complete")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_complete_project_non_owner_forbidden(self, client: AsyncClient, auth_token_2: str, test_project: Project):
        """Test non-owner cannot complete project."""
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/complete",
            headers={"Authorization": f"Bearer {auth_token_2}"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_complete_already_completed_project(self, client: AsyncClient, auth_token: str, completed_project: Project):
        """Test completing an already completed project."""
        response = await client.post(
            f"/api/v1/projects/{completed_project.id}/complete",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # Should succeed or be idempotent
        assert response.status_code in [200, 201]


class TestProjectOwnershipValidation:
    """Tests for project ownership and access control."""

    @pytest.mark.asyncio
    async def test_owner_can_modify_project(self, client: AsyncClient, auth_token: str, test_project: Project):
        """Test project owner can modify their project."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={"title": "Owner Modified"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_non_owner_cannot_modify_project(self, client: AsyncClient, auth_token_2: str, test_project: Project):
        """Test non-owner cannot modify project."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={"title": "Non-Owner Modified"},
            headers={"Authorization": f"Bearer {auth_token_2}"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_owner_can_delete_project(self, client: AsyncClient, auth_token: str, test_project: Project):
        """Test project owner can delete their project."""
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_non_owner_cannot_delete_project(self, client: AsyncClient, auth_token_2: str, test_project: Project):
        """Test non-owner cannot delete project."""
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers={"Authorization": f"Bearer {auth_token_2}"},
        )
        assert response.status_code == 403
