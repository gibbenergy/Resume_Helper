"""
Profile builder - converts table/form data to profile dictionaries.
"""

import logging
from typing import Dict, Any, List, Optional

from backend.core.infrastructure.adapters.table_data_extractor import TableDataExtractor
from backend.core.utils.constants import UIConstants

logger = logging.getLogger(__name__)


class ProfileBuilder:
    """Builds profile dictionaries from form/table data."""
    
    @staticmethod
    def build_profile_dict(
        name_prefix: str,
        email: str,
        full_name: str,
        phone: str,
        current_address: str,
        location: str,
        citizenship: str,
        linkedin_url: str,
        github_url: str,
        portfolio_url: str,
        summary: str,
        education_table: Any,
        experience_table: Any,
        skills_table: Any,
        projects_table: Any,
        certifications_table: Any,
        others_sections_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Build profile dictionary from form values."""
        profile = {
            'name_prefix': name_prefix,
            'email': email,
            'full_name': full_name,
            'phone': phone,
            'current_address': current_address,
            'location': location,
            'citizenship': citizenship,
            'linkedin_url': linkedin_url,
            'github_url': github_url,
            'portfolio_url': portfolio_url,
            'summary': summary,
            'education': [],
            'experience': [],
            'skills': [],
            'projects': [],
            'certifications': [],
            'others': {}
        }

        profile['education'] = ProfileBuilder._extract_education(education_table)
        profile['experience'] = ProfileBuilder._extract_experience(experience_table)
        profile['skills'] = ProfileBuilder._extract_skills(skills_table)
        profile['projects'] = ProfileBuilder._extract_projects(projects_table)
        profile['certifications'] = ProfileBuilder._extract_certifications(certifications_table)
        profile['others'] = ProfileBuilder._extract_others(others_sections_data)

        return profile
    
    @staticmethod
    def _extract_education(education_table: Any) -> List[Dict]:
        """Extract education entries from table data."""
        result = []
        try:
            edu_data = TableDataExtractor.extract_table_data(education_table)
            for row in edu_data:
                if isinstance(row, list) and len(row) >= UIConstants.EDUCATION_INPUT_FIELDS and any(str(x).strip() for x in row):
                    result.append({
                        'institution': str(row[0]),
                        'degree': str(row[1]),
                        'field_of_study': str(row[2]),
                        'gpa': str(row[3]),
                        'start_date': str(row[4]),
                        'end_date': str(row[5]),
                        'description': str(row[6])
                    })
        except Exception as e:
            logger.debug(f"Error extracting education: {e}")
        return result
    
    @staticmethod
    def _extract_experience(experience_table: Any) -> List[Dict]:
        """Extract work experience entries from table data."""
        result = []
        try:
            work_data = TableDataExtractor.extract_table_data(experience_table)
            for row in work_data:
                if isinstance(row, list) and len(row) >= UIConstants.WORK_INPUT_FIELDS and any(str(x).strip() for x in row):
                    achievements_text = str(row[6])
                    achievements_value = ProfileBuilder._parse_achievements(achievements_text)
                    
                    result.append({
                        'company': str(row[0]),
                        'position': str(row[1]),
                        'location': str(row[2]),
                        'start_date': str(row[3]),
                        'end_date': str(row[4]),
                        'description': str(row[5]),
                        'achievements': achievements_value
                    })
        except Exception as e:
            logger.debug(f"Error extracting experience: {e}")
        return result
    
    @staticmethod
    def _parse_achievements(achievements_text: str) -> List[str]:
        """Parse achievements text into a list."""
        if not achievements_text.strip():
            return []
        
        if '-' in achievements_text:
            achievement_lines = achievements_text.split('\n')
            achievements_list = []
            
            for line in achievement_lines:
                line = line.strip()
                if line:
                    if line.startswith('- '):
                        achievements_list.append(line[2:])
                    elif line.startswith('-'):
                        achievements_list.append(line[1:].strip())
                    else:
                        achievements_list.append(line)
            
            return achievements_list
        else:
            return [achievements_text]
    
    @staticmethod
    def _extract_skills(skills_table: Any) -> List[Dict]:
        """Extract skills from table data."""
        result = []
        try:
            skill_data = TableDataExtractor.extract_table_data(skills_table)
            for row in skill_data:
                if isinstance(row, list) and len(row) >= UIConstants.SKILLS_INPUT_FIELDS and any(str(x).strip() for x in row):
                    result.append({
                        'category': str(row[0]),
                        'name': str(row[1]),
                        'proficiency': str(row[2])
                    })
        except Exception as e:
            logger.debug(f"Error extracting skills: {e}")
        return result
    
    @staticmethod
    def _extract_projects(projects_table: Any) -> List[Dict]:
        """Extract projects from table data."""
        result = []
        try:
            project_data = TableDataExtractor.extract_table_data(projects_table)
            for row in project_data:
                if isinstance(row, list) and len(row) >= UIConstants.PROJECTS_INPUT_FIELDS and any(str(x).strip() for x in row):
                    result.append({
                        'name': str(row[0]),
                        'description': str(row[1]),
                        'technologies': str(row[2]),
                        'url': str(row[3]),
                        'start_date': str(row[4]),
                        'end_date': str(row[5])
                    })
        except Exception as e:
            logger.debug(f"Error extracting projects: {e}")
        return result
    
    @staticmethod
    def _extract_certifications(certifications_table: Any) -> List[Dict]:
        """Extract certifications from table data."""
        result = []
        try:
            cert_data = TableDataExtractor.extract_table_data(certifications_table)
            for row in cert_data:
                if isinstance(row, list) and len(row) >= UIConstants.CERTIFICATIONS_INPUT_FIELDS and any(str(x).strip() for x in row):
                    result.append({
                        'name': str(row[0]),
                        'issuer': str(row[1]),
                        'date_obtained': str(row[2]),
                        'credential_id': str(row[3]),
                        'url': str(row[4])
                    })
        except Exception as e:
            logger.debug(f"Error extracting certifications: {e}")
        return result
    
    @staticmethod
    def _extract_others(others_sections_data: Optional[Dict]) -> Dict:
        """Extract other sections data."""
        result = {}
        try:
            if others_sections_data and isinstance(others_sections_data, dict):
                for section_name, items in others_sections_data.items():
                    if items and isinstance(items, list):
                        section_items = []
                        for item in items:
                            if isinstance(item, dict):
                                section_items.append({
                                    'title': item.get('title', ''),
                                    'organization': item.get('organization', ''),
                                    'date': item.get('date', ''),
                                    'location': item.get('location', ''),
                                    'description': item.get('description', ''),
                                    'url': item.get('url', '')
                                })
                        if section_items:
                            result[section_name] = section_items
        except Exception as e:
            logger.debug(f"Error extracting others: {e}")
        return result
 
