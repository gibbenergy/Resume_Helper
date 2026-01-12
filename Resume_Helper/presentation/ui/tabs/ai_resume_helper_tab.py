import os
import json
import uuid
import logging
import re, datetime as dt
import gradio as gr
from gradio import update
from jinja2 import Environment, FileSystemLoader

from infrastructure.generators.cover_letter_generator import generate_cover_letter_pdf
from utils.file_utils import atomic_write_json, atomic_read_json
from infrastructure.providers.litellm_provider import LiteLLMProvider, PROVIDER_MODELS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_ai_resume_helper_tab(resume_helper, all_tabs_components=None):
    if all_tabs_components is None:
        all_tabs_components = {}

    env_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
    
    def load_env_var(key, default=""):
        """Load environment variable or from .env file."""
        value = os.environ.get(key, "")
        if value:
            return value
        
        if os.path.exists(env_file_path):
            try:
                with open(env_file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            env_key, env_value = line.split('=', 1)
                            if env_key.strip() == key:
                                return env_value.strip().strip('"').strip("'")
            except Exception:
                pass
        return default
    
    def save_env_var(key, value):
        """Save environment variable to .env file."""
        try:
            existing_lines = []
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    existing_lines = f.readlines()
            
            key_found = False
            for i, line in enumerate(existing_lines):
                if line.strip().startswith(f"{key}="):
                    existing_lines[i] = f"{key}={value}\n"
                    key_found = True
                    break
            
            if not key_found:
                existing_lines.append(f"{key}={value}\n")
            
            with open(env_file_path, 'w') as f:
                f.writelines(existing_lines)
            return True
        except Exception as e:
            logger.error(f"Error saving to .env: {e}")
            return False

    with gr.Tab("AI Resume Helper") as tab:

        saved_provider = load_env_var("RESUME_HELPER_LAST_PROVIDER", "OpenAI")
        saved_model = load_env_var("RESUME_HELPER_LAST_MODEL", "")
        
        provider_mapping = {
            "OpenAI": "openai",
            "Anthropic (Claude)": "anthropic", 
            "Google (Gemini)": "google",
            "Ollama (Local)": "ollama",
            "Groq (High-Speed)": "groq",
            "Perplexity (Search)": "perplexity",
            "xAI (Grok)": "xai",
            "llama.cpp": "llamacpp",
            "LM Studio": "lmstudio",
            "Lemonade": "lemonade"
        }
        provider_name = provider_mapping.get(saved_provider, "openai")
        env_key = f"{provider_name.upper()}_API_KEY"
        saved_api_key = load_env_var(env_key, "")
        
        current_model = saved_model if saved_model else "Default"
        if provider_name == "ollama":
            status_text = "✅ Ready"
        else:
            status_text = "✅ Ready" if saved_api_key else "⚠️ Setup needed"
        
        from infrastructure.providers.cost_tracker import get_cost_display
        try:
            cost_display = get_cost_display(resume_helper.resume_gen.temp_dir)
        except:
            cost_display = "Total Cost: $0.000000"
        
        current_ai_status = gr.Markdown(f"**Current AI:** {saved_provider} • {current_model} • {status_text} • {cost_display}")
        
        with gr.Accordion("🤖 AI Configuration", open=False):
            with gr.Row():
                provider_selector = gr.Dropdown(
                    label="AI Provider",
                    choices=[
                        "OpenAI", "Anthropic (Claude)", "Google (Gemini)", 
                        "Ollama (Local)", "Groq (High-Speed)", 
                        "Perplexity (Search)", "xAI (Grok)",
                        "llama.cpp", "LM Studio", "Lemonade"
                    ],
                    value=saved_provider,
                    scale=2,
                )
                
                from infrastructure.providers.litellm_provider import PROVIDER_MODELS
                # For local providers, try to fetch models dynamically at startup
                if saved_provider in ["Lemonade", "llama.cpp", "LM Studio", "Ollama (Local)"]:
                    try:
                        provider, _ = initialize_litellm_provider(saved_provider, base_url=saved_base_url)
                        if provider:
                            all_models = provider.get_available_models()
                        else:
                            all_models = []
                    except:
                        all_models = []
                else:
                    all_models = PROVIDER_MODELS.get(provider_name.lower(), {}).get("models", [])
                
                default_model = saved_model if saved_model in all_models else (all_models[0] if all_models else saved_model if saved_model else "gpt-4o")

                model_selector = gr.Dropdown(
                    label="Model",
                    choices=all_models,
                    value=default_model,
                    scale=2,
                    allow_custom_value=True,
                    info="💡 Tip: You can type model name if auto-detection fails"
                )
                
                # Add refresh button for local providers - visible if current provider is local
                is_local_provider_at_startup = saved_provider in ["Lemonade", "llama.cpp", "LM Studio", "Ollama (Local)"]
                refresh_models_btn = gr.Button("🔄", scale=1, min_width=40, visible=is_local_provider_at_startup, variant="secondary")
                
                api_key_input = gr.Textbox(
                    label="API Key",
                    placeholder="(blank for local providers)",
                    value=saved_api_key,
                    type="password",
                    scale=3,
                )
                
                set_btn = gr.Button("Set", variant="primary", scale=1)
                update_btn = gr.Button("🔄 Update LiteLLM", variant="secondary", scale=1)
            
            # Helper function to get provider-specific base URL environment variable name
            def get_base_url_env_var(provider_ui_value):
                """Get the provider-specific base URL environment variable name."""
                provider_base_url_map = {
                    "llama.cpp": "LLAMACPP_API_BASE",
                    "LM Studio": "LMSTUDIO_API_BASE",
                    "Lemonade": "LEMONADE_API_BASE",
                    "Ollama (Local)": "OLLAMA_API_BASE"
                }
                return provider_base_url_map.get(provider_ui_value, "CUSTOM_BASE_URL")
            
            # Base URL configuration - completely hidden, only accessible programmatically
            # Users never see this - defaults work automatically for each provider
            base_url_input = gr.Textbox(
                label="Base URL",
                value="",
                visible=False,  # Completely hidden from UI
                interactive=False
            )

        with gr.Group():
            gr.Markdown("### 📝 Input")

            with gr.Row():
                with gr.Column(scale=3):
                    job_url_input = gr.Textbox(
                        label="🔗 Job URL (Key for preventing duplicates)",
                        placeholder="https://company.com/careers/job-posting",
                        lines=2
                    )
                    
                    job_description = gr.Textbox(
                        label="📋 Job Description",
                        placeholder="Paste the job description here…",
                        lines=10
                    )
                
                with gr.Column(scale=1):
                    match_score_display = gr.Number(
                        label="📈 Match Score",
                        value=0,
                        precision=0,
                        interactive=True
                    )
                    match_score_summary = gr.Markdown(
                        label="📄 Match Score Summary",
                        value="*Summary will appear here after analysis.*"
                    )

            with gr.Accordion("➕ Optional User Prompt", open=False):
                user_prompt = gr.Textbox(
                    label="💭 Custom Instructions",
                    placeholder="e.g. 'Use energetic tone', 'Highlight leadership skills', 'Focus on technical expertise'",
                    lines=3,
                )

            with gr.Accordion("➕Current Resume JSON (auto-loaded)", open=False):
                resume_json = gr.Textbox(
                    label="📄 Current Resume JSON",
                    placeholder="Will be filled automatically",
                    lines=20,
                    interactive=False
                )
            
            with gr.Row():
                update_resume_btn = gr.Button("🔄 Update Resume Data", variant="secondary", scale=1)
                reset_btn = gr.Button("🔄 Reset", variant="secondary", scale=1)

        with gr.Row():
            analyze_btn      = gr.Button("🔍 Analyze Job",     variant="primary", scale=1, interactive=False)
            tailor_btn       = gr.Button("🎯 Tailor Resume",   variant="primary", scale=1, interactive=False)
            cover_letter_btn = gr.Button("✉️  Cover Letter",   variant="primary", scale=1, interactive=False)
            suggestions_btn  = gr.Button("💡 Suggestions",     variant="primary", scale=1, interactive=False)

        gr.Markdown("### 🤖 AI-Generated Content")
        gr.Markdown("💡 **Tip:** All AI-generated content below is **fully editable**! You can modify, refine, or personalize any text before downloading.")
        
        with gr.Tabs() as output_tabs:
            with gr.TabItem("🔍 Job Analysis") as job_analysis_tab:
                job_analysis = gr.Textbox(
                    label="Job Requirements Analysis (✏️ Editable)",
                    placeholder="AI-generated job analysis will appear here. You can edit this text directly after generation.",
                    lines=15, 
                    interactive=True
                )
            with gr.TabItem("🎯 Tailored Resume") as tailored_resume_tab:
                tailored_resume = gr.Textbox(
                    label="Tailored Resume Content (✏️ Editable)",
                    placeholder="AI-tailored resume content will appear here. You can edit this text directly after generation.",
                    lines=15, 
                    interactive=True
                )
            with gr.TabItem("✉️ Cover Letter") as cover_letter_tab:
                cover_letter = gr.Textbox(
                    label="Generated Cover Letter (✏️ Editable)",
                    placeholder="AI-generated cover letter will appear here. You can edit this text directly after generation.",
                    lines=15, 
                    interactive=True
                )
            with gr.TabItem("💡 Improvement Suggestions") as suggestions_tab:
                suggestions = gr.Textbox(
                    label="Improvement Suggestions (✏️ Editable)",
                    placeholder="AI-generated improvement suggestions will appear here. You can edit this text directly after generation.",
                    lines=15, 
                    interactive=True
                )

        ai_status = gr.Textbox(label="🤖 AI Processing Status", interactive=False)
        
        with gr.Row():
            resume_pdf_output = gr.DownloadButton(
                label="⬇️ Download PDF", variant="secondary", interactive=False, visible=False, scale=1
            )
            add_to_tracker_btn = gr.Button(
                "📝 Add to Application Tracker",
                variant="primary",
                interactive=False,
                scale=1
            )
        
        _TAB_INDEX = {
            "🔍 Job Analysis": 0,
            "🎯 Tailored Resume": 1,
            "✉️ Cover Letter": 2,
            "💡 Improvement Suggestions": 3,
        }

        def _tab_update(key: str):
            """Return a gradio.update that selects the correct tab index."""
            return gr.update(selected=_TAB_INDEX[key])

        job_details_state = gr.State({
            "company_name": "",
            "job_position": "",
            "letter_title": "",
            "recipient_greeting": "",
            "recipient_name": "",
            "company_address": ""
        })
        
        litellm_provider_state = gr.State(None)
        
        selected_tab_state = gr.State(0)
        
        job_analysis_pdf_state = gr.State(None)
        tailored_resume_pdf_state = gr.State(None)
        cover_letter_pdf_state = gr.State(None)
        suggestions_pdf_state = gr.State(None)

        def initialize_litellm_provider(provider_ui_value, api_key="", model="", base_url=""):
            """Initialize or update the LiteLLM provider based on UI selections."""
            try:
                provider_mapping = {
                    "OpenAI": "openai",
                    "Anthropic (Claude)": "anthropic", 
                    "Google (Gemini)": "google",
                    "Ollama (Local)": "ollama",
                    "Groq (High-Speed)": "groq",
                    "Perplexity (Search)": "perplexity",
                    "xAI (Grok)": "xai",
                    "llama.cpp": "llamacpp",
                    "LM Studio": "lmstudio",
                    "Lemonade": "lemonade"
                }
                
                provider_name = provider_mapping.get(provider_ui_value, "openai")
                
                provider = LiteLLMProvider(
                    provider=provider_name,
                    model=model if model else None,
                    api_key=api_key if api_key else None,
                    base_url=base_url if base_url else None
                )
                
                return provider, f"✅ Initialized {provider_ui_value} provider successfully"
                
            except Exception as e:
                logger.error(f"Error initializing provider: {e}")
                return None, f"❌ Error initializing provider: {str(e)}"

        def update_model_choices(provider_ui_value, base_url, current_provider_state):
            """Update available models when provider changes."""
            try:
                # Load saved base URL if not provided - use provider-specific environment variable
                if not base_url and provider_ui_value in ["llama.cpp", "LM Studio", "Lemonade"]:
                    base_url_env_var = get_base_url_env_var(provider_ui_value)
                    base_url = load_env_var(base_url_env_var, "")
                
                provider, status_msg = initialize_litellm_provider(provider_ui_value, base_url=base_url)
                
                if provider is None:
                    return gr.update(choices=[], value=""), status_msg, current_provider_state, gr.update(visible=False)
                
                all_models = provider.get_available_models()
                default_model = all_models[0] if all_models else ""
                
                # Show base URL input for llama.cpp, LM Studio, and Lemonade
                show_base_url = provider_ui_value in ["llama.cpp", "LM Studio", "Lemonade"]
                
                return (
                    gr.update(choices=all_models, value=default_model),
                    status_msg,
                    provider,
                    gr.update(visible=show_base_url)
                )
                
            except Exception as e:
                logger.error(f"Error updating models: {e}")
                return (
                    gr.update(choices=[], value=""),
                    f"❌ Error loading models: {str(e)}",
                    current_provider_state,
                    gr.update(visible=False)
                )

        def test_api_connection(provider_ui_value, api_key, model, base_url, current_provider_state):
            """Test the API connection with current settings and save if successful."""
            try:
                if current_provider_state is None:
                    provider, init_msg = initialize_litellm_provider(provider_ui_value, api_key, model, base_url)
                    if provider is None:
                        return init_msg, provider
                else:
                    provider = current_provider_state
                
                if api_key:
                    provider.set_api_key(api_key)
                
                result = provider.test_api_key(api_key or "", model or "")
                
                if "success" in result.lower() or "valid" in result.lower():
                    provider_mapping = {
                        "OpenAI": "openai",
                        "Anthropic (Claude)": "anthropic", 
                        "Google (Gemini)": "google",
                        "Ollama (Local)": "ollama",
                        "Groq (High-Speed)": "groq",
                        "Perplexity (Search)": "perplexity",
                        "xAI (Grok)": "xai",
                        "llama.cpp": "llamacpp",
                        "LM Studio": "lmstudio",
                        "Lemonade": "lemonade"
                    }
                    internal_provider = provider_mapping.get(provider_ui_value, "openai")
                    
                    if api_key:
                        env_key = f"{internal_provider.upper()}_API_KEY"
                        save_env_var(env_key, api_key)
                    save_env_var("RESUME_HELPER_LAST_PROVIDER", provider_ui_value)
                    if model:
                        save_env_var("RESUME_HELPER_LAST_MODEL", model)
                    if base_url:
                        save_env_var("CUSTOM_BASE_URL", base_url)
                    
                    # Check context window for local providers
                    context_warning = ""
                    if provider_ui_value in ["llama.cpp", "LM Studio", "Lemonade", "Ollama (Local)"]:
                        try:
                            ctx_size, ctx_msg = provider.check_context_window()
                            if ctx_msg:
                                context_warning = f"\n\n{ctx_msg}"
                        except Exception as e:
                            logger.debug(f"Could not check context window: {e}")
                    
                    return f"✅ {result} (Settings saved){context_warning}", provider
                else:
                    return f"❌ {result}", provider
                
            except Exception as e:
                logger.error(f"Error testing connection: {e}")
                return f"❌ Connection test failed: {str(e)}", current_provider_state

        def test_api_key(api_key, model):
            """Test API key using LiteLLM provider."""
            try:
                provider = resume_helper.get_litellm_provider()
                result = provider.test_api_key(api_key, model)
                return result
            except Exception as e:
                return f"❌ Error testing API key: {str(e)}"

        def _get_updated_ai_status_markdown(status_text="✅ Ready"):
            """Generates the formatted markdown string for the main AI status display."""
            try:
                provider = load_env_var("RESUME_HELPER_LAST_PROVIDER", "OpenAI")
                model = load_env_var("RESUME_HELPER_LAST_MODEL", "Default")
                cost = get_cost_display(resume_helper.resume_gen.temp_dir)
                return f"**Current AI:** {provider} • {model} • {status_text} • {cost}"
            except Exception as e:
                logger.error(f"Failed to get updated AI status: {e}")
                return "**Current AI:** Error loading status."

        def format_analysis_as_markdown(analysis_data):
            """Formats the analysis dictionary into a markdown string."""
            if not isinstance(analysis_data, dict):
                return "Invalid analysis format."
            
            # Skip match score fields - they're displayed separately in dedicated UI components
            skip_fields = {"match_score", "skills_match", "experience_match", "education_match", "match_summary"}
            
            formatted = ""
            for k, v in analysis_data.items():
                if k in skip_fields:
                    continue
                    
                field_name = k.replace('_', ' ').title()
                formatted += f"### {field_name}\n"
                if isinstance(v, list):
                    formatted += "\n" 
                    for item in v:
                        item_str = str(item)
                        if isinstance(item, dict):
                            item_str = ", ".join([f"{sub_k}: {sub_v}" for sub_k, sub_v in item.items()])
                        
                        if not item_str.strip().startswith('-'):
                           formatted += f"- {item_str}\n"
                        else:
                           formatted += f"{item_str}\n"
                else:
                    formatted += f"{v}\n"
                formatted += "\n"
            return formatted

        def analyze_job(job_desc, model, job_details, resume_data=""):
            """Analyzes the job description and returns a formatted analysis and other UI updates."""
            
            is_valid, error_msg = validate_inputs_for_analysis(job_desc, resume_data)
            if not is_valid:
                status = f"Error: {error_msg}"
                return (
                    error_msg, 
                    status, 
                    gr.update(interactive=True), 
                    gr.update(interactive=False, visible=False), 
                    gr.update(), 
                    0, 
                    "", 
                    gr.update(interactive=False),
                    status,
                    None
                )
            try:
                ai_workflows = resume_helper.ai_workflows
                
                # Parse resume_data (it comes as JSON string from UI)
                try:
                    resume_dict = json.loads(resume_data) if isinstance(resume_data, str) else resume_data
                except:
                    resume_dict = resume_data
                
                # Single API call: analyze job + calculate match score
                result = ai_workflows.analyze_job_description(job_desc, model, resume_data=resume_dict)
                
                if isinstance(result, dict) and result.get("success") == False:
                    status = f"Error: {result.get('error', 'Unknown error')}"
                    return (
                        "Error in analysis. Please check API key and try again.", 
                        status, 
                        gr.update(interactive=True), 
                        gr.update(interactive=False, visible=False), 
                        gr.update(), 
                        0, 
                        "", 
                        gr.update(interactive=False),
                        status,
                        None
                    )
                
                if isinstance(result, dict) and result.get("success") == True and "analysis" in result:
                    try:
                        from infrastructure.providers.cost_tracker import track_llm_operation
                        track_llm_operation(
                            resume_helper.resume_gen.temp_dir,
                            result,
                            model or "unknown",
                            "job_analysis"
                        )
                    except Exception as cost_error:
                        logger.warning(f"Cost tracking failed: {cost_error}")
                    
                    extracted_details = result["analysis"]
                    job_details.update(extracted_details)
                    formatted = format_analysis_as_markdown(extracted_details)
                    
                    match_score = extracted_details.get("match_score", 0)
                    summary_text = extracted_details.get("match_summary", "*No summary provided.*")
                    
                    details = ""
                    if extracted_details.get("skills_match") is not None:
                        details += f"- **Skills Match:** {extracted_details.get('skills_match')}%\n"
                    if extracted_details.get("experience_match") is not None:
                        details += f"- **Experience Match:** {extracted_details.get('experience_match')}%\n"
                    if extracted_details.get("education_match") is not None:
                        details += f"- **Education Match:** {extracted_details.get('education_match')}%\n"
                    
                    match_summary = f"**Summary:** {summary_text}\n\n**Details:**\n{details}" if details else summary_text
                    
                    try:
                        updated_cost = get_cost_display(resume_helper.resume_gen.temp_dir)
                        cost_status = f"Job analysis completed successfully! {updated_cost}"
                    except:
                        cost_status = "Job analysis completed successfully!"

                    try:
                        from infrastructure.generators.analysis_pdf_generator import generate_job_analysis_pdf
                        temp_dir = resume_helper.resume_gen.temp_dir
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        company = extracted_details.get("company_name", "") or job_details.get("company_name", "") or "company"
                        timestamp = dt.datetime.now().strftime("%Y%m%d")
                        filename = f"{_slug(company)}_job_analysis_{timestamp}.pdf"
                        pdf_path = os.path.join(temp_dir, filename)
                        
                        pdf_path = generate_job_analysis_pdf(
                            analysis_content=formatted,
                            company_name=company,
                            job_position=extracted_details.get("position_title", "") or job_details.get("job_position", ""),
                            output_path=pdf_path,
                            temp_dir=temp_dir
                        )
                        
                        pdf_visible = bool(pdf_path and os.path.exists(pdf_path))
                        
                        simple_status = "Job analysis completed successfully!"
                        if not pdf_visible:
                           simple_status += " (PDF generation failed)"
                        
                        updated_status_markdown = _get_updated_ai_status_markdown()
                        
                        job_url_update = extracted_details.get("job_url", "")
                        return (
                            formatted, 
                            simple_status,
                            gr.update(interactive=False),
                            gr.update(interactive=True, value=pdf_path, visible=pdf_visible),
                            gr.update(value=job_url_update) if job_url_update else gr.update(),
                            match_score,
                            match_summary,
                            gr.update(interactive=True),
                            updated_status_markdown,
                            pdf_path if pdf_visible else None
                        )

                    except Exception as pdf_error:
                        logger.error(f"PDF generation error: {pdf_error}")
                        simple_status = "Job analysis successful, but PDF generation failed."
                        updated_status_markdown = _get_updated_ai_status_markdown("⚠️ PDF Error")
                        job_url_update = extracted_details.get("job_url", "")
                        return (
                            formatted, 
                            simple_status,
                            gr.update(interactive=False), 
                            gr.update(interactive=False, visible=False),
                            gr.update(value=job_url_update) if job_url_update else gr.update(),
                            match_score,
                            match_summary,
                            gr.update(interactive=True),
                            updated_status_markdown,
                            None
                        )
                
                status = "Error: Unexpected response format from AI."
                return (
                    status,
                    status, 
                    gr.update(interactive=True), 
                    gr.update(interactive=False, visible=False), 
                    gr.update(), 
                    0, 
                    "", 
                    gr.update(interactive=False),
                    status
                )

            except Exception as e:
                logger.error(f"Exception in analyze_job: {e}")
                status = f"Error: {e}"
                return (
                    f"Error analyzing job description: {str(e)}", 
                    status, 
                    gr.update(interactive=True), 
                    gr.update(interactive=False, visible=False), 
                    gr.update(), 
                    0, 
                    "", 
                    gr.update(interactive=False),
                    status
                )

        def add_to_application_tracker(job_url, company, position, location, job_desc, match_score):
            """Add the analyzed job to the application tracker."""
            try:
                from workflows.application_workflows import ApplicationWorkflows
                
                app_manager = ApplicationWorkflows()
                
                app_data = {
                    "job_url": job_url.strip() if job_url else "",
                    "company": company.strip() if company else "Unknown Company",
                    "position": position.strip() if position else "Unknown Position", 
                    "location": location.strip() if location else "",
                    "description": job_desc.strip() if job_desc else "",
                    "match_score": int(match_score) if match_score else None,
                    "application_source": "AI Analysis",
                    "status": "Applied",
                    "priority": "Medium",
                    "analysis_data": {
                        "analyzed_date": dt.datetime.now().isoformat(),
                        "ai_extracted": True
                    }
                }
                
                result = app_manager.create_application(app_data)
                
                if result.is_success():
                    app_id = result.data.get("app_id", "unknown")
                    return f"✅ Successfully added to Application Tracker!\nApplication ID: {app_id}", "success"
                else:
                    return f"❌ Failed to add to tracker: {result.get_error_message()}", "error"
                    
            except Exception as e:
                logger.error(f"Error adding to application tracker: {e}")
                return f"❌ Error adding to Application Tracker: {str(e)}", "error"

        def tailor_resume_fn(job_desc, user_prompt_text, resume_data, model, job_details):
            req_id = uuid.uuid4()
            error_status_markdown = _get_updated_ai_status_markdown("❌ Error")
            if not job_desc.strip():
                return json.dumps({"error": "No job description provided.", "request_id": str(req_id)}), "Error: No job description provided.", job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None, "", 0, ""
            if not resume_data.strip():
                return json.dumps({"error": "No resume data available.", "request_id": str(req_id)}), "Error: No resume data available.", job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None, "", 0, ""

            updated_job_details = job_details or {}
            auto_analysis_markdown = ""
            auto_match_score = 0
            auto_match_summary = ""

            try:
                try:
                    resume_dict = json.loads(resume_data)
                except json.JSONDecodeError:
                    json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                    data, err = resume_helper.resume_gen.import_json(json_path)
                    if data is None:
                        return json.dumps({"error": f"Invalid JSON: {err}", "request_id": str(req_id)}), f"Error: {err}", updated_job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None, "", 0, ""
                    resume_dict = data
                ai_workflows = resume_helper.ai_workflows
                
                result = ai_workflows.tailor_resume(resume_dict, job_desc, model, user_prompt_text, job_analysis_data=job_details if job_details else None)
                
                if isinstance(result, dict) and result.get("success") == False:
                    error_data = {"error": result.get("error", "Unknown error"), "request_id": str(req_id)}
                    return json.dumps(error_data), f"Error: {result.get('error', 'Unknown error')}", updated_job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None, "", 0, ""
                
                if isinstance(result, dict) and result.get("success") == True:
                    try:
                        from infrastructure.providers.cost_tracker import track_llm_operation
                        track_llm_operation(
                            resume_helper.resume_gen.temp_dir,
                            result,
                            model or "unknown",
                            "tailor_resume"
                        )
                    except Exception as cost_error:
                        logger.warning(f"Cost tracking failed: {cost_error}")
                    tailored_resume = result.get("tailored_resume", {})
                    updated_job_details = dict(job_details)
                    updated_job_details["company_name"] = tailored_resume.get("company_name", job_details.get("company_name", ""))
                    updated_job_details["job_position"] = tailored_resume.get("job_position", job_details.get("job_position", ""))
                    import datetime
                    current_time = datetime.datetime.now().isoformat()
                    original_metadata = resume_dict.get("metadata", {})
                    tailored_resume["metadata"] = {
                        "version": original_metadata.get("version", "1.0"),
                        "created_at": original_metadata.get("created_at", current_time),
                        "last_updated": current_time,
                        "tailored_at": current_time,
                        "tailored_for": {
                            "company": updated_job_details.get("company_name", ""),
                            "position": updated_job_details.get("job_position", ""),
                            "job_url": job_details.get("job_url", ""),
                            "request_id": str(req_id)
                        },
                        "source": "ai_resume_helper",
                        "app_compatible": True,
                        "resume_helper_version": "1.0"
                    }
                    tailored_resume["request_id"] = str(req_id)
                    tailored_json = json.dumps(tailored_resume, indent=2)
                    try:
                        temp_dir = resume_helper.resume_gen.temp_dir
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        company = updated_job_details.get("company_name", "") or "company"
                        timestamp = dt.datetime.now().strftime("%Y%m%d")
                        filename = f"{_slug(company)}_resume_{timestamp}.pdf"
                        pdf_path = os.path.join(temp_dir, filename)
                        
                        ok = resume_helper.resume_gen.generate_pdf(tailored_resume, pdf_path)
                        if ok and os.path.exists(pdf_path):
                            try:
                                import pypdf
                                from pypdf import PdfWriter, PdfReader
                                with open(pdf_path, 'rb') as file:
                                    pdf_reader = PdfReader(file)
                                    pdf_writer = PdfWriter()
                                    
                                    for page in pdf_reader.pages:
                                        pdf_writer.add_page(page)
                                    
                                    metadata = pdf_reader.metadata or {}
                                    metadata.update({
                                        '/ResumeData': json.dumps(tailored_resume),
                                        '/Creator': 'Resume Helper App - AI Resume Helper',
                                        '/ResumeHelperVersion': '1.0',
                                        '/AIGenerated': 'true',
                                        '/Source': 'ai_resume_helper'
                                    })
                                    pdf_writer.add_metadata(metadata)
                                    
                                    with open(pdf_path, 'wb') as output_file:
                                        pdf_writer.write(output_file)
                                        
                                logger.info(f"✅ PDF metadata embedded successfully for AI-generated resume")
                                        
                            except ImportError:
                                logger.warning("⚠️ pypdf not available - PDF metadata embedding skipped")
                            except Exception as e:
                                logger.error(f"❌ PDF metadata embedding failed: {e}")
                        
                        simple_status = "Resume tailored successfully!"
                        if ok and os.path.exists(pdf_path):
                            simple_status += " PDF ready for download."
                            pdf_update = gr.update(interactive=True, value=pdf_path, visible=True)
                        else:
                            simple_status += " (PDF generation failed)"
                            pdf_update = gr.update(interactive=False, visible=False)
                        updated_status_markdown = _get_updated_ai_status_markdown()
                        
                        return tailored_json, simple_status, updated_job_details, gr.update(interactive=False), pdf_update, updated_status_markdown, pdf_path if ok and os.path.exists(pdf_path) else None, auto_analysis_markdown, auto_match_score, auto_match_summary
                    
                    except Exception as pdf_error:
                        logger.error(f"PDF generation error: {pdf_error}")
                        simple_status = "Resume tailored successfully! (PDF generation failed)"
                        updated_status_markdown = _get_updated_ai_status_markdown("⚠️ PDF Error")
                        return tailored_json, simple_status, updated_job_details, gr.update(interactive=False), gr.update(interactive=False, visible=False), updated_status_markdown, None, auto_analysis_markdown, auto_match_score, auto_match_summary
                logger.error(f"Unexpected tailor_resume result format: {result}")
                error_data = {"error": "Unexpected response format", "request_id": str(req_id)}
                return json.dumps(error_data), "Error: Unexpected response format", updated_job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None, "", 0, ""
            except Exception as e:
                logger.error(f"Exception in tailor_resume_fn: {e}")
                return json.dumps({"error": str(e), "request_id": str(req_id)}), f"Error: {e}", updated_job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None, "", 0, ""

        def generate_cover_letter_fn(job_desc, user_prompt_text, resume_data, model, job_details):
            req_id = uuid.uuid4()
            error_status_markdown = _get_updated_ai_status_markdown("❌ Error")
            if not job_desc.strip():
                return "Please enter a job description.", "Error: No job description provided.", job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
            if not resume_data.strip():
                return "Please ensure resume data is loaded.", "Error: No resume data available.", job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
            
            try:
                resume_dict = json.loads(resume_data)
            except json.JSONDecodeError:
                json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                data, err = resume_helper.resume_gen.import_json(json_path)
                if data is None:
                    return "Please ensure resume data is loaded.", f"Error: Invalid JSON and failed to read: {err}", job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
                resume_dict = data
            ai_workflows = resume_helper.ai_workflows
            
            result = ai_workflows.generate_cover_letter(
                resume_dict, 
                job_desc, 
                model, 
                user_prompt_text,
                job_analysis_data=job_details if job_details else None
            )
            if isinstance(result, dict) and "body_content" in result:
                if result["body_content"].startswith("Error"):
                    return "Error generating cover letter.", result["body_content"], job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
                try:
                    from infrastructure.providers.cost_tracker import track_llm_operation
                    track_llm_operation(
                        resume_helper.resume_gen.temp_dir,
                        result,
                        model or "unknown",
                        "cover_letter"
                    )
                except Exception as cost_error:
                    logger.warning(f"Cost tracking failed: {cost_error}")
                
                updated_details = {
                    "company_name": result.get("company_name", job_details.get("company_name", "")),
                    "job_position": result.get("job_position", job_details.get("job_position", "")),
                    "letter_title": result.get("letter_title", job_details.get("letter_title", "")),
                    "recipient_greeting": result.get("recipient_greeting", job_details.get("recipient_greeting", "")),
                    "request_id": str(req_id),
                }
                try:
                    from infrastructure.generators.cover_letter_generator import generate_cover_letter_pdf
                    temp_dir = resume_helper.resume_gen.temp_dir
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    company = updated_details.get("company_name", "") or "company"
                    timestamp = dt.datetime.now().strftime("%Y%m%d")
                    filename = f"{_slug(company)}_cover_letter_{timestamp}.pdf"
                    pdf_path = os.path.join(temp_dir, filename)
                    logger.info(f"Cover letter PDF generation debug:")
                    logger.info(f"  - temp_dir: {temp_dir}")
                    logger.info(f"  - filename: {filename}")
                    logger.info(f"  - pdf_path: {pdf_path}")
                    logger.info(f"  - resume_dict keys: {list(resume_dict.keys())}")
                    if 'personal_info' in resume_dict:
                        logger.info(f"  - personal_info keys: {list(resume_dict['personal_info'].keys())}")
                    logger.info(f"  - cover letter content length: {len(result['body_content'])}")
                    
                    pdf_path = generate_cover_letter_pdf(
                        candidate_data=resume_dict,
                        cover_letter_content=result["body_content"],
                        recipient_data={
                            "recipient_name": updated_details.get("recipient_name", ""),
                            "company_name": updated_details.get("company_name", ""),
                            "company_address": updated_details.get("company_address", ""),
                        },
                        output_path=pdf_path,
                        temp_dir=temp_dir,
                        job_position=updated_details.get("job_position", ""),
                        company_name=company,
                        letter_title=updated_details.get("letter_title", ""),
                        recipient_greeting=updated_details.get("recipient_greeting", ""),
                    )
                    
                    if pdf_path and os.path.exists(pdf_path):
                        simple_status = "Cover letter generated successfully! PDF ready."
                        pdf_update = gr.update(interactive=True, value=pdf_path, visible=True)
                    else:
                        error_msg = f"PDF generation failed - Path: {pdf_path}, Exists: {os.path.exists(pdf_path) if pdf_path else 'N/A'}"
                        logger.error(error_msg)
                        simple_status = f"Cover letter generated! (PDF failed: {error_msg})"
                        pdf_update = gr.update(interactive=False, visible=False)

                    updated_status_markdown = _get_updated_ai_status_markdown()
                    return result["body_content"], simple_status, updated_details, gr.update(interactive=False), pdf_update, updated_status_markdown, pdf_path if pdf_path and os.path.exists(pdf_path) else None

                except Exception as pdf_error:
                    error_msg = f"PDF generation error: {pdf_error}"
                    logger.error(error_msg)
                    import traceback
                    traceback.print_exc()
                    simple_status = f"Cover letter generated! (PDF failed: {str(pdf_error)})"
                    updated_status_markdown = _get_updated_ai_status_markdown("⚠️ PDF Error")
                    return result["body_content"], simple_status, updated_details, gr.update(interactive=False), gr.update(interactive=False, visible=False), updated_status_markdown, None
                    
            return "Error: Unexpected response.", "Error generating cover letter.", job_details, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None

        def provide_suggestions_fn(job_desc, resume_data, model, job_details):
            error_status_markdown = _get_updated_ai_status_markdown("❌ Error")
            if not job_desc.strip():
                status = "Error: No job description provided."
                return "Please enter a job description.", status, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
            if not resume_data.strip():
                status = "Error: No resume data available."
                return "Please ensure resume data is loaded.", status, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
            
            try:
                resume_dict = json.loads(resume_data)
            except json.JSONDecodeError:
                json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                data, err = resume_helper.resume_gen.import_json(json_path)
                if data is None:
                    status = f"Error: Invalid JSON and failed to read: {err}"
                    return "Please ensure resume data is loaded.", status, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
                resume_dict = data
            ai_workflows = resume_helper.ai_workflows
            result = ai_workflows.get_improvement_suggestions(resume_dict, job_desc, model, job_analysis_data=job_details if job_details else None)
            suggestions_content = result.get("content", "")
            
            if "error" in suggestions_content.lower():
                status = f"Error providing suggestions: {suggestions_content}"
                return "Error providing suggestions. Check inputs.", status, gr.update(interactive=True), gr.update(interactive=False, visible=False), error_status_markdown, None
            import re
            suggestions_content = re.sub(r'(\n\- .+?)(?=\n[^\-\n])', r'\1\n', suggestions_content, flags=re.DOTALL)
            suggestions_content = re.sub(r'(\n#+ .+)', r'\n\1', suggestions_content)
            suggestions_content = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', suggestions_content)
            try:
                from infrastructure.providers.cost_tracker import track_llm_operation
                track_llm_operation(
                    resume_helper.resume_gen.temp_dir,
                    result,
                    model or "unknown",
                    "suggestions"
                )
            except Exception as cost_error:
                logger.warning(f"Cost tracking failed: {cost_error}")
            try:
                from infrastructure.generators.analysis_pdf_generator import generate_improvement_suggestions_pdf
                temp_dir = resume_helper.resume_gen.temp_dir
                os.makedirs(temp_dir, exist_ok=True)
                
                company = job_details.get("company_name", "") or "company"
                timestamp = dt.datetime.now().strftime("%Y%m%d")
                filename = f"{_slug(company)}_suggestions_{timestamp}.pdf"
                pdf_path = os.path.join(temp_dir, filename)
                
                full_name = resume_dict.get("personal_info", {}).get("full_name", "")
                pdf_path = generate_improvement_suggestions_pdf(
                    suggestions_content=suggestions_content,
                    full_name=full_name,
                    company_name=company,
                    job_position=job_details.get("job_position", ""),
                    output_path=pdf_path,
                    temp_dir=temp_dir
                )
                
                if pdf_path and os.path.exists(pdf_path):
                    simple_status = "Improvement suggestions generated! PDF ready."
                    updated_status_markdown = _get_updated_ai_status_markdown()
                    return suggestions_content, simple_status, gr.update(interactive=False), gr.update(interactive=True, value=pdf_path, visible=True), updated_status_markdown, pdf_path
                else:
                    simple_status = "Improvement suggestions generated! (PDF generation failed)"
                    updated_status_markdown = _get_updated_ai_status_markdown("⚠️ PDF Error")
                    return suggestions_content, simple_status, gr.update(interactive=False), gr.update(interactive=False, visible=False), updated_status_markdown, None
            except Exception as pdf_error:
                logger.error(f"PDF generation error: {pdf_error}")
                simple_status = f"Suggestions generated! (PDF failed: {str(pdf_error)})"
                updated_status_markdown = _get_updated_ai_status_markdown("⚠️ PDF Error")
                return suggestions_content, simple_status, gr.update(interactive=False), gr.update(interactive=False, visible=False), updated_status_markdown, None

        def _slug(text: str, default: str = "document") -> str:
            """Convert arbitrary text to filesystem-safe slug."""
            text = re.sub(r"[^A-Za-z0-9]+", "_", text or "")
            return text.strip("_").lower() or default

        def validate_inputs_for_analysis(job_desc, resume_data):
            """Validate that both job description and resume data are present and valid. Returns (is_valid, error_message)."""
            if not job_desc or not job_desc.strip():
                return False, "Please enter a job description to analyze."
            
            try:
                resume_dict = json.loads(resume_data)
                
                critical_fields = ['full_name', 'email', 'phone']
                for field in critical_fields:
                    value = resume_dict.get(field)
                    if value and value != "null" and str(value).strip():
                        return True, ""
                
                return False, "Resume data is incomplete. Please add your name, email, or phone to your resume."
                
            except (json.JSONDecodeError, AttributeError):
                return False, "Resume data is incomplete. Please add your name, email, or phone to your resume."

        def check_analyze_button_state(job_desc, resume_data):
            """Enable Analyze Job button only if both job description and resume data exist with valid content."""
            is_valid, _ = validate_inputs_for_analysis(job_desc, resume_data)
            return gr.update(interactive=is_valid)

        def reset_all():
            return (
                gr.update(value="", interactive=True),  # job_description
                "",  # job_analysis
                "",  # tailored_resume
                "",  # cover_letter
                "",  # suggestions
                "",  # ai_status
                gr.update(interactive=False, visible=False),  # resume_pdf_output
                gr.update(value=""),  # job_url_input
                0,  # match_score_display
                gr.update(interactive=False),  # add_to_tracker_btn
                gr.update(interactive=False),  # analyze_btn (disabled since fields will be empty)
                gr.update(interactive=False),  # tailor_btn
                gr.update(interactive=False),  # cover_letter_btn
                gr.update(interactive=False)  # suggestions_btn
            )

        def smart_pdf_handler(tailored_json, cover_letter_text, resume_json_str, job_details, job_analysis_text, suggestions_text, selected_tab_index):
            """Automatically detect what content is available and generate the appropriate PDF based on selected tab."""
            req_id = uuid.uuid4()
            temp_dir = resume_helper.resume_gen.temp_dir
            os.makedirs(temp_dir, exist_ok=True)
            has_tailored_resume = tailored_json and tailored_json.strip() and tailored_json != "{}"
            has_cover_letter = cover_letter_text and cover_letter_text.strip()
            has_job_analysis = job_analysis_text and job_analysis_text.strip()
            has_suggestions = suggestions_text and suggestions_text.strip()
            tab_to_type = {
                0: "job_analysis",                1: "resume",                2: "cover_letter",                3: "suggestions"            }
            
            content_available = {
                "job_analysis": has_job_analysis,
                "resume": has_tailored_resume,
                "cover_letter": has_cover_letter,
                "suggestions": has_suggestions
            }
            
            selected_type = tab_to_type[selected_tab_index]
            if content_available[selected_type]:
                pdf_type = selected_type
                status_msg = f"📄 Generated {selected_type.replace('_', ' ')} PDF"
            else:
                return (
                    gr.update(interactive=False, visible=False),
                    f"❌ No {selected_type.replace('_', ' ')} content available - please generate it first using the button above"
                )
            company = job_details.get("company_name", "") or "company"
            suffix = "resume" if pdf_type == "resume" else "cover_letter"
            timestamp = dt.datetime.now().strftime("%Y%m%d")
            filename = f"{_slug(company)}_{suffix}_{timestamp}.pdf"
            pdf_path = os.path.join(temp_dir, filename)

            try:
                if pdf_type == "resume":
                    data = json.loads(tailored_json)
                    ok = resume_helper.resume_gen.generate_pdf(data, pdf_path)
                elif pdf_type == "cover_letter":
                    candidate_info = (
                        json.loads(resume_json_str)
                        if resume_json_str.strip()
                        else {}
                    )                    
                    pdf_path = generate_cover_letter_pdf(
                        candidate_data=candidate_info,
                        cover_letter_content=cover_letter_text,
                        recipient_data={
                            "recipient_name": job_details.get("recipient_name", ""),
                            "company_name": job_details.get("company_name", ""),
                            "company_address": job_details.get("company_address", ""),
                        },
                        output_path=pdf_path,
                        temp_dir=temp_dir,
                        job_position=job_details.get("job_position", ""),
                        company_name=company,
                        letter_title=job_details.get("letter_title", ""),
                        recipient_greeting=job_details.get("recipient_greeting", ""),
                    )
                    ok = pdf_path and os.path.exists(pdf_path)
                elif pdf_type == "job_analysis":
                    from Resume_Helper.generators.analysis_pdf_generator import generate_job_analysis_pdf
                    pdf_path = generate_job_analysis_pdf(
                        analysis_content=job_analysis_text,
                        company_name=job_details.get("company_name", ""),
                        job_position=job_details.get("job_position", ""),
                        output_path=pdf_path,
                        temp_dir=temp_dir
                    )
                    ok = bool(pdf_path and os.path.exists(pdf_path))
                elif pdf_type == "suggestions":
                    from Resume_Helper.generators.analysis_pdf_generator import generate_improvement_suggestions_pdf
                    candidate_info = (
                        json.loads(resume_json_str)
                        if resume_json_str.strip()
                        else {}
                    )
                    full_name = candidate_info.get("personal_info", {}).get("full_name", "")
                    pdf_path = generate_improvement_suggestions_pdf(
                        suggestions_content=suggestions_text,
                        full_name=full_name,
                        company_name=job_details.get("company_name", ""),
                        job_position=job_details.get("job_position", ""),
                        output_path=pdf_path,
                        temp_dir=temp_dir
                    )
                    ok = bool(pdf_path and os.path.exists(pdf_path))

                if ok and pdf_path and os.path.exists(pdf_path):
                    return (
                        gr.update(interactive=True, value=pdf_path, visible=True),
                        f"✅ {status_msg}"
                    )
                return (
                    gr.update(interactive=False, visible=False),
                    "❌ Error: PDF was not generated"
                )
            except Exception as e:
                return (
                    gr.update(interactive=False, visible=False),
                    f"❌ Error generating PDF: {e}"
                )

        def update_resume_json(name_prefix, email, name, phone, current_address, location, citizenship,
                               linkedin_url, github_url, portfolio_url, summary,
                               edu_table, experience_table, skill_table, project_table, certifications_table, others_data=None):
            req_id = uuid.uuid4()
            try:
                profile = resume_helper.build_profile_dict(
                    name_prefix, email, name, phone, current_address, location, citizenship,
                    linkedin_url, github_url, portfolio_url, summary,
                    edu_table, experience_table, skill_table, project_table, certifications_table,
                    others_data
                )
                out_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                ok, err = resume_helper.resume_gen.export_json(profile, out_path)
                if not ok:
                    return f"Error exporting JSON: {err}"
                data, err = resume_helper.resume_gen.import_json(out_path)
                if data is None:
                    return f"Error reading JSON: {err}"
                return json.dumps(data, indent=2)
            except Exception as e:
                return f"Error: {e}"

        def on_provider_change(provider_ui_value):
            """Handle provider selection change and save immediately."""
            try:
                # Load saved base URL - use provider-specific environment variable
                base_url_env_var = get_base_url_env_var(provider_ui_value)
                saved_base_url = load_env_var(base_url_env_var, "")
                
                # Pass base_url to update_model_choices
                models_result = update_model_choices(provider_ui_value, saved_base_url, None)
                provider_mapping = {
                    "OpenAI": "openai",
                    "Anthropic (Claude)": "anthropic", 
                    "Google (Gemini)": "google",
                    "Ollama (Local)": "ollama",
                    "Groq (High-Speed)": "groq",
                    "Perplexity (Search)": "perplexity",
                    "xAI (Grok)": "xai",
                    "llama.cpp": "llamacpp",
                    "LM Studio": "lmstudio",
                    "Lemonade": "lemonade"
                }
                internal_provider = provider_mapping.get(provider_ui_value, "openai")
                env_key = f"{internal_provider.upper()}_API_KEY"
                saved_key = load_env_var(env_key, "")
                
                save_env_var("RESUME_HELPER_LAST_PROVIDER", provider_ui_value)
                
                # Auto-configure default base URLs in background (hidden from user)
                is_local_provider = provider_ui_value in ["llama.cpp", "LM Studio", "Ollama (Local)", "Lemonade"]
                
                # Auto-fill default base URLs silently
                default_base_urls = {
                    "llama.cpp": "http://localhost:8080/v1",
                    "LM Studio": "http://localhost:1234/v1",
                    "Lemonade": "http://localhost:8000/api/v1",
                    "Ollama (Local)": "http://localhost:11434"
                }
                
                # Load saved base URL or use default
                if provider_ui_value in ["llama.cpp", "LM Studio", "Lemonade", "Ollama (Local)"] and not saved_base_url:
                    saved_base_url = default_base_urls.get(provider_ui_value, "")
                    # Auto-save the default silently to provider-specific env var
                    if saved_base_url:
                        save_env_var(base_url_env_var, saved_base_url)
                
                # Update base_url_input with the provider-specific value
                return (
                    models_result[0],  # model_selector update
                    gr.update(value=saved_key),  # api_key_input update
                    gr.update(value=saved_base_url),  # base_url_input update - always update with provider-specific URL
                    gr.update(visible=is_local_provider)  # refresh_models_btn visibility
                )
            except Exception as e:
                return gr.update(), gr.update(), gr.update(), gr.update()
        
        def set_ai_configuration(provider_ui_value, api_key, model, base_url):
            """Set AI configuration and update current AI status."""
            try:
                provider_mapping = {
                    "OpenAI": "openai",
                    "Anthropic (Claude)": "anthropic", 
                    "Google (Gemini)": "google",
                    "Ollama (Local)": "ollama",
                    "Groq (High-Speed)": "groq",
                    "Perplexity (Search)": "perplexity",
                    "xAI (Grok)": "xai",
                    "llama.cpp": "llamacpp",
                    "LM Studio": "lmstudio",
                    "Lemonade": "lemonade"
                }
                internal_provider = provider_mapping.get(provider_ui_value, "openai")
                # All local providers use the same dummy key format
                if internal_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
                    save_env_var(f"{internal_provider.upper()}_API_KEY", "sk-no-key-required")
                    if base_url:
                        # Save to provider-specific environment variable
                        base_url_env_var = f"{internal_provider.upper()}_API_BASE"
                        save_env_var(base_url_env_var, base_url)
                elif api_key.strip():
                    env_key = f"{internal_provider.upper()}_API_KEY"
                    save_env_var(env_key, api_key)
                
                save_env_var("RESUME_HELPER_LAST_PROVIDER", provider_ui_value)
                if model:
                    save_env_var("RESUME_HELPER_LAST_MODEL", model)
                resume_helper.switch_to_litellm_provider(
                    provider=internal_provider,
                    model=model,
                    api_key=api_key if api_key.strip() else None
                )
                resume_helper.litellm_provider.custom_base_url = base_url
                if base_url and internal_provider in ["llamacpp", "lmstudio", "lemonade"]:
                    resume_helper.litellm_provider._set_base_url(base_url)
                
                from Resume_Helper.workflows.resume_workflows import ResumeAIWorkflows
                resume_helper.ai_workflows = ResumeAIWorkflows(resume_helper.get_litellm_provider())
                test_result = test_api_connection(provider_ui_value, api_key, model, base_url, None)
                current_model_display = model if model else "Default"
                if "success" in test_result[0].lower() or "valid" in test_result[0].lower():
                    status_text = "✅ Ready"
                else:
                    status_text = "⚠️ Setup needed"
                try:
                    cost_display = get_cost_display(resume_helper.resume_gen.temp_dir)
                except:
                    cost_display = "Total Cost: $0.000000"
                
                current_ai_display = f"**Current AI:** {provider_ui_value} • {current_model_display} • {status_text} • {cost_display}"
                
                return gr.update(value=current_ai_display)
                
            except Exception as e:
                logger.error(f"Failed to set AI configuration: {str(e)}", exc_info=True)
                current_ai_display = f"**Current AI:** {provider_ui_value} • Error • ❌ Failed: {str(e)}"
                return gr.update(value=current_ai_display)

        def update_litellm_packages():
            """Update LiteLLM package only to avoid conflicts."""
            try:
                from infrastructure.providers.auto_updater import force_update_litellm
                yield "🔄 Updating LiteLLM..."
                result = force_update_litellm()
                yield result
                
            except ImportError:
                yield "❌ Auto-updater module not found"
            except Exception as e:
                yield f"❌ Update failed: {str(e)}"
              
        def on_model_change(model):
            """Save model immediately when selected."""
            if model:
                save_env_var("RESUME_HELPER_LAST_MODEL", model)
        
        provider_selector.change(
            fn=on_provider_change,
            inputs=[provider_selector],
            outputs=[model_selector, api_key_input, base_url_input, refresh_models_btn],
        )
        
        # Refresh models button handler
        def refresh_local_models(provider_ui_value, base_url):
            """Refresh the list of models from local AI servers."""
            try:
                # Load saved base URL if not provided in input - use provider-specific env var
                if not base_url:
                    base_url_env_var = get_base_url_env_var(provider_ui_value)
                    base_url = load_env_var(base_url_env_var, "")
                
                models_result = update_model_choices(provider_ui_value, base_url, None)
                return models_result[0]  # Return model_selector update
            except Exception as e:
                logger.error(f"Error refreshing models: {e}")
                return gr.update()
        
        refresh_models_btn.click(
            fn=refresh_local_models,
            inputs=[provider_selector, base_url_input],
            outputs=[model_selector]
        )
        
        model_selector.change(
            fn=on_model_change,
            inputs=[model_selector],
            outputs=[]
        )

        set_btn.click(
            fn=set_ai_configuration,
            inputs=[provider_selector, api_key_input, model_selector, base_url_input],
            outputs=[current_ai_status],
        )

        update_btn.click(
            fn=update_litellm_packages,
            inputs=[],
            outputs=[ai_status],
        )
        
        job_description.change(
            fn=check_analyze_button_state,
            inputs=[job_description, resume_json],
            outputs=[analyze_btn],
        )
        
        resume_json.change(
            fn=check_analyze_button_state,
            inputs=[job_description, resume_json],
            outputs=[analyze_btn],
        )
        def analyze_job_with_lock(jd, m, js, resume_data):
            """Locks inputs and buttons, runs analysis, then yields final (unlocked) state."""
            yield (
                "🔄 **Starting job analysis...**\n\n*This may take 15-30 seconds depending on job description complexity.*",
                "🔄 Analyzing job description...",
                gr.update(interactive=False),
                gr.update(interactive=False, visible=False),
                gr.update(interactive=False),
                0,
                "*Analysis in progress...*",
                gr.update(interactive=False),
                gr.update(),  # Keep current_ai_status unchanged during processing
                None,
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False)
            )
            
            final_result = list(analyze_job(jd, m, js, resume_data))
            
            final_result[2] = gr.update(interactive=False)
            if len(final_result) > 4:
                if isinstance(final_result[4], dict) and 'interactive' in final_result[4]:
                    final_result[4]['interactive'] = False
                else:
                    final_result[4] = gr.update(interactive=False)
            
            final_result.extend([
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            ])
            
            yield tuple(final_result)

        def tailor_resume_with_lock(jd, up, res, m, js):
            """Locks inputs and buttons, runs tailoring, then yields final (unlocked) state."""
            yield (
                "🔄 **Analyzing your resume against job requirements...**\n\n*Generating personalized recommendations (30-45 seconds)*",
                "🔄 Tailoring resume...",
                js,
                gr.update(interactive=False),
                gr.update(interactive=False, visible=False),
                gr.update(),  # Keep current_ai_status unchanged during processing
                None,
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(),  # Preserve job_analysis
                gr.update(),  # Preserve match_score_display
                gr.update()   # Preserve match_score_summary
            )
            
            result = list(tailor_resume_fn(jd, up, res, m, js))
            
            final_result = [
                result[0],
                result[1],
                result[2],
                gr.update(interactive=False),
                result[4],
                result[5],
                result[6],
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
                result[7] if result[7] else gr.update(),
                result[8] if result[8] else gr.update(),
                result[9] if result[9] else gr.update(),
            ]
            
            yield tuple(final_result)

        def generate_cover_letter_with_lock(jd, up, res, m, js):
            """Locks inputs and buttons, generates cover letter, then yields final (unlocked) state."""
            yield (
                "🔄 **Creating personalized cover letter...**\n\n*Matching your experience to job requirements (20-40 seconds)*",
                "🔄 Generating cover letter...",
                js,
                gr.update(interactive=False),
                gr.update(interactive=False, visible=False),
                gr.update(),  # Keep current_ai_status unchanged during processing
                None,
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False)
            )
            
            result = list(generate_cover_letter_fn(jd, up, res, m, js))
            
            final_result = [
                result[0],
                result[1],
                result[2],
                gr.update(interactive=False),
                result[4],
                result[5],
                result[6],
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
            ]
            
            yield tuple(final_result)

        def provide_suggestions_with_lock(jd, res, m, js):
            """Locks inputs and buttons, generates suggestions, then yields final (unlocked) state."""
            yield (
                "🔄 **Analyzing resume for improvements...**\n\n*Generating detailed recommendations (25-35 seconds)*",
                "🔄 Generating suggestions...",
                gr.update(interactive=False),
                gr.update(interactive=False, visible=False),
                gr.update(),  # Keep current_ai_status unchanged during processing
                None,
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False)
            )
            
            result = list(provide_suggestions_fn(jd, res, m, js))
            
            final_result = [
                result[0],
                result[1],
                gr.update(interactive=False),
                result[3],
                result[4],
                result[5],
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
            ]
            
            yield tuple(final_result)
        
        analyze_btn.click(
            fn=analyze_job_with_lock,
            inputs=[job_description, model_selector, job_details_state, resume_json],
            outputs=[
                job_analysis, ai_status, job_description, resume_pdf_output, job_url_input,
                match_score_display, match_score_summary, add_to_tracker_btn, current_ai_status,
                job_analysis_pdf_state,
                analyze_btn, tailor_btn, cover_letter_btn, suggestions_btn
            ],
        )
        
        def reset_job_analysis():
            """Clears all job analysis fields and makes them interactive again."""
            return (
                "",  # job_analysis
                "Ready for new analysis.",  # ai_status
                gr.update(value="", interactive=True),  # job_description
                gr.update(value="", interactive=True),  # job_url_input
                gr.update(value=None, visible=False, interactive=False),  # resume_pdf_output
                0,  # match_score_display
                "*Summary will appear here after analysis.*",  # match_score_summary
                gr.update(interactive=False),  # add_to_tracker_btn
                {},  # job_details_state
                gr.update(interactive=False),  # analyze_btn (will be re-enabled by change handler if fields have content)
                gr.update(interactive=False),  # tailor_btn
                gr.update(interactive=False),  # cover_letter_btn
                gr.update(interactive=False)  # suggestions_btn
            )

        reset_btn.click(
            fn=reset_job_analysis,
            inputs=[],
            outputs=[
                job_analysis, ai_status, job_description, job_url_input, 
                resume_pdf_output, match_score_display, match_score_summary, 
                add_to_tracker_btn, job_details_state,
                analyze_btn, tailor_btn, cover_letter_btn, suggestions_btn
            ]
        )
        
        tailor_btn.click(
            fn=tailor_resume_with_lock,
            inputs=[job_description, user_prompt, resume_json, model_selector, job_details_state],
            outputs=[
                tailored_resume, ai_status, job_details_state, job_description, resume_pdf_output,
                current_ai_status, tailored_resume_pdf_state,
                analyze_btn, tailor_btn, cover_letter_btn, suggestions_btn,
                job_analysis, match_score_display, match_score_summary
            ],
        )
        
        cover_letter_btn.click(
            fn=generate_cover_letter_with_lock,
            inputs=[job_description, user_prompt, resume_json, model_selector, job_details_state],
            outputs=[
                cover_letter, ai_status, job_details_state, job_description, resume_pdf_output,
                current_ai_status, cover_letter_pdf_state,
                analyze_btn, tailor_btn, cover_letter_btn, suggestions_btn
            ],
        )
        
        suggestions_btn.click(
            fn=provide_suggestions_with_lock,
            inputs=[job_description, resume_json, model_selector, job_details_state],
            outputs=[
                suggestions, ai_status, job_description, resume_pdf_output, current_ai_status,
                suggestions_pdf_state,
                analyze_btn, tailor_btn, cover_letter_btn, suggestions_btn
            ],
        )

        def handle_add_to_tracker(job_url, job_desc, match_score, job_details):
            """Handle adding the job to application tracker using job URL as unique key."""
            if not job_url or not job_url.strip():
                return "❌ Error: Job URL is required to prevent duplicates. Please enter the job URL above.", gr.update(interactive=True)
            
            company = job_details.get("company_name", "Unknown Company")
            position = job_details.get("position_title", "Unknown Position")
            location = job_details.get("location", "")
            
            logger.info(f"Adding application with Job URL key: {job_url}")
            
            result, status = add_to_application_tracker(job_url, company, position, location, job_desc, match_score)
            
            if "Successfully added" in result:
                result += f"\n🔑 Job URL used as unique key: {job_url[:50]}{'...' if len(job_url) > 50 else ''}"
            
            return result, gr.update()
        
        add_to_tracker_btn.click(
            fn=handle_add_to_tracker,
            inputs=[job_url_input, job_analysis, match_score_display, job_details_state],
            outputs=[ai_status, job_url_input],
        )

        reset_btn.click(
            fn=reset_all,
            inputs=None,
            outputs=[
                job_description, job_analysis, tailored_resume, cover_letter, suggestions, ai_status, 
                resume_pdf_output, job_url_input, match_score_display, add_to_tracker_btn,
                analyze_btn, tailor_btn, cover_letter_btn, suggestions_btn
            ],
        )

        def update_download_for_tab(tab_index, job_pdf, resume_pdf, letter_pdf, sugg_pdf):
            """Update the download button to show the PDF for the selected tab."""
            pdf_map = {
                0: job_pdf,
                1: resume_pdf,
                2: letter_pdf,
                3: sugg_pdf
            }
            selected_pdf = pdf_map.get(tab_index)
            
            if selected_pdf and selected_pdf != "":
                return tab_index, gr.update(value=selected_pdf, visible=True, interactive=True)
            else:
                return tab_index, gr.update(value=None, visible=False, interactive=False)
        
        job_analysis_tab.select(
            fn=lambda j, r, l, s: update_download_for_tab(0, j, r, l, s),
            inputs=[job_analysis_pdf_state, tailored_resume_pdf_state, cover_letter_pdf_state, suggestions_pdf_state],
            outputs=[selected_tab_state, resume_pdf_output]
        )
        tailored_resume_tab.select(
            fn=lambda j, r, l, s: update_download_for_tab(1, j, r, l, s),
            inputs=[job_analysis_pdf_state, tailored_resume_pdf_state, cover_letter_pdf_state, suggestions_pdf_state],
            outputs=[selected_tab_state, resume_pdf_output]
        )
        cover_letter_tab.select(
            fn=lambda j, r, l, s: update_download_for_tab(2, j, r, l, s),
            inputs=[job_analysis_pdf_state, tailored_resume_pdf_state, cover_letter_pdf_state, suggestions_pdf_state],
            outputs=[selected_tab_state, resume_pdf_output]
        )
        suggestions_tab.select(
            fn=lambda j, r, l, s: update_download_for_tab(3, j, r, l, s),
            inputs=[job_analysis_pdf_state, tailored_resume_pdf_state, cover_letter_pdf_state, suggestions_pdf_state],
            outputs=[selected_tab_state, resume_pdf_output]
        )

        if all_tabs_components:
            personal_tab       = all_tabs_components.get("personal_info_tab", {})
            education_tab      = all_tabs_components.get("educations_tab", {})
            work_tab           = all_tabs_components.get("experiences_tab", {})
            skills_tab         = all_tabs_components.get("skills_tab", {})
            projects_tab       = all_tabs_components.get("projects_tab", {})
            certifications_tab = all_tabs_components.get("certifications_tab", {})

            def has_valid_imported_data(json_text):
                """Check if JSON contains valid imported data (not null values)."""
                if not json_text or not json_text.strip():
                    return False
                try:
                    data = json.loads(json_text)
                    if not isinstance(data, dict):
                        return False
                    key_fields = ['full_name', 'email', 'phone']
                    for field in key_fields:
                        value = data.get(field)
                        if value and value != "null" and str(value).strip():
                            return True
                    return False
                except Exception:
                    return False
            
            def form_fields_are_mostly_empty():
                """Check if form fields are mostly empty (indicating data came from import)."""
                try:
                    personal_fields = [
                        personal_tab.get("name_input").value if personal_tab.get("name_input") else "",
                        personal_tab.get("email_input").value if personal_tab.get("email_input") else "",
                        personal_tab.get("phone_input").value if personal_tab.get("phone_input") else "",
                    ]
                    for field in personal_fields:
                        if field and str(field).strip():
                            return False
                    tables = [
                        education_tab.get("edu_list").value if education_tab.get("edu_list") else [],
                        work_tab.get("work_list").value if work_tab.get("work_list") else [],
                        skills_tab.get("skill_list").value if skills_tab.get("skill_list") else [],
                    ]
                    
                    for table in tables:
                        if table and len(table) > 0:
                            return False
                    
                    return True
                except Exception:
                    return True
            
            def load_current_json():
                """Smart auto-update: preserve imported data, auto-update from form changes."""
                try:
                    import_cache_path = os.path.join(resume_helper.resume_gen.temp_dir, "last_import.json")
                    if os.path.exists(import_cache_path):
                        try:
                            with open(import_cache_path, 'r', encoding='utf-8') as f:
                                import_data = json.load(f)
                            if has_valid_imported_data(json.dumps(import_data)):
                                try:
                                    temp_json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                                    with open(temp_json_path, 'w', encoding='utf-8') as temp_f:
                                        json.dump(import_data, temp_f, indent=2)
                                    os.remove(import_cache_path)
                                except:
                                    pass
                                return json.dumps(import_data, indent=2)
                        except Exception:
                            pass
                    json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                    if os.path.exists(json_path):
                        data, err = resume_helper.resume_gen.import_json(json_path)
                        if data is not None:
                            return json.dumps(data, indent=2)
                    others_data = all_tabs_components.get("others_tab", {}).get("sections_data", {}).value if all_tabs_components.get("others_tab", {}).get("sections_data") else None
                    return update_resume_json(
                        personal_tab.get("email_input").value if personal_tab.get("email_input") else "",
                        personal_tab.get("name_input").value if personal_tab.get("name_input") else "",
                        personal_tab.get("phone_input").value if personal_tab.get("phone_input") else "",
                        personal_tab.get("current_address").value if personal_tab.get("current_address") else "",
                        personal_tab.get("location_input").value if personal_tab.get("location_input") else "",
                        personal_tab.get("citizenship").value if personal_tab.get("citizenship") else "",
                        personal_tab.get("linkedin_input").value if personal_tab.get("linkedin_input") else "",
                        personal_tab.get("github_input").value if personal_tab.get("github_input") else "",
                        personal_tab.get("portfolio_input").value if personal_tab.get("portfolio_input") else "",
                        personal_tab.get("summary_input").value if personal_tab.get("summary_input") else "",
                        education_tab.get("edu_list").value if education_tab.get("edu_list") else [],
                        work_tab.get("work_list").value if work_tab.get("work_list") else [],
                        skills_tab.get("skill_list").value if skills_tab.get("skill_list") else [],
                        projects_tab.get("project_list").value if projects_tab.get("project_list") else [],
                        certifications_tab.get("cert_list").value if certifications_tab.get("cert_list") else [],
                        others_data
                    )
                except Exception:
                    return update_resume_json("", "", "", "", "", "", "", "", "", "", "", [], [], [], [], [], None)
            from models.resume import ResumeSchema
            personal_field_order = ResumeSchema.get_field_order('personal_info')
            schema_to_ui_map = {
                'name_prefix': 'name_prefix_input',
                'email': 'email_input',
                'full_name': 'name_input',
                'phone': 'phone_input',
                'current_address': 'current_address',
                'location': 'location_input',
                'citizenship': 'citizenship',
                'linkedin_url': 'linkedin_input',
                'github_url': 'github_input',
                'portfolio_url': 'portfolio_input',
                'summary': 'summary_input'
            }
            personal_inputs = []
            for field_name in personal_field_order:
                component_name = schema_to_ui_map.get(field_name)
                if component_name:
                    component = personal_tab.get(component_name)
                    if component is not None:
                        personal_inputs.append(component)
                    else:
                        import logging
                        logging.error(f"ERROR: Component '{component_name}' for field '{field_name}' not found in personal_tab!")
                else:
                    import logging
                    logging.error(f"ERROR: No UI mapping for schema field '{field_name}'")
            update_inputs = personal_inputs + [
                education_tab.get("edu_list"), 
                work_tab.get("work_list"),
                skills_tab.get("skill_list"),  
                projects_tab.get("project_list"),
                certifications_tab.get("cert_list"),
                all_tabs_components.get("others_tab", {}).get("sections_data") if "others_tab" in all_tabs_components else gr.State({})
            ]
            
            update_resume_btn.click(
                fn=update_resume_json,
                inputs=update_inputs,
                outputs=[resume_json],
    )

            tab.select(fn=load_current_json, inputs=None, outputs=resume_json)

            if "generate_resume_tab" in all_tabs_components:
                gen_tab = all_tabs_components["generate_resume_tab"]
                if "gen_json_btn" in gen_tab:
                    gen_json_inputs = personal_inputs + [
                        education_tab.get("edu_list"),
                        work_tab.get("work_list"),
                        skills_tab.get("skill_list"),
                        projects_tab.get("project_list"),
                        certifications_tab.get("cert_list"),
                        all_tabs_components.get("others_tab", {}).get("sections_data") if "others_tab" in all_tabs_components else gr.State({})
                    ]
                    
                    gen_tab["gen_json_btn"].click(
                        fn=update_resume_json,
                        inputs=gen_json_inputs,
                        outputs=[resume_json],
                    )

        components_dict = {
            "provider_selector": provider_selector,
            "api_key_input": api_key_input,
            "model_selector": model_selector,
            "set_btn": set_btn,
            "update_btn": update_btn,
            "current_ai_status": current_ai_status,
            "job_description": job_description,
            "resume_json": resume_json,
            "analyze_btn": analyze_btn,
            "tailor_btn": tailor_btn,
            "cover_letter_btn": cover_letter_btn,
            "suggestions_btn": suggestions_btn,
            "job_analysis": job_analysis,
            "tailored_resume": tailored_resume,
            "cover_letter": cover_letter,
            "suggestions": suggestions,
            "ai_status": ai_status,
            "resume_pdf_output": resume_pdf_output,
            "reset_btn": reset_btn,
            "update_resume_json": update_resume_json,
            "load_env_var": load_env_var,
            "save_env_var": save_env_var,
            "job_url_input": job_url_input,
            "match_score_display": match_score_display,
            "add_to_tracker_btn": add_to_tracker_btn,
        }

        class TabWithComponents:
            def __init__(self, tab, components):
                self.tab = tab
                self.components = components

        return TabWithComponents(tab, components_dict)
