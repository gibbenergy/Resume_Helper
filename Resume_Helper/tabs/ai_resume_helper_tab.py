import os
import json
import uuid
import logging
import datetime
import gradio as gr
from gradio import update
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from Resume_Helper.cover_letter_generator import generate_cover_letter_pdf
from Resume_Helper.utils.file_utils import atomic_write_json, atomic_read_json

# ------------------------------------------------------------------#
#  Logging
# ------------------------------------------------------------------#
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------#
#  Main factory
# ------------------------------------------------------------------#
def create_ai_resume_helper_tab(resume_helper, all_tabs_components=None):
    if all_tabs_components is None:
        all_tabs_components = {}

    with gr.Tab("AI Resume Helper") as tab:

        # =========================================================
        #  PROVIDER + API CONFIG
        # =========================================================
        with gr.Group():
            gr.Markdown("### AI Provider & API Configuration")
            with gr.Row():
                provider_selector = gr.Dropdown(
                    label="Provider",
                    choices=["Google Gemini", "OpenAI"],
                    value="OpenAI",
                    scale=1,
                )
                api_key_input = gr.Textbox(
                    label="API Key",
                    placeholder="Enter your API key",
                    type="password",
                    scale=2,
                )
                model_selector = gr.Dropdown(
                    label="Model",
                    choices=resume_helper.get_available_models(),
                    value=(
                        resume_helper.ai_features.OPENAI_DEFAULT_MODEL
                        if resume_helper.get_current_provider() == "openai"
                        else resume_helper.get_available_models()[0]
                    ),
                    scale=1,
                )
                test_key_btn = gr.Button("🧪 Test Key", variant="primary", scale=1)

            api_status = gr.Textbox(label="API Status", interactive=False)

        # =========================================================
        #  INPUTS
        # =========================================================
        with gr.Group():
            gr.Markdown("### Input")

            job_description = gr.Textbox(
                label="Job Description",
                placeholder="Paste the job description here…",
                lines=10,
            )

            with gr.Accordion("➕ Optional User Prompt", open=False):
                user_prompt = gr.Textbox(
                    label="User Prompt",
                    placeholder="e.g. 'Use energetic tone', 'Highlight leadership skills'",
                    lines=3,
                )

            with gr.Accordion("➕Current Resume JSON (auto-loaded)", open=False):
                resume_json = gr.Textbox(
                    label="Current Resume JSON",
                    placeholder="Will be filled automatically",
                    lines=8,
                    interactive=False,
                )
            
            update_resume_btn = gr.Button("🔄 Update Resume", variant="secondary")

        # =========================================================
        #  ACTION BUTTONS
        # =========================================================
        with gr.Row():
            analyze_btn      = gr.Button("🔍 Analyze Job",     variant="primary")
            tailor_btn       = gr.Button("🎯 Tailor Resume",   variant="primary")
            cover_letter_btn = gr.Button("✉️  Cover Letter",   variant="primary")
            suggestions_btn  = gr.Button("💡 Suggestions",     variant="primary")

        # =========================================================
        #  OUTPUT TABS
        # =========================================================
        with gr.Tabs() as output_tabs:
            with gr.TabItem("Job Analysis"):
                job_analysis = gr.Textbox(
                    label="Job Requirements Analysis", lines=15, interactive=True
                )
            with gr.TabItem("Tailored Resume"):
                tailored_resume = gr.Textbox(
                    label="Tailored Resume Content", lines=15, interactive=True
                )
            with gr.TabItem("Cover Letter"):
                cover_letter = gr.Textbox(
                    label="Generated Cover Letter", lines=15, interactive=True
                )
            with gr.TabItem("Improvement Suggestions"):
                suggestions = gr.Textbox(
                    label="Improvement Suggestions", lines=15, interactive=True
                )

        ai_status = gr.Textbox(label="Status", interactive=False)
        
        # Index lookup so we can programmatically switch tabs
        _TAB_INDEX = {
            "Job Analysis": 0,
            "Tailored Resume": 1,
            "Cover Letter": 2,
            "Improvement Suggestions": 3,
        }

        def _tab_update(key: str):
            """Return a gradio.update that selects the correct tab index."""
            return gr.update(selected=_TAB_INDEX[key])
            



        # =========================================================
        #  PDF GENERATION
        # =========================================================
        with gr.Row():
            pdf_type_selector = gr.Radio(
                ["Tailored Resume", "Cover Letter"],
                label="Select PDF Type",
                value="Tailored Resume",
            )
            download_resume_btn = gr.Button("Generate PDF", variant="primary")
            resume_pdf_output   = gr.DownloadButton(
                label="Download PDF", interactive=False, visible=True
            )

        # =========================================================
        #  STATE
        # =========================================================
        job_details_state = gr.State({
            "company_name": "",
            "job_position": "",
            "letter_title": "",
            "recipient_greeting": "",
            "recipient_name": "",
            "company_address": ""
        })

        # ------------------------------------------------------------------
        #  HANDLERS
        # ------------------------------------------------------------------
        def test_api_key(api_key, model):
            """Ping the provider with the supplied key."""
            return resume_helper.ai_features.test_api_key(api_key, model)

        def update_model_choices(provider_ui_value):
            """Switch provider and refresh model list."""
            provider_name = "gemini" if provider_ui_value == "Google Gemini" else "openai"
            result = resume_helper.switch_ai_provider(provider_name)
            models = resume_helper.get_available_models()
            default_model = (
                resume_helper.ai_features.OPENAI_DEFAULT_MODEL
                if provider_name == "openai"
                else models[0] if models else ""
            )
            return gr.update(choices=models, value=default_model), result

        # ---------- content-related helpers -----------------
        def analyze_job(job_desc, model):
            if not job_desc.strip():
                return "Please enter a job description to analyze.", "Error: No job description provided."
            try:
                result = resume_helper.analyze_job_description(job_desc, model)
                if isinstance(result, dict) and "error" in result:
                    return "Error in analysis. Please check API key and try again.", f"Error: {result['error']}"
                formatted = ""
                for k, v in result.items():
                    if k == "error":
                        continue
                    formatted += f"### {k.replace('_',' ').title()}\n"
                    if isinstance(v, list):
                        formatted += "\n".join(f"- {item}" for item in v) + "\n\n"
                    else:
                        formatted += f"{v}\n\n"
                return formatted, "Job analysis completed successfully!"
            except Exception as e:
                return "Error analyzing job description.", f"Error: {e}"

        def tailor_resume_fn(job_desc, resume_data, model):
            req_id = uuid.uuid4()
            if not job_desc.strip():
                return json.dumps({"error": "No job description provided.", "request_id": str(req_id)}), "Error: No job description provided."
            if not resume_data.strip():
                return json.dumps({"error": "No resume data available.", "request_id": str(req_id)}), "Error: No resume data available."

            try:
                try:
                    resume_dict = json.loads(resume_data)
                except json.JSONDecodeError:
                    json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                    data, err = resume_helper.resume_gen.import_json(json_path)
                    if data is None:
                        return json.dumps({"error": f"Invalid JSON: {err}", "request_id": str(req_id)}), f"Error: {err}"
                    resume_dict = data

                result = resume_helper.tailor_resume(resume_dict, job_desc, model)
                if isinstance(result, dict) and "error" in result:
                    result.setdefault("request_id", str(req_id))
                    return json.dumps(result), f"Error: {result['error']}"
                result.setdefault("request_id", str(req_id))
                return json.dumps(result, indent=2), "Resume tailored successfully!"
            except Exception as e:
                return json.dumps({"error": str(e), "request_id": str(req_id)}), f"Error: {e}"

        def generate_cover_letter_fn(job_desc, user_prompt_text, resume_data, model, job_details):
            req_id = uuid.uuid4()
            if not job_desc.strip():
                return "Please enter a job description.", "Error: No job description provided.", job_details
            if not resume_data.strip():
                return "Please ensure resume data is loaded.", "Error: No resume data available.", job_details
            try:
                resume_dict = json.loads(resume_data)
            except json.JSONDecodeError:
                json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                data, err = resume_helper.resume_gen.import_json(json_path)
                if data is None:
                    return "Please ensure resume data is loaded.", f"Error: Invalid JSON and failed to read: {err}", job_details
                resume_dict = data

            result = resume_helper.generate_cover_letter(
                resume_dict, job_desc, model, user_prompt_text
            )
            if isinstance(result, dict) and "body_content" in result:
                if result["body_content"].startswith("Error"):
                    return "Error generating cover letter.", result["body_content"], job_details
                updated_details = {
                    **job_details,
                    "company_name": result.get("company_name", job_details.get("company_name", "")),
                    "job_position": result.get("job_position", job_details.get("job_position", "")),
                    "letter_title": result.get("letter_title", job_details.get("letter_title", "")),
                    "recipient_greeting": result.get("recipient_greeting", job_details.get("recipient_greeting", "")),
                    "request_id": str(req_id),
                }
                return result["body_content"], "Cover letter generated successfully!", updated_details
            return "Error: Unexpected response.", "Error generating cover letter.", job_details

        def provide_suggestions_fn(job_desc, resume_data, model):
            if not job_desc.strip():
                return "Please enter a job description.", "Error: No job description provided."
            if not resume_data.strip():
                return "Please ensure resume data is loaded.", "Error: No resume data available."
            try:
                resume_dict = json.loads(resume_data)
            except json.JSONDecodeError:
                json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                data, err = resume_helper.resume_gen.import_json(json_path)
                if data is None:
                    return "Please ensure resume data is loaded.", f"Error: Invalid JSON and failed to read: {err}"
                resume_dict = data
            result = resume_helper.get_improvement_suggestions(resume_dict, job_desc, model)
            if result.startswith("Error"):
                return "Error providing suggestions. Check inputs.", result
            return result, "Improvement suggestions generated successfully!"

        def download_pdf_handler(pdf_type, tailored_json, cover_letter_text, resume_json_str, job_details):
            req_id = uuid.uuid4()
            temp_dir = resume_helper.resume_gen.temp_dir
            os.makedirs(temp_dir, exist_ok=True)

            try:
                if pdf_type == "Tailored Resume":
                    data = json.loads(tailored_json)
                    pdf_path = os.path.join(temp_dir, "tailored_resume.pdf")
                    ok = resume_helper.resume_gen.generate_pdf(data, pdf_path)
                else:
                    # cover letter
                    candidate_info = (
                        json.loads(resume_json_str)
                        if resume_json_str.strip()
                        else {}
                    )
                    pdf_path = os.path.join(temp_dir, "cover_letter.pdf")
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
                        job_description=job_description.value,
                        job_position=job_details.get("job_position", ""),
                        company_name=job_details.get("company_name", ""),
                        letter_title=job_details.get("letter_title", ""),
                        recipient_greeting=job_details.get("recipient_greeting", ""),
                    )
                    ok = pdf_path and os.path.exists(pdf_path)

                if ok and os.path.exists(pdf_path):
                    return gr.update(interactive=True, value=pdf_path), "PDF generated successfully!"
                return gr.update(interactive=False), "Error: PDF was not generated."
            except Exception as e:
                return gr.update(interactive=False), f"Error generating PDF: {e}"

        # ---------- JSON helper -----------------------------
        def update_resume_json(email, name, phone, address, location, citizenship,
                               linkedin, github, portfolio, summary,
                               edu_table, work_table, skill_table, project_table, cert_table):
            req_id = uuid.uuid4()
            try:
                profile = resume_helper.build_profile_dict(
                    email, name, phone, address, location, citizenship,
                    linkedin, github, portfolio, summary,
                    edu_table, work_table, skill_table, project_table, cert_table,
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

        # ------------------------------------------------------------------
        #  EVENT WIRING
        # ------------------------------------------------------------------      
              
        provider_selector.change(
            fn=update_model_choices,
            inputs=[provider_selector],
            outputs=[model_selector, api_status],
        )

        test_key_btn.click(
            fn=test_api_key,
            inputs=[api_key_input, model_selector],
            outputs=[api_status],
        )

            # 🔍  Analyze Job
        analyze_btn.click(
            fn=lambda jd, m: (
                *analyze_job(jd, m),        # returns (text, status)
                _tab_update("Job Analysis") # third item -> switch tabs
            ),
            inputs=[job_description, model_selector],
            outputs=[job_analysis, ai_status, output_tabs],
        )

        # 🎯  Tailor Resume
        tailor_btn.click(
            fn=lambda jd, res, m: (
                *tailor_resume_fn(jd, res, m),   # (text, status)
                _tab_update("Tailored Resume")   # 3rd
            ),
            inputs=[job_description, resume_json, model_selector],
            outputs=[tailored_resume, ai_status, output_tabs],
        )

        # ✉️  Cover Letter
        cover_letter_btn.click(
            fn=lambda jd, up, res, m, js: (
                *generate_cover_letter_fn(jd, up, res, m, js),  # (text, status, state)
                _tab_update("Cover Letter")                     # 4th
            ),
            inputs=[job_description, user_prompt, resume_json, model_selector, job_details_state],
            outputs=[cover_letter, ai_status, job_details_state, output_tabs],
        )

        # 💡  Suggestions
        suggestions_btn.click(
            fn=lambda jd, res, m: (
                *provide_suggestions_fn(jd, res, m),   # (text, status)
                _tab_update("Improvement Suggestions") # 3rd
            ),
            inputs=[job_description, resume_json, model_selector],
            outputs=[suggestions, ai_status, output_tabs],
        )

        download_resume_btn.click(
            fn=download_pdf_handler,
            inputs=[pdf_type_selector, tailored_resume, cover_letter, resume_json, job_details_state],
            outputs=[resume_pdf_output, ai_status],
        )

        # ------------------------------------------------------------------
        #  OPTIONAL: auto-load JSON when tab opens
        # ------------------------------------------------------------------
        if all_tabs_components:
            personal_tab       = all_tabs_components.get("personal_info_tab", {})
            education_tab      = all_tabs_components.get("educations_tab", {})
            work_tab           = all_tabs_components.get("experiences_tab", {})
            skills_tab         = all_tabs_components.get("skills_tab", {})
            projects_tab       = all_tabs_components.get("projects_tab", {})
            certifications_tab = all_tabs_components.get("certifications_tab", {})

            def load_current_json():
                json_path = os.path.join(resume_helper.resume_gen.temp_dir, "resume.json")
                if os.path.exists(json_path):
                    data, err = resume_helper.resume_gen.import_json(json_path)
                    if data is not None:
                        return json.dumps(data, indent=2)

                # fallback: build from form values
                return update_resume_json(
                    personal_tab.get("email_input").value,
                    personal_tab.get("name_input").value,
                    personal_tab.get("phone_input").value,
                    personal_tab.get("current_address").value,
                    personal_tab.get("location_input").value,
                    personal_tab.get("citizenship").value,
                    personal_tab.get("linkedin_input").value,
                    personal_tab.get("github_input").value,
                    personal_tab.get("portfolio_input").value,
                    personal_tab.get("summary_input").value,
                    education_tab.get("edu_list").value,
                    work_tab.get("work_list").value,
                    skills_tab.get("skill_list").value,
                    projects_tab.get("project_list").value,
                    certifications_tab.get("cert_list").value,
                )
            
            update_resume_btn.click(
                fn=update_resume_json,
                inputs=[
                    # Personal
                    personal_tab.get("email_input"),   personal_tab.get("name_input"),
                    personal_tab.get("phone_input"),   personal_tab.get("current_address"),
                    personal_tab.get("location_input"),personal_tab.get("citizenship"),
                    personal_tab.get("linkedin_input"),personal_tab.get("github_input"),
                    personal_tab.get("portfolio_input"),personal_tab.get("summary_input"),
                    # Tables
                    education_tab.get("edu_list"), work_tab.get("work_list"),
                    skills_tab.get("skill_list"),  projects_tab.get("project_list"),
                    certifications_tab.get("cert_list"),
                ],
                outputs=[resume_json],   # you can also add ai_status here if you wish
    )

            tab.select(fn=load_current_json, inputs=None, outputs=resume_json)

            if "generate_resume_tab" in all_tabs_components:
                gen_tab = all_tabs_components["generate_resume_tab"]
                if "gen_json_btn" in gen_tab:
                    gen_tab["gen_json_btn"].click(
                        fn=update_resume_json,
                        inputs=[
                            personal_tab.get("email_input"),
                            personal_tab.get("name_input"),
                            personal_tab.get("phone_input"),
                            personal_tab.get("current_address"),
                            personal_tab.get("location_input"),
                            personal_tab.get("citizenship"),
                            personal_tab.get("linkedin_input"),
                            personal_tab.get("github_input"),
                            personal_tab.get("portfolio_input"),
                            personal_tab.get("summary_input"),
                            education_tab.get("edu_list"),
                            work_tab.get("work_list"),
                            skills_tab.get("skill_list"),
                            projects_tab.get("project_list"),
                            certifications_tab.get("cert_list"),
                        ],
                        outputs=[resume_json],
                    )

        # ------------------------------------------------------------------
        #  EXPORT
        # ------------------------------------------------------------------
        components_dict = {
            "api_key_input": api_key_input,
            "model_selector": model_selector,
            "test_key_btn": test_key_btn,
            "api_status": api_status,
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
            "pdf_type_selector": pdf_type_selector,
            "download_resume_btn": download_resume_btn,
            "resume_pdf_output": resume_pdf_output,
            "update_resume_json": update_resume_json,
        }

        class TabWithComponents:
            def __init__(self, tab, components):
                self.tab = tab
                self.components = components

        return TabWithComponents(tab, components_dict)
