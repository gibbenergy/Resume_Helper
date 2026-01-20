"""
Constants Module - Centralized constants for the Resume Helper application

This module eliminates magic numbers and provides standardized field names,
UI constants, and error messages throughout the application.
"""

from typing import List, Dict


class UIConstants:
    """UI-related constants for form fields and output counts."""
    
    PERSONAL_INFO_FIELDS = 12
    EDUCATION_INPUT_FIELDS = 7
    WORK_INPUT_FIELDS = 7
    SKILLS_INPUT_FIELDS = 3
    PROJECTS_INPUT_FIELDS = 6
    CERTIFICATIONS_INPUT_FIELDS = 5
    
    EDUCATION_TABLE = 1
    WORK_TABLE = 1
    SKILLS_TABLE = 1
    PROJECTS_TABLE = 1
    CERTIFICATIONS_TABLE = 1
    
    OTHERS_COMPONENT_COUNT = 3
    
    FORM_BASE_COUNT = (
        PERSONAL_INFO_FIELDS +
        EDUCATION_INPUT_FIELDS +
        EDUCATION_TABLE +
        WORK_INPUT_FIELDS +
        WORK_TABLE +
        SKILLS_INPUT_FIELDS +
        SKILLS_TABLE +
        PROJECTS_INPUT_FIELDS +
        PROJECTS_TABLE +
        CERTIFICATIONS_INPUT_FIELDS +
        CERTIFICATIONS_TABLE
    )
    
    TOTAL_OUTPUT_COUNT = FORM_BASE_COUNT + OTHERS_COMPONENT_COUNT
    
    PERSONAL_INFO_START = 0
    PERSONAL_INFO_END = PERSONAL_INFO_START + PERSONAL_INFO_FIELDS - 1
    
    EDUCATION_INPUT_START = PERSONAL_INFO_END + 1
    EDUCATION_INPUT_END = EDUCATION_INPUT_START + EDUCATION_INPUT_FIELDS - 1
    
    EDUCATION_TABLE_INDEX = EDUCATION_INPUT_END + 1
    
    WORK_INPUT_START = EDUCATION_TABLE_INDEX + 1
    WORK_INPUT_END = WORK_INPUT_START + WORK_INPUT_FIELDS - 1
    
    WORK_TABLE_INDEX = WORK_INPUT_END + 1
    
    SKILLS_INPUT_START = WORK_TABLE_INDEX + 1
    SKILLS_INPUT_END = SKILLS_INPUT_START + SKILLS_INPUT_FIELDS - 1
    
    SKILLS_TABLE_INDEX = SKILLS_INPUT_END + 1
    
    PROJECTS_INPUT_START = SKILLS_TABLE_INDEX + 1
    PROJECTS_INPUT_END = PROJECTS_INPUT_START + PROJECTS_INPUT_FIELDS - 1
    
    PROJECTS_TABLE_INDEX = PROJECTS_INPUT_END + 1
    
    CERTIFICATIONS_INPUT_START = PROJECTS_TABLE_INDEX + 1
    CERTIFICATIONS_INPUT_END = CERTIFICATIONS_INPUT_START + CERTIFICATIONS_INPUT_FIELDS - 1
    
    CERTIFICATIONS_TABLE_INDEX = CERTIFICATIONS_INPUT_END + 1
    
    OTHERS_COMPONENTS_START = CERTIFICATIONS_TABLE_INDEX + 1
    OTHERS_SECTIONS_DATA_INDEX = OTHERS_COMPONENTS_START
    OTHERS_SECTIONS_DISPLAY_INDEX = OTHERS_COMPONENTS_START + 1
    OTHERS_SECTION_SELECTOR_INDEX = OTHERS_COMPONENTS_START + 2


