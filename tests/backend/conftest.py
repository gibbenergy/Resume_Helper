"""
Shared fixtures for Resume Helper backend tests.

IMPORTANT: All tests use a separate test database to prevent pollution
of the production database. The test database is created fresh for each
test module and deleted after all tests complete.
"""
import os
import pytest
import tempfile
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.api.routers.applications import get_app_workflows
from backend.core.workflows.application_workflows import ApplicationWorkflows
from backend.core.infrastructure.repositories.sql_application_repository import SQLApplicationRepository


# Global test database path - shared across all tests in a session
_test_db_path = None
_test_repository = None
_test_workflows = None


def get_test_db_path():
    """Get or create the test database path."""
    global _test_db_path
    if _test_db_path is None:
        # Create test database in a temp directory
        test_data_dir = os.path.join(tempfile.gettempdir(), "resume_helper_tests")
        os.makedirs(test_data_dir, exist_ok=True)
        _test_db_path = os.path.join(test_data_dir, "test_applications.db")
    return _test_db_path


def get_test_workflows():
    """Get or create test workflows with test database."""
    global _test_repository, _test_workflows
    if _test_workflows is None:
        _test_repository = SQLApplicationRepository(db_path=get_test_db_path())
        _test_workflows = ApplicationWorkflows(repository=_test_repository)
    return _test_workflows


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Session-scoped fixture to set up and tear down test database.

    This runs once at the start of the test session and cleans up
    the test database when all tests are complete.
    """
    # Setup: ensure clean test database
    test_db = get_test_db_path()
    if os.path.exists(test_db):
        os.remove(test_db)

    # Initialize the test database
    get_test_workflows()

    yield  # Run all tests

    # Teardown: remove test database
    global _test_db_path, _test_repository, _test_workflows
    if _test_db_path and os.path.exists(_test_db_path):
        try:
            os.remove(_test_db_path)
        except Exception:
            pass  # Ignore cleanup errors
    _test_db_path = None
    _test_repository = None
    _test_workflows = None


@pytest.fixture(scope="function")
def client():
    """Create a test client that uses the test database."""
    # Override the dependency to use test database
    app.dependency_overrides[get_app_workflows] = get_test_workflows

    with TestClient(app) as test_client:
        yield test_client

    # Clear override after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def profile_cleanup(client):
    """
    Fixture to track and clean up test profiles.

    Usage:
        def test_something(client, profile_cleanup):
            response = client.post("/api/profiles", json={...})
            profile_id = response.json()["profile"]["id"]
            profile_cleanup.track(profile_id)  # Track for cleanup

    Profiles are automatically deleted after the test completes.
    """
    class ProfileCleanup:
        def __init__(self, test_client):
            self.client = test_client
            self.profile_ids = []

        def track(self, profile_id: str):
            """Track a profile ID for cleanup after test."""
            if profile_id and profile_id not in self.profile_ids:
                self.profile_ids.append(profile_id)

        def cleanup(self):
            """Delete all tracked profiles."""
            for profile_id in self.profile_ids:
                try:
                    self.client.delete(f"/api/profiles/{profile_id}")
                except Exception:
                    pass  # Ignore errors during cleanup
            self.profile_ids.clear()

    cleanup = ProfileCleanup(client)
    yield cleanup
    # Cleanup runs after test completes
    cleanup.cleanup()


# Test profile names - used for identifying test artifacts
TEST_PROFILE_NAMES = [
    "Test Profile",
    "Profile With ID",
    "Complete Profile",
    "Retrievable Profile",
    "Deletable Profile",
    "Original Name",
    "Updated Name",
]


@pytest.fixture(scope="module")
def cleanup_test_profiles(request):
    """
    Module-level fixture to clean up any leftover test profiles.

    This runs at the end of the test module to ensure no test artifacts remain.
    """
    yield  # Let tests run first

    # After all tests in module complete, clean up any test profiles
    with TestClient(app) as client:
        try:
            response = client.get("/api/profiles")
            if response.status_code == 200:
                data = response.json()
                profiles = data.get("profiles", [])
                for profile in profiles:
                    profile_name = profile.get("name", "")
                    profile_id = profile.get("id", "")
                    # Delete profiles with test names
                    if profile_name in TEST_PROFILE_NAMES:
                        try:
                            client.delete(f"/api/profiles/{profile_id}")
                        except Exception:
                            pass
        except Exception:
            pass
