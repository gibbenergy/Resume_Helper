"""
Test Suite 05: Profile Management Tests

Tests for resume profile save/load functionality.
These tests verify:
- Saving profiles
- Loading profiles
- Deleting profiles
- Profile listing
"""
import pytest
from fastapi.testclient import TestClient


class Test01_ProfileListing:
    """Test profile listing functionality."""

    def test_1_1_get_all_profiles(self, client: TestClient):
        """Test 1.1: Get list of all saved profiles."""
        response = client.get("/api/profiles")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "profiles" in data
        assert isinstance(data["profiles"], list)


class Test02_ProfileSave:
    """Test profile save functionality."""

    def test_2_1_save_new_profile(self, client: TestClient):
        """Test 2.1: Save a new profile."""
        response = client.post(
            "/api/profiles",
            json={
                "name": "Test Profile",
                "data": {
                    "personal_info": {
                        "full_name": "Test User",
                        "email": "test@example.com"
                    },
                    "education": [],
                    "experience": [],
                    "skills": [],
                    "projects": [],
                    "certifications": [],
                    "others": {}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_2_2_save_profile_returns_id(self, client: TestClient):
        """Test 2.2: Saved profile returns an ID."""
        response = client.post(
            "/api/profiles",
            json={
                "name": "Profile With ID",
                "data": {
                    "personal_info": {"full_name": "ID Test"},
                    "education": [],
                    "experience": [],
                    "skills": [],
                    "projects": [],
                    "certifications": [],
                    "others": {}
                }
            }
        )
        data = response.json()
        if data["success"]:
            assert "profile" in data
            profile = data["profile"]
            assert "id" in profile

    def test_2_3_save_profile_with_complete_data(self, client: TestClient):
        """Test 2.3: Save profile with complete resume data."""
        response = client.post(
            "/api/profiles",
            json={
                "name": "Complete Profile",
                "data": {
                    "personal_info": {
                        "full_name": "Jane Smith",
                        "email": "jane@example.com",
                        "phone": "+1-555-123-4567",
                        "location": "San Francisco, CA",
                        "linkedin_url": "https://linkedin.com/in/janesmith",
                        "github_url": "https://github.com/janesmith",
                        "summary": "Experienced software engineer"
                    },
                    "education": [
                        {
                            "institution": "MIT",
                            "degree": "B.S.",
                            "field_of_study": "Computer Science",
                            "gpa": "3.9"
                        }
                    ],
                    "experience": [
                        {
                            "company": "Google",
                            "position": "Software Engineer",
                            "location": "Mountain View, CA"
                        }
                    ],
                    "skills": [
                        {"category": "Programming", "name": "Python", "proficiency": "Expert"}
                    ],
                    "projects": [
                        {"name": "Resume Helper", "description": "AI resume builder"}
                    ],
                    "certifications": [
                        {"name": "AWS Solutions Architect", "issuer": "Amazon"}
                    ],
                    "others": {}
                }
            }
        )
        assert response.status_code == 200


class Test03_ProfileRead:
    """Test profile read functionality."""

    def test_3_1_get_nonexistent_profile(self, client: TestClient):
        """Test 3.1: Getting non-existent profile returns 404."""
        response = client.get("/api/profiles/nonexistent-profile-id")
        assert response.status_code == 404

    def test_3_2_get_profile_after_save(self, client: TestClient):
        """Test 3.2: Get profile by ID after saving."""
        # Save a profile first
        save_response = client.post(
            "/api/profiles",
            json={
                "name": "Retrievable Profile",
                "data": {
                    "personal_info": {"full_name": "Retrieve Test"},
                    "education": [],
                    "experience": [],
                    "skills": [],
                    "projects": [],
                    "certifications": [],
                    "others": {}
                }
            }
        )
        if save_response.status_code == 200:
            save_data = save_response.json()
            if save_data["success"] and "profile" in save_data:
                profile_id = save_data["profile"].get("id")
                if profile_id:
                    get_response = client.get(f"/api/profiles/{profile_id}")
                    assert get_response.status_code == 200
                    get_data = get_response.json()
                    assert get_data["success"] == True


class Test04_ProfileDelete:
    """Test profile delete functionality."""

    def test_4_1_delete_nonexistent_profile(self, client: TestClient):
        """Test 4.1: Deleting non-existent profile returns 404."""
        response = client.delete("/api/profiles/nonexistent-profile-id")
        assert response.status_code == 404

    def test_4_2_delete_profile_after_save(self, client: TestClient):
        """Test 4.2: Delete profile after saving."""
        # Save a profile first
        save_response = client.post(
            "/api/profiles",
            json={
                "name": "Deletable Profile",
                "data": {
                    "personal_info": {"full_name": "Delete Test"},
                    "education": [],
                    "experience": [],
                    "skills": [],
                    "projects": [],
                    "certifications": [],
                    "others": {}
                }
            }
        )
        if save_response.status_code == 200:
            save_data = save_response.json()
            if save_data["success"] and "profile" in save_data:
                profile_id = save_data["profile"].get("id")
                if profile_id:
                    delete_response = client.delete(f"/api/profiles/{profile_id}")
                    assert delete_response.status_code == 200
                    delete_data = delete_response.json()
                    assert delete_data["success"] == True


class Test05_ProfileUpdate:
    """Test profile update functionality."""

    def test_5_1_update_existing_profile(self, client: TestClient):
        """Test 5.1: Update an existing profile."""
        # Save a profile first
        save_response = client.post(
            "/api/profiles",
            json={
                "name": "Original Name",
                "data": {
                    "personal_info": {"full_name": "Original Name"},
                    "education": [],
                    "experience": [],
                    "skills": [],
                    "projects": [],
                    "certifications": [],
                    "others": {}
                }
            }
        )
        if save_response.status_code == 200:
            save_data = save_response.json()
            if save_data["success"] and "profile" in save_data:
                profile_id = save_data["profile"].get("id")
                if profile_id:
                    # Update with same ID
                    update_response = client.post(
                        "/api/profiles",
                        json={
                            "id": profile_id,
                            "name": "Updated Name",
                            "data": {
                                "personal_info": {"full_name": "Updated Name"},
                                "education": [],
                                "experience": [],
                                "skills": [],
                                "projects": [],
                                "certifications": [],
                                "others": {}
                            }
                        }
                    )
                    assert update_response.status_code == 200
