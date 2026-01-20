"""
AI workflow router - job analysis, resume tailoring, cover letters, etc.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

from backend.api.dependencies import get_resume_helper
from backend.api.models import (
    JobAnalysisRequest,
    TailorResumeRequest,
    CoverLetterRequest,
    ImprovementSuggestionsRequest,
    TestAPIKeyRequest
)
from backend.core.resume_helper import ResumeHelper
from backend.core.infrastructure.providers.litellm_provider import PROVIDER_MODELS

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/analyze-job")
async def analyze_job(
    request: JobAnalysisRequest,
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Analyze job description with resume matching."""
    try:
        resume_dict = request.resume_data.dict()
        result = resume_helper.analyze_job_description(
            request.job_description,
            request.model,
            resume_data=resume_dict
        )
        
        if isinstance(result, dict) and result.get("success") == True and "usage" in result:
            try:
                from backend.core.infrastructure.providers.cost_tracker import track_llm_operation
                usage_obj = result.get("usage", {})
                if not isinstance(usage_obj, dict):
                    usage_dict = {}
                    if hasattr(usage_obj, 'prompt_tokens'):
                        usage_dict['prompt_tokens'] = usage_obj.prompt_tokens
                    if hasattr(usage_obj, 'completion_tokens'):
                        usage_dict['completion_tokens'] = usage_obj.completion_tokens
                    if hasattr(usage_obj, 'total_tokens'):
                        usage_dict['total_tokens'] = usage_obj.total_tokens
                    result_with_dict_usage = result.copy()
                    result_with_dict_usage['usage'] = usage_dict
                else:
                    result_with_dict_usage = result
                
                actual_model = result_with_dict_usage.get("model") or request.model or "unknown"
                
                track_llm_operation(
                    resume_helper.resume_gen.temp_dir,
                    result_with_dict_usage,
                    actual_model,
                    "job_analysis"
                )
            except Exception as cost_error:
                logging.warning(f"Cost tracking failed: {cost_error}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing job: {str(e)}")


