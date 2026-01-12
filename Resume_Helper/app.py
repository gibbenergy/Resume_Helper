"""
Resume Helper - A Gradio application for creating and optimizing resumes.

This application uses a modular structure with separate tab modules.
"""

import os
import sys
import json
import tempfile
import gradio as gr
from gradio import Blocks
import pandas as pd
import logging
import shutil
import webbrowser
import threading
import time
from typing import Optional, Dict, Any, List, Tuple
import uuid

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from infrastructure.adapters.table_data_extractor import TableDataExtractor
from infrastructure.providers.litellm_provider import LiteLLMProvider
from utils.logging_helpers import StandardLogger
from infrastructure.frameworks.response_types import StandardResponse
from utils.constants import UIConstants
from presentation.operations.crud_operations import (
    PersonalInfoCRUD, EducationCRUD, ExperienceCRUD, 
    SkillsCRUD, ProjectsCRUD, CertificationsCRUD
)
from workflows.resume_workflows import ResumeAIWorkflows
from infrastructure.generators.resume_generator import ResumeGenerator
from presentation.ui.tabs import (
    create_personal_info_tab,
    create_educations_tab,
    create_experiences_tab,
    create_skills_tab,
    create_projects_tab,
    create_certifications_tab,
    create_others_tab,
    create_generate_resume_tab,
    create_ai_resume_helper_tab
)
from presentation.ui.tabs.application_tracker_tab import create_application_tracker_tab
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ResumeHelper:
    """Core class for the Resume Helper application."""
    
    def __init__(self):
        self.resume_gen = ResumeGenerator()
        
        env_file_path = os.path.join(current_dir, '.env')
        saved_provider = "openai"
        saved_model = None
        saved_api_key = None
        saved_base_url = None
        
        if os.path.exists(env_file_path):
            try:
                with open(env_file_path, 'r') as f:
                    env_vars = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip().strip('"').strip("'")
                    ui_provider = env_vars.get("RESUME_HELPER_LAST_PROVIDER", "OpenAI")
                    provider_mapping = {
                        "OpenAI": "openai",
                        "Anthropic (Claude)": "anthropic",
                        "Google (Gemini)": "google",
                        "Ollama (Local)": "ollama",
                        "Groq (High-Speed)": "groq",
                        "Perplexity (Search)": "perplexity",
                        "xAI (Grok)": "xai",
                        "llama.cpp": "llamacpp",
                        "LM Studio": "lmstudio",
                        "Lemonade": "lemonade"
                    }
                    saved_provider = provider_mapping.get(ui_provider, "openai")
                    saved_model = env_vars.get("RESUME_HELPER_LAST_MODEL")
                    
                    # Load provider-specific base URL
                    provider_base_url_map = {
                        "llamacpp": "LLAMACPP_API_BASE",
                        "lmstudio": "LMSTUDIO_API_BASE",
                        "lemonade": "LEMONADE_API_BASE",
                        "ollama": "OLLAMA_API_BASE"
                    }
                    base_url_env_var = provider_base_url_map.get(saved_provider, "CUSTOM_BASE_URL")
                    saved_base_url = env_vars.get(base_url_env_var)
                    
                    # All local providers use the same dummy key format
                    if saved_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
                        saved_api_key = "sk-no-key-required"
                    else:
                        env_key = f"{saved_provider.upper()}_API_KEY"
                        saved_api_key = env_vars.get(env_key)
            except Exception as e:
                logger.warning(f"Could not load saved provider config: {e}")
        try:
            # Pass base_url if it's saved (supports custom ports, Lemonade, Harbor, etc.)
            # The provider will handle the priority: custom URL -> Harbor env -> defaults
            logger.info(f"Provider: {saved_provider}, saved_base_url: {saved_base_url}")
            
            self.litellm_provider = LiteLLMProvider(
                provider=saved_provider,
                model=saved_model,
                api_key=saved_api_key,
                base_url=saved_base_url  # Always pass it - provider handles priority
            )
            self.ai_workflows = ResumeAIWorkflows(self.litellm_provider)
            logger.info(f"✅ LiteLLM Provider initialized with {saved_provider}")
        except Exception as e:
            logger.error(f"❌ LiteLLM Provider initialization failed: {e}")
            raise RuntimeError(f"AI provider initialization failed: {e}")
    
    def switch_ai_provider(self, provider_name: str) -> str:
        """Switch between AI providers."""
        try:
            provider_mapping = {
                "openai": "openai",
                "anthropic": "anthropic", 
                "claude": "anthropic",
                "gemini": "google",
                "google": "google",
                "ollama": "ollama",
                "groq": "groq",
                "perplexity": "perplexity",
                "xai": "xai",
                "llamacpp": "llamacpp",
                "lmstudio": "lmstudio",
                "lemonade": "lemonade"
            }
            mapped_provider = provider_mapping.get(provider_name.lower(), provider_name.lower())
            self.litellm_provider = LiteLLMProvider(provider=mapped_provider)
            logger.info(f"✅ Switched to {mapped_provider} provider")
            return f"✅ Switched to {mapped_provider} provider successfully"
        except Exception as e:
            logger.error(f"❌ Failed to switch provider: {e}")
            return f"❌ Failed to switch to {provider_name}: {str(e)}"
    
    def get_current_provider(self) -> str:
        """Get the name of the current AI provider."""
        return self.litellm_provider.get_provider_name()
    
    def get_available_models(self) -> list:
        """Get available models for the current provider."""
        if self.litellm_provider:
            return self.litellm_provider.get_available_models()
        else:
            return []
    
    def get_litellm_provider(self) -> LiteLLMProvider:
        """Get the LiteLLM provider instance."""
        return self.litellm_provider
    
    def switch_to_litellm_provider(self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None) -> str:
        """Switch to using LiteLLM provider with specified settings."""
        try:
            self.litellm_provider = LiteLLMProvider(
                provider=provider,
                model=model,
                api_key=api_key,
                base_url=base_url
            )
            return f"✅ Switched to LiteLLM {provider} provider successfully"
        except Exception as e:
            logger.error(f"Error switching to LiteLLM provider: {e}")
            return f"❌ Error switching to LiteLLM provider: {str(e)}"



    def reset_personal_info(self):
        """Reset personal information fields."""
        return PersonalInfoCRUD.reset()
    
    def reset_all_fields(self):
        """Reset all fields across all tabs dynamically using UIConstants."""
        personal = PersonalInfoCRUD.reset()
        education = EducationCRUD.reset()
        experience = ExperienceCRUD.reset()
        skills = SkillsCRUD.reset()
        projects = ProjectsCRUD.reset()
        certifications = CertificationsCRUD.reset()
        
        empty_table = []
        result = (
            *personal,
            *education,
            empty_table,
            *experience,
            empty_table,
            *skills,
            empty_table,
            *projects,
            empty_table,
            *certifications,
            empty_table,
            {},
            [],
            gr.update(choices=[], value=None)
        )
        
        expected = UIConstants.TOTAL_OUTPUT_COUNT
        actual = len(result)
        if actual != expected:
            logger.error(f"reset_all_fields() count mismatch: expected {expected}, got {actual}")
            logger.error(f"Breakdown: Personal={len(personal)}, Edu={len(education)}+1, Exp={len(experience)}+1, "
                        f"Skills={len(skills)}+1, Projects={len(projects)}+1, Certs={len(certifications)}+1, Others=3")
        
        return result

    def reset_education(self):
        """Reset education fields."""
        return EducationCRUD.reset()

    def reset_experience(self):
        """Reset experience fields."""
        return ExperienceCRUD.reset()

    def reset_skills(self):
        """Reset skills fields."""
        return SkillsCRUD.reset()

    def reset_projects(self):
        """Reset projects fields."""
        return ProjectsCRUD.reset()

    def reset_certifications(self):
        """Reset certifications fields."""
        return CertificationsCRUD.reset()

    def add_education(self, institution, degree, field, start_date, end_date, gpa, description, existing_table=None):
        """Add education to the list."""
        return EducationCRUD.add(institution, degree, field, start_date, end_date, gpa, description, existing_table)

    def clear_education(self):
        """Clear all education entries."""
        return EducationCRUD.clear()

    def add_experience(self, company, position, location, start_date, end_date, description, achievements, existing_table=None):
        """Add experience to the list."""
        return ExperienceCRUD.add(company, position, location, start_date, end_date, description, achievements, existing_table)

    def clear_experience(self):
        """Clear all experience entries."""
        return ExperienceCRUD.clear()

    def add_skill(self, category, skill_name, proficiency, existing_table=None):
        """Add skill to the list."""
        return SkillsCRUD.add(category, skill_name, proficiency, existing_table)

    def clear_skills(self):
        """Clear all skill entries."""
        return SkillsCRUD.clear()

    def add_project(self, title, description, technologies, url, start_date, end_date, existing_table=None):
        """Add project to the list."""
        return ProjectsCRUD.add(title, description, technologies, url, start_date, end_date, existing_table)

    def clear_projects(self):
        """Clear all project entries."""
        return ProjectsCRUD.clear()

    def add_certification(self, name, issuer, date_obtained, credential_id, url, existing_table=None):
        """Add certification to the list."""
        return CertificationsCRUD.add(name, issuer, date_obtained, credential_id, url, existing_table)

    def clear_certifications(self):
        """Clear all certification entries."""
        return CertificationsCRUD.clear()

    def test_api_key(self, api_key: str, model: Optional[str] = None) -> str:
        """Test and save API key with the specified model."""
        return self.litellm_provider.test_api_key(api_key, model or "")
        
    def analyze_job_description(self, job_description: str, model: Optional[str] = None, resume_data: Optional[dict] = None) -> dict:
        """Analyze a job description using AI, including match score if resume provided."""
        return self.ai_workflows.analyze_job_description(job_description, model, resume_data)
        
    def tailor_resume(self, resume_data: dict, job_description: str, model: Optional[str] = None) -> dict:
        """Tailor a resume to match a job description using AI."""
        return self.ai_workflows.tailor_resume(resume_data, job_description, model)
        
    def generate_cover_letter(self, resume_data: dict, job_description: str, model: Optional[str] = None, user_prompt: Optional[str] = None) -> str:
        """Generate a cover letter using AI."""
        result = self.ai_workflows.generate_cover_letter(resume_data, job_description, model, user_prompt)
        if isinstance(result, dict) and "body_content" in result:
            return result["body_content"]
        elif isinstance(result, str):
            return result
        else:
            return "Error generating cover letter"
        
    def get_improvement_suggestions(self, resume_data: dict, job_description: str, model: Optional[str] = None) -> str:
        """Get AI-powered suggestions for resume improvement."""
        return self.ai_workflows.get_improvement_suggestions(resume_data, job_description, model)

    def process_with_ai(self, job_description: str, resume_json: str, model: Optional[str] = None) -> StandardResponse:
        """Process resume with AI features."""
        try:
            from infrastructure.frameworks.response_types import StandardResponse
            
            if not job_description or not resume_json:
                return StandardResponse.error_response(
                    error="Please provide both a job description and a resume",
                    operation="process_with_ai"
                )

            try:
                if isinstance(resume_json, str):
                    resume_data = json.loads(resume_json)
                else:
                    resume_data = resume_json
            except json.JSONDecodeError as e:
                return StandardResponse.error_response(
                    error="Invalid resume JSON format",
                    operation="process_with_ai",
                    error_type="JSONDecodeError"
                )
            analysis = self.analyze_job_description(job_description, model, resume_data)
            if "error" in analysis or not analysis.get("success"):
                return StandardResponse.error_response(
                    error=f"Error analyzing job description: {analysis['error']}",
                    operation="process_with_ai"
                )
            tailored_resume = self.tailor_resume(resume_data, job_description, model)
            if isinstance(tailored_resume, dict) and "error" in tailored_resume:
                return StandardResponse.error_response(
                    error=f"Error tailoring resume: {tailored_resume['error']}",
                    operation="process_with_ai"
                )
            cover_letter = self.generate_cover_letter(tailored_resume, job_description, model)
            if cover_letter.startswith("Error:"):
                return StandardResponse.error_response(
                    error=cover_letter,
                    operation="process_with_ai"
                )
            suggestions = self.get_improvement_suggestions(resume_data, job_description, model)
            if suggestions.startswith("Error:"):
                return StandardResponse.error_response(
                    error=suggestions,
                    operation="process_with_ai"
                )
            return StandardResponse.success_response(
                data={
                    "job_analysis": json.dumps(analysis, indent=2),
                    "tailored_resume": json.dumps(tailored_resume, indent=2),
                    "cover_letter": cover_letter,
                    "suggestions": suggestions,
                    "status": "Success!"
                },
                operation="process_with_ai"
            )
        except Exception as e:
            return StandardResponse.error_response(
                error=f"Error processing resume: {str(e)}",
                operation="process_with_ai",
                error_type=type(e).__name__
            )

    def clear_form(self):
        """Clear all form inputs."""
        PersonalInfoCRUD.reset()
        EducationCRUD.clear()
        ExperienceCRUD.clear()
        SkillsCRUD.clear()
        ProjectsCRUD.clear()
        CertificationsCRUD.clear()

    def load_from_json(self, file_path):
        """Load resume data from JSON using schema-based processing."""
        if not file_path or not file_path.strip() or file_path.strip() == "":
            raise ValueError("No file path provided")
        
        file_path = file_path.strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            from infrastructure.frameworks.schema_engine import SchemaEngine
            from models.resume import ResumeSchema
            from utils.constants import UIConstants
            from utils.logging_helpers import StandardLogger
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            request_id = str(uuid.uuid4())
            SchemaEngine.log_schema_operation("load_resume_json", "ResumeSchema", len(data))
            
            result = []
            personal_info = SchemaEngine.extract_fields(data, ResumeSchema.PERSONAL_INFO)
            personal_order = ResumeSchema.get_field_order('personal_info')
            result.extend([personal_info.get(field, '') for field in personal_order])
            result.append("")
            
            result.extend([""] * UIConstants.EDUCATION_INPUT_FIELDS)
            education_data = SchemaEngine.extract_list_fields(data.get('education', []), ResumeSchema.EDUCATION)
            education_table = SchemaEngine.convert_to_table_format(
                education_data, ResumeSchema.EDUCATION, ResumeSchema.get_field_order('education')
            )
            result.append(education_table)
            
            result.extend([""] * UIConstants.WORK_INPUT_FIELDS)
            experience_data = SchemaEngine.extract_list_fields(data.get('experience', []), ResumeSchema.EXPERIENCE)
            for exp in experience_data:
                achievements = exp.get('achievements', [])
                if isinstance(achievements, list):
                    exp['achievements'] = '\n'.join([f"- {item}" for item in achievements if item])
                else:
                    exp['achievements'] = ''
            
            experience_table = SchemaEngine.convert_to_table_format(
                experience_data, ResumeSchema.EXPERIENCE, ResumeSchema.get_field_order('experience')
            )
            result.append(experience_table)
            
            result.extend([""] * UIConstants.SKILLS_INPUT_FIELDS)
            skills_data = SchemaEngine.extract_list_fields(data.get('skills', []), ResumeSchema.SKILLS)
            skills_table = SchemaEngine.convert_to_table_format(
                skills_data, ResumeSchema.SKILLS, ResumeSchema.get_field_order('skills')
            )
            result.append(skills_table)
            
            result.extend([""] * UIConstants.PROJECTS_INPUT_FIELDS)
            projects_data = SchemaEngine.extract_list_fields(data.get('projects', []), ResumeSchema.PROJECTS)
            projects_table = SchemaEngine.convert_to_table_format(
                projects_data, ResumeSchema.PROJECTS, ResumeSchema.get_field_order('projects')
            )
            result.append(projects_table)
            
            result.extend([""] * UIConstants.CERTIFICATIONS_INPUT_FIELDS)
            certifications_data = SchemaEngine.extract_list_fields(data.get('certifications', []), ResumeSchema.CERTIFICATIONS)
            certifications_table = SchemaEngine.convert_to_table_format(
                certifications_data, ResumeSchema.CERTIFICATIONS, ResumeSchema.get_field_order('certifications')
            )
            result.append(certifications_table)
            
            others_data = data.get('others', {})
            result.append(others_data)
            
            expected_count = UIConstants.FORM_BASE_COUNT + 1
            actual_count = len(result)
            
            StandardLogger.log_data_operation("load_resume_json", request_id, "form_elements", actual_count)
            
            if actual_count != expected_count:
                StandardLogger.log_operation_warning("load_resume_json", request_id,
                    f"Output count mismatch: expected {expected_count}, got {actual_count}")
            
            SchemaEngine.log_schema_operation("load_resume_json", "ResumeSchema", actual_count, success=True)
            return result
            
        except Exception as e:
            from utils.logging_helpers import StandardLogger
            from infrastructure.frameworks.schema_engine import SchemaEngine
            
            request_id = str(uuid.uuid4())
            StandardLogger.log_operation_error("load_resume_json", request_id, e)
            SchemaEngine.log_schema_operation("load_resume_json", "ResumeSchema", 0, success=False)
            raise

    def load_software_developer_example(self):
        """Load Software Developer example from JSON file."""
        try:
            sample_file = os.path.join(current_dir, 'fixtures', 'sample_resume_software_engineer.json')
            with open(sample_file, 'r', encoding='utf-8') as f:
                example_data = json.load(f)

            education_table = []
            for edu in example_data['education']:
                education_table.append([
                    edu['institution'],
                    edu['degree'],
                    edu['field_of_study'],
                    edu['gpa'],
                    edu['start_date'],
                    edu['end_date'],
                    edu['description']
                ])

            # Convert work experience list to table format
            work_table = []
            for work in example_data['experience']:
                # Convert achievements list to string format for table display
                achievements_str = '\n'.join([f"- {achievement}" for achievement in work['achievements']]) if isinstance(work['achievements'], list) else work['achievements']
                work_table.append([
                    work['company'],
                    work['position'],
                    work['location'],
                    work['start_date'],
                    work['end_date'],
                    work['description'],
                    achievements_str
                ])

            # Convert skills to table format
            skills_table = []
            for skill in example_data['skills']:
                skills_table.append([
                    skill['category'],
                    skill['name'],
                    skill['proficiency']
                ])

            # Convert projects list to table format
            projects_table = []
            for project in example_data['projects']:
                projects_table.append([
                    project['name'],
                    project['description'],
                    project['technologies'],
                    project['url'],
                    project['start_date'],
                    project['end_date']
                ])

            # Convert certifications list to table format
            certs_table = []
            for cert in example_data['certifications']:
                certs_table.append([
                    cert['name'],
                    cert['issuer'],
                    cert['date_obtained'],
                    cert['credential_id'],
                    cert['url']
                ])
            
            return [
                # Personal Info
                example_data.get('name_prefix', ''),
                example_data['email'],
                example_data['full_name'],
                example_data['phone'],
                example_data['current_address'],
                example_data['location'],
                example_data['citizenship'],
                example_data['linkedin_url'],
                example_data['github_url'],
                example_data['portfolio_url'],
                example_data['summary'],
                "Example profile loaded successfully!",
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
                example_data.get('others', {})
            ]
        except Exception as e:
            import traceback
            traceback.print_exc()
            return [
                "", "", "", "", "", "", "", "", "", "", "", f"Error loading example: {str(e)}",
                "", "", "", "", "", "", "", [],
                "", "", "", "", "", "", "", [],
                "", "", "", [],
                "", "", "", "", "", "", [],
                "", "", "", "", "", [],
                {}
            ]
    
    def load_process_engineer_example(self):
        """Load Process Engineer example from JSON file."""
        try:
            sample_file = os.path.join(current_dir, 'fixtures', 'sample_resume_process_engineer.json')
            with open(sample_file, 'r', encoding='utf-8') as f:
                example_data = json.load(f)

            education_table = []
            for edu in example_data['education']:
                education_table.append([
                    edu['institution'],
                    edu['degree'],
                    edu['field_of_study'],
                    edu['gpa'],
                    edu['start_date'],
                    edu['end_date'],
                    edu['description']
                ])

            # Convert work experience list to table format
            work_table = []
            for work in example_data['experience']:
                # Convert achievements list to string format for table display
                achievements_str = '\n'.join([f"- {achievement}" for achievement in work['achievements']]) if isinstance(work['achievements'], list) else work['achievements']
                work_table.append([
                    work['company'],
                    work['position'],
                    work['location'],
                    work['start_date'],
                    work['end_date'],
                    work['description'],
                    achievements_str
                ])

            # Convert skills to table format
            skills_table = []
            for skill in example_data['skills']:
                skills_table.append([
                    skill['category'],
                    skill['name'],
                    skill['proficiency']
                ])

            # Convert projects list to table format
            projects_table = []
            for project in example_data['projects']:
                projects_table.append([
                    project['name'],
                    project['description'],
                    project['technologies'],
                    project['url'],
                    project['start_date'],
                    project['end_date']
                ])

            # Convert certifications list to table format
            certs_table = []
            for cert in example_data['certifications']:
                certs_table.append([
                    cert['name'],
                    cert['issuer'],
                    cert['date_obtained'],
                    cert['credential_id'],
                    cert['url']
                ])
            
            return [
                example_data.get('name_prefix', ''),
                example_data['email'],
                example_data['full_name'],
                example_data['phone'],
                example_data['current_address'],
                example_data['location'],
                example_data['citizenship'],
                example_data['linkedin_url'],
                example_data['github_url'],
                example_data['portfolio_url'],
                example_data['summary'],
                "Process Engineer example loaded successfully!",
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
                example_data.get('others', {})
            ]
        except Exception as e:
            import traceback
            traceback.print_exc()
            return [
                "", "", "", "", "", "", "", "", "", "", "", f"Error loading Process Engineer example: {str(e)}",
                "", "", "", "", "", "", "", [],
                "", "", "", "", "", "", "", [],
                "", "", "", [],
                "", "", "", "", "", "", [],
                "", "", "", "", "", [],
                {}
            ]


    def build_profile_dict(self, name_prefix, email, full_name, phone, current_address, location, citizenship,
                     linkedin_url, github_url, portfolio_url, summary,
                     education_table, experience_table, skills_table, projects_table, certifications_table, others_sections_data=None):
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

        try:
            edu_data = TableDataExtractor.extract_table_data(education_table)
            for row in edu_data:
                if isinstance(row, list) and len(row) >= UIConstants.EDUCATION_INPUT_FIELDS and any(str(x).strip() for x in row):
                    education_entry = {
                        'institution': str(row[0]),
                        'degree': str(row[1]),
                        'field_of_study': str(row[2]),
                        'gpa': str(row[3]),
                        'start_date': str(row[4]),
                        'end_date': str(row[5]),
                        'description': str(row[6])
                    }
                    profile['education'].append(education_entry)
        except Exception:
            pass

        try:
            work_data = TableDataExtractor.extract_table_data(experience_table)
            for row in work_data:
                if isinstance(row, list) and len(row) >= UIConstants.WORK_INPUT_FIELDS and any(str(x).strip() for x in row):
                    achievements_text = str(row[6])
                    if achievements_text.strip():
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
                            
                            achievements_value = achievements_list
                        else:
                            achievements_value = [achievements_text]
                    else:
                        achievements_value = []
                    
                    work_entry = {
                        'company': str(row[0]),
                        'position': str(row[1]),
                        'location': str(row[2]),
                        'start_date': str(row[3]),
                        'end_date': str(row[4]),
                        'description': str(row[5]),
                        'achievements': achievements_value
                    }
                    profile['experience'].append(work_entry)
        except Exception as e:
            import traceback
            from utils.logging_helpers import log_error
            log_error(f"Error processing work experience: {str(e)}")
        
        try:
            skill_data = TableDataExtractor.extract_table_data(skills_table)
            skills_list = []
            
            for row in skill_data:
                if isinstance(row, list) and len(row) >= UIConstants.SKILLS_INPUT_FIELDS and any(str(x).strip() for x in row):
                    skills_list.append({
                        'category': str(row[0]),
                        'name': str(row[1]),
                        'proficiency': str(row[2])
                    })
            
            profile['skills'] = skills_list
        except Exception:
            pass

        try:
            project_data = TableDataExtractor.extract_table_data(projects_table)
            for row in project_data:
                if isinstance(row, list) and len(row) >= UIConstants.PROJECTS_INPUT_FIELDS and any(str(x).strip() for x in row):
                    profile['projects'].append({
                        'name': str(row[0]),
                        'description': str(row[1]),
                        'technologies': str(row[2]),
                        'url': str(row[3]),
                        'start_date': str(row[4]),
                        'end_date': str(row[5])
                    })
        except Exception:
            pass

        try:
            cert_data = TableDataExtractor.extract_table_data(certifications_table)
            for row in cert_data:
                if isinstance(row, list) and len(row) >= UIConstants.CERTIFICATIONS_INPUT_FIELDS and any(str(x).strip() for x in row):
                    profile['certifications'].append({
                        'name': str(row[0]),
                        'issuer': str(row[1]),
                        'date_obtained': str(row[2]),
                        'credential_id': str(row[3]),
                        'url': str(row[4])
                    })
        except Exception:
            pass

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
                            profile['others'][section_name] = section_items
        except Exception:
            pass

        return profile


