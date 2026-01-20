"""
Pydantic models for API request/response validation.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    name_prefix: Optional[str] = ""
    email: Optional[str] = ""
    full_name: Optional[str] = ""
    phone: Optional[str] = ""
    current_address: Optional[str] = ""
    location: Optional[str] = ""
    citizenship: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    github_url: Optional[str] = ""
    portfolio_url: Optional[str] = ""
    summary: Optional[str] = ""
    expected_salary: Optional[str] = ""


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = ""
    gpa: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: Optional[str] = ""


class ExperienceEntry(BaseModel):
    company: str
    position: str
    location: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: Optional[str] = ""
    achievements: Optional[List[str]] = []


class SkillEntry(BaseModel):
    category: str
    name: str
    proficiency: Optional[str] = ""


class ProjectEntry(BaseModel):
    name: str
    description: str
    technologies: Optional[str] = ""
    url: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""


class CertificationEntry(BaseModel):
    name: str
    issuer: str
    date_obtained: Optional[str] = ""
    credential_id: Optional[str] = ""
    url: Optional[str] = ""


class ResumeData(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    education: List[EducationEntry] = []
    experience: List[ExperienceEntry] = []
    skills: List[SkillEntry] = []
    projects: List[ProjectEntry] = []
    certifications: List[CertificationEntry] = []
    others: Optional[Dict[str, Any]] = {}


class BuildProfileRequest(BaseModel):
    name_prefix: Optional[str] = ""
    email: Optional[str] = ""
    full_name: Optional[str] = ""
    phone: Optional[str] = ""
    current_address: Optional[str] = ""
    location: Optional[str] = ""
    citizenship: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    github_url: Optional[str] = ""
    portfolio_url: Optional[str] = ""
    summary: Optional[str] = ""
    education_table: Optional[List[List[Any]]] = []
    experience_table: Optional[List[List[Any]]] = []
    skills_table: Optional[List[List[Any]]] = []
    projects_table: Optional[List[List[Any]]] = []
    certifications_table: Optional[List[List[Any]]] = []
    others_sections_data: Optional[Dict[str, Any]] = {}


class JobAnalysisRequest(BaseModel):
    job_description: str
    resume_data: ResumeData
    model: Optional[str] = None


class TailorResumeRequest(BaseModel):
    resume_data: ResumeData
    job_description: str
    model: Optional[str] = None
    user_prompt: Optional[str] = None
    job_analysis_data: Optional[Dict[str, Any]] = None


class CoverLetterRequest(BaseModel):
    resume_data: ResumeData
    job_description: str
    model: Optional[str] = None
    user_prompt: Optional[str] = None
    job_analysis_data: Optional[Dict[str, Any]] = None


class ImprovementSuggestionsRequest(BaseModel):
    resume_data: ResumeData
    job_description: str
    model: Optional[str] = None
    job_analysis_data: Optional[Dict[str, Any]] = None


class TestAPIKeyRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None


class GeneratePDFRequest(BaseModel):
    resume_data: ResumeData
    pdf_type: str = Field(..., description="Type: 'resume' or 'cover_letter'")
    cover_letter_data: Optional[Dict[str, Any]] = None
    job_analysis_data: Optional[Dict[str, Any]] = None


class GenerateDOCXRequest(BaseModel):
    resume_data: ResumeData


class ApplicationCreateRequest(BaseModel):
    job_url: str
    company: str
    position: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    date_applied: Optional[str] = None
    application_source: Optional[str] = None
    priority: Optional[str] = "Medium"
    status: Optional[str] = "Applied"
    description: Optional[str] = None
    notes: Optional[str] = None
    match_score: Optional[int] = None
    hr_contact: Optional[str] = None
    hiring_manager: Optional[str] = None
    recruiter: Optional[str] = None
    referral: Optional[str] = None
    requirements: Optional[List[str]] = []
    analysis_data: Optional[Dict[str, Any]] = {}
    interview_pipeline: Optional[Dict[str, Any]] = {}
    timeline: Optional[List[Dict[str, Any]]] = []
    next_actions: Optional[List[str]] = []
    tags: Optional[List[str]] = []


class ApplicationUpdateRequest(BaseModel):
    job_url: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    date_applied: Optional[str] = None
    application_source: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    match_score: Optional[int] = None
    hr_contact: Optional[str] = None
    hiring_manager: Optional[str] = None
    recruiter: Optional[str] = None
    referral: Optional[str] = None
    requirements: Optional[List[str]] = None
    analysis_data: Optional[Dict[str, Any]] = None
    interview_pipeline: Optional[Dict[str, Any]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    next_actions: Optional[List[str]] = None
    tags: Optional[List[str]] = None

