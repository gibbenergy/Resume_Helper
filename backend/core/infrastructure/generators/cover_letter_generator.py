"""
Cover Letter Generator for the Resume Helper application.
"""

import os
import json
import datetime
import logging
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader

# Import shared paths from package __init__.py
from . import TEMPLATE_DIR, TEMP_DIR

from backend.core.utils.pdf_generator import generate_pdf_sync

logger = logging.getLogger(__name__)


class CoverLetterGenerator:
    """
    Class for generating cover letters in PDF format.
    """
    
    def __init__(self, template_dir: str = None, temp_dir: str = None):
        """
        Initialize the CoverLetterGenerator.
        
        Args:
            template_dir: Directory containing the cover letter template (optional, uses shared path by default)
            temp_dir: Directory for temporary files (optional, uses shared path by default)
        """
        if template_dir is None:
            self.template_dir = TEMPLATE_DIR
        else:
            self.template_dir = template_dir
            
        if temp_dir is None:
            self.temp_dir = TEMP_DIR
        else:
            self.temp_dir = temp_dir
            
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template('classic_cover_letter.html')
    
    def format_cover_letter_data(self, candidate_data: Dict[str, Any], recipient_data: Optional[Dict[str, Any]] = None, 
                             content: str = "", job_description: str = "", 
                             job_position: str = "", company_name: str = "",
                             letter_title: str = "", recipient_greeting: str = "") -> Dict[str, Any]:
        """
        Format candidate and recipient data for the cover letter template.
        
        Args:
            candidate_data: Dictionary containing candidate information
            recipient_data: Dictionary containing recipient information (optional)
            content: Cover letter content
            job_description: Job description text (optional)
            job_position: Job position title (optional)
            company_name: Company name (optional)
            
        Returns:
            Formatted data dictionary for the template
        """
        today = datetime.datetime.now()
        formatted_date = today.strftime("%B %d, %Y")
        
        logger.debug(f"Incoming candidate data: {json.dumps(candidate_data, indent=2)}")
        logger.debug(f"Incoming job details - Position: '{job_position}', Company: '{company_name}'")
        
        if not company_name and recipient_data and recipient_data.get('company_name'):
            company_name = recipient_data.get('company_name')
        
        name_prefix = candidate_data.get('name_prefix', '').strip()
        full_name = candidate_data.get('full_name', 'Candidate Name')
        
        if name_prefix:
            display_name = f"{name_prefix} {full_name}"
        else:
            display_name = full_name
        
        data = {
            'full_name': display_name,
            'signature_name': full_name,
            'current_address': candidate_data.get('current_address', ''),
            'location': candidate_data.get('location', ''),
            'email': candidate_data.get('email', ''),
            'phone': candidate_data.get('phone', ''),
            'linkedin_url': candidate_data.get('linkedin_url', ''),
            'date': formatted_date,
            'job_position': job_position,
            'company_name': company_name,
            'letter_title': letter_title,
            'recipient_greeting': recipient_greeting,
            'recipient_name': '',
            'company_address': '',
            'cover_letter_content': content
        }
        
        if recipient_data:
            data.update({
                'recipient_name': recipient_data.get('recipient_name', ''),
                'company_address': recipient_data.get('company_address', ''),
            })
            
            if not company_name and recipient_data.get('company_name'):
                data['company_name'] = recipient_data.get('company_name')
        
        logger.debug(f"Formatted template data: {json.dumps(data, indent=2)}")
        
        return data
    
    def generate_cover_letter(self, 
                             candidate_data: Dict[str, Any], 
                             cover_letter_content: str,
                             recipient_data: Optional[Dict[str, Any]] = None,
                             output_path: Optional[str] = None,
                             job_description: str = "",
                             job_position: str = "",
                             company_name: str = "",
                             letter_title: str = "",
                             recipient_greeting: str = "") -> str:
        """
        Generate a cover letter PDF from candidate data and cover letter content.
        
        Args:
            candidate_data: Dictionary containing candidate information
            cover_letter_content: Cover letter content generated by AI
            recipient_data: Dictionary containing recipient information (optional)
            output_path: Path to save the PDF file (optional)
            job_description: Job description text (optional)
            job_position: Job position title (optional)
            company_name: Company name (optional)
            
        Returns:
            Path to the generated PDF file
        """
        try:
            if output_path is None:
                output_path = os.path.join(self.temp_dir, 'cover_letter.pdf')
            
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            data = self.format_cover_letter_data(
                candidate_data=candidate_data,
                recipient_data=recipient_data,
                content=cover_letter_content,
                job_description=job_description,
                job_position=job_position,
                company_name=company_name,
                letter_title=letter_title,
                recipient_greeting=recipient_greeting
            )
            
            if not data.get('full_name'):
                logger.warning("full_name is missing or empty in the data dictionary")
            
            html_content = self.template.render(**data)
            
            logger.info(f"Generating cover letter PDF at: {output_path}")
            
            success = generate_pdf_sync(html_content, output_path, self.template_dir)
            if not success:
                logger.error(f"Cover letter PDF generation failed for: {output_path}")
                return None
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Cover letter PDF successfully generated at: {output_path} (Size: {file_size} bytes)")
                
                if file_size > 0:
                    logger.debug(f"PDF validation successful: File size is {file_size} bytes")
                    return output_path
                else:
                    logger.error(f"PDF validation failed: File size is 0 bytes")
                    return None
            else:
                logger.error(f"Error: PDF file not created at {output_path}")
                return None
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Error generating cover letter PDF: {str(e)}")
            return None


def generate_cover_letter_pdf(candidate_data: Dict[str, Any], 
                             cover_letter_content: str,
                             recipient_data: Optional[Dict[str, Any]] = None,
                             output_path: Optional[str] = None,
                             template_dir: Optional[str] = None,
                             temp_dir: Optional[str] = None,
                             job_description: str = "",
                             job_position: str = "",
                             company_name: str = "",
                             letter_title: str = "",
                             recipient_greeting: str = "") -> str:
    """
    Generate a cover letter PDF from candidate data and cover letter content.
    
    Args:
        candidate_data: Dictionary containing candidate information
        cover_letter_content: Cover letter content generated by AI
        recipient_data: Dictionary containing recipient information (optional)
        output_path: Path to save the PDF file (optional)
        template_dir: Directory containing the cover letter template (optional)
        temp_dir: Directory for temporary files (optional)
        job_description: Job description text (optional)
        job_position: Job position title (optional)
        company_name: Company name (optional)
        
    Returns:
        Path to the generated PDF file
    """
    generator = CoverLetterGenerator(template_dir=template_dir, temp_dir=temp_dir)
    return generator.generate_cover_letter(
        candidate_data=candidate_data,
        cover_letter_content=cover_letter_content,
        recipient_data=recipient_data,
        output_path=output_path,
        job_description=job_description,
        job_position=job_position,
        company_name=company_name,
        letter_title=letter_title,
        recipient_greeting=recipient_greeting
    )
