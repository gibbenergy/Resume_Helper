"""
Shared fixtures for Resume Helper backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app


@pytest.fixture(scope="function")
def client():
    """Create a test client for each test."""
    with TestClient(app) as test_client:
        yield test_client
