"""
Resume Helper - Core business logic for creating and optimizing resumes.

This module provides the ResumeHelper class which contains all business logic
for resume management, AI workflows, and data processing.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
import uuid

from backend.core.infrastructure.adapters.table_data_extractor import TableDataExtractor
from backend.core.infrastructure.providers.litellm_provider import LiteLLMProvider
from backend.core.utils.logging_helpers import StandardLogger
from backend.core.infrastructure.frameworks.response_types import StandardResponse
from backend.core.utils.constants import UIConstants
from backend.core.workflows.resume_workflows import ResumeAIWorkflows
from backend.core.infrastructure.generators.resume_generator import ResumeGenerator

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
        
        # Store current directory for fixture loading
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Look for .env in the project root (Resume_Helper-main/)
        project_root = os.path.dirname(os.path.dirname(self.current_dir))  # Go up to Resume_Helper-main/
        env_file_path = os.path.join(project_root, '.env')
        saved_provider = "openai"
        saved_model = None
        saved_api_key = None
        
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
                        "llama.cpp": "llamacpp",
                        "LM Studio": "lmstudio",
                        "Lemonade": "lemonade",
                        "Groq (High-Speed)": "groq",
                        "Perplexity (Search)": "perplexity",
                        "xAI (Grok)": "xai"
                    }
                    saved_provider = provider_mapping.get(ui_provider, "openai")
                    saved_model = env_vars.get("RESUME_HELPER_LAST_MODEL")
                    
                    if saved_provider in ["ollama", "llamacpp", "lmstudio", "lemonade"]:
                        saved_api_key = "sk-no-key-required"
                    else:
                        env_key = f"{saved_provider.upper()}_API_KEY"
                        saved_api_key = env_vars.get(env_key)
            except Exception as e:
                logger.warning(f"Could not load saved provider config: {e}")
        try:
            self.litellm_provider = LiteLLMProvider(
                provider=saved_provider,
                model=saved_model,
                api_key=saved_api_key
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
                "llamacpp": "llamacpp",
                "lmstudio": "lmstudio",
                "lemonade": "lemonade",
                "groq": "groq",
                "perplexity": "perplexity",
                "xai": "xai"
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
    
    def switch_to_litellm_provider(self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None) -> str:
        """Switch to using LiteLLM provider with specified settings."""
        try:
            self.litellm_provider = LiteLLMProvider(
                provider=provider,
                model=model,
                api_key=api_key
            )
            return f"✅ Switched to LiteLLM {provider} provider successfully"
        except Exception as e:
            logger.error(f"Error switching to LiteLLM provider: {e}")
            return f"❌ Error switching to LiteLLM provider: {str(e)}"

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
            
            # Try multiple encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            data = None
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    break  # Success, stop trying
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            
            if data is None:
                raise ValueError("Could not decode JSON file with any supported encoding")
            
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
            sample_file = os.path.join(self.current_dir, 'fixtures', 'sample_resume_software_engineer.json')
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
            sample_file = os.path.join(self.current_dir, 'fixtures', 'sample_resume_process_engineer.json')
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