class ErrorMessages:
    """Standardized error messages for consistent user feedback."""
    
    INVALID_JSON = "Invalid JSON format"
    FILE_NOT_FOUND = "File not found: {path}"
    FILE_READ_ERROR = "Error reading file: {path}"
    FILE_WRITE_ERROR = "Error writing file: {path}"
    INVALID_FILE_TYPE = "Unsupported file type: {file_type}"
    
    EMPTY_DATA = "No data provided"
    MISSING_REQUIRED_FIELD = "Required field '{field}' is missing"
    INVALID_DATA_FORMAT = "Invalid data format for '{field}'"
    OUTPUT_COUNT_MISMATCH = "Expected {expected} outputs, got {actual}"
    
    API_ERROR = "API call failed: {error}"
    PROCESSING_ERROR = "Error processing {operation}: {error}"
    TIMEOUT_ERROR = "Operation timed out: {operation}"
    
    EMPTY_RESUME_DATA = "No resume data available"
    EMPTY_JOB_DESCRIPTION = "Job description is required"
    INVALID_RESUME_STRUCTURE = "Invalid resume data structure"
    
    APPLICATION_NOT_FOUND = "Application not found: {app_id}"
    APPLICATION_EXISTS = "Application with this job URL already exists"
    INVALID_APPLICATION_DATA = "Invalid application data: {error}"
    
    MODEL_NOT_AVAILABLE = "AI model not available: {model}"
    API_KEY_INVALID = "Invalid API key for provider: {provider}"
    PROMPT_TOO_LONG = "Input text too long for model: {model}"
    
    INVALID_EMAIL_FORMAT = "Please enter a valid email address (e.g., user@domain.com)"
    INVALID_PHONE_FORMAT = "Please enter a valid phone number (e.g., +1-555-123-4567)"
    INVALID_URL_FORMAT = "Please enter a valid URL (e.g., https://example.com)"
    INVALID_LINKEDIN_URL = "Please enter a valid LinkedIn URL (e.g., https://linkedin.com/in/username)"
    INVALID_GITHUB_URL = "Please enter a valid GitHub URL (e.g., https://github.com/username)"
    INVALID_DATE_FORMAT = "Please enter a valid date (e.g., YYYY-MM-DD or MM/DD/YYYY)"
    TEXT_TOO_LONG = "{field} is too long (max {max_length} characters)"
    TEXT_TOO_SHORT = "{field} must be at least {min_length} characters"
    NUMBER_OUT_OF_RANGE = "{field} must be between {min_value} and {max_value}"
    INVALID_ENUM_VALUE = "{field} must be one of: {allowed_values}"
    DATE_CONSISTENCY_ERROR = "Start date must be before end date"
    FUTURE_DATE_ERROR = "Date cannot be in the future"
    
    XSS_DETECTED = "Potential security threat detected in input"
    INJECTION_DETECTED = "Malicious content detected in input"
    UNSAFE_FILE_CONTENT = "File contains potentially unsafe content"
    FILE_TOO_LARGE = "File is too large (max {max_size}MB)"
    INVALID_FILE_TYPE = "File type not allowed. Allowed types: {allowed_types}"


class FileTypes:
    """Supported file types and their extensions."""
    
    JSON = '.json'
    PDF = '.pdf'
    DOCX = '.docx'
    DOC = '.doc'
    
    SUPPORTED_IMPORT = [JSON, PDF, DOCX, DOC]
    SUPPORTED_EXPORT = [JSON, PDF, DOCX]
    
    MIME_TYPES = {
        JSON: 'application/json',
        PDF: 'application/pdf',
        DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        DOC: 'application/msword'
    }


class AIConstants:
    """Constants for AI operations and workflows."""
    
    DEFAULT_MODELS = {
        'openai': 'gpt-4.1',
        'anthropic': 'claude-opus-4-1-20250805',
        'google': 'gemini-2.5-pro',
        'groq': 'gpt-oss-20B',
        'ollama': 'llama3.1',
        'perplexity': 'sonar-pro',
        'xai': 'grok-4'
    }
    
    TOKEN_LIMITS = {
        'gpt-4o': 128000,
        'claude-3-5-sonnet-20241022': 200000,
        'gemini-1.5-pro': 1000000,
        'llama-3.1-70b-versatile': 131072
    }
    
    OPERATION_TIMEOUTS = {
        'job_analysis': 30,
        'resume_tailoring': 45,
        'cover_letter_generation': 30,
        'improvement_suggestions': 25
    }


