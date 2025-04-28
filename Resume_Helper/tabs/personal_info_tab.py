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
                email_input = gr.Textbox(label="Email", interactive=True)
                name_input = gr.Textbox(label="Full Name", interactive=True)
                phone_input = gr.Textbox(label="Phone", interactive=True)
                current_address = gr.Textbox(label="Current Address", interactive=True)
                location_input = gr.Textbox(label="Location", interactive=True)
                citizenship = gr.Textbox(label="Citizenship", interactive=True)
                linkedin_input = gr.Textbox(label="LinkedIn URL", interactive=True)
                github_input = gr.Textbox(label="GitHub URL", interactive=True)
                portfolio_input = gr.Textbox(label="Portfolio URL", interactive=True)
                summary_input = gr.Textbox(label="Professional Summary", lines=3, interactive=True)
                info_output = gr.Textbox(label="Status", interactive=False)

        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Profile Management")
                example1_btn = gr.Button("Load Software Developer Example", variant="primary")
                gr.Markdown("""
                * Full Stack Developer with 5 years experience
                * Expertise in Python, JavaScript, React
                * Multiple cloud certifications
                """)
                gr.Markdown("---")
                gr.Markdown("#### Form Controls")
                with gr.Row():
                    reset_personal_btn = gr.Button("Reset Form", variant="secondary")

        # Set up event handlers
        reset_personal_btn.click(
            fn=resume_helper.reset_personal_info,
            inputs=None,
            outputs=[
                email_input, name_input, phone_input, current_address,
                location_input, citizenship, linkedin_input, github_input,
                portfolio_input, summary_input, info_output
            ],
            show_progress=True
        )
        
        # Return the components that need to be accessed by other tabs or the main app
        components_dict = {
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
            "example1_btn": example1_btn
        }
        
        # Create a namespace to store components
        class TabWithComponents:
            def __init__(self, tab, components):
                self.tab = tab
                self.components = components
        
        # Return a wrapper that has both the tab and components
        return TabWithComponents(tab, components_dict)