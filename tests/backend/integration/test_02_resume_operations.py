"""
Test Suite 02: Resume Operations Tests

Tests for resume CRUD operations and data management.
These tests verify:
- Building resume profiles
- Loading example profiles
- JSON generation
- Resume data validation
- Profile building from form data
"""
import pytest
from fastapi.testclient import TestClient


class Test01_ExampleProfiles:
    """Test loading example resume profiles."""

    def test_1_1_load_software_developer_example(self, client: TestClient):
        """Test 1.1: Load software developer example profile."""
        response = client.get("/api/resume/example/software-developer")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        # Verify example data structure
        assert isinstance(data["data"], (dict, list))

    def test_1_2_load_process_engineer_example(self, client: TestClient):
        """Test 1.2: Load process engineer example profile."""
        response = client.get("/api/resume/example/process-engineer")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data


class Test02_BuildProfile:
    """Test building resume profiles from form data."""

    def test_2_1_build_minimal_profile(self, client: TestClient):
        """Test 2.1: Build profile with minimal data."""
        response = client.post(
            "/api/resume/build-profile",
            json={
                "full_name": "John Doe",
                "email": "john@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data

    def test_2_2_build_complete_profile(self, client: TestClient):
        """Test 2.2: Build profile with complete data."""
        response = client.post(
            "/api/resume/build-profile",
            json={
                "full_name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1-555-123-4567",
                "location": "San Francisco, CA",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "github_url": "https://github.com/janesmith",
                "summary": "Experienced software engineer with 5+ years...",
                "education_table": [
                    ["MIT", "B.S.", "Computer Science", "3.9", "2015", "2019", "Dean's List"]
                ],
                "experience_table": [
                    ["Google", "Software Engineer", "Mountain View, CA", "2019", "Present", "Backend development", "Led team of 5"]
                ],
                "skills_table": [
                    ["Programming", "Python", "Expert"],
                    ["Programming", "JavaScript", "Advanced"]
                ],
                "projects_table": [
                    ["Resume Helper", "AI-powered resume builder", "Python, FastAPI", "https://github.com/", "2024", "Present"]
                ],
                "certifications_table": [
                    ["AWS Solutions Architect", "Amazon", "2023", "ABC123", "https://aws.com/verify"]
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_2_3_build_profile_with_empty_tables(self, client: TestClient):
        """Test 2.3: Build profile with empty table data."""
        response = client.post(
            "/api/resume/build-profile",
            json={
                "full_name": "Test User",
                "email": "test@example.com",
                "education_table": [],
                "experience_table": [],
                "skills_table": [],
                "projects_table": [],
                "certifications_table": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True


class Test03_GenerateJSON:
    """Test JSON generation from resume data."""

    def test_3_1_generate_json_minimal(self, client: TestClient):
        """Test 3.1: Generate JSON with minimal resume data."""
        response = client.post(
            "/api/resume/generate-json",
            json={
                "personal_info": {
                    "full_name": "John Doe",
                    "email": "john@example.com"
                },
                "education": [],
                "experience": [],
                "skills": [],
                "projects": [],
                "certifications": [],
                "others": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "personal_info" in data
        assert data["personal_info"]["full_name"] == "John Doe"

    def test_3_2_generate_json_complete(self, client: TestClient):
        """Test 3.2: Generate JSON with complete resume data."""
        response = client.post(
            "/api/resume/generate-json",
            json={
                "personal_info": {
                    "full_name": "Jane Smith",
                    "email": "jane@example.com",
                    "phone": "+1-555-123-4567",
                    "location": "San Francisco, CA"
                },
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "B.S.",
                        "field_of_study": "Computer Science",
                        "gpa": "3.9",
                        "start_date": "2015",
                        "end_date": "2019"
                    }
                ],
                "experience": [
                    {
                        "company": "Google",
                        "position": "Software Engineer",
                        "location": "Mountain View, CA",
                        "start_date": "2019",
                        "end_date": "Present",
                        "description": "Backend development",
                        "achievements": ["Led team of 5", "Improved performance by 50%"]
                    }
                ],
                "skills": [
                    {"category": "Programming", "name": "Python", "proficiency": "Expert"}
                ],
                "projects": [
                    {
                        "name": "Resume Helper",
                        "description": "AI-powered resume builder",
                        "technologies": "Python, FastAPI",
                        "url": "https://github.com/"
                    }
                ],
                "certifications": [
                    {
                        "name": "AWS Solutions Architect",
                        "issuer": "Amazon",
                        "date_obtained": "2023"
                    }
                ],
                "others": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["education"]) == 1
        assert len(data["experience"]) == 1
        assert len(data["skills"]) == 1


class Test04_DataValidation:
    """Test resume data validation."""

    def test_4_1_validate_email_format(self, client: TestClient):
        """Test 4.1: Various email formats are handled."""
        # API should accept various email formats
        response = client.post(
            "/api/resume/build-profile",
            json={
                "full_name": "Test User",
                "email": "test.user+tag@sub.example.com"
            }
        )
        assert response.status_code == 200

    def test_4_2_handle_special_characters(self, client: TestClient):
        """Test 4.2: Special characters in names handled correctly."""
        response = client.post(
            "/api/resume/build-profile",
            json={
                "full_name": "José García-López",
                "email": "jose@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_4_3_handle_unicode_content(self, client: TestClient):
        """Test 4.3: Unicode content is handled correctly."""
        response = client.post(
            "/api/resume/build-profile",
            json={
                "full_name": "田中太郎",
                "email": "tanaka@example.jp",
                "summary": "経験豊富なソフトウェアエンジニア"
            }
        )
        assert response.status_code == 200
