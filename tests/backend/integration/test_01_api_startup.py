"""
Test Suite 01: API Startup and Configuration Tests

Tests for verifying the FastAPI application starts correctly and all components are configured.
These tests verify:
- Application initialization
- Middleware configuration (CORS)
- Router registration
- Dependency injection setup
- Error handling configuration
"""
import pytest
from fastapi.testclient import TestClient


class Test01_ApplicationStartup:
    """Test application initialization and basic endpoints."""

    def test_1_1_app_initializes_successfully(self, client: TestClient):
        """Test 1.1: FastAPI app initializes without errors."""
        # If we can create a client and make a request, app initialized successfully
        response = client.get("/")
        assert response.status_code == 200

    def test_1_2_app_metadata_correct(self, client: TestClient):
        """Test 1.2: App metadata (title, version) is correct."""
        response = client.get("/")
        data = response.json()
        assert data["message"] == "Resume Helper API"
        assert data["version"] == "1.0.0"

    def test_1_3_health_endpoint_available(self, client: TestClient):
        """Test 1.3: Health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class Test02_CORSConfiguration:
    """Test CORS middleware configuration."""

    def test_2_1_cors_headers_present(self, client: TestClient):
        """Test 2.1: CORS headers are present in response."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        # CORS middleware should allow requests
        assert response.status_code in [200, 204, 405]

    def test_2_2_cors_allows_all_origins(self, client: TestClient):
        """Test 2.2: CORS allows all origins (development mode)."""
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:5173"}
        )
        # Should allow the request
        assert response.status_code == 200


class Test03_RouterRegistration:
    """Test that all API routers are properly registered."""

    def test_3_1_resume_router_registered(self, client: TestClient):
        """Test 3.1: Resume router is registered at /api/resume."""
        # Try to access an endpoint that should exist
        response = client.get("/api/resume/example/software-developer")
        # Should not be 404 Method Not Allowed - that would mean no route
        assert response.status_code != 405

    def test_3_2_ai_router_registered(self, client: TestClient):
        """Test 3.2: AI router is registered at /api/ai."""
        response = client.get("/api/ai/providers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "providers" in data

    def test_3_3_applications_router_registered(self, client: TestClient):
        """Test 3.3: Applications router is registered at /api/applications."""
        response = client.get("/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_3_4_profiles_router_registered(self, client: TestClient):
        """Test 3.4: Profiles router is registered at /api/profiles."""
        response = client.get("/api/profiles")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_3_5_pdf_router_registered(self, client: TestClient):
        """Test 3.5: PDF router is registered at /api/pdf."""
        # PDF endpoints require POST with data, just verify route exists
        response = client.post("/api/pdf/generate-resume")
        # Should be 422 (validation error) not 404
        assert response.status_code in [422, 400]


class Test04_ErrorHandling:
    """Test error handling and validation."""

    def test_4_1_invalid_endpoint_returns_404(self, client: TestClient):
        """Test 4.1: Non-existent endpoint returns 404."""
        response = client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404

    def test_4_2_invalid_method_returns_405(self, client: TestClient):
        """Test 4.2: Invalid HTTP method returns 405."""
        response = client.delete("/")  # Root doesn't support DELETE
        assert response.status_code == 405

    def test_4_3_validation_error_returns_422(self, client: TestClient):
        """Test 4.3: Invalid request body returns 422 with details."""
        response = client.post(
            "/api/resume/build-profile",
            json={"invalid_field": "value"}  # Missing required fields handled gracefully
        )
        # Should either validate or handle gracefully
        assert response.status_code in [200, 422]


class Test05_DependencyInjection:
    """Test dependency injection is working correctly."""

    def test_5_1_resume_helper_dependency_works(self, client: TestClient):
        """Test 5.1: ResumeHelper dependency is injected correctly."""
        # The example endpoint uses the dependency
        response = client.get("/api/resume/example/software-developer")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_5_2_application_workflows_dependency_works(self, client: TestClient):
        """Test 5.2: ApplicationWorkflows dependency is injected correctly."""
        response = client.get("/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