def create_app():
    """Create the Gradio application."""
    resume_helper = ResumeHelper()
    
    # CSS to remove borders ONLY from gr.Group section containers, and style form inputs with subtle borders
    custom_css = """
    /* Remove borders ONLY from gr.Group containers themselves - these create section separators */
    .gradio-container .gr-group {
        border: none !important;
        border-top: none !important;
        border-bottom: none !important;
        border-left: none !important;
        border-right: none !important;
        box-shadow: none !important;
    }
    
    /* Remove borders from pseudo-elements on gr.Group only */
    .gradio-container .gr-group::before,
    .gradio-container .gr-group::after {
        display: none !important;
        border: none !important;
    }
    
    /* Remove HR elements (horizontal rules) that might appear as borders between sections */
    .gradio-container .gr-group hr {
        display: none !important;
        border: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Remove borders between sibling gr.Group sections */
    .gradio-container .gr-group + .gr-group {
        border-top: none !important;
    }
    
    /* Style form inputs with subtle borders */
    .gradio-container input[type="text"],
    .gradio-container input[type="number"],
    .gradio-container input[type="email"],
    .gradio-container input[type="url"],
    .gradio-container textarea,
    .gradio-container select {
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 4px !important;
        transition: border-color 0.2s ease !important;
    }
    
    /* Subtle border on focus */
    .gradio-container input[type="text"]:focus,
    .gradio-container input[type="number"]:focus,
    .gradio-container input[type="email"]:focus,
    .gradio-container input[type="url"]:focus,
    .gradio-container textarea:focus,
    .gradio-container select:focus {
        border-color: rgba(255, 255, 255, 0.3) !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Subtle borders for Gradio textbox and number components */
    .gradio-container [class*="textbox"] input,
    .gradio-container [class*="Textbox"] input,
    .gradio-container [class*="number"] input,
    .gradio-container [class*="Number"] input {
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 4px !important;
    }
    
    /* Subtle borders for dropdowns */
    .gradio-container [class*="dropdown"] select,
    .gradio-container [class*="Dropdown"] select {
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 4px !important;
    }
    """
    
    # JavaScript to force dark mode on load
    js_force_dark = """
    function() {
        if (document.querySelectorAll('.dark').length) {
            return;
        }
        const url = new URL(window.location);
        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """
    
    with gr.Blocks(title="Resume Helper", css=custom_css, js=js_force_dark) as app:
        gr.Markdown(
            "<h1 style='text-align: center; font-size: 48px; font-weight: bold; margin: 30px 0;'>Resume Helper</h1>"
        )
        
        with gr.Tabs() as tabs:
            personal_info_tab_wrapper = create_personal_info_tab(resume_helper)
            educations_tab_wrapper = create_educations_tab(resume_helper)
            experiences_tab_wrapper = create_experiences_tab(resume_helper)
            skills_tab_wrapper = create_skills_tab(resume_helper)
            projects_tab_wrapper = create_projects_tab(resume_helper)
            certifications_tab_wrapper = create_certifications_tab(resume_helper)
            others_tab_wrapper = create_others_tab(resume_helper)
            
            personal_info_tab = personal_info_tab_wrapper.tab
            educations_tab = educations_tab_wrapper.tab
            experiences_tab = experiences_tab_wrapper.tab
            skills_tab = skills_tab_wrapper.tab
            projects_tab = projects_tab_wrapper.tab
            certifications_tab = certifications_tab_wrapper.tab
            others_tab = others_tab_wrapper.tab
            
            all_tabs_components = {
                'personal_info_tab': personal_info_tab_wrapper.components,
                'educations_tab': educations_tab_wrapper.components,
                'experiences_tab': experiences_tab_wrapper.components,
                'skills_tab': skills_tab_wrapper.components,
                'projects_tab': projects_tab_wrapper.components,
                'certifications_tab': certifications_tab_wrapper.components,
                'others_tab': others_tab_wrapper.components,
            }
            generate_resume_tab_wrapper = create_generate_resume_tab(resume_helper, all_tabs_components)
            all_tabs_components['generate_resume_tab'] = generate_resume_tab_wrapper.components
            
            ai_resume_helper_tab_wrapper = create_ai_resume_helper_tab(resume_helper, all_tabs_components)
            all_tabs_components['ai_resume_helper_tab'] = ai_resume_helper_tab_wrapper.components
            application_tracker_tab_wrapper = create_application_tracker_tab(resume_helper)
            all_tabs_components['application_tracker_tab'] = application_tracker_tab_wrapper.components
            
            if hasattr(generate_resume_tab_wrapper, 'connect_to_ai_resume_helper'):
                success = generate_resume_tab_wrapper.connect_to_ai_resume_helper(ai_resume_helper_tab_wrapper)
                from utils.logging_helpers import log_info
            log_info(f"AI Resume Helper connection established: {success}")
            
            generate_resume_tab = generate_resume_tab_wrapper.tab
            ai_resume_helper_tab = ai_resume_helper_tab_wrapper.tab
            application_tracker_tab = application_tracker_tab_wrapper.tab
            
            def load_example_with_others():
                example_result = resume_helper.load_software_developer_example()
                
                others_data = example_result[-1] if example_result else {}
                
                if others_data and isinstance(others_data, dict) and 'load_data_from_dict' in others_tab_wrapper.components:
                    updated_sections, updated_table, updated_selector, _ = others_tab_wrapper.components['load_data_from_dict'](others_data)
                    example_result = example_result[:-1] + [updated_sections, updated_table, updated_selector]
                
                return example_result

            if 'example_software_btn' in personal_info_tab_wrapper.components:
                personal_info_tab_wrapper.components['example_software_btn'].click(
                    fn=load_example_with_others,
                    inputs=[],
                    outputs=[
                        personal_info_tab_wrapper.components['name_prefix_input'],
                        personal_info_tab_wrapper.components['email_input'], 
                        personal_info_tab_wrapper.components['name_input'], 
                        personal_info_tab_wrapper.components['phone_input'], 
                        personal_info_tab_wrapper.components['current_address'],
                        personal_info_tab_wrapper.components['location_input'], 
                        personal_info_tab_wrapper.components['citizenship'], 
                        personal_info_tab_wrapper.components['linkedin_input'], 
                        personal_info_tab_wrapper.components['github_input'],
                        personal_info_tab_wrapper.components['portfolio_input'], 
                        personal_info_tab_wrapper.components['summary_input'], 
                        personal_info_tab_wrapper.components['info_output'],
                        # Education
                        educations_tab_wrapper.components['institution_input'], 
                        educations_tab_wrapper.components['degree_input'], 
                        educations_tab_wrapper.components['field_input'],
                        educations_tab_wrapper.components['edu_start_input'], 
                        educations_tab_wrapper.components['edu_end_input'], 
                        educations_tab_wrapper.components['gpa_input'], 
                        educations_tab_wrapper.components['edu_desc_input'],
                        educations_tab_wrapper.components['edu_list'],
                        # Work Experience
                        experiences_tab_wrapper.components['company_input'], 
                        experiences_tab_wrapper.components['position_input'], 
                        experiences_tab_wrapper.components['work_location_input'],
                        experiences_tab_wrapper.components['work_start_input'], 
                        experiences_tab_wrapper.components['work_end_input'], 
                        experiences_tab_wrapper.components['work_desc_input'], 
                        experiences_tab_wrapper.components['achievements_input'],
                        experiences_tab_wrapper.components['work_list'],
                        # Skills
                        skills_tab_wrapper.components['category_input'], 
                        skills_tab_wrapper.components['skill_input'], 
                        skills_tab_wrapper.components['proficiency_input'],
                        skills_tab_wrapper.components['skill_list'],
                        # Projects
                        projects_tab_wrapper.components['project_title_input'], 
                        projects_tab_wrapper.components['project_desc_input'], 
                        projects_tab_wrapper.components['project_tech_input'],
                        projects_tab_wrapper.components['project_url_input'], 
                        projects_tab_wrapper.components['project_start_input'], 
                        projects_tab_wrapper.components['project_end_input'],
                        projects_tab_wrapper.components['project_list'],
                        # Certifications
                        certifications_tab_wrapper.components['cert_name_input'], 
                        certifications_tab_wrapper.components['cert_issuer_input'], 
                        certifications_tab_wrapper.components['cert_date_input'],
                        certifications_tab_wrapper.components['cert_id_input'], 
                        certifications_tab_wrapper.components['cert_url_input'],
                        certifications_tab_wrapper.components['cert_list'],
                        # Others
                        others_tab_wrapper.components['sections_data'],
                        others_tab_wrapper.components['sections_display'],
                        others_tab_wrapper.components['section_selector']
                    ],
                    show_progress=True
                )
            
            def load_process_example_with_others():
                example_result = resume_helper.load_process_engineer_example()
                
                others_data = example_result[-1] if example_result else {}
                
                if others_data and isinstance(others_data, dict) and 'load_data_from_dict' in others_tab_wrapper.components:
                    updated_sections, updated_table, updated_selector, _ = others_tab_wrapper.components['load_data_from_dict'](others_data)
                    example_result = example_result[:-1] + [updated_sections, updated_table, updated_selector]
                
                return example_result
            
            if 'example_process_btn' in personal_info_tab_wrapper.components:
                personal_info_tab_wrapper.components['example_process_btn'].click(
                    fn=load_process_example_with_others,
                    inputs=[],
                    outputs=[
                        # Personal Info
                        personal_info_tab_wrapper.components['name_prefix_input'],
                        personal_info_tab_wrapper.components['email_input'], 
                        personal_info_tab_wrapper.components['name_input'], 
                        personal_info_tab_wrapper.components['phone_input'], 
                        personal_info_tab_wrapper.components['current_address'],
                        personal_info_tab_wrapper.components['location_input'], 
                        personal_info_tab_wrapper.components['citizenship'], 
                        personal_info_tab_wrapper.components['linkedin_input'], 
                        personal_info_tab_wrapper.components['github_input'],
                        personal_info_tab_wrapper.components['portfolio_input'], 
                        personal_info_tab_wrapper.components['summary_input'], 
                        personal_info_tab_wrapper.components['info_output'],
                        # Education
                        educations_tab_wrapper.components['institution_input'], 
                        educations_tab_wrapper.components['degree_input'], 
                        educations_tab_wrapper.components['field_input'],
                        educations_tab_wrapper.components['edu_start_input'], 
                        educations_tab_wrapper.components['edu_end_input'], 
                        educations_tab_wrapper.components['gpa_input'], 
                        educations_tab_wrapper.components['edu_desc_input'],
                        educations_tab_wrapper.components['edu_list'],
                        # Work Experience
                        experiences_tab_wrapper.components['company_input'], 
                        experiences_tab_wrapper.components['position_input'], 
                        experiences_tab_wrapper.components['work_location_input'],
                        experiences_tab_wrapper.components['work_start_input'], 
                        experiences_tab_wrapper.components['work_end_input'], 
                        experiences_tab_wrapper.components['work_desc_input'], 
                        experiences_tab_wrapper.components['achievements_input'],
                        experiences_tab_wrapper.components['work_list'],
                        # Skills
                        skills_tab_wrapper.components['category_input'], 
                        skills_tab_wrapper.components['skill_input'], 
                        skills_tab_wrapper.components['proficiency_input'],
                        skills_tab_wrapper.components['skill_list'],
                        # Projects
                        projects_tab_wrapper.components['project_title_input'], 
                        projects_tab_wrapper.components['project_desc_input'], 
                        projects_tab_wrapper.components['project_tech_input'],
                        projects_tab_wrapper.components['project_url_input'], 
                        projects_tab_wrapper.components['project_start_input'], 
                        projects_tab_wrapper.components['project_end_input'],
                        projects_tab_wrapper.components['project_list'],
                        # Certifications
                        certifications_tab_wrapper.components['cert_name_input'], 
                        certifications_tab_wrapper.components['cert_issuer_input'], 
                        certifications_tab_wrapper.components['cert_date_input'],
                        certifications_tab_wrapper.components['cert_id_input'], 
                        certifications_tab_wrapper.components['cert_url_input'],
                        certifications_tab_wrapper.components['cert_list'],
                        # Others
                        others_tab_wrapper.components['sections_data'],
                        others_tab_wrapper.components['sections_display'],
                        others_tab_wrapper.components['section_selector']
                    ],
                    show_progress=True
                )
            
            if 'reset_personal_btn' in personal_info_tab_wrapper.components:
                personal_info_tab_wrapper.components['reset_personal_btn'].click(
                    fn=resume_helper.reset_all_fields,
                    inputs=[],
                    outputs=[
                        personal_info_tab_wrapper.components['name_prefix_input'],
                        personal_info_tab_wrapper.components['email_input'], 
                        personal_info_tab_wrapper.components['name_input'], 
                        personal_info_tab_wrapper.components['phone_input'], 
                        personal_info_tab_wrapper.components['current_address'],
                        personal_info_tab_wrapper.components['location_input'], 
                        personal_info_tab_wrapper.components['citizenship'], 
                        personal_info_tab_wrapper.components['linkedin_input'], 
                        personal_info_tab_wrapper.components['github_input'],
                        personal_info_tab_wrapper.components['portfolio_input'], 
                        personal_info_tab_wrapper.components['summary_input'], 
                        personal_info_tab_wrapper.components['info_output'],
                        educations_tab_wrapper.components['institution_input'], 
                        educations_tab_wrapper.components['degree_input'], 
                        educations_tab_wrapper.components['field_input'],
                        educations_tab_wrapper.components['edu_start_input'], 
                        educations_tab_wrapper.components['edu_end_input'], 
                        educations_tab_wrapper.components['gpa_input'], 
                        educations_tab_wrapper.components['edu_desc_input'],
                        educations_tab_wrapper.components['edu_list'],
                        experiences_tab_wrapper.components['company_input'], 
                        experiences_tab_wrapper.components['position_input'], 
                        experiences_tab_wrapper.components['work_location_input'],
                        experiences_tab_wrapper.components['work_start_input'], 
                        experiences_tab_wrapper.components['work_end_input'], 
                        experiences_tab_wrapper.components['work_desc_input'], 
                        experiences_tab_wrapper.components['achievements_input'],
                        experiences_tab_wrapper.components['work_list'],
                        skills_tab_wrapper.components['category_input'], 
                        skills_tab_wrapper.components['skill_input'], 
                        skills_tab_wrapper.components['proficiency_input'],
                        skills_tab_wrapper.components['skill_list'],
                        projects_tab_wrapper.components['project_title_input'], 
                        projects_tab_wrapper.components['project_desc_input'], 
                        projects_tab_wrapper.components['project_tech_input'],
                        projects_tab_wrapper.components['project_url_input'], 
                        projects_tab_wrapper.components['project_start_input'], 
                        projects_tab_wrapper.components['project_end_input'],
                        projects_tab_wrapper.components['project_list'],
                        certifications_tab_wrapper.components['cert_name_input'], 
                        certifications_tab_wrapper.components['cert_issuer_input'], 
                        certifications_tab_wrapper.components['cert_date_input'],
                        certifications_tab_wrapper.components['cert_id_input'], 
                        certifications_tab_wrapper.components['cert_url_input'],
                        certifications_tab_wrapper.components['cert_list'],
                        others_tab_wrapper.components['sections_data'],
                        others_tab_wrapper.components['sections_display'],
                        others_tab_wrapper.components['section_selector']
                    ],
                    show_progress=True
                )
    
    return app

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Resume Helper Web Application')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=53441, help='Port to bind the server to')
    parser.add_argument('--allow-iframe', action='store_true', help='Allow the app to be embedded in iframes')
    parser.add_argument('--allow-cors', action='store_true', help='Allow cross-origin requests')
    
    args = parser.parse_args()
    
    app = create_app()
    app.queue(
        default_concurrency_limit=1,
        max_size=10,
        api_open=False
    ).launch(
        server_name=args.host,
        server_port=args.port,
        share=False,
        show_error=True,
        max_threads=40,
        allowed_paths=["*"] if args.allow_cors else None,        
        favicon_path=None,
        inbrowser=True          
    )

