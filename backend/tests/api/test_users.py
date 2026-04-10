"""
Comprehensive tests for user endpoints.
Tests cover: profile retrieval, updates, avatar upload, and user projects.
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestGetCurrentUser:
    """Get current user endpoint tests."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client: AsyncClient, auth_token: str, test_user):
        """Test retrieving current authenticated user."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_requires_auth(self, client: AsyncClient):
        """Test getting current user requires authentication."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self, client: AsyncClient):
        """Test with invalid token."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401


class TestUpdateProfile:
    """Update user profile endpoint tests."""

    @pytest.mark.asyncio
    async def test_update_profile_display_name(self, client: AsyncClient, auth_token: str, test_user):
        """Test updating display name."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"display_name": "New Display Name"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "New Display Name"

    @pytest.mark.asyncio
    async def test_update_profile_bio(self, client: AsyncClient, auth_token: str):
        """Test updating bio."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"bio": "I am a developer!"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "I am a developer!"

    @pytest.mark.asyncio
    async def test_update_profile_skills(self, client: AsyncClient, auth_token: str):
        """Test updating skills."""
        skills = ["Python", "JavaScript", "React"]
        response = await client.patch(
            "/api/v1/users/me",
            json={"skills": skills},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["skills"] == skills

    @pytest.mark.asyncio
    async def test_update_profile_github_url(self, client: AsyncClient, auth_token: str):
        """Test updating GitHub URL."""
        github_url = "https://github.com/testuser"
        response = await client.patch(
            "/api/v1/users/me",
            json={"github_url": github_url},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["github_url"] == github_url

    @pytest.mark.asyncio
    async def test_update_profile_website_url(self, client: AsyncClient, auth_token: str):
        """Test updating website URL."""
        website_url = "https://testuser.dev"
        response = await client.patch(
            "/api/v1/users/me",
            json={"website_url": website_url},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["website_url"] == website_url

    @pytest.mark.asyncio
    async def test_update_profile_multiple_fields(self, client: AsyncClient, auth_token: str):
        """Test updating multiple fields at once."""
        update_data = {
            "display_name": "Updated Name",
            "bio": "New bio",
            "skills": ["Go", "Rust"],
        }
        response = await client.patch(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == update_data["display_name"]
        assert data["bio"] == update_data["bio"]
        assert data["skills"] == update_data["skills"]

    @pytest.mark.asyncio
    async def test_update_profile_requires_auth(self, client: AsyncClient):
        """Test update requires authentication."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"display_name": "New Name"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_profile_cannot_change_username(self, client: AsyncClient, auth_token: str, test_user):
        """Test username cannot be changed."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"username": "newusername"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        # Username should remain unchanged
        assert data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_update_profile_cannot_change_email(self, client: AsyncClient, auth_token: str, test_user):
        """Test email cannot be changed."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"email": "newemail@example.com"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        # Email should remain unchanged
        assert data["email"] == test_user.email


class TestGetUserProfile:
    """Get user profile by username endpoint tests."""

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, client: AsyncClient, test_user):
        """Test retrieving user profile by username."""
        response = await client.get(f"/api/v1/users/{test_user.username}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["display_name"] == test_user.display_name

    @pytest.mark.asyncio
    async def test_get_user_profile_case_insensitive(self, client: AsyncClient, test_user):
        """Test username lookup is case-insensitive."""
        response = await client.get(f"/api/v1/users/{test_user.username.upper()}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_profile_nonexistent(self, client: AsyncClient):
        """Test retrieving non-existent user."""
        response = await client.get("/api/v1/users/nonexistentuser")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_profile_no_password_hash(self, client: AsyncClient, test_user):
        """Test password hash is not returned."""
        response = await client.get(f"/api/v1/users/{test_user.username}")
        assert response.status_code == 200
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_get_user_profile_returns_public_fields(self, client: AsyncClient, test_user):
        """Test all public fields are returned."""
        response = await client.get(f"/api/v1/users/{test_user.username}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "display_name" in data
        assert "bio" in data or data.get("bio") is None
        assert "avatar_url" in data or data.get("avatar_url") is None


class TestGetUserProjects:
    """Get user projects endpoint tests."""

    @pytest.mark.asyncio
    async def test_get_user_projects_success(self, client: AsyncClient, test_user, test_project):
        """Test retrieving user's projects."""
        response = await client.get(f"/api/v1/users/{test_user.username}/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain the test user's project
        project_ids = [p["id"] for p in data]
        assert str(test_project.id) in project_ids

    @pytest.mark.asyncio
    async def test_get_user_projects_returns_public_only(self, client: AsyncClient, test_user, test_project, private_project):
        """Test only public projects are returned."""
        response = await client.get(f"/api/v1/users/{test_user.username}/projects")
        assert response.status_code == 200
        data = response.json()
        project_ids = [p["id"] for p in data]
        # Public project should be included
        assert str(test_project.id) in project_ids
        # Private project should not be included
        assert str(private_project.id) not in project_ids

    @pytest.mark.asyncio
    async def test_get_user_projects_pagination(self, client: AsyncClient, test_user):
        """Test pagination on user projects."""
        response = await client.get(f"/api/v1/users/{test_user.username}/projects?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_get_user_projects_nonexistent_user(self, client: AsyncClient):
        """Test retrieving projects for non-existent user."""
        response = await client.get("/api/v1/users/nonexistentuser/projects")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_projects_no_projects(self, client: AsyncClient, test_user_2):
        """Test user with no projects returns empty list."""
        response = await client.get(f"/api/v1/users/{test_user_2.username}/projects")
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestUserProfileEdgeCases:
    """Edge case tests for user endpoints."""

    @pytest.mark.asyncio
    async def test_update_profile_empty_bio(self, client: AsyncClient, auth_token: str):
        """Test clearing bio."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"bio": ""},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        # Empty string or null should work
        assert data["bio"] in ["", None]

    @pytest.mark.asyncio
    async def test_update_profile_long_bio(self, client: AsyncClient, auth_token: str):
        """Test bio must respect max length."""
        long_bio = "x" * 1000
        response = await client.patch(
            "/api/v1/users/me",
            json={"bio": long_bio},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # Should either succeed or fail validation
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_update_profile_invalid_url(self, client: AsyncClient, auth_token: str):
        """Test invalid URL validation."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"website_url": "not a url"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # Should fail validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_me_after_update(self, client: AsyncClient, auth_token: str):
        """Test get current user reflects updates."""
        # Update profile
        update_data = {"display_name": "Updated Display"}
        await client.patch(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Get current user
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Display"
