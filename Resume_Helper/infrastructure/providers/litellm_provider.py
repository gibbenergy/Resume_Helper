"""
LiteLLM Provider - A unified AI provider using LiteLLM

This module provides a unified interface to multiple AI providers (OpenAI, Claude, Gemini, Ollama, etc.) 
using the LiteLLM library. This is part of Phase 2 of the multi-provider architecture migration.
"""

import os
import json
import logging
import uuid
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from dotenv import load_dotenv

import litellm
from litellm import completion
from litellm.exceptions import APIError, AuthenticationError, RateLimitError, APIConnectionError

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROVIDER_MODELS = {
    "openai": {
        "default": "gpt-5-2025-08-07",
        "models": [
            "gpt-5-2025-08-07",
            "gpt-5.1-2025-11-13",
            "gpt-5-mini-2025-08-07",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo"
        ]
    },
    "anthropic": {
        "default": "claude-opus-4-1-20250805",
        "models": [
            "claude-opus-4-1-20250805",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514"
        ]
    },
    "google": {
        "default": "gemini-2.5-pro",
        "models": [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp"
        ]
    },
    "ollama": {
        "default": "ollama/gpt-oss:latest",
        "models": [
            "ollama/gpt-oss:latest",
            "ollama/deepseek-r1",
            "ollama/mistral-small",
            "ollama/qwen2.5:7b",
            "ollama/llama3.1:8b-instruct",
            "ollama/mistral", 
            "ollama/deepseek-r1:1.5b", 
            "ollama/llama3.2:1b", 
            "ollama/deepseek-r1:14b", 
            "ollama/llama3.3:70b", 
            "ollama/deepseek-r1:32b",            
            "ollama/deepseek-r1:671b"
        ]
    },
    "groq": {
        "default": "groq/gpt-oss-20B",
        "models": [
            "groq/gpt-oss-20B",
            "groq/gpt-oss-120B",
            "groq/llama-3.3-70b-versatile",
            "groq/llama-3.1-70b-versatile",
            "groq/llama-3.1-8b-instant",
            "groq/gemma2-9b-it"
        ]
    },
    "perplexity": {
        "default": "sonar-pro",
        "models": [
            "sonar-pro",
            "sonar-reasoning",
            "llama-3.3-sonar-large-128k-online",
            "llama-3.3-sonar-small-128k-online",
            "sonar-deep-research"
        ]
    },
    "xai": {
        "default": "grok-4",
        "models": [
            "grok-4",
            "grok-3",
            "grok-2",
            "grok-2-mini"
        ]
    },
    "llamacpp": {
        "default": None,  # Will be set dynamically from server
        "models": [],  # Fetched dynamically from /v1/models
        "base_url": "http://localhost:8080/v1"
    },
    "lmstudio": {
        "default": None,  # Will be set dynamically from server
        "models": [],  # Fetched dynamically from /v1/models
        "base_url": "http://localhost:1234/v1"
    },
    "lemonade": {
        "default": None,  # Will be set dynamically from server
        "models": [],  # Fetched dynamically from /api/v1/models
        "base_url": "http://localhost:8000/api/v1"
    }
}

