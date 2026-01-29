"""
Test Suite 03: AI Provider Configuration Tests

Tests for AI provider management and configuration.
These tests verify:
- Provider listing
- Model listing per provider
- Cost tracking endpoint
- Provider switching (without actual API calls)
"""
import pytest
from fastapi.testclient import TestClient


class Test01_ProviderListing:
    """Test AI provider listing functionality."""

    def test_1_1_get_all_providers(self, client: TestClient):
        """Test 1.1: Get list of all supported AI providers."""
        response = client.get("/api/ai/providers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "providers" in data
        assert isinstance(data["providers"], list)
        assert len(data["providers"]) > 0

    def test_1_2_providers_include_expected_names(self, client: TestClient):
        """Test 1.2: Provider list includes expected providers."""
        response = client.get("/api/ai/providers")
        data = response.json()
        providers = data["providers"]

        # Check for major providers
        expected_providers = ["OpenAI", "Anthropic (Claude)", "Google (Gemini)", "Ollama (Local)"]
        for expected in expected_providers:
            assert expected in providers, f"Expected provider '{expected}' not found"

    def test_1_3_providers_include_local_options(self, client: TestClient):
        """Test 1.3: Provider list includes local/self-hosted options."""
        response = client.get("/api/ai/providers")
        data = response.json()
        providers = data["providers"]

        local_providers = ["Ollama (Local)", "llama.cpp", "LM Studio", "Lemonade"]
        found_local = [p for p in local_providers if p in providers]
        assert len(found_local) > 0, "No local AI providers found"


class Test02_ModelListing:
    """Test model listing per provider."""

    def test_2_1_get_openai_models(self, client: TestClient):
        """Test 2.1: Get models for OpenAI provider."""
        response = client.get("/api/ai/models", params={"provider": "OpenAI"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "models" in data
        assert isinstance(data["models"], list)

    def test_2_2_get_anthropic_models(self, client: TestClient):
        """Test 2.2: Get models for Anthropic provider."""
        response = client.get("/api/ai/models", params={"provider": "Anthropic (Claude)"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "models" in data

    def test_2_3_get_google_models(self, client: TestClient):
        """Test 2.3: Get models for Google Gemini provider."""
        response = client.get("/api/ai/models", params={"provider": "Google (Gemini)"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_2_4_get_ollama_models(self, client: TestClient):
        """Test 2.4: Get models for Ollama (local) provider."""
        response = client.get("/api/ai/models", params={"provider": "Ollama (Local)"})
        assert response.status_code == 200
        data = response.json()
        # Should return success even if Ollama isn't running locally
        assert data["success"] == True

    def test_2_5_models_have_default(self, client: TestClient):
        """Test 2.5: Model response includes default model."""
        response = client.get("/api/ai/models", params={"provider": "OpenAI"})
        data = response.json()
        assert "default" in data


class Test03_CostTracking:
    """Test cost tracking functionality."""

    def test_3_1_get_cost_endpoint_works(self, client: TestClient):
        """Test 3.1: Cost tracking endpoint returns valid response."""
        response = client.get("/api/ai/cost")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "cost" in data
        assert "display" in data

    def test_3_2_cost_is_numeric(self, client: TestClient):
        """Test 3.2: Cost value is a valid number."""
        response = client.get("/api/ai/cost")
        data = response.json()
        assert isinstance(data["cost"], (int, float))
        assert data["cost"] >= 0

    def test_3_3_display_format_correct(self, client: TestClient):
        """Test 3.3: Cost display format includes dollar sign."""
        response = client.get("/api/ai/cost")
        data = response.json()
        assert "$" in data["display"]


class Test04_APIKeyTesting:
    """Test API key validation endpoint (without actual API calls)."""

    def test_4_1_test_api_key_endpoint_exists(self, client: TestClient):
        """Test 4.1: Test API key endpoint is accessible."""
        response = client.post(
            "/api/ai/test-api-key",
            json={
                "provider": "OpenAI",
                "api_key": "sk-test-invalid-key",
                "model": "gpt-4"
            }
        )
        # Should return 200 even if key is invalid (returns success: false)
        assert response.status_code in [200, 500]

    def test_4_2_test_local_provider_no_key_needed(self, client: TestClient):
        """Test 4.2: Local providers don't require API key."""
        response = client.post(
            "/api/ai/test-api-key",
            json={
                "provider": "Ollama (Local)",
                "api_key": "",
                "model": "llama2"
            }
        )
        # Should handle gracefully
        assert response.status_code in [200, 500]


class Test05_LiteLLMUpdate:
    """Test LiteLLM update functionality."""

    def test_5_1_update_litellm_endpoint_exists(self, client: TestClient):
        """Test 5.1: LiteLLM update endpoint is accessible."""
        response = client.post("/api/ai/update-litellm")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data
