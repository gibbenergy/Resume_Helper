"""
Shared fixtures for Resume Helper backend tests.

IMPORTANT: All tests must clean up any artifacts they create.
This prevents test data from polluting production databases.
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app


@pytest.fixture(scope="function")
def client():
    """Create a test client for each test."""
    with TestClient(app) as test_client:
        yield test_client


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
