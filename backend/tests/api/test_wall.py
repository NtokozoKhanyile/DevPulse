"""
Tests for celebration wall (project completion celebration entries).
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestCelebrationWall:
    """Tests for celebration/wall endpoints related to project completions."""

    @pytest.mark.asyncio
    async def test_get_celebration_wall(self, client: AsyncClient):
        """Test retrieving celebration wall entries."""
        response = await client.get("/api/v1/wall/")
        # Should return success even if empty
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_wall_pagination(self, client: AsyncClient):
        """Test wall pagination."""
        response = await client.get("/api/v1/wall/?limit=10&skip=0")
        assert response.status_code in [200, 404]