class ValidationRules:
    """Validation rules for data integrity."""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    PHONE_PATTERN = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
    
    URL_PATTERN = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=,]*)$'
    
    LINKEDIN_PATTERN = r'^https?:\/\/(www\.)?linkedin\.com\/(in|pub)\/[a-zA-Z0-9\-\_]+\/?$'
    
    GITHUB_PATTERN = r'^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9\-\_]+\/?$'
    
    DATE_PATTERNS = [
        r'^\d{4}-\d{2}-\d{2}$',
        r'^\d{2}\/\d{2}\/\d{4}$',
        r'^\d{2}-\d{2}-\d{4}$',
        r'^\d{4}-\d{2}$',
        r'^\d{2}\/\d{4}$',
    ]
    
    REQUIRED_FIELDS = {
        'personal_info': ['full_name', 'email'],
        'education': ['institution', 'degree'],
        'experience': ['company', 'position'],
        'skills': ['category', 'name'],
        'projects': ['name', 'description'],
        'certifications': ['name', 'issuer'],
        'application': ['company', 'position', 'job_url']
    }
    
    MAX_LENGTHS = {
        'full_name': 100,
        'email': 254,
        'phone': 20,
        'summary': 1000,
        'description': 2000,
        'achievements': 2000,
        'company': 100,
        'position': 100,
        'institution': 100,
        'degree': 100,
        'field_of_study': 100,
        'location': 100,
        'current_address': 200,
        'citizenship': 50,
        'linkedin_url': 300,
        'github_url': 300,
        'portfolio_url': 300,
        'job_url': 500,
        'notes': 2000,
        'technologies': 500,
        'category': 50,
        'name': 100,
        'skill_name': 100,
        'proficiency': 20,
        'issuer': 100,
        'certification_id': 50
    }
    
    MIN_LENGTHS = {
        'full_name': 2,
        'company': 2,
        'position': 2,
        'institution': 2,
        'degree': 2,
        'summary': 10,
        'description': 10
    }
    
    NUMERIC_RANGES = {
        'match_score': {'min': 0, 'max': 100},
        'gpa': {'min': 0.0, 'max': 4.0},
        'salary_min': {'min': 0, 'max': 1000000},
        'salary_max': {'min': 0, 'max': 1000000}
    }
    
    ALLOWED_VALUES = {
        'status': ['Applied', 'Interview', 'Offer', 'Rejected', 'Withdrawn'],
        'priority': ['Low', 'Medium', 'High'],
        'source': ['Job Board', 'Company Website', 'Referral', 'Recruiter', 'LinkedIn', 'Other'],
        'proficiency': ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    }
    
    UPLOAD_RESTRICTIONS = {
        'max_file_size': 10 * 1024 * 1024,
        'allowed_extensions': ['pdf', 'doc', 'docx', 'txt', 'json'],
        'allowed_mime_types': [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/json'
        ]
    }


def get_field_position(field_name: str) -> int:
    """Get the position index of a field in the form output array."""
    positions = {
        'email': 0, 'full_name': 1, 'phone': 2, 'address': 3, 'location': 4,
        'citizenship': 5, 'linkedin': 6, 'github': 7, 'portfolio': 8, 'summary': 9,
        'info_output': 10,
        'education_table': UIConstants.EDUCATION_TABLE_INDEX,
        'work_table': UIConstants.WORK_TABLE_INDEX,
        'skills_table': UIConstants.SKILLS_TABLE_INDEX,
        'projects_table': UIConstants.PROJECTS_TABLE_INDEX,
        'certifications_table': UIConstants.CERTIFICATIONS_TABLE_INDEX,
        'others_sections_data': UIConstants.OTHERS_SECTIONS_DATA_INDEX,
        'others_sections_display': UIConstants.OTHERS_SECTIONS_DISPLAY_INDEX,
        'others_section_selector': UIConstants.OTHERS_SECTION_SELECTOR_INDEX
    }
    return positions.get(field_name, -1)


def validate_output_count(outputs: List) -> bool:
    """Validate that the output array has the correct number of elements."""
    return len(outputs) == UIConstants.TOTAL_OUTPUT_COUNT 
