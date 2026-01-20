"""
Dependencies for FastAPI application.
Provides shared instances like ResumeHelper.
"""

from typing import Generator
from backend.core.services import ResumeService as ResumeHelper

# Global instance
_resume_helper: ResumeHelper = None

def get_resume_helper() -> ResumeHelper:
    """Get or create ResumeHelper instance."""
    global _resume_helper
    if _resume_helper is None:
        _resume_helper = ResumeHelper()
    return _resume_helper

 
