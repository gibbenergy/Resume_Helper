"""
PDF Generator for Job Analysis and Improvement Suggestions.
"""

import os
import re
import datetime as dt
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
import logging
import markdown2

# Import shared paths from package __init__.py
from . import TEMPLATE_DIR, TEMP_DIR

from backend.core.utils.pdf_generator import generate_pdf_sync

logger = logging.getLogger(__name__)


def _slug(text: str, default: str = "document") -> str:
    """Convert arbitrary text to filesystem-safe slug."""
    text = re.sub(r"[^A-Za-z0-9]+", "_", text or "")
    return text.strip("_").lower() or default


def _format_markdown(content: str) -> str:
    """Format markdown content for HTML display."""
    if not content:
        return ""
    return markdown2.markdown(content)


def generate_job_analysis_pdf(
    analysis_content: str,
    company_name: str = "",
    job_position: str = "",
    output_path: Optional[str] = None,
    temp_dir: Optional[str] = None
) -> Optional[str]:
    """
    Generate a PDF for job analysis report.
    
    Args:
        analysis_content: The formatted analysis text
        company_name: Company name for the header
        job_position: Job position for the header
        output_path: Output file path, auto-generated if None
        temp_dir: Directory for temp files (optional, uses shared path by default)
        
    Returns:
        Path to generated PDF file, or None if failed
    """
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("job_analysis_template.html")
        
        formatted_content = _format_markdown(analysis_content)
        
        if not output_path:
            if not temp_dir:
                temp_dir = TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            
            company_slug = _slug(company_name) if company_name else "company"
            timestamp = dt.datetime.now().strftime("%Y%m%d")
            filename = f"{company_slug}_job_analysis_{timestamp}.pdf"
            output_path = os.path.join(temp_dir, filename)
        
        html_content = template.render(
            analysis_content=formatted_content,
            company_name=company_name,
            job_position=job_position,
            analysis_date=dt.datetime.now().strftime("%B %d, %Y")
        )
        
        success = generate_pdf_sync(html_content, output_path)
        
        if success and os.path.exists(output_path):
            logger.info(f"Job analysis PDF generated: {output_path}")
            return output_path
        else:
            logger.error("PDF generation failed - file not created")
            return None
            
    except Exception as e:
        logger.error(f"Error generating job analysis PDF: {e}")
        return None


def generate_improvement_suggestions_pdf(
    suggestions_content: str,
    full_name: str = "",
    company_name: str = "",
    job_position: str = "",
    output_path: Optional[str] = None,
    temp_dir: Optional[str] = None
) -> Optional[str]:
    """
    Generate a PDF for improvement suggestions report.
    
    Args:
        suggestions_content: The formatted suggestions text
        full_name: Candidate's full name
        company_name: Target company name
        job_position: Target job position
        output_path: Output file path, auto-generated if None
        temp_dir: Directory for temp files (optional, uses shared path by default)
        
    Returns:
        Path to generated PDF file, or None if failed
    """
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("improvement_suggestions_template.html")
        
        # Content already has markdown bold headers from JSON formatting
        formatted_content = _format_markdown(suggestions_content)
        
        if not output_path:
            if not temp_dir:
                temp_dir = TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            
            name_slug = _slug(full_name) if full_name else "candidate"
            timestamp = dt.datetime.now().strftime("%Y%m%d")
            filename = f"{name_slug}_improvement_suggestions_{timestamp}.pdf"
            output_path = os.path.join(temp_dir, filename)
        
        html_content = template.render(
            suggestions_content=formatted_content,
            full_name=full_name,
            company_name=company_name,
            job_position=job_position,
            analysis_date=dt.datetime.now().strftime("%B %d, %Y")
        )
        
        success = generate_pdf_sync(html_content, output_path)
        
        if success and os.path.exists(output_path):
            logger.info(f"Improvement suggestions PDF generated: {output_path}")
            return output_path
        else:
            logger.error("PDF generation failed - file not created")
            return None
            
    except Exception as e:
        logger.error(f"Error generating improvement suggestions PDF: {e}")
        return None 
