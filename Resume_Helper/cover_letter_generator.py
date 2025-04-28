"""
Cover Letter Generator for the Resume Helper application.
"""

import os
import json
import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class CoverLetterGenerator:
    """
    Class for generating cover letters in PDF format.
    """
    
    def __init__(self, template_dir: str = None, temp_dir: str = None):
        """
        Initialize the CoverLetterGenerator.
        
        Args:
            template_dir: Directory containing the cover letter template
            temp_dir: Directory for temporary files
        """
        # Set template directory
        if template_dir is None:
            self.template_dir = os.path.join(os.path.dirname(__file__), 'Resume_Templates')
        else:
            self.template_dir = template_dir
            
        # Set temporary directory
        if temp_dir is None:
            self.temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        else:
            self.temp_dir = temp_dir
            
        # Create temporary directory if it doesn't exist
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
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
        # Format current date
        today = datetime.datetime.now()
        formatted_date = today.strftime("%B %d, %Y")
        
        # Log the incoming candidate data for debugging
        print(f"Incoming candidate data: {json.dumps(candidate_data, indent=2)}")
        print(f"Incoming job details - Position: '{job_position}', Company: '{company_name}'")
        
        # Use provided job position and company name if available
        # If not provided, try to get from recipient data
        if not company_name and recipient_data and recipient_data.get('company_name'):
            company_name = recipient_data.get('company_name')
        
        # Ensure all required keys are present in candidate_data
        required_keys = ['full_name', 'current_address', 'location', 'email', 'phone', 'linkedin_url']
        for key in required_keys:
            if key not in candidate_data or not candidate_data[key]:
                print(f"Warning: Missing or empty candidate data for key: {key}")
        
        # Prepare template data with candidate information
        data = {
            # Candidate information - ensure all keys exist with fallbacks
            'full_name': candidate_data.get('full_name', candidate_data.get('name', 'Candidate Name')),
            'current_address': candidate_data.get('current_address', candidate_data.get('address', '')),
            'location': candidate_data.get('location', ''),
            'email': candidate_data.get('email', ''),
            'phone': candidate_data.get('phone', ''),
            'linkedin_url': candidate_data.get('linkedin_url', ''),
            
            # Date information
            'date': formatted_date,
            
            # Job and company information - use explicitly provided values
            'job_position': job_position,
            'company_name': company_name,
            
            # Letter title and greeting (if provided)
            'letter_title': letter_title,
            'recipient_greeting': recipient_greeting,
            
            # Recipient information (defaults)
            'recipient_name': '',
            'company_address': '',
            
            # Cover letter content
            'cover_letter_content': content
        }
        
        # Add recipient information if provided
        if recipient_data:
            data.update({
                'recipient_name': recipient_data.get('recipient_name', ''),
                # Only update company_name if not already set and available in recipient_data
                'company_address': recipient_data.get('company_address', ''),
            })
            
            # Only override company_name from recipient_data if job_position wasn't explicitly provided
            if not company_name and recipient_data.get('company_name'):
                data['company_name'] = recipient_data.get('company_name')
        
        # Log the formatted data for debugging
        print(f"Formatted template data: {json.dumps(data, indent=2)}")
        
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
            cover_letter_content: Cover letter content generated by Gemini
            recipient_data: Dictionary containing recipient information (optional)
            output_path: Path to save the PDF file (optional)
            job_description: Job description text (optional)
            job_position: Job position title (optional)
            company_name: Company name (optional)
            
        Returns:
            Path to the generated PDF file
        """
        try:
            # Set default output path if not provided
            if output_path is None:
                output_path = os.path.join(self.temp_dir, 'cover_letter.pdf')
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Format data for template
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
            
            # Save formatted data for debugging
            debug_path = output_path.replace('.pdf', '_debug.json')
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"Saved debug data to: {debug_path}")
            
            # Verify critical fields are present
            if not data.get('full_name'):
                print("WARNING: full_name is missing or empty in the data dictionary")
            
            # Render HTML template
            html_content = self.template.render(**data)
            
            # Save rendered HTML for debugging
            html_debug_path = output_path.replace('.pdf', '_debug.html')
            with open(html_debug_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Saved debug HTML to: {html_debug_path}")
            
            print(f"Generating cover letter PDF at: {output_path}")
            
            # Generate PDF using WeasyPrint
            HTML(string=html_content, base_url=self.template_dir).write_pdf(output_path)
            
            # Verify the PDF was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"Cover letter PDF successfully generated at: {output_path} (Size: {file_size} bytes)")
                
                # Verify the PDF is valid (non-zero size)
                if file_size > 0:
                    print(f"PDF validation successful: File size is {file_size} bytes")
                    return output_path
                else:
                    print(f"PDF validation failed: File size is 0 bytes")
                    return None
            else:
                print(f"Error: PDF file not created at {output_path}")
                return None
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error generating cover letter PDF: {str(e)}")
            return None


# Function to generate a cover letter PDF (for direct use in other modules)
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
        cover_letter_content: Cover letter content generated by Gemini
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