"""
Comprehensive tests for authentication endpoints.
Tests cover: registration, login, token refresh, logout, rate limiting, and edge cases.
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import create_access_token, create_refresh_token


# ============================================================================
# Utility Functions
# ============================================================================

def truncate_password(pwd: str, max_bytes: int = 72) -> str:
    """Truncate password safely to bcrypt's 72-byte limit."""
    encoded = pwd.encode('utf-8')
    if len(encoded) > max_bytes:
        return encoded[:max_bytes].decode('utf-8', errors='ignore')
    return pwd


class TestRegister:
    """Registration endpoint tests."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json=test_user_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration fails with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": test_user.email,  # Same email
                "password": truncate_password("Pass123!"),
                "display_name": "New User",
            },
        )
        assert response.status_code == 409
        assert "Email or username already registered" in response.text

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user: User):
        """Test registration fails with duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user.username,  # Same username
                "email": "new@example.com",
                "password": truncate_password("Pass123!"),
                "display_name": "New User",
            },
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration fails with invalid email format."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser2",
                "email": "invalid-email",  # Invalid format
                "password": "SecurePass123!",
                "display_name": "Test User",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration fails with password too short."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "Short1!",  # Less than 8 characters
                "display_name": "Test User",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_username(self, client: AsyncClient):
        """Test registration fails with username too short."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",  # Less than 3 characters
                "email": "test2@example.com",
                "password": "SecurePass123!",
                "display_name": "Test User",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_username_characters(self, client: AsyncClient):
        """Test registration fails with invalid username characters."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "test user",  # Space not allowed
                "email": "test2@example.com",
                "password": "SecurePass123!",
                "display_name": "Test User",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_field(self, client: AsyncClient):
        """Test registration fails when required field is missing."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                # Missing password
                "display_name": "Test User",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_creates_inactive_user(self, client: AsyncClient, db_session: AsyncSession, test_user_data: dict):
        """Test that newly registered user is created as active (not email-verified)."""
        response = await client.post(
            "/api/v1/auth/register",
            json=test_user_data,
        )
        assert response.status_code == 201

        # Verify user in database
        stmt = select(User).where(User.username == test_user_data["username"].lower())
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.is_active is True
        assert user.is_verified is False


class TestLogin:
    """Login endpoint tests."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User, test_user_data: dict):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User, test_user_data: dict):
        """Test login fails with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_email(self, client: AsyncClient):
        """Test login fails with non-existent email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client: AsyncClient, inactive_user: User):
        """Test login fails for inactive user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": inactive_user.email,
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_case_insensitive_email(self, client: AsyncClient, test_user: User, test_user_data: dict):
        """Test login is case-insensitive for email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"].upper(),  # UPPERCASE
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_rate_limit(self, client: AsyncClient):
        """Test rate limiting on login attempts."""
        # Make 10 failed login attempts (should still succeed)
        for i in range(10):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": f"test{i}@example.com",
                    "password": "WrongPassword123!",
                },
            )
            assert response.status_code == 401

        # 11th attempt should be rate limited
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 429


class TestRefresh:
    """Token refresh endpoint tests."""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient, refresh_token: str):
        """Test successful token refresh."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh fails with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token(self, client: AsyncClient, auth_token: str):
        """Test refresh fails when access token is provided instead of refresh token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_token},  # Using access token
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_after_logout(self, client: AsyncClient, test_user: User, refresh_token: str):
        """Test refresh fails after logout (token blacklisted)."""
        # First logout to blacklist the token
        auth_token = create_access_token(str(test_user.id))
        await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Try to refresh with blacklisted token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 401


class TestLogout:
    """Logout endpoint tests."""

    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, test_user: User, auth_token: str, refresh_token: str):
        """Test successful logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_logout_requires_auth(self, client: AsyncClient, refresh_token: str):
        """Test logout requires authentication."""
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token(self, client: AsyncClient, auth_token: str):
        """Test logout with invalid refresh token doesn't fail."""
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "invalid.token.here"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # Should succeed since invalid tokens are ignored
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_logout_requires_valid_access_token(self, client: AsyncClient, refresh_token: str):
        """Test logout requires valid access token."""
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer invalid.access.token"},
        )
        assert response.status_code == 401


class TestAuthIntegration:
    """Integration tests for auth flow."""

    @pytest.mark.asyncio
    async def test_full_auth_flow(self, client: AsyncClient):
        """Test complete authentication flow: register -> login -> refresh -> logout."""
        # Register user
        register_data = {
            "username": "fullflowuser",
            "email": "fullflow@example.com",
            "password": truncate_password("Pass123!"),
            "display_name": "Full Flow User",
        }
        register_response = await client.post(
            "/api/v1/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201
        reg_data = register_response.json()

        # Login (should get same/similar tokens)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": register_data["email"],
                "password": register_data["password"],
            },
        )
        assert login_response.status_code == 200
        login_data = login_response.json()

        # Refresh token
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": login_data["refresh_token"]},
        )
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()

        # Logout
        logout_response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_data["refresh_token"]},
            headers={"Authorization": f"Bearer {refresh_data['access_token']}"},
        )
        assert logout_response.status_code == 204

    @pytest.mark.asyncio
    async def test_tokens_are_different_on_each_login(self, client: AsyncClient, test_user: User, test_user_data: dict):
        """Test that each login generates new tokens."""
        response1 = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        data1 = response1.json()

        response2 = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        data2 = response2.json()

        # Tokens should be different
        assert data1["access_token"] != data2["access_token"]
        assert data1["refresh_token"] != data2["refresh_token"]
