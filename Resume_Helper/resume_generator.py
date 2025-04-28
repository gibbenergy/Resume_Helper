import os
import json
import tempfile
import uuid
import logging
import time
import datetime
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Tuple, List, Optional
from weasyprint import HTML
from Resume_Helper.utils.file_utils import atomic_write_json, atomic_read_json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'Resume_Templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template('classic_template.html')
        self.temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # Clean up old files in temp directory
        self.cleanup_temp_folder()

    def cleanup_temp_folder(self, max_age_hours=0):
        """
        Remove files older than max_age_hours from the temp directory.
        
        Args:
            max_age_hours: Maximum age of files in hours before deletion
        
        Returns:
            tuple: (num_files_removed, num_files_kept)
        """
        if not os.path.exists(self.temp_dir):
            return 0, 0
            
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        
        files_removed = 0
        files_kept = 0
        
        logger.info(f"Cleaning up temp folder: {self.temp_dir}")
        
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            
            # Skip directories
            if not os.path.isfile(file_path):
                continue
                
            # Check file age
            file_age = now - os.path.getmtime(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    files_removed += 1
                    logger.info(f"Removed old temp file: {filename} (age: {datetime.timedelta(seconds=int(file_age))})")
                except Exception as e:
                    logger.error(f"Error removing temp file {filename}: {str(e)}")
            else:
                files_kept += 1
                
        logger.info(f"Temp folder cleanup complete: {files_removed} files removed, {files_kept} files kept")
        return files_removed, files_kept



    def format_profile_data(self, profile):
        """Format profile data for the template."""
        # Ensure backward compatibility by converting field names
        # For templates that still use 'educations' and 'experiences'
        
        # Handle education field
        if 'education' in profile:
            profile['educations'] = profile['education']  # For backward compatibility
        elif 'educations' in profile and 'education' not in profile:
            profile['education'] = profile['educations']
            
        # Handle experience field
        if 'experience' in profile:
            profile['experiences'] = profile['experience']  # For backward compatibility
        elif 'work_experience' in profile:
            profile['experience'] = profile['work_experience']
            profile['experiences'] = profile['work_experience']  # For backward compatibility
        elif 'experiences' in profile and 'experience' not in profile:
            profile['experience'] = profile['experiences']
            
        # Handle summary field
        if 'summary' in profile and 'professional_summary' not in profile:
            profile['professional_summary'] = profile['summary']
            
        # Group skills by category
        skills_by_category = {}
        if isinstance(profile.get('skills'), dict):
            # Skills are already grouped by category
            skills_by_category = profile['skills']
        elif isinstance(profile.get('skills'), list):
            # Convert list of skills to category groups
            for skill in profile['skills']:
                cat = skill.get('category', '')
                if cat not in skills_by_category:
                    skills_by_category[cat] = []
                skill_text = skill.get('skill_name', '') or skill.get('name', '')
                if skill.get('proficiency'):
                    skill_text += f" ({skill['proficiency']})"
                skills_by_category[cat].append(skill_text)

        # Format data for template
        data = {
            'full_name': profile.get('full_name', ''),
            'email': profile.get('email', ''),
            'phone': profile.get('phone', ''),
            'current_address': profile.get('current_address', ''),
            'location': profile.get('location', ''),
            'linkedin_url': profile.get('linkedin_url', ''),
            'github_url': profile.get('github_url', ''),
            'portfolio_url': profile.get('portfolio_url', ''),
            'summary': profile.get('summary', ''),
            'professional_summary': profile.get('professional_summary', profile.get('summary', '')),
            'educations': profile.get('educations', profile.get('education', [])),
            'experiences': profile.get('experiences', profile.get('work_experience', [])),
            'projects': profile.get('projects', []),
            'skills': skills_by_category,
            'certifications': profile.get('certifications', [])
        }
        return data

    def generate_resume(self, profile_data: Dict[str, Any], output_path: str = None) -> str:
        """Generate PDF resume from profile data."""
        try:
            # Use default output path if none provided
            if output_path is None:
                # Ensure temp directory exists
                os.makedirs(self.temp_dir, exist_ok=True)
                output_path = os.path.join(self.temp_dir, 'resume.pdf')
            
            print(f"Generating resume PDF at: {output_path}")
            
            # Generate PDF
            success = self.generate_pdf(profile_data, output_path)
            
            if success and os.path.exists(output_path):
                print(f"Resume PDF successfully generated at: {output_path}")
                # Get absolute path to ensure Gradio can access it
                abs_path = os.path.abspath(output_path)
                print(f"Absolute path: {abs_path}")
                return abs_path
            else:
                print(f"Resume PDF generation failed. File does not exist at: {output_path}")
                return None
        except Exception as e:
            print(f"Error in generate_resume: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def export_json(self, profile_data: Dict[str, Any], output_path: str = None) -> Tuple[bool, str]:
        """
        Export profile data as JSON using atomic write operations.
        
        Args:
            profile_data: The profile data to export
            output_path: The path to write the data to
            
        Returns:
            A tuple of (success, error_message)
        """
        # Generate a unique request ID for logging
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Starting JSON export")
        
        try:
            # Use default output path if none provided
            if output_path is None:
                # Ensure temp directory exists
                os.makedirs(self.temp_dir, exist_ok=True)
                output_path = os.path.join(self.temp_dir, 'resume.json')
            
            logger.info(f"[Request {request_id}] Exporting JSON to: {output_path}")
            
            # Format data for export, ensuring field names are updated
            data = self.format_profile_data(profile_data)
            
            # Add a unique identifier to the data for tracking
            data['_export_id'] = request_id
            data['_export_timestamp'] = str(uuid.uuid1())  # Time-based UUID
            
            # Use atomic write operation
            success, error_msg = atomic_write_json(data, output_path)
            
            if success:
                logger.info(f"[Request {request_id}] JSON file successfully exported")
                return True, ""
            else:
                logger.error(f"[Request {request_id}] JSON export failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error exporting JSON: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            import traceback
            logger.error(f"[Request {request_id}] {traceback.format_exc()}")
            return False, error_msg

    def import_json(self, input_path: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Import profile data from a JSON file using atomic read operations.
        
        Args:
            input_path: The path to read the data from
            
        Returns:
            A tuple of (data, error_message)
        """
        # Generate a unique request ID for logging
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Starting JSON import from {input_path}")
        
        # Use atomic read operation
        data, error_msg = atomic_read_json(input_path)
        
        if data is not None:
            logger.info(f"[Request {request_id}] JSON file successfully imported")
            
            # Log the export ID if present
            if '_export_id' in data:
                logger.info(f"[Request {request_id}] Imported data with export ID: {data['_export_id']}")
            
            return data, ""
        else:
            logger.error(f"[Request {request_id}] JSON import failed: {error_msg}")
            return None, error_msg
    
    def generate_pdf(self, profile: Dict[str, Any], output_path: str, template_style: str = None) -> bool:
        """Generate PDF resume from profile data using WeasyPrint."""
        try:
            # Ensure temp directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Format data for template
            data = self.format_profile_data(profile)
            
            # Save formatted data for debugging
            debug_path = output_path.replace('.pdf', '_debug.json')
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            # Render HTML
            html_content = self.template.render(**data)
            
            print(f"Generating PDF at: {output_path}")
            
            # Use WeasyPrint to generate PDF directly from HTML string
            HTML(string=html_content, base_url=self.template_dir).write_pdf(output_path)
            
            # Verify the PDF was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"PDF successfully generated at: {output_path} (Size: {file_size} bytes)")
                
                # Verify the PDF is valid (non-zero size)
                if file_size > 0:
                    print(f"PDF validation successful: File size is {file_size} bytes")
                    return True
                else:
                    print(f"PDF validation failed: File size is 0 bytes")
                    return False
            else:
                print(f"PDF generation failed: File not created at {output_path}")
                return False
                
        except Exception as e:
            print(f"Error in generate_pdf: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
