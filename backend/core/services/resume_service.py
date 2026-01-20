"""
Resume Service - Core orchestration for resume operations.

This service coordinates between:
- AI workflows (job analysis, resume tailoring, cover letters)
- Resume generation (PDF/DOCX output)
- Provider management (LLM switching)

It does NOT handle:
- File I/O (delegated to adapters)
- Configuration (delegated to EnvLoader)
- Table/form conversion (delegated to ProfileBuilder)
"""

import json
import logging
from typing import Optional, Dict, Any, List

from backend.core.infrastructure.config.env_loader import EnvLoader
from backend.core.infrastructure.providers.litellm_provider import LiteLLMProvider
from backend.core.infrastructure.generators.resume_generator import ResumeGenerator
from backend.core.infrastructure.frameworks.response_types import StandardResponse
from backend.core.workflows.resume_workflows import ResumeAIWorkflows
from backend.core.infrastructure.adapters.resume_loader import ResumeLoader
from backend.core.infrastructure.adapters.profile_builder import ProfileBuilder
from backend.core.services.fixture_service import FixtureService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class ResumeService:
    """Core orchestration service for resume operations."""
    
    def __init__(self):
        """Initialize the resume service with all dependencies."""
        self.resume_gen = ResumeGenerator()
        self.env_loader = EnvLoader()
        self.fixture_service = FixtureService()
        
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the LLM provider from saved configuration."""
        try:
            provider, model, api_key = self.env_loader.get_saved_provider_config()
            
            self.litellm_provider = LiteLLMProvider(
                provider=provider,
                model=model,
                api_key=api_key
            )
            self.ai_workflows = ResumeAIWorkflows(self.litellm_provider)
            logger.info(f"LiteLLM Provider initialized with {provider}")
        except Exception as e:
            logger.error(f"LiteLLM Provider initialization failed: {e}")
            raise RuntimeError(f"AI provider initialization failed: {e}")
    
    # ========== Provider Management ==========
    
    def switch_ai_provider(self, provider_name: str) -> str:
        """Switch between AI providers."""
        try:
            provider_mapping = {
                "openai": "openai",
                "anthropic": "anthropic",
                "claude": "anthropic",
                "gemini": "google",
                "google": "google",
                "ollama": "ollama",
                "llamacpp": "llamacpp",
                "lmstudio": "lmstudio",
                "lemonade": "lemonade",
                "groq": "groq",
                "perplexity": "perplexity",
                "xai": "xai"
            }
            mapped_provider = provider_mapping.get(provider_name.lower(), provider_name.lower())
            self.litellm_provider = LiteLLMProvider(provider=mapped_provider)
            logger.info(f"Switched to {mapped_provider} provider")
            return f"Switched to {mapped_provider} provider successfully"
        except Exception as e:
            logger.error(f"Failed to switch provider: {e}")
            return f"Failed to switch to {provider_name}: {str(e)}"
    
    def switch_to_litellm_provider(
        self,
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> str:
        """Switch to LiteLLM provider with specified settings."""
        try:
            self.litellm_provider = LiteLLMProvider(
                provider=provider,
                model=model,
                api_key=api_key
            )
            return f"Switched to LiteLLM {provider} provider successfully"
        except Exception as e:
            logger.error(f"Error switching to LiteLLM provider: {e}")
            return f"Error switching to LiteLLM provider: {str(e)}"
    
    def get_current_provider(self) -> str:
        """Get the name of the current AI provider."""
        return self.litellm_provider.get_provider_name()
    
    def get_available_models(self) -> list:
        """Get available models for the current provider."""
        if self.litellm_provider:
            return self.litellm_provider.get_available_models()
        return []
    
    def get_litellm_provider(self) -> LiteLLMProvider:
        """Get the LiteLLM provider instance."""
        return self.litellm_provider
    
    def test_api_key(self, api_key: str, model: Optional[str] = None) -> str:
        """Test and save API key with the specified model."""
        return self.litellm_provider.test_api_key(api_key, model or "")
    
    # ========== AI Workflow Delegation ==========
    
    def analyze_job_description(
        self,
        job_description: str,
        model: Optional[str] = None,
        resume_data: Optional[dict] = None
    ) -> dict:
        """Analyze a job description using AI."""
        return self.ai_workflows.analyze_job_description(job_description, model, resume_data)
    
    def tailor_resume(
        self,
        resume_data: dict,
        job_description: str,
        model: Optional[str] = None
    ) -> dict:
        """Tailor a resume to match a job description."""
        return self.ai_workflows.tailor_resume(resume_data, job_description, model)
    
    def generate_cover_letter(
        self,
        resume_data: dict,
        job_description: str,
        model: Optional[str] = None,
        user_prompt: Optional[str] = None
    ) -> str:
        """Generate a cover letter using AI."""
        result = self.ai_workflows.generate_cover_letter(resume_data, job_description, model, user_prompt)
        if isinstance(result, dict) and "body_content" in result:
            return result["body_content"]
        elif isinstance(result, str):
            return result
        return "Error generating cover letter"
    
    def get_improvement_suggestions(
        self,
        resume_data: dict,
        job_description: str,
        model: Optional[str] = None
    ) -> str:
        """Get AI-powered suggestions for resume improvement."""
        return self.ai_workflows.get_improvement_suggestions(resume_data, job_description, model)
    
    # ========== Full Processing Pipeline ==========
    
    def process_with_ai(
        self,
        job_description: str,
        resume_json: str,
        model: Optional[str] = None
    ) -> StandardResponse:
        """Process resume with complete AI pipeline."""
        try:
            if not job_description or not resume_json:
                return StandardResponse.error_response(
                    error="Please provide both a job description and a resume",
                    operation="process_with_ai"
                )

            try:
                if isinstance(resume_json, str):
                    resume_data = json.loads(resume_json)
                else:
                    resume_data = resume_json
            except json.JSONDecodeError:
                return StandardResponse.error_response(
                    error="Invalid resume JSON format",
                    operation="process_with_ai",
                    error_type="JSONDecodeError"
                )
            
            analysis = self.analyze_job_description(job_description, model, resume_data)
            if "error" in analysis or not analysis.get("success"):
                return StandardResponse.error_response(
                    error=f"Error analyzing job description: {analysis.get('error', 'Unknown error')}",
                    operation="process_with_ai"
                )
            
            tailored_resume = self.tailor_resume(resume_data, job_description, model)
            if isinstance(tailored_resume, dict) and "error" in tailored_resume:
                return StandardResponse.error_response(
                    error=f"Error tailoring resume: {tailored_resume['error']}",
                    operation="process_with_ai"
                )
            
            cover_letter = self.generate_cover_letter(tailored_resume, job_description, model)
            if cover_letter.startswith("Error:"):
                return StandardResponse.error_response(
                    error=cover_letter,
                    operation="process_with_ai"
                )
            
            suggestions = self.get_improvement_suggestions(resume_data, job_description, model)
            if suggestions.startswith("Error:"):
                return StandardResponse.error_response(
                    error=suggestions,
                    operation="process_with_ai"
                )
            
            return StandardResponse.success_response(
                data={
                    "job_analysis": json.dumps(analysis, indent=2),
                    "tailored_resume": json.dumps(tailored_resume, indent=2),
                    "cover_letter": cover_letter,
                    "suggestions": suggestions,
                    "status": "Success!"
                },
                operation="process_with_ai"
            )
        except Exception as e:
            return StandardResponse.error_response(
                error=f"Error processing resume: {str(e)}",
                operation="process_with_ai",
                error_type=type(e).__name__
            )
    
    # ========== Data Loading (Delegated) ==========
    
    def load_from_json(self, file_path: str) -> List[Any]:
        """Load resume data from JSON file."""
        return ResumeLoader.load_from_json(file_path)
    
    def load_software_developer_example(self) -> List[Any]:
        """Load Software Developer example."""
        return self.fixture_service.load_software_developer_example()
    
    def load_process_engineer_example(self) -> List[Any]:
        """Load Process Engineer example."""
        return self.fixture_service.load_process_engineer_example()
    
    # ========== Profile Building (Delegated) ==========
    
    def build_profile_dict(
        self,
        name_prefix: str,
        email: str,
        full_name: str,
        phone: str,
        current_address: str,
        location: str,
        citizenship: str,
        linkedin_url: str,
        github_url: str,
        portfolio_url: str,
        summary: str,
        education_table: Any,
        experience_table: Any,
        skills_table: Any,
        projects_table: Any,
        certifications_table: Any,
        others_sections_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Build profile dictionary from form values."""
        return ProfileBuilder.build_profile_dict(
            name_prefix, email, full_name, phone, current_address,
            location, citizenship, linkedin_url, github_url, portfolio_url,
            summary, education_table, experience_table, skills_table,
            projects_table, certifications_table, others_sections_data
        )
 
