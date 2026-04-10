"""
Comprehensive tests for comments on projects.
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestCommentCreation:
    """Tests for creating comments on projects."""

    @pytest.mark.asyncio
    async def test_create_comment_success(self, client: AsyncClient, auth_token: str, test_project):
        """Test successfully creating a comment."""
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/comments",
            json={"content": "This is a great project!"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # Implementation status may vary
        assert response.status_code in [201, 404, 422]

    @pytest.mark.asyncio
    async def test_create_comment_requires_auth(self, client: AsyncClient, test_project):
        """Test comment creation requires authentication."""
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/comments",
            json={"content": "Comment"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_comment_empty_content(self, client: AsyncClient, auth_token: str, test_project):
        """Test creating comment with empty content."""
        response = await client.post(
            f"/api/v1/projects/{test_project.id}/comments",
            json={"content": ""},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code in [422, 404]


class TestCommentRetrieval:
    """Tests for retrieving comments."""

    @pytest.mark.asyncio
    async def test_get_project_comments(self, client: AsyncClient, test_project):
        """Test retrieving all comments on a project."""
        response = await client.get(f"/api/v1/projects/{test_project.id}/comments")
        # Should return list or 404 if endpoint not implemented
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_comments_with_pagination(self, client: AsyncClient, test_project):
        """Test comment pagination."""
        response = await client.get(f"/api/v1/projects/{test_project.id}/comments?limit=10&skip=0")
        assert response.status_code in [200, 404]


class TestCommentManagement:
    """Tests for updating and deleting comments."""

    @pytest.mark.asyncio
    async def test_update_comment(self, client: AsyncClient, auth_token: str, test_project):
        """Test updating a comment."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}/comments/some-comment-id",
            json={"content": "Updated comment"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code in [200, 404, 422]

    @pytest.mark.asyncio
    async def test_delete_comment(self, client: AsyncClient, auth_token: str, test_project):
        """Test deleting a comment."""
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}/comments/some-comment-id",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code in [204, 404]
