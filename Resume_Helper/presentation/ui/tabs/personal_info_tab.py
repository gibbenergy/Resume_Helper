"""
Personal Information Tab for the Resume Helper application.
"""

import gradio as gr

def create_personal_info_tab(resume_helper):
    """
    Create the Personal Information tab for the Resume Helper application.
    
    Args:
        resume_helper: An instance of the ResumeHelper class
        
    Returns:
        A Gradio Tab object containing the Personal Information UI
    """
    with gr.Tab("Personal Information") as tab:
        with gr.Row():
            with gr.Column():
                name_prefix_input = gr.Dropdown(
                    label="Name Prefix (Optional)",
                    choices=["", "Dr.", "Prof.", "Mr.", "Mrs.", "Ms.", "Mx.", "Rev.", "Hon.", "Capt."],
                    value="",
                    interactive=True,
                    allow_custom_value=True
                )
                email_input = gr.Textbox(label="Email", lines=2, interactive=True)
                phone_input = gr.Textbox(label="Phone", lines=2, interactive=True)
                location_input = gr.Textbox(label="Location", lines=2, interactive=True)
                linkedin_input = gr.Textbox(label="LinkedIn URL", lines=2, interactive=True)
            with gr.Column():
                name_input = gr.Textbox(label="Full Name", lines=2, interactive=True)
                current_address = gr.Textbox(label="Current Address", lines=2, interactive=True)
                citizenship = gr.Textbox(label="Citizenship", lines=2, interactive=True)
                github_input = gr.Textbox(label="GitHub URL", lines=2, interactive=True)
                portfolio_input = gr.Textbox(label="Portfolio URL", lines=2, interactive=True)
        
        with gr.Row():
            summary_input = gr.Textbox(label="Professional Summary", lines=3, interactive=True)

        with gr.Row():
            info_output = gr.Textbox(label="Status", lines=1, interactive=False, visible=False)

        with gr.Row():
            reset_personal_btn = gr.Button("Reset Form", variant="secondary")
        
        with gr.Row():
            example_software_btn = gr.Button("Load Software Developer Example", variant="primary")
            example_process_btn = gr.Button("Load Process Engineer Example", variant="primary")
        components_dict = {
            "name_prefix_input": name_prefix_input,
            "email_input": email_input,
            "name_input": name_input,
            "phone_input": phone_input,
            "current_address": current_address,
            "location_input": location_input,
            "citizenship": citizenship,
            "linkedin_input": linkedin_input,
            "github_input": github_input,
            "portfolio_input": portfolio_input,
            "summary_input": summary_input,
            "info_output": info_output,
            "reset_personal_btn": reset_personal_btn,
            "example_software_btn": example_software_btn,
            "example_process_btn": example_process_btn
        }
        class TabWithComponents:
            def __init__(self, tab, components):
                self.tab = tab
                self.components = components
        return TabWithComponents(tab, components_dict)