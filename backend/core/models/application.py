"""
Application Schema - Schema definitions for job application data processing

This module defines the schema structure for job application data, including
all fields, validation rules, and form mappings.
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime


class ApplicationSchema:
    """Schema definitions for job application data processing."""
    
    # Main application fields schema
    FIELDS = {
        'job_url': {
            'default': '',
            'type': str,
            'required': True,
            'max_length': 500
        },
        'company': {
            'default': '',
            'type': str,
            'required': True,
            'max_length': 100
        },
        'position': {
            'default': '',
            'aliases': ['title', 'job_title'],
            'type': str,
            'required': True,
            'max_length': 100
        },
        'location': {
            'default': '',
            'type': str,
            'max_length': 500
        },
        'salary_min': {
            'default': None,
            'type': int,
            'validator': lambda x: x >= 0 if x is not None else True
        },
        'salary_max': {
            'default': None,
            'type': int,
            'validator': lambda x: x >= 0 if x is not None else True
        },
        'date_applied': {
            'default': lambda: date.today().isoformat(),
            'type': str,
            'max_length': 20
        },
        'application_source': {
            'default': 'Other',
            'aliases': ['source'],
            'type': str,
            'max_length': 50
        },
        'priority': {
            'default': 'Medium',
            'type': str,
            'max_length': 20,
            'validator': lambda x: x in ['High', 'Medium', 'Low'] if x else True
        },
        'status': {
            'default': 'Applied',
            'type': str,
            'max_length': 50,
            'validator': lambda x: x in [
                'Applied', 'Offer', 'Rejected', 'Withdrawn'
            ] if x else True
        },
        'description': {
            'default': '',
            'aliases': ['job_description'],
            'type': str,
            'max_length': 25000  # Increased to handle full job analysis text
        },
        'match_score': {
            'default': None,
            'type': int,
            'validator': lambda x: 0 <= x <= 100 if x is not None else True
        },
        'requirements': {
            'default': [],
            'type': list
        },
        'analysis_data': {
            'default': {},
            'type': dict
        },
        'hr_contact': {
            'default': '',
            'aliases': ['hr'],
            'type': str,
            'max_length': 100
        },
        'hiring_manager': {
            'default': '',
            'aliases': ['manager'],
            'type': str,
            'max_length': 100
        },
        'recruiter': {
            'default': '',
            'type': str,
            'max_length': 100
        },
        'referral': {
            'default': '',
            'aliases': ['referral_contact'],
            'type': str,
            'max_length': 100
        },
        'interview_pipeline': {
            'default': {},
            'type': dict
        },
        'timeline': {
            'default': [],
            'type': list
        },
        'notes': {
            'default': '',
            'type': str,
            'max_length': 2000
        },
        'next_actions': {
            'default': [],
            'type': list
        },
        'tags': {
            'default': [],
            'type': list
        },
        'documents': {
            'default': [],
            'type': list
        },
        'created_date': {
            'default': lambda: datetime.now().isoformat(),
            'type': str
        },
        'last_updated': {
            'default': lambda: datetime.now().isoformat(),
            'type': str
        }
    }
    
    # Form field mapping for application tracker tab
    FORM_MAPPING = [
        'job_url',           # 0
        'company',           # 1
        'position',          # 2
        'location',          # 3
        'date_applied',      # 4
        'status',            # 5
        'priority',          # 6
        'application_source', # 7
        'salary_min',        # 8
        'salary_max',        # 9
        'match_score',       # 10
        'description',       # 11
        'notes',             # 12
        'hr_contact',        # 13
        'hiring_manager',    # 14
        'recruiter',         # 15
        'referral'           # 16
    ]
    
    # Interview round schema
    INTERVIEW_ROUND = {
        'status': {
            'default': 'not_started',
            'type': str,
            'validator': lambda x: x in [
                'not_started', 'scheduled', 'completed', 
                'passed', 'failed', 'cancelled', 'on_hold', 'rescheduled'
            ] if x else True
        },
        'date': {
            'default': '',
            'type': str,
            'max_length': 20
        },
        'time': {
            'default': '',
            'type': str,
            'max_length': 10
        },
        'location': {
            'default': '',
            'type': str,
            'max_length': 200
        },
        'interviewer': {
            'default': '',
            'type': str,
            'max_length': 100
        },
        'outcome': {
            'default': '',
            'type': str,
            'validator': lambda x: x in ['passed', 'failed', 'pending', ''] if x else True
        },
        'notes': {
            'default': '',
            'type': str,
            'max_length': 1000
        }
    }
    
    # Timeline entry schema
    TIMELINE_ENTRY = {
        'date': {
            'default': lambda: date.today().isoformat(),
            'type': str,
            'required': True
        },
        'event': {
            'default': '',
            'type': str,
            'required': True,
            'max_length': 200
        },
        'notes': {
            'default': '',
            'type': str,
            'max_length': 500
        }
    }
    
    # Document schema
    DOCUMENT = {
        'name': {
            'default': '',
            'type': str,
            'required': True,
            'max_length': 100
        },
        'type': {
            'default': '',
            'type': str,
            'max_length': 50
        },
        'path': {
            'default': '',
            'type': str,
            'required': True,
            'max_length': 500
        },
        'upload_date': {
            'default': lambda: datetime.now().isoformat(),
            'type': str
        },
        'size': {
            'default': 0,
            'type': int
        }
    }
    
    # Protected fields that should not be updated directly
    PROTECTED_FIELDS = ['created_date', 'id']
    
    # Fields that require special processing
    SPECIAL_PROCESSING = {
        'salary_min': 'integer_conversion',
        'salary_max': 'integer_conversion', 
        'match_score': 'integer_conversion',
        'date_applied': 'date_validation',
        'timeline': 'timeline_management',
        'interview_pipeline': 'interview_management'
    }
    
    @classmethod
    def get_form_fields(cls) -> List[str]:
        """Get list of form field names in order."""
        return cls.FORM_MAPPING.copy()
    
    @classmethod
    def get_required_fields(cls) -> List[str]:
        """Get list of required field names."""
        return [
            field_name for field_name, config in cls.FIELDS.items()
            if config.get('required', False)
        ]
    
    @classmethod
    def get_field_config(cls, field_name: str) -> Dict[str, Any]:
        """Get configuration for a specific field."""
        return cls.FIELDS.get(field_name, {})
    
    @classmethod
    def create_timeline_entry(cls, event: str, notes: str = "", date_val: Optional[str] = None) -> Dict[str, str]:
        """Create a properly formatted timeline entry."""
        entry_date = date_val if date_val is not None else date.today().isoformat()
        return {
            'date': entry_date,
            'event': event,
            'notes': notes
        }
    
    @classmethod
    def create_default_timeline(cls, app_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create default timeline entry for new application."""
        source = app_data.get('application_source', 'Other')
        return [cls.create_timeline_entry(
            event="Application submitted",
            notes=f"Applied through {source}"
        )]
    
    @classmethod
    def process_form_integers(cls, value: Any) -> Any:
        """Process integer fields from form input."""
        if value is None or value == "" or value == "None":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def validate_salary_range(cls, salary_min: Any, salary_max: Any) -> bool:
        """Validate that salary range is logical."""
        if salary_min is not None and salary_max is not None:
            try:
                min_val = int(salary_min) if salary_min else 0
                max_val = int(salary_max) if salary_max else 0
                return min_val <= max_val
            except (ValueError, TypeError):
                return False
        return True
    
    @classmethod
    def get_default_interview_pipeline(cls) -> Dict[str, Dict[str, str]]:
        """Get default interview pipeline structure."""
        default_rounds = [
            "phone_screen", "technical", "panel", 
            "manager", "culture_fit", "final_round"
        ]
        pipeline = {}
        for round_name in default_rounds:
            pipeline[round_name] = {
                'status': 'not_started',
                'date': '',
                'time': '',
                'location': '',
                'interviewer': '',
                'outcome': '',
                'notes': ''
            }
        return pipeline
    
    @classmethod
    def truncate_description(cls, description: str, max_length: int = 25000) -> str:
        """
        Intelligently truncate job description while preserving important information.
        
        Args:
            description: Full job description text
            max_length: Maximum allowed length
            
        Returns:
            Truncated description with ellipsis if needed
        """
        if not description or len(description) <= max_length:
            return description
        
        # Find a good truncation point (end of sentence or paragraph)
        truncate_at = max_length - 50  # Leave space for ellipsis message
        
        # Look for sentence endings near the truncation point
        sentence_endings = ['. ', '.\n', '?\n', '!\n']
        best_cut = truncate_at
        
        for i in range(max(0, truncate_at - 200), min(len(description), truncate_at + 50)):
            for ending in sentence_endings:
                if description[i:i+len(ending)] == ending:
                    best_cut = i + 1
                    break
        
        truncated = description[:best_cut].strip()
        return f"{truncated}\n\n... [Job description truncated for storage. Full details available in analysis.]"  
