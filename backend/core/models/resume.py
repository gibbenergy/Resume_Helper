"""
Resume Schema - Schema definitions for resume data processing

This module defines the schema structure for resume data, including personal info,
education, experience, skills, projects, and certifications.
"""

from typing import Dict, Any, List


class ResumeSchema:
    """Schema definitions for resume data processing."""
    
    # Personal Information Schema
    PERSONAL_INFO = {
        'name_prefix': {
            'default': '',
            'type': str,
            'max_length': 10
        },
        'email': {
            'default': '',
            'type': str,
            'max_length': 254
        },
        'full_name': {
            'default': '',
            'type': str,
            'max_length': 100,
            'required': True
        },
        'phone': {
            'default': '',
            'type': str,
            'max_length': 20
        },
        'current_address': {
            'default': '',
            'aliases': ['address'],
            'type': str,
            'max_length': 200
        },
        'location': {
            'default': '',
            'type': str,
            'max_length': 100
        },
        'citizenship': {
            'default': '',
            'type': str,
            'max_length': 100
        },
        'linkedin_url': {
            'default': '',
            'aliases': ['linkedin'],
            'type': str
        },
        'github_url': {
            'default': '',
            'aliases': ['github'],
            'type': str
        },
        'portfolio_url': {
            'default': '',
            'aliases': ['portfolio'],
            'type': str
        },
        'summary': {
            'default': '',
            'type': str,
            'max_length': 1000
        }
    }
    
    # Education Schema
    EDUCATION = {
        'institution': {
            'default': '',
            'type': str,
            'max_length': 100,
            'required': True
        },
        'degree': {
            'default': '',
            'type': str,
            'max_length': 100,
            'required': True
        },
        'field_of_study': {
            'default': '',
            'aliases': ['field', 'major'],
            'type': str,
            'max_length': 100
        },
        'gpa': {
            'default': '',
            'type': str,
            'max_length': 10
        },
        'start_date': {
            'default': '',
            'type': str,
            'max_length': 20
        },
        'end_date': {
            'default': '',
            'type': str,
            'max_length': 20
        },
        'description': {
            'default': '',
            'type': str,
            'max_length': 2000
        }
    }
    
    # Experience Schema
    EXPERIENCE = {
        'company': {
            'default': '',
            'type': str,
            'max_length': 100,
            'required': True
        },
        'position': {
            'default': '',
            'aliases': ['title', 'job_title'],
            'type': str,
            'max_length': 100,
            'required': True
        },
        'location': {
            'default': '',
            'type': str,
            'max_length': 100
        },
        'start_date': {
            'default': '',
            'type': str,
            'max_length': 20
        },
        'end_date': {
            'default': '',
            'type': str,
            'max_length': 20
        },
        'description': {
            'default': '',
            'type': str,
            'max_length': 2000
        },
        'achievements': {
            'default': '',
            'type': str,
            'max_length': 2000
        }
    }
    
    # Skills Schema
    SKILLS = {
        'category': {
            'default': '',
            'type': str,
            'max_length': 50,
            'required': True
        },
        'name': {
            'default': '',
            'aliases': ['skill', 'skill_name'],
            'type': str,
            'max_length': 100,
            'required': True
        },
        'proficiency': {
            'default': '',
            'aliases': ['level'],
            'type': str,
            'max_length': 20
        }
    }
    
    # Projects Schema
    PROJECTS = {
        'name': {
            'default': '',
            'aliases': ['title', 'project_name'],
            'type': str,
            'max_length': 100,
            'required': True
        },
        'description': {
            'default': '',
            'type': str,
            'max_length': 2000,
            'required': True
        },
        'technologies': {
            'default': '',
            'aliases': ['tech', 'tech_stack'],
            'type': str,
            'max_length': 500
        },
        'url': {
            'default': '',
            'aliases': ['link', 'project_url'],
            'type': str
        },
        'start_date': {
            'default': '',
            'type': str,
            'max_length': 20
        },
        'end_date': {
            'default': '',
            'type': str,
            'max_length': 20
        }
    }
    
    # Certifications Schema
    CERTIFICATIONS = {
        'name': {
            'default': '',
            'aliases': ['certification', 'cert_name'],
            'type': str,
            'max_length': 100,
            'required': True
        },
        'issuer': {
            'default': '',
            'aliases': ['issuing_organization', 'organization'],
            'type': str,
            'max_length': 100,
            'required': True
        },
        'date_obtained': {
            'default': '',
            'aliases': ['date', 'issue_date'],
            'type': str,
            'max_length': 20
        },
        'credential_id': {
            'default': '',
            'aliases': ['id', 'certificate_id'],
            'type': str,
            'max_length': 100
        },
        'url': {
            'default': '',
            'aliases': ['credential_url', 'cert_url'],
            'type': str
        }
    }
    
    # Field order for table display
    FIELD_ORDER = {
        'personal_info': [
            'name_prefix', 'email', 'full_name', 'phone', 'current_address', 'location',
            'citizenship', 'linkedin_url', 'github_url', 'portfolio_url', 'summary'
        ],
        'education': [
            'institution', 'degree', 'field_of_study', 'gpa', 
            'start_date', 'end_date', 'description'
        ],
        'experience': [
            'company', 'position', 'location', 'start_date', 'end_date',
            'description', 'achievements'
        ],
        'skills': [
            'category', 'name', 'proficiency'
        ],
        'projects': [
            'name', 'description', 'technologies', 'url', 'start_date', 'end_date'
        ],
        'certifications': [
            'name', 'issuer', 'date_obtained', 'credential_id', 'url'
        ]
    }
    
    # Section mappings for data processing
    SECTION_MAPPINGS = {
        'personal_info': {
            'schema': PERSONAL_INFO,
            'field_order': FIELD_ORDER['personal_info']
        },
        'education': {
            'schema': EDUCATION,
            'field_order': FIELD_ORDER['education']
        },
        'experience': {
            'schema': EXPERIENCE,
            'field_order': FIELD_ORDER['experience']
        },
        'skills': {
            'schema': SKILLS,
            'field_order': FIELD_ORDER['skills']
        },
        'projects': {
            'schema': PROJECTS,
            'field_order': FIELD_ORDER['projects']
        },
        'certifications': {
            'schema': CERTIFICATIONS,
            'field_order': FIELD_ORDER['certifications']
        }
    }
    
    @classmethod
    def get_field_order(cls, section_name: str) -> List[str]:
        """Get field order for a specific section."""
        return cls.SECTION_MAPPINGS.get(section_name, {}).get('field_order', []) 
