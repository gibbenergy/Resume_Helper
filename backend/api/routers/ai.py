"""
AI workflow router - job analysis, resume tailoring, cover letters, etc.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

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
        # Match Gradio's call signature: use keyword argument for resume_data
        result = resume_helper.analyze_job_description(
            request.job_description,
            request.model,
            resume_data=resume_dict
        )
        # Track cost after operation (matching Gradio behavior)
        if isinstance(result, dict) and result.get("success") == True and "usage" in result:
            try:
                from backend.core.infrastructure.providers.cost_tracker import track_llm_operation
                # Convert usage object to dict if needed (LiteLLM Usage objects need to be converted)
                usage_obj = result.get("usage", {})
                if not isinstance(usage_obj, dict):
                    # Convert LiteLLM Usage object to dict
                    usage_dict = {}
                    if hasattr(usage_obj, 'prompt_tokens'):
                        usage_dict['prompt_tokens'] = usage_obj.prompt_tokens
                    if hasattr(usage_obj, 'completion_tokens'):
                        usage_dict['completion_tokens'] = usage_obj.completion_tokens
                    if hasattr(usage_obj, 'total_tokens'):
                        usage_dict['total_tokens'] = usage_obj.total_tokens
                    # Update result with dict version
                    result_with_dict_usage = result.copy()
                    result_with_dict_usage['usage'] = usage_dict
                else:
                    result_with_dict_usage = result
                
                # Get actual model from result if available, otherwise use request model
                actual_model = result_with_dict_usage.get("model") or request.model or "unknown"
                
                track_llm_operation(
                    resume_helper.resume_gen.temp_dir,
                    result_with_dict_usage,
                    actual_model,
                    "job_analysis"
                )
            except Exception as cost_error:
                import logging
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
        # Use the workflow directly to pass job_analysis_data
        result = resume_helper.ai_workflows.tailor_resume(
            resume_dict,
            request.job_description,
            request.model,
            request.user_prompt,
            request.job_analysis_data
        )
        # Track cost after operation (matching Gradio behavior)
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
                import logging
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
        # Use the workflow directly to pass job_analysis_data
        result = resume_helper.ai_workflows.generate_cover_letter(
            resume_dict,
            request.job_description,
            request.model,
            request.user_prompt,
            request.job_analysis_data
        )
        # Track cost after operation (matching Gradio behavior)
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
                import logging
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
        resume_dict = request.resume_data.dict()
        # Use the workflow directly to pass job_analysis_data
        result = resume_helper.ai_workflows.get_improvement_suggestions(
            resume_dict,
            request.job_description,
            request.model,
            request.job_analysis_data
        )
        # Track cost after operation (matching Gradio behavior)
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
                import logging
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
        import logging
        logger = logging.getLogger(__name__)
        
        # Switch provider first
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
        
        # Local providers don't need real API keys - use dummy key
        api_key_to_use = request.api_key
        if mapped_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            api_key_to_use = "sk-no-key-required"
        
        result = resume_helper.switch_to_litellm_provider(
            provider=mapped_provider,
            model=request.model,
            api_key=api_key_to_use
        )
        
        # Recreate ai_workflows after switching provider (matching Gradio behavior)
        # This ensures the workflows use the new provider, but note: this clears the cache
        from backend.core.workflows.resume_workflows import ResumeAIWorkflows
        resume_helper.ai_workflows = ResumeAIWorkflows(resume_helper.get_litellm_provider())
        
        # Check if provider switch succeeded - this validates the API key
        # If switch succeeded, the API key is valid even if test_api_key fails due to truncation
        provider_switch_success = (
            "✅" in str(result) or 
            "success" in str(result).lower() or 
            "Switched" in str(result) or
            "switched" in str(result).lower()
        )
        
        # Test the API key (matching Gradio behavior: call set_api_key first, then test_api_key)
        # Gradio does: provider.set_api_key(api_key) then provider.test_api_key(api_key, model)
        provider = resume_helper.get_litellm_provider()
        
        if mapped_provider not in ["ollama", "llamacpp", "lmstudio", "lemonade"] and request.api_key:
            # Set API key first (like Gradio does)
            # Note: set_api_key() internally calls test_api_key(), but Gradio still calls test_api_key() again
            provider.set_api_key(request.api_key)
        
        # Now test the API key (Gradio calls this even after set_api_key)
        if mapped_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
            test_result = provider.test_api_key("sk-no-key-required", request.model or "")
        else:
            test_result = provider.test_api_key(request.api_key or "", request.model or "")
        
        # Save API key to .env file if test is successful (matching Gradio behavior exactly)
        # Gradio checks: "success" in result.lower() or "valid" in result.lower()
        test_explicit_success = "success" in test_result.lower() or "valid" in test_result.lower()
        
        # Check if test failed due to truncation (not an actual invalid key)
        is_truncation_error = (
            "truncated" in test_result.lower() or 
            "finish_reason" in test_result.lower() or
            "max_tokens" in test_result.lower() or
            "token limit" in test_result.lower() or
            "content length: 0" in test_result.lower()
        )
        
        # Overall success: either explicit success OR (provider switch succeeded AND truncation error)
        # This handles the case where API key is valid but test fails due to max_tokens=5 truncation
        test_success = test_explicit_success or (provider_switch_success and is_truncation_error)
        
        # Save API key if provider switch succeeded OR test succeeded
        # This matches Gradio behavior: save key if switch succeeds, even if test fails due to truncation
        should_save_key = test_success or provider_switch_success
        
        if should_save_key:
            # Get .env file path (same location as Gradio)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            env_file_path = os.path.join(project_root, '.env')
            
            def save_env_var(key: str, value: str):
                """Save environment variable to .env file (matching Gradio implementation)."""
                try:
                    # Read existing .env file
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
                    
                    # Update or add the variable
                    env_vars[key] = value
                    
                    # Write back to .env file
                    with open(env_file_path, 'w', encoding='utf-8') as f:
                        for env_key, env_value in env_vars.items():
                            f.write(f'{env_key}={env_value}\n')
                    
                    # Also set in current process environment
                    os.environ[key] = value
                except Exception as e:
                    # Log but don't fail - API key still works in memory
                    import logging
                    logging.warning(f"Failed to save {key} to .env file: {e}")
            
            # Save API key to .env file (matching Gradio behavior)
            if mapped_provider == "ollama":
                save_env_var("OLLAMA_API_KEY", "ollama-local-dummy-key")
            elif request.api_key and request.api_key.strip():
                env_key = f"{mapped_provider.upper()}_API_KEY"
                save_env_var(env_key, request.api_key)
            
            # Save provider and model preferences
            save_env_var("RESUME_HELPER_LAST_PROVIDER", request.provider)
            if request.model:
                save_env_var("RESUME_HELPER_LAST_MODEL", request.model)
        
        # If we're treating truncation as success, modify the message to be clearer
        if test_success and is_truncation_error and not test_explicit_success:
            final_message = "✅ API key is valid (provider switch successful, test truncated but key is valid)"
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
        
        # Extract numeric value from "Total Cost: $X.XXXXXX"
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
            "message": "❌ Auto-updater module not found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating LiteLLM: {str(e)}")

