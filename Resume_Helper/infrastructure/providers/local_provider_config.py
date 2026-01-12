"""
Local Provider Configuration
Centralized settings for local AI providers (Ollama, llama.cpp, LM Studio, etc.)
"""

# Local provider settings - consistent across all local AI providers
LOCAL_PROVIDER_CONFIG = {
    "ollama": {
        "base_url": "http://localhost:11434",
        "default_model": "ollama/gpt-oss:latest",
        "requires_api_key": False,
        "max_tokens": {
            "job_analysis": 8192,      # Increased for comprehensive JSON analysis
            "cover_letter": 4096,       # Increased for detailed cover letters
            "resume_tailoring": 6144,   # Increased for complete resume sections
            "suggestions": 4096,        # Increased for detailed suggestions
            "default": 4096
        },
        "temperature": 0.8,  # Higher temperature for more creative outputs
        "timeout": 600  # 10 minutes for local inference with larger models
    },
    "llamacpp": {
        "base_url": "http://localhost:8080/v1",
        "default_model": "openai/local-model",
        "requires_api_key": False,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 600
    },
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "default_model": "openai/local-model",
        "requires_api_key": False,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 600
    },
    "lemonade": {
        "base_url": "http://localhost:8000/api/v1",
        "default_model": "openai/local-model",
        "requires_api_key": False,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 600
    }
}

# Cloud provider settings for comparison
CLOUD_PROVIDER_CONFIG = {
    "openai": {
        "requires_api_key": True,
        "max_tokens": {
            "job_analysis": 8192,      # High limit for reasoning models
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 120
    },
    "anthropic": {
        "requires_api_key": True,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 120
    },
    "google": {
        "requires_api_key": True,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 120
    },
    "groq": {
        "requires_api_key": True,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 120
    },
    "perplexity": {
        "requires_api_key": True,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 120
    },
    "xai": {
        "requires_api_key": True,
        "max_tokens": {
            "job_analysis": 8192,
            "cover_letter": 4096,
            "resume_tailoring": 6144,
            "suggestions": 4096,
            "default": 4096
        },
        "temperature": 0.8,
        "timeout": 120
    }
}

# Combine all provider configs
ALL_PROVIDER_CONFIG = {**LOCAL_PROVIDER_CONFIG, **CLOUD_PROVIDER_CONFIG}


def get_provider_config(provider: str) -> dict:
    """Get configuration for a specific provider."""
    return ALL_PROVIDER_CONFIG.get(provider.lower(), {
        "requires_api_key": True,
        "max_tokens": {"default": 2048},
        "temperature": 0.7,
        "timeout": 60
    })


def get_max_tokens(provider: str, operation: str = "default") -> int:
    """Get max_tokens for a specific provider and operation."""
    config = get_provider_config(provider)
    max_tokens_config = config.get("max_tokens", {})
    return max_tokens_config.get(operation, max_tokens_config.get("default", 2048))


def is_local_provider(provider: str) -> bool:
    """Check if a provider is a local provider."""
    return provider.lower() in LOCAL_PROVIDER_CONFIG


def requires_api_key(provider: str) -> bool:
    """Check if a provider requires an API key."""
    config = get_provider_config(provider)
    return config.get("requires_api_key", True)


def get_base_url(provider: str) -> str:
    """Get the base URL for a local provider."""
    config = get_provider_config(provider)
    return config.get("base_url", "")


def get_timeout(provider: str) -> int:
    """Get timeout for a specific provider."""
    config = get_provider_config(provider)
    return config.get("timeout", 60)