class LiteLLMProvider:
    """
    A unified AI provider using LiteLLM that supports 100+ LLM providers.
    
    This provider can switch between different AI services (OpenAI, Claude, Gemini, Ollama, etc.)
    through a single unified interface powered by LiteLLM.
    """
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the LiteLLM Provider."""
        self.provider = provider.lower()
        self.custom_base_url = base_url  # Set this BEFORE _get_default_model so it can use it
        self.current_model = model or self._get_default_model(self.provider)
        
        if api_key:
            self._set_provider_api_key(api_key)
        else:
            self._load_api_key_from_env()
        
        # Set custom base URL if provided or use default for provider
        if base_url:
            self._set_base_url(base_url)
        else:
            self._set_default_base_url()
        
        litellm.drop_params = True
        
        logger.info(f"LiteLLM Provider initialized with {self.provider} using model {self.current_model}")
    
    def _get_default_model(self, provider: str) -> str:
        """Get the default model for a provider."""
        provider_config = PROVIDER_MODELS.get(provider)
        if provider_config:
            default = provider_config["default"]
            # For local providers with None default, fetch from server
            if default is None and provider in ["ollama", "llamacpp", "lmstudio"]:
                available_models = self._fetch_local_models_for_provider(provider)
                if available_models:
                    logger.info(f"Using first available model: {available_models[0]}")
                    return available_models[0]  # Return first available model
                # Return a safe fallback that indicates manual selection needed
                logger.warning(f"No models found for {provider}, using generic OpenAI-compatible placeholder")
                return "openai/model"  # Generic OpenAI-compatible placeholder for manual entry
            return default
        return "gpt-4.1"
    
    def _fetch_local_models_for_provider(self, provider: str) -> List[str]:
        """Fetch models for a specific provider (used during initialization)."""
        import requests
        
        try:
            if provider == "ollama":
                base_url = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
                url = f"{base_url}/api/tags"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    return [f"ollama/{m.get('name', '')}" for m in models if m.get('name')]
            
            elif provider in ["llamacpp", "lmstudio", "lemonade"]:
                # Check for custom base_url first (for Lemonade and other routers)
                base_url = self.custom_base_url if self.custom_base_url else None
                
                # Fall back to Harbor environment variables
                if not base_url:
                    harbor_env_map = {
                        "llamacpp": "LLAMACPP_API_BASE",
                        "lmstudio": "LMSTUDIO_API_BASE",
                        "lemonade": "LEMONADE_API_BASE"
                    }
                    env_var = harbor_env_map.get(provider)
                    base_url = os.getenv(env_var) if env_var else None
                
                # Fall back to default from config
                if not base_url:
                base_url = PROVIDER_MODELS.get(provider, {}).get("base_url", "")
                
                if base_url:
                    url = f"{base_url}/models"
                    logger.info(f"Fetching models from {provider} at {url}")
                    response = requests.get(url, timeout=5)  # Increased timeout for LLM routers
                    if response.status_code == 200:
                        data = response.json()
                        models = data.get("data", [])
                        model_list = [f"openai/{m.get('id', '')}" for m in models if m.get('id')]
                        if model_list:
                            logger.info(f"Successfully fetched {len(model_list)} models from {provider}")
                            return model_list
                        else:
                            logger.warning(f"No models found in response from {base_url}")
        
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout fetching models from {provider}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error fetching models from {provider}: {e}")
        except Exception as e:
            logger.warning(f"Error fetching models from {provider}: {e}")
        
        return []
    
    def _load_api_key_from_env(self):
        """Load API key from environment variables."""
        # All local providers use the same dummy key format
        if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            # Set dummy key for LiteLLM (actual value doesn't matter for local providers)
        if self.provider == "ollama":
                os.environ["OLLAMA_API_KEY"] = "sk-no-key-required"
            # Only set OLLAMA_API_BASE if not already set (preserve Harbor environment)
            if "OLLAMA_API_BASE" not in os.environ:
                os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
                logger.info(f"Set default OLLAMA_API_BASE to http://localhost:11434")
            else:
                logger.info(f"Using existing OLLAMA_API_BASE: {os.environ['OLLAMA_API_BASE']}")
            else:
                # OpenAI-compatible local providers
                os.environ["OPENAI_API_KEY"] = "sk-no-key-required"
        
            logger.info(f"Set dummy API key for {self.provider} (local provider)")
            return
        
        # Cloud providers - need real API keys from .env
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY", 
            "google": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "perplexity": "PERPLEXITY_API_KEY",
            "xai": "XAI_API_KEY"
        }
        
        env_key = env_key_map.get(self.provider)
        if env_key:
            api_key = os.getenv(env_key)
            if api_key:
                self._set_provider_api_key(api_key)
                logger.info(f"Loaded API key for {self.provider}")
    
    def _set_provider_api_key(self, api_key: str):
        """Set the API key for the current provider."""
        # All local providers use the same dummy key format
        if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
        if self.provider == "ollama":
                os.environ["OLLAMA_API_KEY"] = "sk-no-key-required"
            os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
            else:
            os.environ["OPENAI_API_KEY"] = api_key if api_key else "sk-no-key-required"
            return
        
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "perplexity": "PERPLEXITY_API_KEY",
            "xai": "XAI_API_KEY"
        }
        
        env_key = env_key_map.get(self.provider)
        if env_key:
            os.environ[env_key] = api_key

    def _set_base_url(self, base_url: str):
        """Set custom base URL for OpenAI-compatible providers."""
        self.custom_base_url = base_url
        if self.provider in ["llamacpp", "lmstudio", "lemonade"]:
            litellm.api_base = base_url
            logger.info(f"Set custom base URL for {self.provider}: {base_url}")
        else:
            # Clear litellm.api_base for other providers to avoid pollution
            if hasattr(litellm, 'api_base') and litellm.api_base is not None:
                litellm.api_base = None
                logger.info(f"Cleared litellm.api_base for {self.provider}")
    
    def _set_default_base_url(self):
        """Set default base URL based on provider.
        
        Priority order:
        1. Harbor environment variables (OLLAMA_API_BASE, LLAMACPP_API_BASE, LMSTUDIO_API_BASE)
        2. PROVIDER_MODELS default base_url
        """
        # Check for Harbor environment variables first
        harbor_env_map = {
            "ollama": "OLLAMA_API_BASE",
            "llamacpp": "LLAMACPP_API_BASE",
            "lmstudio": "LMSTUDIO_API_BASE",
            "lemonade": "LEMONADE_API_BASE"
        }
        
        env_var = harbor_env_map.get(self.provider)
        if env_var:
            harbor_url = os.getenv(env_var)
            # Use Harbor URL if it's set and different from default localhost
            if harbor_url:
                # Check if it's a Harbor URL (not localhost)
                is_harbor_url = "localhost" not in harbor_url and "127.0.0.1" not in harbor_url
                if is_harbor_url:
                    self.custom_base_url = harbor_url
                    if self.provider in ["llamacpp", "lmstudio", "lemonade"]:
                        litellm.api_base = harbor_url
                    logger.info(f"🚢 Harbor URL detected for {self.provider}: {harbor_url}")
                    return
        
        # Fall back to default configuration
        provider_config = PROVIDER_MODELS.get(self.provider)
        if provider_config and "base_url" in provider_config:
            default_url = provider_config["base_url"]
            self.custom_base_url = default_url
            if self.provider in ["llamacpp", "lmstudio", "lemonade"]:
                litellm.api_base = default_url
                logger.info(f"Set default base URL for {self.provider}: {default_url}")
        
        # Clear litellm.api_base for providers that don't need it (e.g., Ollama)
        if self.provider not in ["llamacpp", "lmstudio", "lemonade"]:
            if hasattr(litellm, 'api_base') and litellm.api_base is not None:
                litellm.api_base = None
                logger.info(f"Cleared litellm.api_base for {self.provider}")
    
    def get_base_url(self) -> Optional[str]:
        """Get the current base URL."""
        return self.custom_base_url

    
    # NOTE: This method is currently unused - the UI recreates the LiteLLMProvider object instead
    # Kept for potential future use (hot-swapping, programmatic provider changes, API endpoints)
    # def switch_provider(self, provider: str, model: Optional[str] = None, base_url: Optional[str] = None) -> str:
    #     """
    #     Switch to a different AI provider.
    #     
    #     Args:
    #         provider: Name of the provider to switch to
    #         model: Optional specific model to use, defaults to provider's default
    #         base_url: Optional custom base URL for OpenAI-compatible providers
    #         
    #     Returns:
    #         Status message
    #     """
    #     if provider.lower() not in PROVIDER_MODELS:
    #         available_providers = list(PROVIDER_MODELS.keys())
    #         return f"Provider {provider} not supported. Available: {available_providers}"
    #     
    #     old_provider = self.provider
    #     self.provider = provider.lower()
    #     
    #     if model:
    #         self.current_model = model
    #     else:
    #         self.current_model = self._get_default_model(self.provider)
    #     
    #     # Handle custom base URL
    #     if base_url:
    #         self.custom_base_url = base_url
    #         self._set_base_url(base_url)
    #     else:
    #         self._set_default_base_url()
    #     
    #     self._load_api_key_from_env()
    #     
    #     logger.info(f"Switched from {old_provider} to {self.provider} using model {self.current_model}")
    #     return f"Switched to {self.provider} with model {self.current_model}"
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model, defaults to current model
            
        Returns:
            Dictionary with model information
        """
        target_model = model_name or self.current_model
        
        if "/" in target_model:
            model_provider = target_model.split("/")[0]
        else:
            model_provider = self.provider
        
        return {
            "model": target_model,
            "provider": model_provider,
            "current_provider": self.provider,
            "is_current": target_model == self.current_model,
            "available_in_provider": target_model in self.get_available_models()
        }
    
    def _call_litellm_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> Tuple[Optional[Dict], Optional[str]]:
        """Call LiteLLM completion API with error handling."""
        try:
            model_to_use = model or self.current_model
            
            # Add custom base URL for llamacpp, lmstudio, and lemonade
            if self.provider in ["llamacpp", "lmstudio", "lemonade"] and self.custom_base_url:
                kwargs["api_base"] = self.custom_base_url
                logger.info(f"Using custom base URL: {self.custom_base_url}")
            
            # Remove response_format for providers that don't support it
            if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"] and "response_format" in kwargs:
                logger.info(f"{self.provider} detected - removing response_format parameter and adding JSON instruction to prompt")
                kwargs.pop("response_format")
                if messages and len(messages) > 0:
                    last_msg = messages[-1]["content"]
                    if "JSON" in last_msg or "json" in last_msg:
                        messages[-1]["content"] = last_msg + "\n\nIMPORTANT: Return ONLY valid JSON, no other text or explanation."
            
            # Use raw HTTP client for Lemonade to bypass LiteLLM response parsing issues
            if self.provider == "lemonade" and self.custom_base_url:
                import requests
                url = f"{self.custom_base_url}/chat/completions"
                # Strip openai/ prefix from model name for actual API call
                api_model = model_to_use.replace("openai/", "") if model_to_use.startswith("openai/") else model_to_use
                payload = {
                    "model": api_model,
                    "messages": messages,
                    **{k: v for k, v in kwargs.items() if k not in ["api_base", "custom_llm_provider"]}
                }
                logger.info(f"Direct API call to Lemonade: {url} with model {api_model}")
                logger.info(f"Payload: {len(messages)} messages, max_tokens: {payload.get('max_tokens', 'not set')}")
                resp = requests.post(url, json=payload, timeout=300)
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"Lemonade response status: {resp.status_code}")
                
                # Extract content, handling reasoning_content for DeepSeek-R1 models
                content = ""
                finish_reason = None
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
                    finish_reason = choice.get("finish_reason")
                    
                    # Handle reasoning models - use reasoning_content if content is empty
                    if not content and "reasoning_content" in message and message["reasoning_content"]:
                        content = message["reasoning_content"]
                        logger.info(f"Using reasoning_content as fallback (content was empty), length: {len(content)}")
                    elif "reasoning_content" in message and message["reasoning_content"]:
                        # Reasoning is separate, just use final content
                        logger.info("DeepSeek-R1 reasoning model detected with separate reasoning")
                    
                    logger.info(f"Extracted content length: {len(content)}")
                else:
                    logger.error(f"No choices in response! Data: {data}")
                
                # Check if hit token limit
                if finish_reason == "length":
                    usage = data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    total_tokens = usage.get("total_tokens", 0)
                    
                    # If we got some content despite hitting limit, use it (reasoning_content might have data)
                    if content and len(content) > 0:
                        logger.warning(f"⚠️ Token limit reached but got partial response ({len(content)} chars). Prompt: {prompt_tokens} tokens, Total: {total_tokens} tokens")
                        # Don't return error, return what we got
                    else:
                        # No content at all - this is a real error
                        error_msg = f"❌ Token limit reached with no usable response. Model context: {total_tokens} tokens (prompt: {prompt_tokens}). Try a model with larger context or reduce prompt size."
                        logger.error(error_msg)
                        return None, error_msg
                
                result = {
                    "choices": [{"message": {"content": content}}],
                    "model": data.get("model", model_to_use),
                    "usage": data.get("usage", {})
                }
                return result, None
            
            response = completion(model=model_to_use, messages=messages, **kwargs)
            
            content = ""
            model_used = model_to_use
            usage_info = {}
            
            choices = getattr(response, 'choices', [])
            if choices and len(choices) > 0:
                first_choice = choices[0]
                message = getattr(first_choice, 'message', None)
                if message:
                    content = getattr(message, 'content', "")
                    if len(content) == 0:
                        # Check for refusal or finish_reason
                        finish_reason = getattr(first_choice, 'finish_reason', 'unknown')
                        refusal = None
                        if hasattr(message, '__dict__'):
                            provider_fields = message.__dict__.get('provider_specific_fields')
                            if provider_fields and isinstance(provider_fields, dict):
                                refusal = provider_fields.get('refusal')
                        
                        if refusal:
                            logger.error(f"LLM refused to generate content: {refusal}")
                        elif finish_reason == 'length':
                            logger.error(f"LLM hit token limit (finish_reason=length). Consider increasing max_tokens.")
                        
                        # Try alternative access methods
                        if hasattr(message, 'text'):
                            content = message.text
                        elif isinstance(message, dict):
                            content = message.get('content', '')
            
            model_used = getattr(response, 'model', model_to_use)
                
            usage_info = getattr(response, 'usage', {})
            
            result = {
                "choices": [{"message": {"content": content}}],
                "model": model_used,
                "usage": usage_info
            }
            
            return result, None
        except Exception as e:
            error_msg = f"LiteLLM completion failed: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Full error details: {type(e).__name__}: {e}", exc_info=True)
            return None, error_msg
    
    def prompt_function(self, messages: List[Dict[str, str]], request_id: Optional[str] = None, 
                       model: Optional[str] = None, **kwargs) -> Dict:
        """Universal prompt function using LiteLLM."""
        if not request_id:
            request_id = str(uuid.uuid4())
        
        response, error = self._call_litellm_completion(messages, model, **kwargs)
        
        if response:
            content = response["choices"][0]["message"]["content"]
            
            current_model = model or self.current_model
            if current_model and ('deepseek-r1' in current_model.lower() or 'r1' in current_model.lower()):
                content = self._parse_reasoning_response(content)
            
            return {
                "success": True,
                "content": content,
                "usage": response.get("usage", {}),
                "request_id": request_id
            }
        else:
            return {
                "success": False,
                "error": error,
                "request_id": request_id
            }
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for the current provider.
        For local providers (Ollama, llama.cpp, LM Studio), fetch from server dynamically.
        For cloud providers, return hardcoded list.
        
        Returns:
            List of model names
        """
        # For local providers, try to fetch models from the server
        if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            dynamic_models = self._fetch_local_models()
            if dynamic_models:
                return dynamic_models
            # Fallback to empty list if server is not running
            return []
        
        # For cloud providers, return hardcoded list
        provider_config = PROVIDER_MODELS.get(self.provider)
        return provider_config["models"] if provider_config else [self.current_model]
    
    def _fetch_local_models(self) -> List[str]:
        """
        Fetch available models from local AI servers (Ollama, llama.cpp, LM Studio, Lemonade).
        Uses Harbor environment variables if available, otherwise localhost.
        
        Returns:
            List of model identifiers, or empty list if unavailable
        """
        import requests
        
        try:
            if self.provider == "ollama":
                # Ollama uses a different endpoint and response format
                base_url = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
                url = f"{base_url}/api/tags"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    model_list = [f"ollama/{m.get('name', '')}" for m in models if m.get('name')]
                    logger.info(f"Fetched {len(model_list)} models from Ollama at {base_url}")
                    return model_list
            
            elif self.provider in ["llamacpp", "lmstudio", "lemonade"]:
                # All OpenAI-compatible providers use the same endpoint and format
                # Priority: custom_base_url > provider-specific env var > default config
                base_url = self.custom_base_url if self.custom_base_url else None
                
                # Check for provider-specific environment variable if no custom URL
                if not base_url:
                    env_map = {
                    "llamacpp": "LLAMACPP_API_BASE",
                        "lmstudio": "LMSTUDIO_API_BASE",
                        "lemonade": "LEMONADE_API_BASE"
                }
                    env_var = env_map.get(self.provider)
                base_url = os.getenv(env_var) if env_var else None
                
                # Fall back to default from config
                if not base_url:
                    base_url = PROVIDER_MODELS.get(self.provider, {}).get("base_url", "")
                
                if not base_url:
                    logger.warning(f"No base URL configured for {self.provider}")
                    return []
                
                # Try multiple endpoint variations for compatibility
                endpoints_to_try = [
                    f"{base_url}/models",                    # Standard OpenAI format
                    f"{base_url}/models?show_all=true",      # Extended format (some servers)
                ]
                
                for url in endpoints_to_try:
                    try:
                        logger.info(f"Fetching models from {self.provider} at {url}")
                        response = requests.get(url, timeout=5)
                        
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("data", [])
                            
                            if models:
                    model_list = [f"openai/{m.get('id', '')}" for m in models if m.get('id')]
                    logger.info(f"Fetched {len(model_list)} models from {self.provider} at {base_url}")
                    return model_list
                            else:
                                logger.warning(f"Empty models list from {url}")
                    except requests.exceptions.Timeout:
                        logger.warning(f"Timeout fetching from {url}")
                        continue
        except requests.exceptions.RequestException as e:
                        logger.warning(f"Request failed for {url}: {e}")
                        continue
                
                # If we get here, all endpoints failed
                logger.warning(f"No models found from any endpoint for {self.provider} at {base_url}")
        
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout fetching models from {self.provider}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error fetching models from {self.provider}: {e}")
        except Exception as e:
            logger.error(f"Error fetching models from {self.provider}: {e}")
        
        return []
    
    def set_model(self, model_name: str) -> str:
        """Set the model to use."""
        available_models = self.get_available_models()
        if model_name not in available_models:
            return f"Model {model_name} not available. Available: {available_models}"
        
        self.current_model = model_name
        return f"Model set to {model_name}"
    
    def test_api_key(self, api_key: str, model: str) -> str:
        """Test if an API key is valid."""
        try:
            # For local providers (Ollama, llama.cpp, LM Studio, Lemonade), skip API key test and just test connection
            if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
                provider_names = {
                    "ollama": "Ollama",
                    "llamacpp": "llama.cpp",
                    "lmstudio": "LM Studio",
                    "lemonade": "Lemonade"
                }
                provider_display = provider_names.get(self.provider, self.provider)
                logger.info(f"Testing {provider_display} connection...")
                
                # Try to connect
                test_messages = [{"role": "user", "content": "test"}]
                response, error = self._call_litellm_completion(test_messages, model or self.current_model, max_tokens=5)
                
                if response:
                    return f"✅ {provider_display} connection successful"
                else:
                    # Enhanced error message for local providers
                    if "connection" in error.lower() or "refused" in error.lower() or "failed to connect" in error.lower():
                        server_instructions = {
                            "ollama": "Please start Ollama server first:\n1. Open terminal\n2. Run: ollama serve",
                            "llamacpp": f"Please start llama.cpp server first:\n1. Navigate to: test_setup\\llama.cpp\n2. Run: start_server.bat\n3. Server will start at {self.custom_base_url or 'http://localhost:8080'}",
                            "lmstudio": f"Please start LM Studio server first:\n1. Open LM Studio\n2. Go to Local Server tab\n3. Click 'Start Server'\n4. Ensure it's running at {self.custom_base_url or 'http://localhost:1234'}"
                        }
                        instructions = server_instructions.get(self.provider, f"Please start {provider_display} server")
                        return f"❌ {provider_display} server not running!\n\n{instructions}"
                    else:
                        return f"❌ {provider_display} connection failed: {error}"
            
            old_key = os.environ.get(f"{self.provider.upper()}_API_KEY")
            self._set_provider_api_key(api_key)
            
            test_messages = [{"role": "user", "content": "Hello"}]
            response, error = self._call_litellm_completion(test_messages, model, max_tokens=5)
            
            if old_key:
                self._set_provider_api_key(old_key)
            
            return "✅ API key is valid" if response else f"❌ API key test failed: {error}"
        except Exception as e:
            logger.error(f"API key test failed: {str(e)}", exc_info=True)
            return f"❌ API key test failed: {str(e)}"
    
    def set_api_key(self, api_key: str) -> str:
        """Set the API key for the current provider."""
        self._set_provider_api_key(api_key)
        return self.test_api_key(api_key, self.current_model)
    
    def get_provider_name(self) -> str:
        """Get the name of the current AI provider."""
        return f"litellm-{self.provider}"

    def _parse_reasoning_response(self, content: str) -> str:
        """Parse DeepSeek R1 reasoning response to extract final answer from thinking tags."""
        
        if '<think>' in content:
            pattern = r'<think>.*?</think>\s*'
            final_answer = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            
            if final_answer:
                logger.debug(f"Removed <think> tags, extracted final answer: '{final_answer[:100]}...'")
                return final_answer
        
        if '<thinking>' in content:
            pattern = r'<thinking>.*?</thinking>\s*'
            final_answer = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            
            if final_answer:
                logger.debug(f"Removed <thinking> tags, extracted final answer: '{final_answer[:100]}...'")
                return final_answer
        
        return content 
    
    def check_context_window(self) -> Tuple[Optional[int], str]:
        """
        Check if the model has sufficient context window for Resume Helper.
        
        Returns:
            Tuple of (context_size, warning_message)
            - context_size: Detected context size in tokens, or None if unknown
            - warning_message: Warning/info message for the user, or empty string if OK
        """
        MIN_RECOMMENDED_CONTEXT = 8192
        
        # For local providers, try to detect context from server
        if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            try:
                import requests
                base_url = self.custom_base_url
                
                if not base_url:
                    # Get default base URL
                    base_url = PROVIDER_MODELS.get(self.provider, {}).get("base_url", "")
                
                if not base_url:
                    return None, ""
                
                # Try to get model info
                if self.provider == "lemonade":
                    # Lemonade provides model info in /models endpoint
                    url = f"{base_url}/models"
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        models = data.get("data", [])
                        
                        # Find current model
                        current_model_name = self.current_model.replace("openai/", "") if self.current_model else ""
                        for model in models:
                            if model.get("id") == current_model_name:
                                # Check if context size info is available
                                recipe_options = model.get("recipe_options", {})
                                ctx_size = recipe_options.get("ctx_size")
                                
                                if ctx_size and isinstance(ctx_size, (int, float)):
                                    ctx_size = int(ctx_size)
                                    if ctx_size < MIN_RECOMMENDED_CONTEXT:
                                        warning = (
                                            f"⚠️ Warning: Model context window is {ctx_size} tokens.\n"
                                            f"Resume Helper works best with {MIN_RECOMMENDED_CONTEXT}+ tokens.\n\n"
                                            f"To increase context:\n"
                                            f"1. Stop Lemonade server\n"
                                            f"2. Restart with: lemonade-server serve --ctx-size {MIN_RECOMMENDED_CONTEXT}\n"
                                            f"3. Or create ~/.cache/lemonade/recipe_options.json with:\n"
                                            f'   {{"{{model_name}}": {{"ctx_size": {MIN_RECOMMENDED_CONTEXT}}}}}'
                                        )
                                        return ctx_size, warning
                                    else:
                                        return ctx_size, f"✅ Context window: {ctx_size} tokens (sufficient)"
                                
                                # If no ctx_size in recipe_options, assume default 4096
                                logger.info(f"No ctx_size found in model info, assuming 4096")
                                warning = (
                                    f"⚠️ Warning: Could not detect context size (likely 4096 tokens default).\n"
                                    f"Resume Helper needs {MIN_RECOMMENDED_CONTEXT}+ tokens.\n\n"
                                    f"To set larger context:\n"
                                    f"Restart Lemonade with: lemonade-server serve --ctx-size {MIN_RECOMMENDED_CONTEXT}"
                                )
                                return 4096, warning
                
                elif self.provider in ["llamacpp", "lmstudio"]:
                    # These usually don't expose context size through API
                    # Just provide general guidance
                    logger.info(f"{self.provider} doesn't expose context size through API")
                    return None, f"ℹ️ Ensure your {self.provider} server is configured with {MIN_RECOMMENDED_CONTEXT}+ token context for best results."
                
                elif self.provider == "ollama":
                    # Ollama model context is set per-model, check if it's accessible
                    url = f"{base_url}/api/show"
                    current_model_name = self.current_model.replace("ollama/", "") if self.current_model else ""
                    response = requests.post(url, json={"name": current_model_name}, timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        # Ollama context is in modelinfo or parameters
                        params = data.get("parameters", "")
                        # Look for num_ctx parameter
                        import re
                        match = re.search(r'num_ctx\s+(\d+)', params)
                        if match:
                            ctx_size = int(match.group(1))
                            if ctx_size < MIN_RECOMMENDED_CONTEXT:
                                warning = (
                                    f"⚠️ Warning: Model context is {ctx_size} tokens.\n"
                                    f"Resume Helper needs {MIN_RECOMMENDED_CONTEXT}+ tokens.\n\n"
                                    f"To increase: Create a Modelfile with:\n"
                                    f"FROM {current_model_name}\n"
                                    f"PARAMETER num_ctx {MIN_RECOMMENDED_CONTEXT}"
                                )
                                return ctx_size, warning
                            else:
                                return ctx_size, f"✅ Context window: {ctx_size} tokens (sufficient)"
                
            except Exception as e:
                logger.debug(f"Could not check context window: {e}")
                return None, ""
        
        # For cloud providers, they usually have large enough context
        return None, "" 

