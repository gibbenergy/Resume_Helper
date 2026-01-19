"""
Generators package for Resume Helper

This package provides document generators for resumes, cover letters, and analysis reports.
Shared paths and utilities are defined here for use by all generator modules.
"""

import os
import sys

# =============================================================================
# Package-level path setup
# =============================================================================

# Get the directory of this __init__.py file (generators/)
_GENERATORS_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up two levels: generators/ -> infrastructure/ -> Resume_Helper/
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(_GENERATORS_DIR))

# Add parent to sys.path for imports (if not already there)
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

# Define shared paths that all generators need
TEMPLATE_DIR = os.path.join(_GENERATORS_DIR, 'templates')
TEMP_DIR = os.path.join(_PACKAGE_ROOT, 'temp')

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# =============================================================================
# Expose generators for easier imports
# =============================================================================

from .resume_generator import ResumeGenerator
from .analysis_pdf_generator import (
    generate_job_analysis_pdf,
    generate_improvement_suggestions_pdf
)

# Define what gets imported with "from generators import *"
__all__ = [
    'ResumeGenerator',
    'generate_job_analysis_pdf',
    'generate_improvement_suggestions_pdf',
    'TEMPLATE_DIR',
    'TEMP_DIR',
]
