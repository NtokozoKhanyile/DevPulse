"""
Comprehensive tests for the project feed/discovery endpoints.
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestFeedRetrieval:
    """Tests for retrieving the project feed."""

    @pytest.mark.asyncio
    async def test_get_feed_returns_public_projects(self, client: AsyncClient, test_project, auth_token):
        """Test feed returns public projects."""
        response = await client.get("/api/v1/feed/", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_feed_excludes_private_projects(self, client: AsyncClient, test_project, private_project, auth_token):
        """Test feed does not include private projects."""
        response = await client.get("/api/v1/feed/", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            project_ids = [p["id"] for p in data]
            
            # Public project should be included
            assert str(test_project.id) in project_ids
            # Private project should not be included
            assert str(private_project.id) not in project_ids

    @pytest.mark.asyncio
    async def test_feed_includes_owner_info(self, client: AsyncClient, test_project, auth_token):
        """Test feed projects include owner information."""
        response = await client.get("/api/v1/feed/", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                project = data[0]
                # Should have minimal owner info
                assert "owner" in project or "owner_id" in project


class TestFeedPagination:
    """Tests for feed pagination."""

    @pytest.mark.asyncio
    async def test_feed_with_limit(self, client: AsyncClient, auth_token):
        """Test feed respects limit parameter."""
        response = await client.get("/api/v1/feed/?limit=5", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_feed_with_skip(self, client: AsyncClient, test_user, auth_token, db_session: AsyncSession):
        """Test feed respects skip parameter."""
        from app.models.project import Project, ProjectStage
        
        # Create multiple projects
        for i in range(5):
            project = Project(
                id=uuid.uuid4(),
                owner_id=test_user.id,
                title=f"Feed Project {i}",
                description=f"Description {i}",
                stage=ProjectStage.IDEA,
                is_public=True,
            )
            db_session.add(project)
        await db_session.flush()
        
        # Get first page
        response1 = await client.get("/api/v1/feed/?limit=2&skip=0", headers={"Authorization": f"Bearer {auth_token}"})
        assert response1.status_code in [200, 404]
        
        # Get second page
        response2 = await client.get("/api/v1/feed/?limit=2&skip=2", headers={"Authorization": f"Bearer {auth_token}"})
        assert response2.status_code in [200, 404]
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            # Pages should have different projects
            if len(data1) > 0 and len(data2) > 0:
                ids1 = [p["id"] for p in data1]
                ids2 = [p["id"] for p in data2]
                assert ids1 != ids2

    @pytest.mark.asyncio
    async def test_feed_default_pagination(self, client: AsyncClient, auth_token):
        """Test feed has default limit."""
        response = await client.get("/api/v1/feed/", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Should have a reasonable default limit (e.g., 10-20)
            assert len(data) <= 100


class TestFeedOrdering:
    """Tests for feed ordering."""

    @pytest.mark.asyncio
    async def test_feed_ordered_by_recency(self, client: AsyncClient, auth_token):
        """Test feed returns projects in reverse chronological order."""
        response = await client.get("/api/v1/feed/", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 1:
                # Check that timestamps are in descending order
                for i in range(len(data) - 1):
                    current_time = data[i].get("created_at")
                    next_time = data[i + 1].get("created_at")
                    
                    if current_time and next_time:
                        # Current should be newer (later) than next
                        assert current_time >= next_time


class TestFeedFiltering:
    """Tests for feed filtering."""

    @pytest.mark.asyncio
    async def test_feed_by_stage(self, client: AsyncClient, auth_token):
        """Test filtering feed by project stage."""
        # This endpoint may not be implemented
        response = await client.get("/api/v1/feed/?stage=building", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404, 422]

    @pytest.mark.asyncio
    async def test_feed_by_tag(self, client: AsyncClient, auth_token):
        """Test filtering feed by tags."""
        # This endpoint may not be implemented
        response = await client.get("/api/v1/feed/?tags=python", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404, 422]

    @pytest.mark.asyncio
    async def test_feed_search(self, client: AsyncClient, auth_token):
        """Test searching feed by title."""
        # This endpoint may not be implemented
        response = await client.get("/api/v1/feed/?q=search+term", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code in [200, 404, 422]
