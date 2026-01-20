"""
Fixture service - loads sample/example resume data.
"""

import os
import json
import logging
from typing import List, Any, Dict

logger = logging.getLogger(__name__)


class FixtureService:
    """Loads sample resume fixtures for demonstration."""
    
    def __init__(self, fixtures_dir: str = None):
        """Initialize with fixtures directory path."""
        if fixtures_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            fixtures_dir = os.path.join(os.path.dirname(current_dir), 'fixtures')
        self.fixtures_dir = fixtures_dir
    
    def load_software_developer_example(self) -> List[Any]:
        """Load Software Developer example from JSON file."""
        return self._load_example('sample_resume_software_engineer.json', 'Software Developer')
    
    def load_process_engineer_example(self) -> List[Any]:
        """Load Process Engineer example from JSON file."""
        return self._load_example('sample_resume_process_engineer.json', 'Process Engineer')
    
    def _load_example(self, filename: str, example_name: str) -> List[Any]:
        """Load an example resume from a JSON file."""
        try:
            sample_file = os.path.join(self.fixtures_dir, filename)
            with open(sample_file, 'r', encoding='utf-8') as f:
                example_data = json.load(f)
            
            return self._convert_to_form_format(example_data, example_name)
        except Exception as e:
            logger.error(f"Error loading {example_name} example: {e}")
            return self._get_error_response(f"Error loading {example_name} example: {str(e)}")
    
    def _convert_to_form_format(self, data: Dict, example_name: str) -> List[Any]:
        """Convert JSON data to form format."""
        education_table = self._build_education_table(data.get('education', []))
        work_table = self._build_work_table(data.get('experience', []))
        skills_table = self._build_skills_table(data.get('skills', []))
        projects_table = self._build_projects_table(data.get('projects', []))
        certs_table = self._build_certifications_table(data.get('certifications', []))
        
        return [
            data.get('name_prefix', ''),
            data.get('email', ''),
            data.get('full_name', ''),
            data.get('phone', ''),
            data.get('current_address', ''),
            data.get('location', ''),
            data.get('citizenship', ''),
            data.get('linkedin_url', ''),
            data.get('github_url', ''),
            data.get('portfolio_url', ''),
            data.get('summary', ''),
            f"{example_name} example loaded successfully!",
            "", "", "", "", "", "", "",
            education_table,
            "", "", "", "", "", "", "",
            work_table,
            "", "", "",
            skills_table,
            "", "", "", "", "", "",
            projects_table,
            "", "", "", "", "",
            certs_table,
            data.get('others', {})
        ]
    
    def _build_education_table(self, education: List[Dict]) -> List[List]:
        """Build education table from list."""
        table = []
        for edu in education:
            table.append([
                edu.get('institution', ''),
                edu.get('degree', ''),
                edu.get('field_of_study', ''),
                edu.get('gpa', ''),
                edu.get('start_date', ''),
                edu.get('end_date', ''),
                edu.get('description', '')
            ])
        return table
    
    def _build_work_table(self, experience: List[Dict]) -> List[List]:
        """Build work experience table from list."""
        table = []
        for work in experience:
            achievements = work.get('achievements', [])
            if isinstance(achievements, list):
                achievements_str = '\n'.join([f"- {a}" for a in achievements])
            else:
                achievements_str = str(achievements)
            
            table.append([
                work.get('company', ''),
                work.get('position', ''),
                work.get('location', ''),
                work.get('start_date', ''),
                work.get('end_date', ''),
                work.get('description', ''),
                achievements_str
            ])
        return table
    
    def _build_skills_table(self, skills: List[Dict]) -> List[List]:
        """Build skills table from list."""
        table = []
        for skill in skills:
            table.append([
                skill.get('category', ''),
                skill.get('name', ''),
                skill.get('proficiency', '')
            ])
        return table
    
    def _build_projects_table(self, projects: List[Dict]) -> List[List]:
        """Build projects table from list."""
        table = []
        for project in projects:
            table.append([
                project.get('name', ''),
                project.get('description', ''),
                project.get('technologies', ''),
                project.get('url', ''),
                project.get('start_date', ''),
                project.get('end_date', '')
            ])
        return table
    
    def _build_certifications_table(self, certifications: List[Dict]) -> List[List]:
        """Build certifications table from list."""
        table = []
        for cert in certifications:
            table.append([
                cert.get('name', ''),
                cert.get('issuer', ''),
                cert.get('date_obtained', ''),
                cert.get('credential_id', ''),
                cert.get('url', '')
            ])
        return table
    
    def _get_error_response(self, error_message: str) -> List[Any]:
        """Return error response in form format."""
        return [
            "", "", "", "", "", "", "", "", "", "", "", error_message,
            "", "", "", "", "", "", "", [],
            "", "", "", "", "", "", "", [],
            "", "", "", [],
            "", "", "", "", "", "", [],
            "", "", "", "", "", [],
            {}
        ]
 
