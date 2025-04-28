from types import SimpleNamespace
import os, json, uuid, logging
import gradio as gr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_generate_resume_tab(resume_helper, all_tabs_components=None):
    if all_tabs_components is None:
        all_tabs_components = {}

    with gr.Tab("Generate Resume") as tab:
        # ------------------------------------------------------
        #  IMPORT PROFILE
        # ------------------------------------------------------
        gr.Markdown("### Import Profile")
        with gr.Row():
            json_file       = gr.File(label="JSON Profile",
                                      file_types=[".json"],
                                      type="filepath")
            load_json_btn   = gr.Button("📂 Load from JSON", variant="primary")

        # ------------------------------------------------------
        #  EXPORT / GENERATE
        # ------------------------------------------------------
        gr.Markdown("### Export / Generate")
        with gr.Row():
            gen_pdf_btn     = gr.Button("📄 Generate PDF",   variant="primary")
            pdf_dl_btn      = gr.DownloadButton("⬇️ Download PDF",
                                                interactive=False, visible=True)

            gen_json_btn    = gr.Button("💾 Generate JSON",  variant="secondary")
            json_dl_btn     = gr.DownloadButton("⬇️ Download JSON",
                                                interactive=False, visible=True)

        # ------------------------------------------------------
        #  OUTPUT AREAS
        # ------------------------------------------------------
        gr.Markdown("### Generated Data")
        json_output   = gr.TextArea(label="JSON Output",   interactive=False)
        status_output = gr.Textbox (label="Status",        interactive=False)

        # ======================================================
        #  HANDLERS
        # ======================================================
        # 1) Load profile from JSON ----------------------------
        def load_json_handler(json_file):
            try:
                profile_vals = resume_helper.load_from_json(json_file.name)
                return profile_vals
            except Exception as e:
                logging.exception("Error loading JSON")
                # return empty placeholders for every bound output component
                return [""] * 45  # adjust length if outputs change

        # 2) Generate PDF resume -------------------------------
        def generate_resume_handler(
            email, name, phone, address, location, citizenship,
            linkedin, github, portfolio, summary,
            edu_table, work_table, skill_table, project_table, cert_table,
        ):
            try:
                profile = resume_helper.build_profile_dict(
                    email, name, phone, address, location, citizenship,
                    linkedin, github, portfolio, summary,
                    edu_table, work_table, skill_table, project_table, cert_table,
                )
                profile.setdefault("full_name", profile.get("name", name))

                # create temp dir & PDF
                temp_dir = resume_helper.resume_gen.temp_dir
                os.makedirs(temp_dir, exist_ok=True)
                pdf_path = os.path.join(temp_dir, "resume.pdf")

                ok = resume_helper.resume_gen.generate_pdf(profile, pdf_path)
                if ok and os.path.exists(pdf_path):
                    size = os.path.getsize(pdf_path)
                    return (
                        json.dumps(profile, indent=2),
                        gr.update(value=os.path.abspath(pdf_path), interactive=True),
                        f"Resume generated ✔️  ({size} bytes)",
                    )
                return (
                    json.dumps(profile, indent=2),
                    gr.update(interactive=False),
                    "❌ PDF not created—see logs.",
                )
            except Exception as e:
                logging.exception("PDF generation failed")
                return "", gr.update(interactive=False), f"Error: {e}"

        # 3) Export JSON --------------------------------------
        def export_json_handler(
            email, name, phone, address, location, citizenship,
            linkedin, github, portfolio, summary,
            edu_table, work_table, skill_table, project_table, cert_table,
        ):
            rid = uuid.uuid4()
            logger.info(f"[{rid}] JSON export start")
            try:
                profile = resume_helper.build_profile_dict(
                    email, name, phone, address, location, citizenship,
                    linkedin, github, portfolio, summary,
                    edu_table, work_table, skill_table, project_table, cert_table,
                )
                profile.setdefault("full_name", profile.get("name", name))

                temp_dir = resume_helper.resume_gen.temp_dir
                os.makedirs(temp_dir, exist_ok=True)
                json_path = os.path.join(temp_dir, "resume.json")

                ok, msg = resume_helper.resume_gen.export_json(profile, json_path)
                if ok:
                    size = os.path.getsize(json_path)
                    logger.info(f"[{rid}] JSON saved ({size} bytes)")
                    return (
                        json.dumps(profile, indent=2),
                        gr.update(value=os.path.abspath(json_path), interactive=True),
                        f"JSON exported ✔️  ({size} bytes)",
                    )
                logger.error(f"[{rid}] export failed: {msg}")
                return json.dumps(profile, indent=2), gr.update(interactive=False), f"❌ {msg}"
            except Exception as e:
                logger.exception(f"[{rid}] JSON export exception")
                return "", gr.update(interactive=False), f"Error: {e}"

        # ======================================================
        #  WIRE BUTTONS TO HANDLERS
        # ======================================================
        if all_tabs_components:
            personal   = all_tabs_components.get("personal_info_tab", {})
            education  = all_tabs_components.get("educations_tab", {})
            work       = all_tabs_components.get("experiences_tab", {})
            skills     = all_tabs_components.get("skills_tab", {})
            projects   = all_tabs_components.get("projects_tab", {})
            certs      = all_tabs_components.get("certifications_tab", {})

            # Collect outputs for load-JSON (same order as ResumeHelper expects)
            all_outputs = [
                # Personal (11 items incl. info_output)
                personal.get(k) for k in [
                    "email_input","name_input","phone_input","current_address",
                    "location_input","citizenship","linkedin_input","github_input",
                    "portfolio_input","summary_input","info_output"
                ]
            ] + [
                # Education (8)
                education.get(k) for k in [
                    "institution_input","degree_input","field_input","edu_start_input",
                    "edu_end_input","gpa_input","edu_desc_input","edu_list"
                ]
            ] + [
                # Work (8)
                work.get(k) for k in [
                    "company_input","position_input","work_location_input","work_start_input",
                    "work_end_input","work_desc_input","achievements_input","work_list"
                ]
            ] + [
                # Skills (4)
                skills.get(k) for k in [
                    "category_input","skill_input","proficiency_input","skill_list"
                ]
            ] + [
                # Projects (7)
                projects.get(k) for k in [
                    "project_title_input","project_desc_input","project_tech_input",
                    "project_url_input","project_start_input","project_end_input",
                    "project_list"
                ]
            ] + [
                # Certifications (6)
                certs.get(k) for k in [
                    "cert_name_input","cert_issuer_input","cert_date_input",
                    "cert_id_input","cert_url_input","cert_list"
                ]
            ]

            load_json_btn.click(load_json_handler, json_file, all_outputs)

            gen_pdf_btn.click(
                generate_resume_handler,
                inputs=[
                    # Personal
                    personal.get("email_input"),   personal.get("name_input"),
                    personal.get("phone_input"),   personal.get("current_address"),
                    personal.get("location_input"),personal.get("citizenship"),
                    personal.get("linkedin_input"),personal.get("github_input"),
                    personal.get("portfolio_input"),personal.get("summary_input"),
                    # Tables
                    education.get("edu_list"), work.get("work_list"),
                    skills.get("skill_list"),  projects.get("project_list"),
                    certs.get("cert_list"),
                ],
                outputs=[json_output, pdf_dl_btn, status_output],
            )

            gen_json_btn.click(
                export_json_handler,
                inputs=[
                    personal.get("email_input"),   personal.get("name_input"),
                    personal.get("phone_input"),   personal.get("current_address"),
                    personal.get("location_input"),personal.get("citizenship"),
                    personal.get("linkedin_input"),personal.get("github_input"),
                    personal.get("portfolio_input"),personal.get("summary_input"),
                    education.get("edu_list"), work.get("work_list"),
                    skills.get("skill_list"),  projects.get("project_list"),
                    certs.get("cert_list"),
                ],
                outputs=[json_output, json_dl_btn, status_output],
            )

    # ------------------------------------------------------
    #  EXPORT COMPONENTS
    # ------------------------------------------------------
    return SimpleNamespace(
        tab=tab,
        components={
            "json_file":        json_file,
            "load_json_btn":    load_json_btn,
            "gen_pdf_btn":      gen_pdf_btn,
            "pdf_download_btn": pdf_dl_btn,
            "gen_json_btn":     gen_json_btn,
            "json_download_btn":json_dl_btn,
            "json_output":      json_output,
            "status_output":    status_output,
        },
    )
