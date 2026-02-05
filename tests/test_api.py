"""Tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from smartpdf.api.fastapi_app import app


client = TestClient(app)


class TestAPI:
    """Test API endpoints."""
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "SmartPDF-Science" in response.json()["name"]
    
    def test_health(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    @pytest.mark.skip(reason="Requires actual PDF file")
    def test_convert_endpoint(self):
        """Test PDF conversion endpoint."""
        # Would need actual PDF file for this test
        pass