import pytest
from httpx import AsyncClient

class TestStatus:
    """Status endpoint tests"""

    @pytest.mark.asyncio
    async def test_status_get (self, client: AsyncClient) -> None:
        """
        Test GET /api/status endpoint

        Should return 200 or 503 status code
        """
        response = await client.get ("/api/status")

        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json ()
            assert "data" in data
            assert "status" in data["data"]

    @pytest.mark.asyncio
    async def test_version_get (self, client: AsyncClient) -> None:
        """
        Test GET /api/version endpoint

        Should return application version
        """
        response = await client.get ("/api/version")

        assert response.status_code == 200

        data = response.json ()
        assert "data" in data
        assert "version" in data["data"]
        assert isinstance (data["data"]["version"], str)
