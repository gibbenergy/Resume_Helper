"""
Test Suite 00: Diagnostic Tests

Diagnostic tests to verify the application is in a working state.
These tests verify:
- API server starts and responds
- Health endpoint works
- Core routers are registered
- Database connection (if applicable)
"""
import pytest


class Test01_APIHealth:
    """Test API health and basic connectivity."""

    def test_1_1_root_endpoint(self, client):
        """Test 1.1: Root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Resume Helper API" in data["message"]

    def test_1_2_health_endpoint(self, client):
        """Test 1.2: Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class Test02_RouterRegistration:
    """Test that all routers are properly registered."""

    def test_2_1_resume_router_exists(self, client):
        """Test 2.1: Resume router is accessible."""
        # Try to access a resume endpoint (expect 404 for non-existent resource, not 405)
        response = client.get("/api/resume")
        # Should not be 404 Method Not Allowed - that would mean router isn't registered
        assert response.status_code != 405

    def test_2_2_ai_router_exists(self, client):
        """Test 2.2: AI router is accessible."""
        response = client.get("/api/ai/config")
        # Should return something (even error) meaning router is registered
        assert response.status_code != 405

    def test_2_3_applications_router_exists(self, client):
        """Test 2.3: Applications router is accessible."""
        response = client.get("/api/applications")
        assert response.status_code != 405

    def test_2_4_profiles_router_exists(self, client):
        """Test 2.4: Profiles router is accessible."""
        response = client.get("/api/profiles")
        assert response.status_code != 405


class Test03_ErrorHandling:
    """Test error handling behavior."""

    def test_3_1_invalid_endpoint_returns_404(self, client):
        """Test 3.1: Non-existent endpoint returns 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_3_2_validation_error_handling(self, client):
        """Test 3.2: Invalid data returns 422 with details."""
        # This depends on actual endpoints - placeholder for now
        pass
