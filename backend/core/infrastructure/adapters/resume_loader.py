"""
Resume loader - handles loading resume data from various file formats.
"""

import os
import json
import uuid
import logging
from typing import List, Any

from backend.core.infrastructure.frameworks.schema_engine import SchemaEngine
from backend.core.models.resume import ResumeSchema
from backend.core.utils.constants import UIConstants
from backend.core.utils.logging_helpers import StandardLogger

logger = logging.getLogger(__name__)


class ResumeLoader:
    """Loads resume data from JSON files."""
    
    SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    @staticmethod
    def load_from_json(file_path: str) -> List[Any]:
        """
        Load resume data from JSON file using schema-based processing.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of form elements
            
        Raises:
            ValueError: If file path is invalid
            FileNotFoundError: If file doesn't exist
        """
        if not file_path or not file_path.strip():
            raise ValueError("No file path provided")
        
        file_path = file_path.strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        data = ResumeLoader._read_json_file(file_path)
        return ResumeLoader._convert_to_form_format(data)
    
    @staticmethod
    def _read_json_file(file_path: str) -> dict:
        """Read JSON file with multiple encoding attempts."""
        for encoding in ResumeLoader.SUPPORTED_ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return json.load(f)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        
        raise ValueError("Could not decode JSON file with any supported encoding")
    
    @staticmethod
    def _convert_to_form_format(data: dict) -> List[Any]:
        """Convert JSON data to form element list."""
        request_id = str(uuid.uuid4())
        SchemaEngine.log_schema_operation("load_resume_json", "ResumeSchema", len(data))
        
        result = []
        
        # Extract personal info (handle both nested and flat formats)
        if 'personal_info' in data:
            personal_info = SchemaEngine.extract_fields(data.get('personal_info', {}), ResumeSchema.PERSONAL_INFO)
        else:
            personal_info = SchemaEngine.extract_fields(data, ResumeSchema.PERSONAL_INFO)
        
        personal_order = ResumeSchema.get_field_order('personal_info')
        result.extend([personal_info.get(field, '') for field in personal_order])
        result.append("")
        
        # Education
        result.extend([""] * UIConstants.EDUCATION_INPUT_FIELDS)
        education_data = SchemaEngine.extract_list_fields(data.get('education', []), ResumeSchema.EDUCATION)
        education_table = SchemaEngine.convert_to_table_format(
            education_data, ResumeSchema.EDUCATION, ResumeSchema.get_field_order('education')
        )
        result.append(education_table)
        
        # Experience
        result.extend([""] * UIConstants.WORK_INPUT_FIELDS)
        # Preserve achievements lists before schema extraction converts them to strings
        raw_experience = data.get('experience', [])
        raw_achievements = []
        for exp in raw_experience:
            achievements = exp.get('achievements', [])
            raw_achievements.append(achievements if isinstance(achievements, list) else [])

        experience_data = SchemaEngine.extract_list_fields(raw_experience, ResumeSchema.EXPERIENCE)
        for i, exp in enumerate(experience_data):
            achievements = raw_achievements[i] if i < len(raw_achievements) else []
            exp['achievements'] = '\n'.join([f"- {item}" for item in achievements if item])
        
        experience_table = SchemaEngine.convert_to_table_format(
            experience_data, ResumeSchema.EXPERIENCE, ResumeSchema.get_field_order('experience')
        )
        result.append(experience_table)
        
        # Skills
        result.extend([""] * UIConstants.SKILLS_INPUT_FIELDS)
        skills_data = SchemaEngine.extract_list_fields(data.get('skills', []), ResumeSchema.SKILLS)
        skills_table = SchemaEngine.convert_to_table_format(
            skills_data, ResumeSchema.SKILLS, ResumeSchema.get_field_order('skills')
        )
        result.append(skills_table)
        
        # Projects
        result.extend([""] * UIConstants.PROJECTS_INPUT_FIELDS)
        projects_data = SchemaEngine.extract_list_fields(data.get('projects', []), ResumeSchema.PROJECTS)
        projects_table = SchemaEngine.convert_to_table_format(
            projects_data, ResumeSchema.PROJECTS, ResumeSchema.get_field_order('projects')
        )
        result.append(projects_table)
        
        # Certifications
        result.extend([""] * UIConstants.CERTIFICATIONS_INPUT_FIELDS)
        certifications_data = SchemaEngine.extract_list_fields(data.get('certifications', []), ResumeSchema.CERTIFICATIONS)
        certifications_table = SchemaEngine.convert_to_table_format(
            certifications_data, ResumeSchema.CERTIFICATIONS, ResumeSchema.get_field_order('certifications')
        )
        result.append(certifications_table)
        
        # Others
        others_data = data.get('others', {})
        result.append(others_data)
        
        # Validation
        expected_count = UIConstants.FORM_BASE_COUNT + 1
        actual_count = len(result)
        
        StandardLogger.log_data_operation("load_resume_json", request_id, "form_elements", actual_count)
        
        if actual_count != expected_count:
            StandardLogger.log_operation_warning("load_resume_json", request_id,
                f"Output count mismatch: expected {expected_count}, got {actual_count}")
        
        SchemaEngine.log_schema_operation("load_resume_json", "ResumeSchema", actual_count, success=True)
        return result
 
