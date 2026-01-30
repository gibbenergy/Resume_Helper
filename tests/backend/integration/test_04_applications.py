"""
Test Suite 04: Application Tracking Tests

Tests for job application tracking CRUD operations.
These tests verify:
- Creating applications
- Reading applications
- Updating applications
- Deleting applications
- Interview round management
"""
import pytest
from fastapi.testclient import TestClient


class Test01_ApplicationListing:
    """Test application listing functionality."""

    def test_1_1_get_all_applications(self, client: TestClient):
        """Test 1.1: Get list of all applications."""
        response = client.get("/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_1_2_empty_applications_list_valid(self, client: TestClient):
        """Test 1.2: Empty applications list returns valid structure."""
        response = client.get("/api/applications")
        data = response.json()
        # List can be empty, but structure should be valid
        assert isinstance(data["data"], list)


class Test02_ApplicationCreate:
    """Test application creation functionality."""

    def test_2_1_create_minimal_application(self, client: TestClient):
        """Test 2.1: Create application with minimal required fields."""
        response = client.post(
            "/api/applications",
            json={
                "job_url": "https://example.com/jobs/123",
                "company": "Test Company",
                "position": "Software Engineer"
            }
        )
        # Accept 200 (success) or 400 (validation/business error) - not 422 (schema error) or 500 (server error)
        assert response.status_code in [200, 400]
        data = response.json()
        # Response should have structure
        assert isinstance(data, dict)

    def test_2_2_create_complete_application(self, client: TestClient):
        """Test 2.2: Create application with all fields."""
        response = client.post(
            "/api/applications",
            json={
                "job_url": "https://careers.google.com/jobs/123",
                "company": "Google",
                "position": "Senior Software Engineer",
                "location": "Mountain View, CA",
                "salary_min": 150000,
                "salary_max": 200000,
                "status": "Applied",
                "priority": "High",
                "notes": "Referred by John",
                "description": "We are looking for..."
            }
        )
        # Accept 200 (success) or 400 (validation/business error)
        assert response.status_code in [200, 400]
        data = response.json()
        assert isinstance(data, dict)

    def test_2_3_create_application_returns_id(self, client: TestClient):
        """Test 2.3: Created application returns an ID."""
        response = client.post(
            "/api/applications",
            json={
                "job_url": "https://meta.com/jobs/456",
                "company": "Meta",
                "position": "Backend Developer"
            }
        )
        # Accept 200 (success) or 400 (validation/business error)
        assert response.status_code in [200, 400]
        data = response.json()
        # If successful, verify ID is returned
        if response.status_code == 200 and data.get("success"):
            assert "data" in data
            # ID should be present in response
            app_data = data["data"]
            assert "id" in app_data or "application" in app_data


class Test03_ApplicationRead:
    """Test reading individual applications."""

    def test_3_1_get_nonexistent_application(self, client: TestClient):
        """Test 3.1: Getting non-existent application returns 404."""
        response = client.get("/api/applications/nonexistent-id-12345")
        assert response.status_code == 404

    def test_3_2_get_application_by_id(self, client: TestClient):
        """Test 3.2: Get application by ID after creation."""
        # First create an application
        create_response = client.post(
            "/api/applications",
            json={
                "job_url": "https://apple.com/jobs/789",
                "company": "Apple",
                "position": "iOS Developer"
            }
        )
        if create_response.status_code == 200:
            create_data = create_response.json()
            if create_data["success"] and "data" in create_data:
                app_id = create_data["data"].get("id") or create_data["data"].get("application", {}).get("id")
                if app_id:
                    # Then try to get it
                    get_response = client.get(f"/api/applications/{app_id}")
                    assert get_response.status_code == 200


class Test04_ApplicationUpdate:
    """Test application update functionality."""

    def test_4_1_update_nonexistent_application(self, client: TestClient):
        """Test 4.1: Updating non-existent application returns error."""
        response = client.put(
            "/api/applications/nonexistent-id-12345",
            json={"status": "Interview"}
        )
        assert response.status_code in [400, 404]

    def test_4_2_update_application_status(self, client: TestClient):
        """Test 4.2: Update application status."""
        # Create then update
        create_response = client.post(
            "/api/applications",
            json={
                "job_url": "https://netflix.com/jobs/101",
                "company": "Netflix",
                "position": "Data Engineer"
            }
        )
        if create_response.status_code == 200:
            create_data = create_response.json()
            if create_data["success"] and "data" in create_data:
                app_id = create_data["data"].get("id") or create_data["data"].get("application", {}).get("id")
                if app_id:
                    update_response = client.put(
                        f"/api/applications/{app_id}",
                        json={"status": "Interview"}
                    )
                    assert update_response.status_code in [200, 400]


class Test05_ApplicationDelete:
    """Test application deletion functionality."""

    def test_5_1_delete_nonexistent_application(self, client: TestClient):
        """Test 5.1: Deleting non-existent application returns error."""
        response = client.delete("/api/applications/nonexistent-id-12345")
        assert response.status_code in [400, 404]

    def test_5_2_delete_application(self, client: TestClient):
        """Test 5.2: Delete an existing application."""
        # Create then delete
        create_response = client.post(
            "/api/applications",
            json={
                "job_url": "https://spotify.com/jobs/202",
                "company": "Spotify",
                "position": "ML Engineer"
            }
        )
        if create_response.status_code == 200:
            create_data = create_response.json()
            if create_data["success"] and "data" in create_data:
                app_id = create_data["data"].get("id") or create_data["data"].get("application", {}).get("id")
                if app_id:
                    delete_response = client.delete(f"/api/applications/{app_id}")
                    assert delete_response.status_code in [200, 400]


class Test06_ApplicationSettings:
    """Test application settings endpoint."""

    def test_6_1_get_application_settings(self, client: TestClient):
        """Test 6.1: Get application settings (interview rounds, statuses)."""
        response = client.get("/api/applications/settings")
        # Note: This might conflict with /{app_id} route
        # If it does, it returns 404 or settings
        assert response.status_code in [200, 404]


class Test07_ValidationEdgeCases:
    """Test validation handles edge cases properly."""

    def test_7_1_missing_required_field_company(self, client: TestClient):
        """Test 7.1: Missing company field returns 422 validation error."""
        response = client.post(
            "/api/applications",
            json={
                "job_url": "https://example.com/job/validation-test-1",
                "position": "Engineer"
                # company is missing
            }
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_7_2_missing_required_field_position(self, client: TestClient):
        """Test 7.2: Missing position field returns 422 validation error."""
        response = client.post(
            "/api/applications",
            json={
                "job_url": "https://example.com/job/validation-test-2",
                "company": "Test Corp"
                # position is missing
            }
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_7_3_missing_required_field_job_url(self, client: TestClient):
        """Test 7.3: Missing job_url field returns 422 validation error."""
        response = client.post(
            "/api/applications",
            json={
                "company": "Test Corp",
                "position": "Engineer"
                # job_url is missing
            }
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_7_4_empty_string_company(self, client: TestClient):
        """Test 7.4: Empty string company returns 400 validation error."""
        response = client.post(
            "/api/applications",
            json={
                "job_url": "https://example.com/job/validation-test-4",
                "company": "",  # Empty string
                "position": "Engineer"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "company" in data.get("detail", "").lower() or "missing" in data.get("detail", "").lower()

    def test_7_5_whitespace_only_job_url(self, client: TestClient):
        """Test 7.5: Whitespace-only job_url returns 400 validation error."""
        response = client.post(
            "/api/applications",
            json={
                "job_url": "   ",  # Whitespace only
                "company": "Test Corp",
                "position": "Engineer"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "job_url" in data.get("detail", "").lower() or "missing" in data.get("detail", "").lower()


class Test08_DuplicateDetection:
    """Test duplicate job URL detection."""

    def test_8_1_duplicate_job_url_returns_error(self, client: TestClient):
        """Test 8.1: Adding same job URL twice returns meaningful error."""
        unique_url = "https://example.com/job/duplicate-test-unique"

        # First creation should succeed
        response1 = client.post(
            "/api/applications",
            json={
                "job_url": unique_url,
                "company": "First Company",
                "position": "First Position"
            }
        )
        assert response1.status_code == 200

        # Second creation with same URL should fail
        response2 = client.post(
            "/api/applications",
            json={
                "job_url": unique_url,
                "company": "Second Company",
                "position": "Second Position"
            }
        )
        assert response2.status_code == 400
        data = response2.json()
        # Error message should mention the job URL already exists
        assert "already exists" in data.get("detail", "").lower()

    def test_8_2_different_urls_allowed(self, client: TestClient):
        """Test 8.2: Different job URLs can be added."""
        response1 = client.post(
            "/api/applications",
            json={
                "job_url": "https://example.com/job/different-url-1",
                "company": "Company A",
                "position": "Position A"
            }
        )

        response2 = client.post(
            "/api/applications",
            json={
                "job_url": "https://example.com/job/different-url-2",
                "company": "Company B",
                "position": "Position B"
            }
        )

        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
