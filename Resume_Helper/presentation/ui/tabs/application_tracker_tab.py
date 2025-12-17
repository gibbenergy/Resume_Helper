"""
Application Tracker Tab - UI for job application tracking system

This module provides the user interface for managing job applications,
including table view, add/edit forms, and basic filtering.
"""

import os
import re
import time
import json
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple

import gradio as gr

from workflows.application_workflows import ApplicationWorkflows
from infrastructure.repositories.sql_application_repository import create_job_url_hash

logger = logging.getLogger(__name__)

def create_application_tracker_tab(resume_helper=None):
    """
    Create the Application Tracker tab with all necessary components.
    
    Args:
        resume_helper: Main resume helper instance (for future integration)
        
    Returns:
        TabWithComponents: Tab object with component references
    """
    
    app_manager = ApplicationWorkflows()
    
    with gr.Tab("Application Tracker") as tab:
        
        with gr.Group() as controls_section:
            with gr.Row():
                with gr.Column(scale=2):
                    search_input = gr.Textbox(
                        label="🔍 Search Applications",
                        placeholder="Search by company, position...",
                        value="",
                        interactive=True
                    )
                with gr.Column(scale=1):
                    sort_dropdown = gr.Dropdown(
                        label="📊 Sort By",
                        choices=[
                            "date_applied", 
                            "company", 
                            "match_score", 
                            "status", 
                            "priority"
                        ],
                        value="date_applied",
                        interactive=True
                    )
                with gr.Column(scale=1):
                    sort_order = gr.Radio(
                        label="⬆️⬇️ Order",
                        choices=["Descending", "Ascending"],
                        value="Descending",
                        interactive=True
                    )
                with gr.Column(scale=1):
                    filter_status = gr.Dropdown(
                        label="🎯 Filter by Status",
                        choices=["All"] + app_manager.get_settings().get("status_options", []),
                        value="All",
                        interactive=True
                    )
            with gr.Row():
                add_app_btn = gr.Button("➕ Add Application", variant="primary")
                refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
        
        with gr.Group() as applications_table_section:
            gr.Markdown("### 📋 Applications")
            
            applications_table = gr.DataFrame(
                headers=["Company", "Position", "Applied", "Match", "Status", "Priority", "Current Round", "Documents"],
                datatype=["str", "str", "str", "str", "str", "str", "str", "str"],
                value=[],
                interactive=False,
                wrap=True,
                label="Job Applications"
            )
        
        with gr.Group(visible=False) as interview_section:
            gr.Markdown("### 🎯 Interview Pipeline Management")
            interview_app_info = gr.Markdown("**Select an application to manage interviews**")
            
            interview_rounds_display = gr.Dataframe(
                headers=["Round", "Status", "Date", "Details"],
                datatype=["str", "str", "str", "str"],
                row_count=(1, "dynamic"),
                col_count=(4, "fixed"),
                interactive=False,
                wrap=True,
                value=[]
            )
            
            current_round_display = gr.Markdown(visible=False)
            current_round_name = gr.State(value="")
            
            with gr.Group(visible=False) as round_form:
                round_form_title = gr.Markdown("#### 📝 Edit Round Details")
                with gr.Row():
                    round_date = gr.Textbox(
                        label="Date",
                        placeholder="YYYY-MM-DD",
                        value=date.today().isoformat(),
                        interactive=True,
                        scale=1
                    )
                    round_time = gr.Textbox(
                        label="Time",
                        placeholder="HH:MM",
                        value="",
                        interactive=True,
                        scale=1
                    )
                    round_location = gr.Textbox(
                        label="Location",
                        placeholder="Office/Zoom",
                        value="",
                        interactive=True,
                        scale=2
                    )
                with gr.Row():
                    round_interviewer = gr.Textbox(
                        label="Interviewer",
                        placeholder="Name",
                        value="",
                        interactive=True,
                        scale=1
                    )
                    round_status = gr.Dropdown(
                        label="Status",
                        choices=app_manager.get_settings().get("interview_round_statuses", ["scheduled", "completed", "cancelled", "rescheduled"]),
                        value="scheduled",
                        interactive=True,
                        scale=1
                    )
                    round_outcome = gr.Dropdown(
                        label="Outcome",
                        choices=app_manager.get_settings().get("interview_round_outcomes", ["pending", "passed", "failed", "needs_follow_up"]),
                        value="pending",
                        interactive=True,
                        scale=1
                    )
                round_notes = gr.Textbox(
                    label="Notes",
                    lines=2,
                    placeholder="Feedback, preparation notes, next steps...",
                    interactive=True
                )
                with gr.Row():
                    save_round_btn = gr.Button("💾 Save", variant="primary", size="sm", scale=1)
                    cancel_round_btn = gr.Button("❌ Cancel", variant="secondary", size="sm", scale=1)
            
            with gr.Group() as navigation_buttons:
                gr.Markdown("---")
                with gr.Row():
                    advance_round_btn = gr.Button("⏭️ Advance", variant="primary", size="lg", scale=1)
                    go_back_round_btn = gr.Button("⬅️ Go Back", variant="secondary", size="lg", scale=1)
                    interview_close_btn = gr.Button("❌ Close", variant="secondary", size="lg", scale=1)

        with gr.Group(visible=False) as details_section:
            gr.Markdown("### 📝 Application Details")
            
            with gr.Row():
                with gr.Column(scale=2):
                    details_company = gr.Textbox(label="Company", interactive=False)
                    details_position = gr.Textbox(label="Position", interactive=False)
                    details_url = gr.Textbox(label="Job URL", interactive=False)
                    details_location = gr.Textbox(label="Location", interactive=False)
                
                with gr.Column(scale=1):
                    details_match_score = gr.Number(label="Match Score", interactive=False)
                    details_status = gr.Textbox(label="Status", interactive=False)
                    details_priority = gr.Textbox(label="Priority", interactive=False)
                    details_date_applied = gr.Textbox(label="Date Applied", interactive=False)
            
            with gr.Row():
                details_notes = gr.Textbox(
                    label="Notes",
                    lines=3,
                    interactive=False
                )
            
            with gr.Accordion("📁 Documents", open=False):
                gr.Markdown("**📎 Upload and manage documents like resume, cover letter, portfolio, references, etc.**")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📤 Upload Documents")
                        doc_upload = gr.File(
                            label="📁 Drop File Here - Auto Upload",
                            file_types=[
                                ".pdf", ".doc", ".docx", ".txt", ".rtf",  # Documents
                                ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",  # Images
                                ".py", ".js", ".java", ".cpp", ".c", ".h", ".cs",  # Code files
                                ".json", ".xml", ".yaml", ".yml", ".csv",  # Data files
                                ".md", ".rst", ".tex",  # Markup
                                ".zip", ".tar", ".gz", ".rar"  # Archives
                            ],
                            type="filepath"
                        )
                        gr.Markdown("*Files are automatically uploaded when you drop them above*")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 📋 Your Documents")
                        documents_list = gr.Dataframe(
                            headers=["Document Name", "Upload Date", "File Size", "Status"],
                            datatype=["str", "str", "str", "str"],
                            interactive=False,
                            wrap=True,
                            value=[["No documents uploaded yet", "", "", ""]],
                            elem_classes=["clickable-documents"]
                        )
                        
                        with gr.Group(visible=False) as doc_action_popup:
                            gr.Markdown("### Document Actions")
                            selected_doc_name = gr.Textbox(label="Selected Document", interactive=False)
                            with gr.Row():
                                download_doc_btn = gr.DownloadButton("⬇️ Download", variant="secondary", scale=1)
                                delete_doc_btn = gr.Button("🗑️ Delete", variant="stop", scale=1)
                                cancel_doc_btn = gr.Button("❌ Cancel", variant="secondary", scale=1)
                
                selected_doc_index = gr.State(value=-1)
                
        
                details_resume_path = gr.Textbox(visible=False, value="")
                details_cover_path = gr.Textbox(visible=False, value="")
                details_resume_status = gr.Markdown(visible=False, value="")
                details_cover_status = gr.Markdown(visible=False, value="")
                details_resume_download = gr.DownloadButton(visible=False, interactive=False)
                details_cover_download = gr.DownloadButton(visible=False, interactive=False)
            
            with gr.Row():
                manage_interviews_btn = gr.Button("📅 Manage Interviews", variant="primary", scale=1)
                edit_app_btn = gr.Button("✏️ Edit", variant="secondary", scale=1)
                delete_app_btn = gr.Button("🗑️ Delete", variant="secondary", scale=1)
                close_details_btn = gr.Button("❌ Close", variant="secondary", scale=1)
        
        with gr.Group(visible=False) as form_section:
            form_title = gr.Markdown("### ➕ Add New Application")
            
            with gr.Row():
                with gr.Column(scale=2):
                    form_job_url = gr.Textbox(
                        label="Job URL *",
                        placeholder="https://company.com/careers/job-posting",
                        interactive=True
                    )
                    form_company = gr.Textbox(
                        label="Company *",
                        placeholder="Google, Meta, Amazon...",
                        interactive=True
                    )
                    form_position = gr.Textbox(
                        label="Position *",
                        placeholder="Software Engineer, Product Manager...",
                        interactive=True
                    )
                    form_location = gr.Textbox(
                        label="Location",
                        placeholder="San Francisco, Remote, New York...",
                        interactive=True
                    )
                
                with gr.Column(scale=1):
                    form_date_applied = gr.Textbox(
                        label="Date Applied",
                        value=date.today().isoformat(),
                        interactive=True
                    )
                    form_status = gr.Dropdown(
                        label="Status",
                        choices=app_manager.get_settings().get("status_options", []),
                        value="Applied",
                        interactive=True
                    )
                    form_priority = gr.Dropdown(
                        label="Priority",
                        choices=app_manager.get_settings().get("priority_levels", []),
                        value="Medium",
                        interactive=True
                    )
                    form_source = gr.Dropdown(
                        label="Application Source",
                        choices=app_manager.get_settings().get("application_sources", []),
                        value="Other",
                        interactive=True
                    )
            
            with gr.Row():
                form_salary_min = gr.Number(
                    label="Salary Min",
                    placeholder="50000",
                    interactive=True
                )
                form_salary_max = gr.Number(
                    label="Salary Max", 
                    placeholder="150000",
                    interactive=True
                )
                form_match_score = gr.Number(
                    label="Match Score (0-100)",
                    minimum=0,
                    maximum=100,
                    interactive=True
                )
            
            with gr.Row():
                form_description = gr.Textbox(
                    label="Job Description",
                    lines=4,
                    placeholder="Paste the full job description here...",
                    interactive=True
                )
            
            with gr.Row():
                form_notes = gr.Textbox(
                    label="Notes",
                    lines=3,
                    placeholder="Any additional notes about this application...",
                    interactive=True
                )
            with gr.Accordion("👥 Contact Information", open=False):
                with gr.Row():
                    form_hr_contact = gr.Textbox(
                        label="HR Contact",
                        placeholder="hr@company.com",
                        interactive=True
                    )
                    form_hiring_manager = gr.Textbox(
                        label="Hiring Manager",
                        placeholder="manager@company.com",
                        interactive=True
                    )
                    form_recruiter = gr.Textbox(
                        label="Recruiter",
                        placeholder="recruiter@company.com",
                        interactive=True
                    )
                    form_referral = gr.Textbox(
                        label="Referral Contact",
                        placeholder="friend@company.com",
                        interactive=True
                    )
            
            with gr.Row():
                save_app_btn = gr.Button("💾 Save Application", variant="primary")
                cancel_form_btn = gr.Button("❌ Cancel", variant="secondary")
        
        status_message = gr.Markdown("Ready to manage your job applications.")
        
        selected_app_id = gr.State(value="")
        edit_mode = gr.State(value=False)
        current_round_name = gr.State(value="")
        interview_pipeline_data = gr.State(value={})
        
        def load_applications_data():
            """Load and format applications for table display."""
            try:
                applications = app_manager.get_all_applications()
                
                if not applications:
                    return [], "No applications found. Click 'Add Application' to get started!"
                
                table_data = []
                for app in applications:
                    current_round = "—"
                    pipeline = app.get("interview_pipeline", {})
                    
                    logger.info(f"App {app.get('company', 'Unknown')}: pipeline = {pipeline}")
                    
                    round_names = app_manager.get_settings().get("default_interview_rounds", [])
                    
                    if not pipeline:
                        current_round = "Not Started"
                    else:
                        for round_name in round_names:
                            round_data = pipeline.get(round_name, {})
                            status = round_data.get("status", "not_started")
                            if status == "scheduled":
                                current_round = round_name.replace("_", " ").title() + " 📅"
                                break
                            elif status == "completed":
                                outcome = round_data.get("outcome", "")
                                if outcome == "passed":
                                    continue
                                else:
                                    current_round = round_name.replace("_", " ").title() + " ✅"
                                    break
                            elif status in ["cancelled", "on_hold"]:
                                current_round = round_name.replace("_", " ").title() + " ⏸️"
                                break
                        
                        if current_round == "—":
                            if round_names:
                                first_round = round_names[0]
                                first_status = pipeline.get(first_round, {}).get("status", "not_started")
                                if first_status == "not_started":
                                    current_round = first_round.replace("_", " ").title() + " ⭕"
                    
                    docs = []
                    documents = app.get("documents", [])
                    
                    for doc in documents:
                        doc_path = doc.get("path", "")
                        if doc_path and os.path.isfile(doc_path):
                            docs.append("📄")
                    
                    doc_status = f"{len(docs)} docs" if docs else "—"
                    
                    table_data.append([
                        app.get("company", ""),
                        app.get("position", ""),
                        app.get("date_applied", ""),
                        f"{app.get('match_score', 0)}%" if app.get('match_score') else "—",
                        app.get("status", ""),
                        app.get("priority", ""),
                        current_round,
                        doc_status
                    ])
                
                return table_data, f"Loaded {len(applications)} applications"
                
            except Exception as e:
                logger.error(f"Error loading applications: {e}")
                return [], f"Error loading applications: {str(e)}"
        
        def refresh_data():
            """Refresh all data displays."""
            table_data, message = load_applications_data()
            return table_data, message, gr.update(visible=True), gr.update(visible=True)
        
        def filter_and_sort_applications(search_query, sort_by, status_filter, sort_order):
            """Filter and sort applications based on user inputs."""
            try:
                all_apps = app_manager.get_all_applications()
                
                if status_filter and status_filter != "All":
                    all_apps = [app for app in all_apps if app.get("status") == status_filter]
                
                if search_query and search_query.strip():
                    search_lower = search_query.lower().strip()
                    filtered_apps = []
                    for app in all_apps:
                        searchable_text = " ".join([
                            app.get("company", ""),
                            app.get("position", "")
                        ]).lower()
                        
                        if search_lower in searchable_text:
                            filtered_apps.append(app)
                    all_apps = filtered_apps
                
                reverse_sort = (sort_order == "Descending")
                
                if sort_by == "company":
                    all_apps.sort(key=lambda x: x.get("company", "").lower(), reverse=reverse_sort)
                elif sort_by == "match_score":
                    all_apps.sort(key=lambda x: x.get("match_score") or 0, reverse=reverse_sort)
                elif sort_by == "status":
                    # Status order based on hiring pipeline progression (normal hiring process flow)
                    # Status values are: Applied, Offer, Accepted, Rejected, Withdrawn
                    # Interview stages (Phone Screen, Interview, Technical, etc.) are tracked in "Current Round" column, NOT in status
                    if reverse_sort:
                        status_order = {
                            "Accepted": 0,
                            "Offer": 1,
                            "Applied": 2,
                            "Rejected": 3,
                            "Withdrawn": 4
                        }
                        default_val = 2
                    else:
                        status_order = {
                            "Rejected": 0,
                            "Applied": 1,
                            "Offer": 2,
                            "Accepted": 3,
                            "Withdrawn": 4
                        }
                        default_val = 1
                    all_apps.sort(key=lambda x: status_order.get(x.get("status", ""), default_val), reverse=False)
                elif sort_by == "priority":
                    priority_order = {"High": 0, "Medium": 1, "Low": 2}
                    all_apps.sort(key=lambda x: priority_order.get(x.get("priority", "Medium"), 1), reverse=reverse_sort)
                else:
                    all_apps.sort(key=lambda x: x.get("date_applied", ""), reverse=reverse_sort)
                
                table_data = []
                for app in all_apps:
                    pipeline = app.get("interview_pipeline", {})
                    settings = app_manager.get_settings()
                    round_names = settings.get("default_interview_rounds", [])
                    
                    current_round = "Not Started"
                    for round_name in round_names:
                        round_data = pipeline.get(round_name, {})
                        round_status = round_data.get("status", "not_started")
                        if round_status == "scheduled":
                            current_round = round_name.replace("_", " ").title()
                            break
                        elif round_status == "completed":
                            continue
                        else:
                            break
                    
                    if all(pipeline.get(r, {}).get("status") == "completed" for r in round_names if r in pipeline):
                        if pipeline:
                            current_round = "All Completed"
                    
                    docs = []
                    for doc in app.get("documents", []):
                        if doc.get("type"):
                            docs.append("📄")
                    
                    doc_status = f"{len(docs)} docs" if docs else "—"
                    
                    table_data.append([
                        app.get("company", ""),
                        app.get("position", ""),
                        app.get("date_applied", ""),
                        f"{app.get('match_score', 0)}%" if app.get('match_score') else "—",
                        app.get("status", ""),
                        app.get("priority", ""),
                        current_round,
                        doc_status
                    ])
                
                count_msg = f"Found {len(all_apps)} application(s)"
                if search_query and search_query.strip():
                    count_msg += f" matching '{search_query}'"
                
                return table_data, count_msg
                
            except Exception as e:
                logger.error(f"Error filtering applications: {e}")
                return [], f"Error filtering: {str(e)}"
        
        def save_application_handler(app_id, edit_mode_val, *form_values):
            """Handle saving application (both new and existing)."""
            try:
                from infrastructure.frameworks.schema_engine import SchemaEngine
                from models.application import ApplicationSchema
                app_data = SchemaEngine.map_form_to_data(
                    list(form_values), 
                    ApplicationSchema.FORM_MAPPING, 
                    ApplicationSchema.FIELDS
                )
                
                if edit_mode_val and app_id:
                    result = app_manager.update_application(app_id, app_data)
                    success = result.is_success()
                    message = result.get_data().get("message", "") if success else result.get_error_message()
                    action = "updated"
                else:
                    result = app_manager.create_application(app_data)
                    success = result.is_success()
                    if success:
                        app_id = result.get_data().get("app_id", "")
                        message = result.get_data().get("message", "")
                    else:
                        message = result.get_error_message()
                    action = "created"
                
                if success:
                    table_data, _, table_vis, controls_vis = refresh_data()
                    
                    return (
                        table_data,
                        gr.update(visible=False),
                        False,
                        "",
                        f"✅ Application {action} successfully!",
                        "", "", "", "", date.today().isoformat(), "Applied", "Medium", "Other",
                        None, None, None, "", "", "", "", "", "",
                        controls_vis,
                        table_vis
                    )
                else:
                    return (
                        gr.update(),
                        gr.update(),
                        edit_mode_val,
                        app_id,
                        f"❌ {message}",
                        *form_values
                    )
                    
            except Exception as e:
                logger.error(f"Error saving application: {e}")
                return (
                    gr.update(), gr.update(), edit_mode_val, app_id,
                    f"❌ Error saving application: {str(e)}",
                    *form_values
                )
        
        def show_form(title="Add New Application"):
            """Show the application form and hide applications table and controls."""
            return (
                gr.update(visible=True),
                gr.update(value=f"### {title}"),
                "Form opened",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False)
            )
        
        def hide_form():
            """Hide the application form and show applications table."""
            return (
                gr.update(visible=False),
                "Form closed",
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=True)
            )
        
        def get_current_round(pipeline_data):
            """Get the current active round based on sequential progression."""
            round_names = app_manager.get_settings().get("default_interview_rounds", [])
            current_pipeline = pipeline_data or {}
            for i, round_name in enumerate(round_names):
                round_data = current_pipeline.get(round_name, {"status": "not_started"})
                status = round_data.get("status", "not_started")
                
                if status in ["not_started", "scheduled"]:
                    return round_name, i
                elif status != "completed":
                    return round_name, i
            return None, len(round_names)
        
        def manage_interviews(app_id):
            """Show interview management section with Dataframe table."""
            try:
                if not app_id:
                    return (
                        gr.update(visible=False),
                        "No application selected",
                        gr.update(),
                        [],
                        gr.update(),
                        {},
                        gr.update(visible=True),
                        gr.update(visible=True)
                    )
                
                app = app_manager.get_application(app_id)
                if not app:
                    return (
                        gr.update(visible=False),
                        "Application not found",
                        gr.update(),
                        [],
                        gr.update(),
                        {},
                        gr.update(visible=True),
                        gr.update(visible=True)
                    )
                
                app_info = f"**{app.get('company', 'Unknown')} - {app.get('position', 'Unknown')}**"
                
                pipeline = app.get("interview_pipeline", {})
                round_names = app_manager.get_settings().get("default_interview_rounds", [])
                current_round, current_index = get_current_round(pipeline)
                
                table_data = []
                for i, round_name in enumerate(round_names):
                    round_data = pipeline.get(round_name, {"status": "not_started"})
                    status = round_data.get("status", "not_started")
                    round_display = round_name.replace("_", " ").title()
                    if status == "completed":
                        status_icon = "✅"
                        status_text = "Completed"
                        outcome = round_data.get("outcome", "")
                        if outcome and outcome != "pending":
                            status_text += f" - {outcome.title()}"
                    elif status == "scheduled":
                        status_icon = "📅"
                        status_text = "Scheduled"
                    else:
                        status_icon = "⭕"
                        status_text = "Not Started"
                    
                    if round_name == current_round:
                        round_display += " 👉"
                    
                    details_parts = []
                    if round_data.get("location"):
                        details_parts.append(f"📍 {round_data['location']}")
                    if round_data.get("interviewer"):
                        details_parts.append(f"👤 {round_data['interviewer']}")
                    if round_data.get("notes"):
                        note_preview = round_data['notes'][:50] + "..." if len(round_data['notes']) > 50 else round_data['notes']
                        details_parts.append(f"📝 {note_preview}")
                    details_str = " | ".join(details_parts) if details_parts else "—"
                    date_str = round_data.get("date", "—")
                    if round_data.get("time"):
                        date_str += f" {round_data['time']}"
                    
                    table_data.append([
                        f"{status_icon} {round_display}",
                        status_text,
                        date_str,
                        details_str
                    ])
                if current_round:
                    current_display = f"**Current Round:** {current_round.replace('_', ' ').title()}"
                else:
                    current_display = "**All interview rounds completed!**"
                
                return (
                    gr.update(visible=True),
                    "Interview management opened - Click any row to edit",
                    app_info,
                    table_data,
                    current_display,
                    pipeline,
                    gr.update(visible=False),
                    gr.update(visible=False)
                )
                
            except Exception as e:
                logger.error(f"Error managing interviews: {e}")
                return (
                    gr.update(visible=False),
                    f"Error: {str(e)}",
                    gr.update(),
                    [],
                    gr.update(),
                    {},
                    gr.update(visible=True),
                    gr.update(visible=True)
                )
        
        def advance_to_next_round(app_id, pipeline_data):
            """Advance application to next interview round in sequential order."""
            try:
                if not app_id:
                    return "No application selected", gr.update(), gr.update(), gr.update(), {}
                
                round_names = app_manager.get_settings().get("default_interview_rounds", [])
                current_round, current_index = get_current_round(pipeline_data)
                
                if current_round is None:
                    return "All rounds completed - cannot advance further", gr.update(), gr.update(), gr.update(), {}
                
                existing_round_data = pipeline_data.get(current_round, {})
                existing_date = existing_round_data.get("date", date.today().isoformat())
                current_updates = {
                    "status": "completed",
                    "date": existing_date,
                    "notes": "Round completed, advanced to next",
                    "outcome": "passed"
                }
                
                result1 = app_manager.update_interview_round(app_id, current_round, current_updates)
                success1 = result1.is_success()
                
                next_index = current_index + 1
                if next_index < len(round_names):
                    next_round = round_names[next_index]
                    
                    existing_next_data = pipeline_data.get(next_round, {})
                    
                    if not existing_next_data or existing_next_data.get("status") == "not_started":
                        current_round_data = pipeline_data.get(current_round, {})
                        next_updates = {
                            "status": "scheduled",
                            "date": existing_next_data.get("date") if existing_next_data.get("date") else date.today().isoformat(),
                            "time": current_round_data.get("time", ""),
                            "location": current_round_data.get("location", ""),
                            "interviewer": current_round_data.get("interviewer", ""),
                            "notes": "Advanced from previous round",
                            "outcome": "pending"
                        }
                    else:
                        next_updates = {
                            "status": "scheduled",
                            "date": existing_next_data.get("date", date.today().isoformat()),
                            "outcome": existing_next_data.get("outcome", "pending")
                        }
                    
                    result2 = app_manager.update_interview_round(app_id, next_round, next_updates)
                    success2 = result2.is_success()
                else:
                    success2 = True
                
                if success1 and success2:
                    result = manage_interviews(app_id)
                    return result[1], result[2], result[3], result[4], result[5]
                else:
                    return "Error advancing round", gr.update(), gr.update(), gr.update(), {}
                    
            except Exception as e:
                logger.error(f"Error advancing round: {e}")
                return f"Error: {str(e)}", gr.update(), gr.update(), gr.update(), {}
        
        def go_back_to_previous_round(app_id, pipeline_data):
            """Go back to previous interview round in sequential order - reverses the advance action."""
            try:
                if not app_id:
                    return "No application selected", gr.update(), gr.update(), gr.update(), {}
                
                round_names = app_manager.get_settings().get("default_interview_rounds", [])
                current_round, current_index = get_current_round(pipeline_data)
                
                if current_index <= 0:
                    return "Already at first round - cannot go back further", gr.update(), gr.update(), gr.update(), {}
                
                if current_round:
                    current_updates = {
                        "status": "not_started",
                        "date": "",
                        "notes": "",
                        "outcome": ""
                    }
                    result1 = app_manager.update_interview_round(app_id, current_round, current_updates)
                    success1 = result1.is_success()
                else:
                    if current_index > 0:
                        last_round = round_names[current_index - 1]
                        current_updates = {
                            "status": "scheduled",
                            "date": date.today().isoformat(),
                            "notes": "Reverted from completed status",
                            "outcome": "pending"
                        }
                        result1 = app_manager.update_interview_round(app_id, last_round, current_updates)
                        success1 = result1.is_success()
                        
                        if success1:
                            result = manage_interviews(app_id)
                            return result[1], result[2], result[3], result[4], result[5]
                        else:
                            return "Error going back to previous round", gr.update(), gr.update(), gr.update(), {}
                    else:
                        return "Cannot go back further", gr.update(), gr.update(), gr.update(), {}
                
                previous_index = current_index - 1
                previous_round = round_names[previous_index]
                previous_updates = {
                    "status": "scheduled",
                    "date": date.today().isoformat(),
                    "notes": "Went back to this round",
                    "outcome": "pending"
                }
                
                result2 = app_manager.update_interview_round(app_id, previous_round, previous_updates)
                success2 = result2.is_success()
                
                if success1 and success2:
                    result = manage_interviews(app_id)
                    return result[1], result[2], result[3], result[4], result[5]
                else:
                    return "Error going back to previous round", gr.update(), gr.update(), gr.update(), {}
                    
            except Exception as e:
                logger.error(f"Error going back to previous round: {e}")
                return f"Error: {str(e)}", gr.update(), gr.update(), gr.update(), {}
        
        def save_round_details(app_id, round_name, date_val, time_val, location_val, interviewer_val, status_val, outcome_val, notes_val):
            """Save interview round details with all form fields and refresh display."""
            try:
                if not app_id:
                    return "No application selected", gr.update(visible=False), gr.update(), gr.update(), {}
                
                if not round_name:
                    app = app_manager.get_application(app_id)
                    pipeline = app.get("interview_pipeline", {}) if app else {}
                    current_round, _ = get_current_round(pipeline)
                    round_name = current_round
                
                if not round_name:
                    return "No active round to save details for", gr.update(visible=True), gr.update(), gr.update(), {}
                full_datetime = f"{date_val} {time_val}".strip() if time_val else date_val
                
                round_updates = {
                    "status": status_val,
                    "date": full_datetime,
                    "location": location_val,
                    "interviewer": interviewer_val,
                    "notes": notes_val,
                    "outcome": outcome_val
                }
                
                result = app_manager.update_interview_round(app_id, round_name, round_updates)
                success = result.is_success()
                message = result.get_data().get("message", "") if success else result.get_error_message()
                
                if success:
                    interview_result = manage_interviews(app_id)
                    return (
                        f"✅ Interview details saved for {round_name.replace('_', ' ').title()}: {message}", 
                        gr.update(visible=False),
                        interview_result[3],
                        interview_result[4],
                        interview_result[5]
                    )
                else:
                    return f"❌ Error saving: {message}", gr.update(visible=True), gr.update(), gr.update(), {}
                    
            except Exception as e:
                logger.error(f"Error saving round details: {e}")
                return f"❌ Error: {str(e)}", gr.update(visible=True), gr.update(), gr.update(), {}
        
        def upload_document(app_id, file_path):
            """Upload a document for the selected application."""
            try:
                if not app_id:
                    return "❌ No application selected. Please select an application first.", gr.update()
                
                if not file_path:
                    return "❌ Please select a file to upload.", gr.update()
                
                app = app_manager.get_application(app_id)
                if not app:
                    return "❌ Application not found.", gr.update()
                    
                original_filename = os.path.basename(file_path)
                doc_name, file_ext = os.path.splitext(original_filename)
                
                doc_name = re.sub(r'[^a-zA-Z0-9_\-\s]', '', doc_name).strip()
                if not doc_name:
                    doc_name = "Document"
                
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                docs_dir = os.path.join(base_dir, "data", "documents", app_id)
                os.makedirs(docs_dir, exist_ok=True)
                
                logger.info(f"Saving document to: {docs_dir}")
                
                import shutil
                safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', doc_name)
                new_filename = f"{safe_name}_{int(time.time())}{file_ext}"
                dest_path = os.path.join(docs_dir, new_filename)
                
                logger.info(f"Copying from {file_path} to {dest_path}")
                shutil.copy2(file_path, dest_path)
                
                if not os.path.exists(dest_path):
                    raise Exception(f"File copy failed - destination file does not exist: {dest_path}")
                
                logger.info(f"File copied successfully to: {dest_path}")
                
                file_size = os.path.getsize(dest_path)
                
                doc_type = "other"
                if file_ext.lower() in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
                    doc_type = "document"
                elif file_ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']:
                    doc_type = "image"
                elif file_ext.lower() in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs']:
                    doc_type = "code"
                elif file_ext.lower() in ['.zip', '.tar', '.gz', '.rar']:
                    doc_type = "archive"
                
                doc_data = {
                    "name": original_filename,
                    "type": doc_type,
                    "path": dest_path,
                    "size": file_size
                }
                
                result = app_manager.repository.add_document(app_id, doc_data)
                
                if result.is_success():
                    docs_data = load_documents_list(app_id)
                    file_size_mb = round(file_size / (1024 * 1024), 2)
                    return f"✅ '{original_filename}' uploaded successfully! ({file_size_mb} MB)", docs_data
                else:
                    # Clean up file if database insert failed
                    try:
                        os.remove(dest_path)
                    except:
                        pass
                    return f"❌ Error saving document to database: {result.get_error_message()}", gr.update()
                    
            except Exception as e:
                logger.error(f"Error uploading document: {e}")
                return f"❌ Error uploading document: {str(e)}", gr.update()
        
        def show_document_actions(evt: gr.SelectData, app_id):
            """Show action popup and prepare download button when a document is clicked."""
            try:
                if not app_id:
                    return gr.update(visible=False), "", -1, gr.update(value=None)
                
                if evt.index is None or len(evt.index) < 1:
                    return gr.update(visible=False), "", -1, gr.update(value=None)
                
                row_index = evt.index[0]
                
                app = app_manager.get_application(app_id)
                if not app:
                    return gr.update(visible=False), "", -1, gr.update(value=None)
                
                documents = app.get("documents", [])
                
                if row_index >= len(documents):
                    return gr.update(visible=False), "", -1, gr.update(value=None)
                
                selected_doc = documents[row_index]
                doc_name = selected_doc.get("name", "Unknown")
                doc_path = selected_doc.get("path", "")
                
                if not doc_path or not os.path.exists(doc_path):
                    return (
                        gr.update(visible=True),
                        f"{doc_name} (File Missing)",
                        row_index,
                        gr.update(value=None, interactive=False)
                    )
                
                return (
                    gr.update(visible=True),
                    doc_name,
                    row_index,
                    gr.update(value=doc_path, interactive=True)
                )
                
            except Exception as e:
                logger.error(f"Error showing document actions: {e}")
                return gr.update(visible=False), "", -1, gr.update(value=None)

        def delete_document(app_id, doc_index):
            """Delete a document by index from database."""
            try:
                if not app_id:
                    return "❌ No application selected.", gr.update(), gr.update(visible=False), "", -1, gr.update(value=None)
                
                if doc_index < 0:
                    return "❌ No document selected.", gr.update(), gr.update(visible=False), "", -1, gr.update(value=None)
                
                app = app_manager.get_application(app_id)
                if not app:
                    return "❌ Application not found.", gr.update(), gr.update(visible=False), "", -1, gr.update(value=None)
                
                documents = app.get("documents", [])
                
                if doc_index >= len(documents):
                    return "❌ Invalid document selection.", gr.update(), gr.update(visible=False), "", -1, gr.update(value=None)
                
                doc_to_remove = documents[doc_index]
                doc_id = doc_to_remove.get("id")
                doc_name = doc_to_remove.get("name", "Unknown")
                doc_path = doc_to_remove.get("path", "")
                
                if doc_id:
                    result = app_manager.repository.delete_document(doc_id)
                    
                    if not result.is_success():
                        return f"❌ Error deleting from database: {result.get_error_message()}", gr.update(), gr.update(visible=False), "", -1, gr.update(value=None)
                    
                    if doc_path and os.path.exists(doc_path):
                        try:
                            os.remove(doc_path)
                            logger.info(f"Deleted file: {doc_path}")
                        except Exception as e:
                            logger.warning(f"Could not delete file {doc_path}: {e}")
                    
                    docs_data = load_documents_list(app_id)
                    return f"✅ '{doc_name}' deleted successfully!", docs_data, gr.update(visible=False), "", -1, gr.update(value=None)
                else:
                    return "❌ Document ID not found.", gr.update(), gr.update(visible=False), "", -1, gr.update(value=None)
                    
            except Exception as e:
                logger.error(f"Error deleting document: {e}")
                return f"❌ Error deleting document: {str(e)}", gr.update(), gr.update(visible=False), "", -1, gr.update(value=None)
        
        def cancel_document_action():
            """Cancel document action and hide popup."""
            return gr.update(visible=False), "", -1, gr.update(value=None)
        
        def load_documents_list(app_id):
            """Load documents list for the selected application from database."""
            try:
                if not app_id:
                    return [["No documents uploaded yet", "", "", ""]]
                
                app = app_manager.get_application(app_id)
                if not app:
                    return [["No documents uploaded yet", "", "", ""]]
                
                # Get documents from database (relationship in Application model)
                documents = app.get("documents", [])
                
                if not documents:
                    return [["No documents uploaded yet", "", "", ""]]
                
                docs_data = []
                
                for doc in documents:
                    file_path = doc.get("path", "")
                    file_exists = os.path.exists(file_path) if file_path else False
                    status = "✅ Available" if file_exists else "❌ Missing"
                    
                    upload_date = doc.get("upload_date", "Unknown")
                    if upload_date and upload_date != "Unknown":
                        try:
                            if isinstance(upload_date, str):
                                upload_date = upload_date.split('T')[0] if 'T' in upload_date else upload_date
                        except:
                            upload_date = "Unknown"
                    
                    file_size = doc.get("size", 0)
                    if file_size:
                        file_size_mb = round(file_size / (1024 * 1024), 2)
                        size_str = f"{file_size_mb} MB" if file_size_mb >= 0.01 else f"{round(file_size / 1024, 2)} KB"
                    else:
                        size_str = "Unknown"
                    
                    docs_data.append([
                        doc.get("name", "Unknown"),
                        upload_date,
                        size_str,
                        status
                    ])
                
                return docs_data
                
            except Exception as e:
                logger.error(f"Error loading documents: {e}")
                return [["Error loading documents", "", "", ""]]
        
        def show_application_details(evt: gr.SelectData):
            """Show details for selected application."""
            try:
                logger.info(f"Table row selection event: {evt}")
                
                if evt.index is None or len(evt.index) < 1:
                    logger.warning("No valid selection index")
                    return (gr.update(), "No application selected", "", "", "", "", "", "", "", "", "", "", "", "", "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), [], [], gr.update(visible=True), gr.update(visible=True))
                
                applications = app_manager.get_all_applications()
                selected_row = evt.index[0]
                
                logger.info(f"Selected row: {selected_row}, Total applications: {len(applications)}")
                
                if selected_row >= len(applications):
                    logger.warning(f"Invalid selection: row {selected_row} >= {len(applications)} applications")
                    return (gr.update(), "Invalid selection", "", "", "", "", "", "", "", "", "", "", "", "", "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), [], [], gr.update(visible=True), gr.update(visible=True))
                
                app = applications[evt.index[0]]
                app_id = app.get("id", "")
                
                docs_data = load_documents_list(app_id)
                
                return (
                    app_id,
                    f"Selected: {app.get('company', '')} - {app.get('position', '')}",
                    app.get("company", ""),
                    app.get("position", ""),
                    app.get("job_url", ""),
                    app.get("location", ""),
                    app.get("match_score", 0),
                    app.get("status", ""),
                    app.get("priority", ""),
                    app.get("date_applied", ""),
                    app.get("notes", ""),
                                    "",
                "",
                "",
                "",
                    gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                    docs_data,
                    [],
                    gr.update(visible=False),
                    gr.update(visible=False)
                )
                
            except Exception as e:
                logger.error(f"Error showing application details: {e}")
                import traceback
                traceback.print_exc()
                return (
                    "", f"Error: {str(e)}", "", "", "", "", "", "", "", "", "", "", "", "", "",
                    gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), [], [], gr.update(visible=True), gr.update(visible=True)
                )
        
        def edit_application(app_id):
            """Load application data for editing and hide details section."""
            try:
                if not app_id:
                    return (gr.update(), "No application selected for editing", 
                           *[gr.update() for _ in range(17)], gr.update(visible=True))
                
                app = app_manager.get_application(app_id)
                if not app:
                    return (gr.update(), f"Application not found: {app_id}",
                           *[gr.update() for _ in range(17)], gr.update(visible=True))
                return (
                    gr.update(visible=True),
                    gr.update(value="### ✏️ Edit Application"),
                    app.get("job_url", ""),
                    app.get("company", ""),
                    app.get("position", ""),
                    app.get("location", ""),
                    app.get("date_applied", ""),
                    app.get("status", "Applied"),
                    app.get("priority", "Medium"),
                    app.get("application_source", "Other"),
                    app.get("salary_min"),
                    app.get("salary_max"),
                    app.get("match_score"),
                    app.get("description", ""),
                    app.get("notes", ""),
                    app.get("hr_contact", ""),
                    app.get("hiring_manager", ""),
                    app.get("recruiter", ""),
                    app.get("referral", ""),
                    f"Editing application: {app.get('company', '')} - {app.get('position', '')}",
                    gr.update(visible=False)
                )
                
            except Exception as e:
                logger.error(f"Error editing application: {e}")
                return (gr.update(), f"Error editing application: {str(e)}",
                       *[gr.update() for _ in range(17)], gr.update(visible=True))
        
        def delete_application(app_id):
            """Delete selected application."""
            try:
                if not app_id:
                    return gr.update(), gr.update(), gr.update(visible=False), "", "No application selected for deletion", gr.update(visible=True)
                
                app = app_manager.get_application(app_id)
                if not app:
                    return gr.update(), gr.update(), gr.update(visible=False), "", f"Application not found: {app_id}", gr.update(visible=True)
                
                company = app.get("company", "Unknown")
                position = app.get("position", "Unknown")
                
                result = app_manager.delete_application(app_id)
                
                if result.is_success():
                    table_data, _, table_section_update, controls_update = refresh_data()
                    
                    return (
                        table_data,
                        gr.update(visible=False),
                        "",
                        f"✅ Deleted application: {company} - {position}",
                        table_section_update
                    )
                else:
                    return (
                        gr.update(),
                        gr.update(),
                        app_id,
                        f"❌ {result.get_error_message()}",
                        gr.update()
                    )
                    
            except Exception as e:
                logger.error(f"Error deleting application: {e}")
                return gr.update(), gr.update(), app_id, f"❌ Error deleting application: {str(e)}", gr.update()
        
        tab.select(
            fn=refresh_data,
            inputs=[],
            outputs=[applications_table, status_message, applications_table_section, controls_section]
        )
        
        refresh_btn.click(
            fn=refresh_data,
            inputs=[],
            outputs=[applications_table, status_message, applications_table_section, controls_section]
        )
        search_input.change(
            fn=filter_and_sort_applications,
            inputs=[search_input, sort_dropdown, filter_status, sort_order],
            outputs=[applications_table, status_message]
        )
        
        sort_dropdown.change(
            fn=filter_and_sort_applications,
            inputs=[search_input, sort_dropdown, filter_status, sort_order],
            outputs=[applications_table, status_message]
        )
        
        sort_order.change(
            fn=filter_and_sort_applications,
            inputs=[search_input, sort_dropdown, filter_status, sort_order],
            outputs=[applications_table, status_message]
        )
        
        filter_status.change(
            fn=filter_and_sort_applications,
            inputs=[search_input, sort_dropdown, filter_status, sort_order],
            outputs=[applications_table, status_message]
        )
        add_app_btn.click(
            fn=lambda: show_form("➕ Add New Application"),
            inputs=[],
            outputs=[form_section, form_title, status_message, details_section, applications_table_section, controls_section]
        )
        add_app_btn.click(
            fn=lambda: (False, ""),
            inputs=[],
            outputs=[edit_mode, selected_app_id]
        )
        
        save_app_btn.click(
            fn=save_application_handler,
            inputs=[
                selected_app_id, edit_mode,
                form_job_url, form_company, form_position, form_location,
                form_date_applied, form_status, form_priority, form_source,
                form_salary_min, form_salary_max, form_match_score,
                form_description, form_notes,
                form_hr_contact, form_hiring_manager, form_recruiter, form_referral
            ],
            outputs=[
                applications_table, form_section, edit_mode, selected_app_id, status_message,
                form_job_url, form_company, form_position, form_location,
                form_date_applied, form_status, form_priority, form_source,
                form_salary_min, form_salary_max, form_match_score,
                form_description, form_notes,
                form_hr_contact, form_hiring_manager, form_recruiter, form_referral,
                controls_section, applications_table_section
            ]
        )
        cancel_form_btn.click(
            fn=hide_form,
            inputs=[],
            outputs=[form_section, status_message, details_section, applications_table_section, controls_section]
        )
        cancel_form_btn.click(
            fn=lambda: (False, ""),
            inputs=[],
            outputs=[edit_mode, selected_app_id]
        )
        manage_interviews_btn.click(
            fn=manage_interviews,
            inputs=[selected_app_id],
            outputs=[interview_section, status_message, interview_app_info, interview_rounds_display, current_round_display, interview_pipeline_data, details_section, controls_section]
        )
        
        interview_close_btn.click(
            fn=lambda: (gr.update(visible=False), "Interview management closed", gr.update(visible=True), gr.update(visible=False)),
            inputs=[],
            outputs=[interview_section, status_message, details_section, controls_section]
        )
        
        def load_round_from_table_click(app_id, pipeline_data, evt: gr.SelectData):
            """Load round details when user clicks a row in the Dataframe."""
            try:
                if not app_id or evt is None:
                    return (gr.update(visible=False), gr.update(), "No row selected", 
                            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), "", gr.update(visible=True))
                
                row_index = evt.index[0] if isinstance(evt.index, (list, tuple)) else evt.index
                
                round_names = app_manager.get_settings().get("default_interview_rounds", [])
                if row_index >= len(round_names):
                    return (gr.update(visible=False), gr.update(), "Invalid row", 
                            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), "", gr.update(visible=True))
                
                round_key = round_names[row_index]
                round_data = pipeline_data.get(round_key, {})
                round_display = round_key.replace("_", " ").title()
                
                return (
                    gr.update(visible=True),
                    gr.update(value=f"#### 📝 {round_display}"),
                    f"Editing: {round_display}",
                    round_data.get("date", date.today().isoformat()),
                    round_data.get("time", ""),
                    round_data.get("location", ""),
                    round_data.get("interviewer", ""),
                    round_data.get("status", "scheduled"),
                    round_data.get("outcome", "pending"),
                    round_data.get("notes", ""),
                    round_key,
                    gr.update(visible=False)
                )
                
            except Exception as e:
                logger.error(f"Error loading round from table click: {e}")
                return (gr.update(visible=False), gr.update(), f"Error: {str(e)}",
                       gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), "", gr.update(visible=True))
        interview_rounds_display.select(
            fn=load_round_from_table_click,
            inputs=[selected_app_id, interview_pipeline_data],
            outputs=[round_form, round_form_title, status_message, round_date, round_time, round_location, round_interviewer, round_status, round_outcome, round_notes, current_round_name, navigation_buttons]
        )
        def save_round_details(app_id, round_name, rdate, rtime, rlocation, rinterviewer, rstatus, routcome, rnotes):
            """Save interview round details."""
            try:
                if not app_id or not round_name:
                    return "No round selected", gr.update(), gr.update(), gr.update(), {}, gr.update()
                
                updates = {
                    "status": rstatus,
                    "date": rdate,
                    "time": rtime,
                    "location": rlocation,
                    "interviewer": rinterviewer,
                    "outcome": routcome,
                    "notes": rnotes
                }
                
                result = app_manager.update_interview_round(app_id, round_name, updates)
                
                if result.is_success():
                    interview_result = manage_interviews(app_id)                
                    return (
                        f"✅ Saved {round_name.replace('_', ' ').title()}",
                        gr.update(visible=False),
                        interview_result[3],
                        interview_result[4],
                        interview_result[5],
                        gr.update(visible=True)
                    )
                else:
                    return f"❌ {result.get_error_message()}", gr.update(), gr.update(), gr.update(), {}, gr.update()
                    
            except Exception as e:
                logger.error(f"Error saving round details: {e}")
                return f"❌ Error: {str(e)}", gr.update(), gr.update(), gr.update(), {}, gr.update()
        
        advance_round_btn.click(
            fn=advance_to_next_round,
            inputs=[selected_app_id, interview_pipeline_data],
            outputs=[status_message, interview_app_info, interview_rounds_display, current_round_display, interview_pipeline_data]
        )
        
        save_round_btn.click(
            fn=save_round_details,
            inputs=[selected_app_id, current_round_name, round_date, round_time, round_location, round_interviewer, round_status, round_outcome, round_notes],
            outputs=[status_message, round_form, interview_rounds_display, current_round_display, interview_pipeline_data, navigation_buttons]
        )
        
        cancel_round_btn.click(
            fn=lambda: (gr.update(visible=False), "Round form cancelled", gr.update(visible=True)),
            inputs=[],
            outputs=[round_form, status_message, navigation_buttons]
        )
        applications_table.select(
            fn=show_application_details,
            inputs=[],
            outputs=[
                selected_app_id, status_message, details_company, details_position, 
                details_url, details_location, details_match_score, details_status,
                details_priority, details_date_applied, details_notes,
                details_resume_path, details_cover_path, details_resume_status, 
                details_cover_status, details_section, details_resume_download, details_cover_download,
                documents_list, interview_rounds_display, applications_table_section, controls_section
            ]
        )
        documents_list.select(
            fn=show_document_actions,
            inputs=[selected_app_id],
            outputs=[doc_action_popup, selected_doc_name, selected_doc_index, download_doc_btn]
        )
        doc_upload.upload(
            fn=upload_document,
            inputs=[selected_app_id, doc_upload],
            outputs=[status_message, documents_list]
        )
        delete_doc_btn.click(
            fn=delete_document,
            inputs=[selected_app_id, selected_doc_index],
            outputs=[status_message, documents_list, doc_action_popup, selected_doc_name, selected_doc_index, download_doc_btn]
        )
        cancel_doc_btn.click(
            fn=cancel_document_action,
            inputs=[],
            outputs=[doc_action_popup, selected_doc_name, selected_doc_index, download_doc_btn]
        )
        close_details_btn.click(
            fn=lambda: (gr.update(visible=False), "", "Details closed", gr.update(visible=True), gr.update(visible=True)),
            inputs=[],
            outputs=[details_section, selected_app_id, status_message, applications_table_section, controls_section]
        )
        edit_app_btn.click(
            fn=edit_application,
            inputs=[selected_app_id],
            outputs=[
                form_section, form_title,
                form_job_url, form_company, form_position, form_location,
                form_date_applied, form_status, form_priority, form_source,
                form_salary_min, form_salary_max, form_match_score,
                form_description, form_notes,
                form_hr_contact, form_hiring_manager, form_recruiter, form_referral,
                status_message,
                details_section
            ]
        )
        edit_app_btn.click(
            fn=lambda: True,
            inputs=[],
            outputs=[edit_mode]
        )
        
        delete_app_btn.click(
            fn=delete_application,
            inputs=[selected_app_id],
            outputs=[applications_table, details_section, selected_app_id, status_message, applications_table_section]
        )
        go_back_round_btn.click(
            fn=go_back_to_previous_round,
            inputs=[selected_app_id, interview_pipeline_data],
            outputs=[status_message, interview_app_info, interview_rounds_display, current_round_display, interview_pipeline_data]
        )
        
        components_dict = {
            "applications_table": applications_table,
            "search_input": search_input,
            "sort_dropdown": sort_dropdown,
            "filter_status": filter_status,
            "add_app_btn": add_app_btn,
            "refresh_btn": refresh_btn,
            "form_section": form_section,
            "form_title": form_title,
            "save_app_btn": save_app_btn,
            "cancel_form_btn": cancel_form_btn,
            "status_message": status_message,
            "interview_section": interview_section,
            "manage_interviews_btn": manage_interviews_btn,
            "advance_round_btn": advance_round_btn,
            "save_round_btn": save_round_btn,
            "go_back_round_btn": go_back_round_btn,
            "interview_pipeline_data": interview_pipeline_data,
            "current_round_name": current_round_name,
            "details_resume_path": details_resume_path,
            "details_cover_path": details_cover_path,
            "details_resume_download": details_resume_download,
            "details_cover_download": details_cover_download,
            "details_resume_status": details_resume_status,
            "details_cover_status": details_cover_status,
            "doc_upload": doc_upload,
            "documents_list": documents_list,
            "doc_action_popup": doc_action_popup,
            "selected_doc_name": selected_doc_name,
            "selected_doc_index": selected_doc_index,
            "download_doc_btn": download_doc_btn,
            "delete_doc_btn": delete_doc_btn,
            "cancel_doc_btn": cancel_doc_btn,
            "details_section": details_section,
            "details_company": details_company,
            "details_position": details_position,
            "details_url": details_url,
            "details_location": details_location,
            "details_match_score": details_match_score,
            "details_status": details_status,
            "details_priority": details_priority,
            "details_date_applied": details_date_applied,
            "details_notes": details_notes,
            "close_details_btn": close_details_btn,
            "selected_app_id": selected_app_id,
            "edit_mode": edit_mode,
            "app_manager": app_manager
        }
        
        class TabWithComponents:
            def __init__(self, tab, components):
                self.tab = tab
                self.components = components
        
        return TabWithComponents(tab, components_dict) 
