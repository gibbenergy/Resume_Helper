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
        ],
        "base_url": "http://localhost:11434"
    },
    "llamacpp": {
        "default": "openai/gpt-oss",
        "models": [],
        "base_url": "http://localhost:8080/v1"
    },
    "lmstudio": {
        "default": "openai/gpt-oss",
        "models": [],
        "base_url": "http://localhost:1234/v1"
    },
    "lemonade": {
        "default": "openai/gpt-oss",
        "models": [],
        "base_url": "http://localhost:8000/api/v1"
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
            return provider_config["default"]
        return "gpt-4.1"
    
    def _load_api_key_from_env(self):
        """Load API key from environment variables."""
        # Local providers don't need real API keys
        if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            self._set_local_provider_config()
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
    
    def _set_local_provider_config(self):
        """Set configuration for local providers."""
        if self.provider == "ollama":
            os.environ["OLLAMA_API_KEY"] = "sk-no-key-required"
            if "OLLAMA_API_BASE" not in os.environ:
                os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
        elif self.provider in ["llamacpp", "lmstudio", "lemonade"]:
            # OpenAI-compatible local providers - set OPENAI_API_KEY and litellm.api_base
            os.environ["OPENAI_API_KEY"] = "sk-no-key-required"
            base_urls = {
                "llamacpp": "http://localhost:8080/v1",
                "lmstudio": "http://localhost:1234/v1",
                "lemonade": "http://localhost:8000/api/v1"
            }
            base_url = base_urls.get(self.provider)
            if base_url:
                self.custom_base_url = base_url
                litellm.api_base = base_url
                logger.info(f"Set litellm.api_base for {self.provider}: {base_url}")
    
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
        """Set default base URL based on provider."""
        # Check for environment variables first
        env_map = {
            "ollama": "OLLAMA_API_BASE",
            "llamacpp": "LLAMACPP_API_BASE",
            "lmstudio": "LMSTUDIO_API_BASE",
            "lemonade": "LEMONADE_API_BASE"
        }
        
        url_set = False
        env_var = env_map.get(self.provider)
        if env_var:
            env_url = os.getenv(env_var)
            if env_url:
                self.custom_base_url = env_url
                if self.provider in ["llamacpp", "lmstudio", "lemonade"]:
                    litellm.api_base = env_url
                logger.info(f"Using env base URL for {self.provider}: {env_url}")
                url_set = True
        
        # Fall back to default configuration if not set from env
        if not url_set:
            provider_config = PROVIDER_MODELS.get(self.provider)
            if provider_config and "base_url" in provider_config:
                default_url = provider_config["base_url"]
                self.custom_base_url = default_url
                if self.provider in ["llamacpp", "lmstudio", "lemonade"]:
                    litellm.api_base = default_url
                    logger.info(f"Set default base URL for {self.provider}: {default_url}")
        
        # ALWAYS clear litellm.api_base for providers that don't need it (Ollama uses OLLAMA_API_BASE)
        if self.provider not in ["llamacpp", "lmstudio", "lemonade"]:
            if hasattr(litellm, 'api_base') and litellm.api_base is not None:
                litellm.api_base = None
                logger.info(f"Cleared litellm.api_base for {self.provider}")
    
    def get_base_url(self) -> Optional[str]:
        """Get the current base URL."""
        return self.custom_base_url

    def _set_provider_api_key(self, api_key: str):
        """Set the API key for the current provider."""
        # Local providers don't need real API keys
        if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            self._set_local_provider_config()
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

    
    def switch_provider(self, provider: str, model: Optional[str] = None) -> str:
        """
        Switch to a different AI provider.
        
        Args:
            provider: Name of the provider to switch to
            model: Optional specific model to use, defaults to provider's default
            
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
            
            # Add custom base URL for llamacpp, lmstudio, and lemonade
            if self.provider in ["llamacpp", "lmstudio", "lemonade"] and self.custom_base_url:
                kwargs["api_base"] = self.custom_base_url
                logger.info(f"Using custom base URL: {self.custom_base_url}")
            
            # Remove response_format for local providers that don't support it
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
                # Strip any provider prefix (openai/, ollama/, etc.) from model name for actual API call
                api_model = model_to_use
                for prefix in ["openai/", "ollama/", "lemonade/"]:
                    if api_model.startswith(prefix):
                        api_model = api_model[len(prefix):]
                        break
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
                
                # Check for error in response body (Lemonade returns 200 with error in body)
                if "error" in data:
                    error_info = data["error"]
                    error_msg = error_info.get("message", str(error_info))
                    error_details = error_info.get("details", {}).get("response", {}).get("error", {})
                    if error_details.get("type") == "exceed_context_size_error":
                        n_ctx = error_details.get("n_ctx", "unknown")
                        n_prompt = error_details.get("n_prompt_tokens", "unknown")
                        error_msg = (
                            f"❌ CONTEXT SIZE ERROR: Model has {n_ctx} tokens but your prompt needs {n_prompt} tokens.\n\n"
                            f"📋 TO FIX: Run this command in your terminal:\n\n"
                            f"    lemonade-server serve --ctx-size 8192\n\n"
                            f"This will restart Lemonade with 8192 token context (enough for Resume Helper)."
                        )
                    logger.error(f"Lemonade error: {error_msg}")
                    return None, error_msg
                
                # Extract content, handling reasoning_content for DeepSeek-R1 models
                content = ""
                finish_reason = None
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    message_data = choice.get("message", {})
                    content = message_data.get("content", "")
                    finish_reason = choice.get("finish_reason")
                    
                    # Handle reasoning models - use reasoning_content if content is empty
                    if not content and "reasoning_content" in message_data and message_data["reasoning_content"]:
                        content = message_data["reasoning_content"]
                        logger.info(f"Using reasoning_content as fallback (content was empty), length: {len(content)}")
                    elif "reasoning_content" in message_data and message_data["reasoning_content"]:
                        # Reasoning is separate, just use final content
                        logger.info("DeepSeek-R1 reasoning model detected with separate reasoning")
                    
                    logger.info(f"Extracted content length: {len(content)}")
                else:
                    logger.error(f"No choices in response! Data: {data}")
                    return None, f"Lemonade returned empty response. Check server logs."
                
                # Check if hit token limit
                if finish_reason == "length":
                    usage = data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    total_tokens = usage.get("total_tokens", 0)
                    
                    # If we got some content despite hitting limit, use it
                    if content and len(content) > 0:
                        logger.warning(f"⚠️ Token limit reached but got partial response ({len(content)} chars). Prompt: {prompt_tokens} tokens, Total: {total_tokens} tokens")
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
                finish_reason = getattr(first_choice, 'finish_reason', None)
                message = getattr(first_choice, 'message', None)
                if message:
                    content = getattr(message, 'content', "")
                    
                    # Check for truncation (finish_reason='length' or very short content)
                    if finish_reason == 'length':
                        logger.warning(f"⚠️ LLM response was truncated (finish_reason=length). Content length: {len(content)}")
                    elif len(content) > 0 and len(content) < 50:
                        logger.warning(f"⚠️ LLM response is very short ({len(content)} chars), might be truncated")
                    
                    if len(content) == 0:
                        # Check for refusal or finish_reason
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
                    
                    # Store finish_reason in result for caller to check
                    if finish_reason == 'length' and len(content) < 100:
                        # Response was truncated and is too short
                        logger.error(f"❌ LLM response truncated and incomplete. Content: {content[:100]}")
                        return None, f"Response was truncated (finish_reason=length). Only received {len(content)} characters. Please increase max_tokens or reduce input size."
            
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
            # For all local providers, skip API key test and just test connection
            if self.provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
                logger.info(f"Testing {self.provider} connection...")
                test_messages = [{"role": "user", "content": "test"}]
                response, error = self._call_litellm_completion(test_messages, model or self.current_model, max_tokens=5)
                if response:
                    return f"✅ {self.provider} connection successful"
                else:
                    return f"❌ {self.provider} connection failed: {error}"
            
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

 