@router.post("/tailor-resume")
async def tailor_resume(
    request: TailorResumeRequest,
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Tailor resume to job description."""
    try:
        resume_dict = request.resume_data.dict()
        result = resume_helper.ai_workflows.tailor_resume(
            resume_dict,
            request.job_description,
            request.model,
            request.user_prompt,
            request.job_analysis_data
        )
        
        if isinstance(result, dict) and result.get("success") == True and "usage" in result:
            try:
                from backend.core.infrastructure.providers.cost_tracker import track_llm_operation
                track_llm_operation(
                    resume_helper.resume_gen.temp_dir,
                    result,
                    request.model or "unknown",
                    "tailor_resume"
                )
            except Exception as cost_error:
                logging.warning(f"Cost tracking failed: {cost_error}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tailoring resume: {str(e)}")


@router.post("/generate-cover-letter")
async def generate_cover_letter(
    request: CoverLetterRequest,
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Generate cover letter."""
    try:
        resume_dict = request.resume_data.dict()
        result = resume_helper.ai_workflows.generate_cover_letter(
            resume_dict,
            request.job_description,
            request.model,
            request.user_prompt,
            request.job_analysis_data
        )
        
        if isinstance(result, dict) and "usage" in result:
            try:
                from backend.core.infrastructure.providers.cost_tracker import track_llm_operation
                track_llm_operation(
                    resume_helper.resume_gen.temp_dir,
                    result,
                    request.model or "unknown",
                    "cover_letter"
                )
            except Exception as cost_error:
                logging.warning(f"Cost tracking failed: {cost_error}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")


@router.post("/improvement-suggestions")
async def get_improvement_suggestions(
    request: ImprovementSuggestionsRequest,
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Get improvement suggestions for resume."""
    try:
        logger.info(f"Improvement suggestions request received - model: {request.model}, has_job_analysis: {request.job_analysis_data is not None}")
        resume_dict = request.resume_data.dict()
        result = resume_helper.ai_workflows.get_improvement_suggestions(
            resume_dict,
            request.job_description,
            request.model,
            request.job_analysis_data
        )
        
        if isinstance(result, dict) and "usage" in result:
            try:
                from backend.core.infrastructure.providers.cost_tracker import track_llm_operation
                track_llm_operation(
                    resume_helper.resume_gen.temp_dir,
                    result,
                    request.model or "unknown",
                    "suggestions"
                )
            except Exception as cost_error:
                logging.warning(f"Cost tracking failed: {cost_error}")
        if isinstance(result, dict):
            return result
        else:
            return {"content": result, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")


@router.post("/test-api-key")
async def test_api_key(
    request: TestAPIKeyRequest,
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Test and save API key for AI provider."""
    try:
        import os
        
        provider_mapping = {
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
        mapped_provider = provider_mapping.get(request.provider, request.provider.lower())
        
        api_key_to_use = request.api_key
        if mapped_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            api_key_to_use = "sk-no-key-required"
        
        result = resume_helper.switch_to_litellm_provider(
            provider=mapped_provider,
            model=request.model,
            api_key=api_key_to_use
        )
        
        from backend.core.workflows.resume_workflows import ResumeAIWorkflows
        resume_helper.ai_workflows = ResumeAIWorkflows(resume_helper.get_litellm_provider())
        
        provider_switch_success = (
            "✅" in str(result) or 
            "success" in str(result).lower() or 
            "Switched" in str(result) or
            "switched" in str(result).lower()
        )
        
        provider = resume_helper.get_litellm_provider()
        
        if mapped_provider not in ["ollama", "llamacpp", "lmstudio", "lemonade"] and request.api_key:
            provider.set_api_key(request.api_key)
        
        if mapped_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            test_result = provider.test_api_key("sk-no-key-required", request.model or "")
        else:
            test_result = provider.test_api_key(request.api_key or "", request.model or "")
        
        test_explicit_success = "success" in test_result.lower() or "valid" in test_result.lower()
        
        is_truncation_error = (
            "truncated" in test_result.lower() or 
            "finish_reason" in test_result.lower() or
            "max_tokens" in test_result.lower() or
            "token limit" in test_result.lower() or
            "content length: 0" in test_result.lower()
        )
        
        test_success = test_explicit_success or (provider_switch_success and is_truncation_error)
        should_save_key = test_success or provider_switch_success
        
        if should_save_key:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            env_file_path = os.path.join(project_root, '.env')
            
            def save_env_var(key: str, value: str):
                """Save environment variable to .env file."""
                try:
                    env_vars = {}
                    if os.path.exists(env_file_path):
                        with open(env_file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#') and '=' in line:
                                    parts = line.split('=', 1)
                                    if len(parts) == 2:
                                        env_key = parts[0].strip()
                                        env_vars[env_key] = parts[1].strip().strip('"').strip("'")
                    
                    env_vars[key] = value
                    
                    with open(env_file_path, 'w', encoding='utf-8') as f:
                        for env_key, env_value in env_vars.items():
                            f.write(f'{env_key}={env_value}\n')
                    
                    os.environ[key] = value
                except Exception as e:
                    logging.warning(f"Failed to save {key} to .env file: {e}")
            
            if mapped_provider == "ollama":
                save_env_var("OLLAMA_API_KEY", "ollama-local-dummy-key")
            elif request.api_key and request.api_key.strip():
                env_key = f"{mapped_provider.upper()}_API_KEY"
                save_env_var(env_key, request.api_key)
            
            save_env_var("RESUME_HELPER_LAST_PROVIDER", request.provider)
            if request.model:
                save_env_var("RESUME_HELPER_LAST_MODEL", request.model)
        
        if test_success and is_truncation_error and not test_explicit_success:
            final_message = "✅ API key is valid (provider switch successful)"
        else:
            final_message = test_result
        
        response_data = {
            "success": test_success,
            "message": final_message,
            "provider": mapped_provider
        }
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing API key: {str(e)}")


@router.get("/providers")
async def get_providers() -> Dict[str, Any]:
    """Get available AI providers."""
    providers = [
        "OpenAI",
        "Anthropic (Claude)",
        "Google (Gemini)",
        "Ollama (Local)",
        "llama.cpp",
        "LM Studio",
        "Lemonade",
        "Groq (High-Speed)",
        "Perplexity (Search)",
        "xAI (Grok)"
    ]
    return {"success": True, "providers": providers}


@router.get("/models")
async def get_models(provider: str) -> Dict[str, Any]:
    """Get available models for a provider."""
    provider_mapping = {
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
    mapped_provider = provider_mapping.get(provider, provider.lower())
    
    if mapped_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
        try:
            provider_urls = {
                "ollama": "http://localhost:11434/api/tags",
                "llamacpp": "http://localhost:8080/v1/models",
                "lmstudio": "http://localhost:1234/v1/models",
                "lemonade": "http://localhost:8000/api/v1/models"
            }
            
            url = provider_urls.get(mapped_provider)
            if url:
                logger.info(f"Fetching models from {mapped_provider} at {url}")
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    models = []
                    if mapped_provider == "ollama":
                        models = [f"ollama/{m['name']}" for m in data.get('models', [])]
                    else:
                        all_models = data.get('data', [])
                        for m in all_models:
                            model_id = m.get('id', '')
                            if 'embed' not in model_id.lower() and 'whisper' not in model_id.lower():
                                models.append(f"openai/{model_id}")
                    
                    if models:
                        default = models[0]
                        return {
                            "success": True,
                            "models": models,
                            "default": default
                        }
        except Exception as e:
            logger.warning(f"Could not fetch models from {mapped_provider}: {e}")
    
    provider_config = PROVIDER_MODELS.get(mapped_provider, {})
    models = provider_config.get("models", [])
    default = provider_config.get("default", models[0] if models else None)
    
    return {
        "success": True,
        "models": models,
        "default": default
    }


@router.get("/cost")
async def get_cost(
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Get total cost from cost tracking."""
    try:
        from backend.core.infrastructure.providers.cost_tracker import get_cost_display
        cost_display = get_cost_display(resume_helper.resume_gen.temp_dir)
        
        cost_value = 0.0
        if cost_display and "$" in cost_display:
            try:
                cost_str = cost_display.split("$")[1].strip()
                cost_value = float(cost_str)
            except (ValueError, IndexError):
                pass
        return {
            "success": True,
            "cost": cost_value,
            "display": cost_display
        }
    except Exception as e:
        return {
            "success": True,
            "cost": 0.0,
            "display": "Total Cost: $0.000000"
        }


@router.post("/update-litellm")
async def update_litellm() -> Dict[str, Any]:
    """Update LiteLLM package to get current market pricing for cost estimation."""
    try:
        from backend.core.infrastructure.providers.auto_updater import force_update_litellm
        result = force_update_litellm()
        return {
            "success": True,
            "message": result
        }
    except ImportError:
        return {
            "success": False,
            "message": "Auto-updater module not found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating LiteLLM: {str(e)}")
