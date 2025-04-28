"""
Resume Helper application tab modules.
This package contains the individual tab modules for the Resume Helper Gradio application.
"""

from .personal_info_tab import create_personal_info_tab
from .educations_tab import create_educations_tab  # Keep function name for backward compatibility
from .experiences_tab import create_experiences_tab  # Keep function name for backward compatibility
from .skills_tab import create_skills_tab
from .projects_tab import create_projects_tab
from .certifications_tab import create_certifications_tab
from .generate_resume_tab import create_generate_resume_tab
from .ai_resume_helper_tab import create_ai_resume_helper_tab

__all__ = [
    'create_personal_info_tab',
    'create_educations_tab',  # Education tab (singular)
    'create_experiences_tab',  # Experience tab (singular)
    'create_skills_tab',
    'create_projects_tab',
    'create_certifications_tab',
    'create_generate_resume_tab',
    'create_ai_resume_helper_tab',
]