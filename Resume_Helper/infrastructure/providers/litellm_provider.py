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
        "default": "openai/local-model",
        "models": [
            "openai/local-model"
        ],
        "base_url": "http://localhost:8080/v1"
    },
    "lmstudio": {
        "default": "openai/local-model",
        "models": [
            "openai/local-model"
        ],
        "base_url": "http://localhost:1234/v1"
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
        self.current_model = model or self._get_default_model(self.provider)
        self.custom_base_url = base_url
        
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
            return provider_config["default"]
        return "gpt-4.1"
    
    def _load_api_key_from_env(self):
        """Load API key from environment variables."""
        if self.provider == "ollama":
            os.environ["OLLAMA_API_KEY"] = "ollama-local-dummy-key"
            os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
            logger.info(f"Set dummy API key for Ollama (local provider) at http://localhost:11434")
            return
        
        if self.provider in ["llamacpp", "lmstudio"]:
            os.environ["OPENAI_API_KEY"] = "sk-no-key-required"
            logger.info(f"Set dummy API key for {self.provider} (local provider)")
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
            api_key = os.getenv(env_key)
            if api_key:
                self._set_provider_api_key(api_key)
                logger.info(f"Loaded API key for {self.provider}")
    
    def _set_provider_api_key(self, api_key: str):
        """Set the API key for the current provider."""
        if self.provider == "ollama":
            os.environ["OLLAMA_API_KEY"] = "ollama-local-dummy-key"
            os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
            return
        
        if self.provider in ["llamacpp", "lmstudio"]:
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
        if self.provider in ["llamacpp", "lmstudio"]:
            litellm.api_base = base_url
            logger.info(f"Set custom base URL for {self.provider}: {base_url}")
    
    def _set_default_base_url(self):
        """Set default base URL based on provider."""
        provider_config = PROVIDER_MODELS.get(self.provider)
        if provider_config and "base_url" in provider_config:
            default_url = provider_config["base_url"]
            self.custom_base_url = default_url
            if self.provider in ["llamacpp", "lmstudio"]:
                litellm.api_base = default_url
                logger.info(f"Set default base URL for {self.provider}: {default_url}")
    
    def get_base_url(self) -> Optional[str]:
        """Get the current base URL."""
        return self.custom_base_url

    
    def switch_provider(self, provider: str, model: Optional[str] = None, base_url: Optional[str] = None) -> str:
        """
        Switch to a different AI provider.
        
        Args:
            provider: Name of the provider to switch to
            model: Optional specific model to use, defaults to provider's default
            base_url: Optional custom base URL for OpenAI-compatible providers
            
        Returns:
            Status message
        """
        if provider.lower() not in PROVIDER_MODELS:
            available_providers = list(PROVIDER_MODELS.keys())
            return f"Provider {provider} not supported. Available: {available_providers}"
        
        old_provider = self.provider
        self.provider = provider.lower()
        
        if model:
            self.current_model = model
        else:
            self.current_model = self._get_default_model(self.provider)
        
        # Handle custom base URL
        if base_url:
            self.custom_base_url = base_url
            self._set_base_url(base_url)
        else:
            self._set_default_base_url()
        
        self._load_api_key_from_env()
        
        logger.info(f"Switched from {old_provider} to {self.provider} using model {self.current_model}")
        return f"Switched to {self.provider} with model {self.current_model}"
    
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
            
            # Add custom base URL for llamacpp and lmstudio
            if self.provider in ["llamacpp", "lmstudio"] and self.custom_base_url:
                kwargs["api_base"] = self.custom_base_url
                logger.info(f"Using custom base URL: {self.custom_base_url}")
            
            # Remove response_format for providers that don't support it
            if self.provider in ["ollama", "llamacpp", "lmstudio"] and "response_format" in kwargs:
                logger.info(f"{self.provider} detected - removing response_format parameter and adding JSON instruction to prompt")
                kwargs.pop("response_format")
                if messages and len(messages) > 0:
                    last_msg = messages[-1]["content"]
                    if "JSON" in last_msg or "json" in last_msg:
                        messages[-1]["content"] = last_msg + "\n\nIMPORTANT: Return ONLY valid JSON, no other text or explanation."
            
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
        """Get available models for the current provider."""
        provider_config = PROVIDER_MODELS.get(self.provider)
        return provider_config["models"] if provider_config else [self.current_model]
    
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
            # For Ollama, skip API key test and just test connection
            if self.provider == "ollama":
                logger.info("Testing Ollama connection...")
                test_messages = [{"role": "user", "content": "test"}]
                response, error = self._call_litellm_completion(test_messages, model or self.current_model, max_tokens=5)
                if response:
                    return "✅ Ollama connection successful"
                else:
                    return f"❌ Ollama connection failed: {error}"
            
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

