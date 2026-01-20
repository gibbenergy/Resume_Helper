"""
Environment configuration loader.
Handles .env file parsing and provider configuration.
"""

import os
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class EnvLoader:
    """Loads and manages environment configuration."""
    
    PROVIDER_MAPPING = {
        "OpenAI": "openai",
        "Anthropic (Claude)": "anthropic",
        "Google (Gemini)": "google",
        "Ollama (Local)": "ollama",
        "llama.cpp": "llamacpp",
        "LM Studio": "lmstudio",
        "Lemonade": "lemonade",
        "Groq (High-Speed)": "groq",
        "Perplexity (Search)": "perplexity",
        "xAI (Grok)": "xai"
    }
    
    LOCAL_PROVIDERS = ["ollama", "llamacpp", "lmstudio", "lemonade"]
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize with optional project root path."""
        if project_root is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
        self.project_root = project_root
        self.env_file_path = os.path.join(project_root, '.env')
    
    def load_env_vars(self) -> Dict[str, str]:
        """Load all environment variables from .env file."""
        env_vars = {}
        if os.path.exists(self.env_file_path):
            try:
                with open(self.env_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip().strip('"').strip("'")
            except Exception as e:
                logger.warning(f"Could not load .env file: {e}")
        return env_vars
    
    def get_saved_provider_config(self) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Get saved provider configuration from .env file.
        
        Returns:
            Tuple of (provider, model, api_key)
        """
        env_vars = self.load_env_vars()
        
        ui_provider = env_vars.get("RESUME_HELPER_LAST_PROVIDER", "OpenAI")
        saved_provider = self.PROVIDER_MAPPING.get(ui_provider, "openai")
        saved_model = env_vars.get("RESUME_HELPER_LAST_MODEL")
        
        if saved_provider in self.LOCAL_PROVIDERS:
            saved_api_key = "sk-no-key-required"
        else:
            env_key = f"{saved_provider.upper()}_API_KEY"
            saved_api_key = env_vars.get(env_key)
        
        return saved_provider, saved_model, saved_api_key
    
    def save_env_var(self, key: str, value: str) -> bool:
        """
        Save an environment variable to .env file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            env_vars = self.load_env_vars()
            env_vars[key] = value
            
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                for env_key, env_value in env_vars.items():
                    f.write(f'{env_key}={env_value}\n')
            
            os.environ[key] = value
            return True
        except Exception as e:
            logger.warning(f"Failed to save {key} to .env file: {e}")
            return False
