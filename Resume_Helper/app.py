"""
Resume Helper - A Gradio application for creating and optimizing resumes.

This application uses a modular structure with separate tab modules.
"""

import os
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

from Resume_Helper.resume_generator import ResumeGenerator
from Resume_Helper.unified_ai_features import UnifiedAIFeatures, AIProvider

# Import tab modules
from Resume_Helper.tabs import (
    create_personal_info_tab,
    create_educations_tab,
    create_experiences_tab,
    create_skills_tab,
    create_projects_tab,
    create_certifications_tab,
    create_generate_resume_tab,
    create_ai_resume_helper_tab
)

# Configure logging
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
        # Initialize unified AI provider (default to OpenAI)
        self.ai_features = UnifiedAIFeatures(provider="openai")
    
    def switch_ai_provider(self, provider_name: str) -> str:
        """
        Switch between AI providers.
        
        Args:
            provider_name: The name of the provider to switch to ("openai" or "gemini").
            
        Returns:
            A message indicating success or failure.
        """
        return self.ai_features.set_provider(provider_name)
    
    def get_current_provider(self) -> str:
        """
        Get the name of the current AI provider.
        
        Returns:
            The name of the current AI provider.
        """
        return self.ai_features.get_provider_name()
    
    def get_available_models(self) -> list:
        """
        Get a list of available models for the current provider.
        
        Returns:
            A list of model names.
        """
        return self.ai_features.get_available_models()

    def extract_table_data(self, table):
        """Extract data from a Gradio DataFrame component."""
        try:
            if table is None:
                return []
            
            # If it's a pandas DataFrame
            if hasattr(table, 'values') and hasattr(table, 'to_dict'):
                return table.values.tolist()
            
            # If it's a dict with 'data' key (Gradio DataFrame format)
            if isinstance(table, dict) and 'data' in table:
                return table['data']
            
            # If it's already a list
            if isinstance(table, list):
                return table
            
            return []
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []

    def reset_personal_info(self):
        """Reset personal information fields."""
        try:
            return [""] * 11  # 10 fields + status message
        except Exception as e:
            return [""] * 11

    def reset_education(self):
        """Reset education fields."""
        try:
            return [""] * 7  # 7 input fields
        except Exception as e:
            return [""] * 7

    def add_education(self, institution, degree, field, start_date, end_date, gpa, description, existing_table=None):
        """Add education to the list."""
        try:
            # Create new entry
            new_entry = [institution, degree, field, gpa, start_date, end_date, description]
            
            # Initialize list if no existing data
            if existing_table is None or not existing_table:
                return [new_entry]
            
            # Convert existing_table to list if it's a DataFrame
            if hasattr(existing_table, 'values') and hasattr(existing_table, 'to_dict'):
                existing_data = existing_table.values.tolist()
            # Handle Gradio DataFrame format
            elif isinstance(existing_table, dict) and 'data' in existing_table:
                existing_data = existing_table['data']
            # If it's already a list
            elif isinstance(existing_table, list):
                existing_data = existing_table
            else:
                existing_data = []
            
            # Create a new list with existing data + new entry
            result = list(existing_data)  # Create a copy of existing data
            result.append(new_entry)  # Add new entry
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return original data if there's an error
            return existing_table if existing_table is not None else []

    def remove_education(self, edu_list, selected_rows):
        """Remove selected education entries."""
        try:
            if not edu_list or not selected_rows:
                return edu_list
            return [row for i, row in enumerate(edu_list) if i not in selected_rows]
        except Exception as e:
            return edu_list

    def clear_education(self):
        """Clear all education entries."""
        try:
            return []
        except Exception as e:
            return []

    def reset_work_experience(self):
        """Reset work experience fields."""
        try:
            return [""] * 7  # 7 input fields
        except Exception as e:
            return [""] * 7

    def add_work_experience(self, company, position, location, start_date, end_date, description, achievements, existing_table=None):
        """Add work experience to the list."""
        try:
            # Create new entry
            new_entry = [company, position, location, start_date, end_date, description, achievements]
            
            # Initialize list if no existing data
            if existing_table is None or not existing_table:
                return [new_entry]
            
            # Convert existing_table to list if it's a DataFrame
            if hasattr(existing_table, 'values') and hasattr(existing_table, 'to_dict'):
                existing_data = existing_table.values.tolist()
            # Handle Gradio DataFrame format
            elif isinstance(existing_table, dict) and 'data' in existing_table:
                existing_data = existing_table['data']
            # If it's already a list
            elif isinstance(existing_table, list):
                existing_data = existing_table
            else:
                existing_data = []
            
            # Create a new list with existing data + new entry
            result = list(existing_data)  # Create a copy of existing data
            result.append(new_entry)  # Add new entry
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return original data if there's an error
            return existing_table if existing_table is not None else []

    def remove_work_experience(self, work_list, selected_rows):
        """Remove selected work experience entries."""
        try:
            if not work_list or not selected_rows:
                return work_list
            return [row for i, row in enumerate(work_list) if i not in selected_rows]
        except Exception as e:
            return work_list

    def clear_work_experience(self):
        """Clear all work experience entries."""
        try:
            return []
        except Exception as e:
            return []

    def reset_skills(self):
        """Reset skills fields."""
        try:
            return [""] * 3  # 3 input fields
        except Exception as e:
            return [""] * 3

    def add_skill(self, category, skill_name, proficiency, existing_table=None):
        """Add skill to the list."""
        try:
            # Create new entry
            new_entry = [category, skill_name, proficiency]
            
            # Initialize list if no existing data
            if existing_table is None or not existing_table:
                return [new_entry]
            
            # Convert existing_table to list if it's a DataFrame
            if hasattr(existing_table, 'values') and hasattr(existing_table, 'to_dict'):
                existing_data = existing_table.values.tolist()
            # Handle Gradio DataFrame format
            elif isinstance(existing_table, dict) and 'data' in existing_table:
                existing_data = existing_table['data']
            # If it's already a list
            elif isinstance(existing_table, list):
                existing_data = existing_table
            else:
                existing_data = []
            
            # Create a new list with existing data + new entry
            result = list(existing_data)  # Create a copy of existing data
            result.append(new_entry)  # Add new entry
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return original data if there's an error
            return existing_table if existing_table is not None else []

    def remove_skill(self, skill_list, selected_rows):
        """Remove selected skill entries."""
        try:
            if not skill_list or not selected_rows:
                return skill_list
            return [row for i, row in enumerate(skill_list) if i not in selected_rows]
        except Exception as e:
            return skill_list

    def clear_skills(self):
        """Clear all skill entries."""
        try:
            return []
        except Exception as e:
            return []

    def reset_projects(self):
        """Reset projects fields."""
        try:
            return [""] * 6  # 6 input fields
        except Exception as e:
            return [""] * 6

    def add_project(self, title, description, technologies, url, start_date, end_date, existing_table=None):
        """Add project to the list."""
        try:
            # Create new entry
            new_entry = [title, description, technologies, url, start_date, end_date]
            
            # Initialize list if no existing data
            if existing_table is None or not existing_table:
                return [new_entry]
            
            # Convert existing_table to list if it's a DataFrame
            if hasattr(existing_table, 'values') and hasattr(existing_table, 'to_dict'):
                existing_data = existing_table.values.tolist()
            # Handle Gradio DataFrame format
            elif isinstance(existing_table, dict) and 'data' in existing_table:
                existing_data = existing_table['data']
            # If it's already a list
            elif isinstance(existing_table, list):
                existing_data = existing_table
            else:
                existing_data = []
            
            # Create a new list with existing data + new entry
            result = list(existing_data)  # Create a copy of existing data
            result.append(new_entry)  # Add new entry
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return original data if there's an error
            return existing_table if existing_table is not None else []

    def remove_project(self, project_list, selected_rows):
        """Remove selected project entries."""
        try:
            if not project_list or not selected_rows:
                return project_list
            return [row for i, row in enumerate(project_list) if i not in selected_rows]
        except Exception as e:
            return project_list

    def clear_projects(self):
        """Clear all project entries."""
        try:
            return []
        except Exception as e:
            return []

    def reset_certifications(self):
        """Reset certifications fields."""
        try:
            return [""] * 5  # 5 input fields
        except Exception as e:
            return [""] * 5

    def add_certification(self, name, issuer, date_obtained, credential_id, url, existing_table=None):
        """Add certification to the list."""
        try:
            # Create new entry
            new_entry = [name, issuer, date_obtained, credential_id, url]
            
            # Initialize list if no existing data
            if existing_table is None or not existing_table:
                return [new_entry]
            
            # Convert existing_table to list if it's a DataFrame
            if hasattr(existing_table, 'values') and hasattr(existing_table, 'to_dict'):
                existing_data = existing_table.values.tolist()
            # Handle Gradio DataFrame format
            elif isinstance(existing_table, dict) and 'data' in existing_table:
                existing_data = existing_table['data']
            # If it's already a list
            elif isinstance(existing_table, list):
                existing_data = existing_table
            else:
                existing_data = []
            
            # Create a new list with existing data + new entry
            result = list(existing_data)  # Create a copy of existing data
            result.append(new_entry)  # Add new entry
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return original data if there's an error
            return existing_table if existing_table is not None else []

    def remove_certification(self, cert_list, selected_rows):
        """Remove selected certification entries."""
        try:
            if not cert_list or not selected_rows:
                return cert_list
            return [row for i, row in enumerate(cert_list) if i not in selected_rows]
        except Exception as e:
            return cert_list

    def clear_certifications(self):
        """Clear all certification entries."""
        try:
            return []
        except Exception as e:
            return []

    def test_api_key(self, api_key: str, model: str = None) -> str:
        """Test and save API key with the specified model."""
        return self.ai_features.test_api_key(api_key, model)
        
    def analyze_job_description(self, job_description: str, model: str = None) -> dict:
        """
        Analyze a job description using AI.
        
        Args:
            job_description: The job description text
            model: The model to use
            
        Returns:
            Analysis results
        """
        if not self.ai_features:
            return {"error": "AI provider not configured"}
        
        return self.ai_features.analyze_job_description(job_description, model)
        
    def tailor_resume(self, resume_data: dict, job_description: str, model: str = None) -> dict:
        """
        Tailor a resume to better match a job description.
        
        Args:
            resume_data: The resume data as a dictionary
            job_description: The job description to tailor the resume for
            model: The Gemini model to use
            
        Returns:
            A dictionary containing the tailored resume
        """
        if not self.ai_features:
            return {"error": "Gemini API key not configured"}
            
        return self.ai_features.tailor_resume(resume_data, job_description, model)
        
    def generate_cover_letter(self, resume_data: dict, job_description: str, model: str = None, user_prompt: str = None) -> str:
        """
        Generate a cover letter based on a resume and job description.
        
        Args:
            resume_data: The resume data as a dictionary
            job_description: The job description to tailor the cover letter for
            model: The Gemini model to use
            user_prompt: Optional user instructions for customizing the cover letter
            
        Returns:
            A string containing the generated cover letter
        """
        if not self.ai_features:
            return "Error: Gemini API key not configured"
            
        return self.ai_features.generate_cover_letter(resume_data, job_description, model, user_prompt)
        
    def get_improvement_suggestions(self, resume_data: dict, job_description: str, model: str = None) -> str:
        """
        Get suggestions for improving a resume based on a job description.
        
        Args:
            resume_data: The resume data as a dictionary
            job_description: The job description to compare the resume against
            model: The Gemini model to use
            
        Returns:
            A string containing improvement suggestions
        """
        if not self.ai_features:
            return "Error: Gemini API key not configured"
            
        return self.ai_features.get_improvement_suggestions(resume_data, job_description, model)

    def process_with_ai(self, job_description: str, resume_json: str, model: str = None) -> tuple:
        """Process resume with AI features."""
        try:
            if not job_description or not resume_json:
                return None, None, None, None, "Please provide both a job description and a resume"

            # Parse resume JSON
            try:
                if isinstance(resume_json, str):
                    resume_data = json.loads(resume_json)
                else:
                    resume_data = resume_json
            except json.JSONDecodeError:
                return None, None, None, None, "Invalid resume JSON format"
            
            # Analyze job description
            analysis = self.analyze_job_description(job_description, model)
            if "error" in analysis:
                return None, None, None, None, f"Error analyzing job description: {analysis['error']}"
            
            # Tailor resume
            tailored_resume = self.tailor_resume(resume_data, job_description, model)
            if isinstance(tailored_resume, dict) and "error" in tailored_resume:
                return None, None, None, None, f"Error tailoring resume: {tailored_resume['error']}"
            
            # Generate cover letter
            cover_letter = self.generate_cover_letter(tailored_resume, job_description, model)
            if cover_letter.startswith("Error:"):
                return None, None, None, None, cover_letter
            
            # Get improvement suggestions
            suggestions = self.get_improvement_suggestions(resume_data, job_description, model)
            if suggestions.startswith("Error:"):
                return None, None, None, None, suggestions
            
            return (
                json.dumps(analysis, indent=2),
                json.dumps(tailored_resume, indent=2),
                cover_letter,
                suggestions,
                "Success!"
            )
        except Exception as e:
            error_msg = f"Error processing resume: {str(e)}"
            return None, None, None, None, error_msg

    def clear_form(self):
        """Clear all form inputs. This is used before loading new data."""
        # Reset all personal info fields to empty
        self.reset_personal_info()
        
        # Clear all table data
        self.clear_education()
        self.clear_work_experience()
        self.clear_skills()
        self.clear_projects()
        self.clear_certifications()

    def load_from_json(self, file_path):
        """Load resume data from a JSON file and return values to populate the form."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Prepare result to return values
            result = []
            
            # Personal info values
            email = data.get('email', '')
            full_name = data.get('full_name', '')
            phone = data.get('phone', '')
            address = data.get('current_address', '')
            location = data.get('location', '')
            citizenship = data.get('citizenship', '')
            linkedin = data.get('linkedin_url', '')
            github = data.get('github_url', '')
            portfolio = data.get('portfolio_url', '')
            summary = data.get('summary', '')
            
            # Add personal info to result
            result.extend([
                email, full_name, phone, address, location, 
                citizenship, linkedin, github, portfolio, summary, ""
            ])
            
            # Add empty education input fields
            result.extend(["", "", "", "", "", "", ""])
            
            # Process education data
            education_entries = []
            # Try both singular and plural forms for backward compatibility
            for entry in data.get('education', []) or data.get('educations', []):
                if entry:  # Skip empty entries
                    education_entries.append([
                        entry.get('institution', ''),
                        entry.get('degree', ''),
                        entry.get('field_of_study', ''),
                        entry.get('gpa', ''),
                        entry.get('start_date', ''),
                        entry.get('end_date', ''),
                        entry.get('description', '')
                    ])
            result.append(education_entries)
            
            # Add empty work experience input fields
            result.extend(["", "", "", "", "", "", ""])
            
            # Process work experience data
            work_entries = []
            # Try both singular and plural forms for backward compatibility
            for entry in data.get('work_experience', []) or data.get('experience', []) or data.get('experiences', []):
                if not entry:  # Skip empty entries
                    continue
                
                company = entry.get('company', '')
                position = entry.get('position', '')
                location = entry.get('location', '')
                start_date = entry.get('start_date', '')
                end_date = entry.get('end_date', '')
                description = entry.get('description', '')
                
                # Process achievements
                achievements = entry.get('achievements', '')
                formatted_achievements = ''
                
                if isinstance(achievements, list):
                    formatted_achievements = '\n'.join([f"- {item}" for item in achievements if item])
                elif isinstance(achievements, str) and achievements:
                    lines = achievements.split('\n')
                    processed_lines = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Remove bullet if present
                            if line.startswith('- '):
                                line = line[2:]
                            elif line.startswith('-'):
                                line = line[1:].strip()
                            processed_lines.append(f"- {line}")
                    formatted_achievements = '\n'.join(processed_lines)
                
                work_entries.append([
                    company,
                    position,
                    location,
                    start_date,
                    end_date,
                    description,
                    formatted_achievements
                ])
            result.append(work_entries)
            
            # Add empty skills input fields
            result.extend(["", "", ""])
            
            # Process skills data
            skills_entries = []
            
            # First try the array format
            if 'skills' in data and isinstance(data['skills'], list):
                for skill in data['skills']:
                    if isinstance(skill, dict):
                        skills_entries.append([
                            skill.get('category', ''),
                            skill.get('name', ''),
                            skill.get('proficiency', '')
                        ])
            # Then try the dictionary format
            elif 'skills_dict' in data and isinstance(data['skills_dict'], dict):
                for category, skills in data['skills_dict'].items():
                    if isinstance(skills, list):
                        for skill in skills:
                            # Try to parse proficiency if in format "Name (Proficiency)"
                            name = skill
                            proficiency = ''
                            if '(' in skill and skill.endswith(')'):
                                parts = skill.split('(')
                                if len(parts) == 2:
                                    name = parts[0].strip()
                                    proficiency = parts[1].rstrip(')')
                            skills_entries.append([category, name, proficiency])
            # Finally try the raw skills list if present
            elif 'skills' in data and isinstance(data['skills'], dict):
                for category, skills in data['skills'].items():
                    if isinstance(skills, list):
                        for skill in skills:
                            if isinstance(skill, str):
                                skills_entries.append([category, skill, ''])
                            elif isinstance(skill, dict):
                                skills_entries.append([
                                    category,
                                    skill.get('name', ''),
                                    skill.get('proficiency', '')
                                ])
            
            result.append(skills_entries)
            
            # Add empty projects input fields
            result.extend(["", "", "", "", "", ""])
            
            # Process projects data
            project_entries = []
            for project in data.get('projects', []):
                if project:  # Skip empty entries
                    project_entries.append([
                        project.get('name', '') or project.get('title', ''),
                        project.get('description', ''),
                        project.get('technologies', ''),
                        project.get('url', ''),
                        project.get('start_date', ''),
                        project.get('end_date', '')
                    ])
            result.append(project_entries)
            
            # Add empty certifications input fields
            result.extend(["", "", "", "", ""])
            
            # Process certifications data
            cert_entries = []
            for cert in data.get('certifications', []):
                if cert:  # Skip empty entries
                    cert_entries.append([
                        cert.get('name', ''),
                        cert.get('issuer', ''),
                        cert.get('date', '') or cert.get('date_obtained', ''),
                        cert.get('id', '') or cert.get('credential_id', ''),
                        cert.get('url', '')
                    ])
            result.append(cert_entries)
            
            print(f"Processed JSON data, returning {len(result)} elements")
            return result
            
        except Exception as e:
            print(f"Error loading resume data: {str(e)}")
            raise

    def load_software_developer_example(self):
        """Load example profile with direct UI updates."""
        try:
            example_data = {
                'email': 'dev.example@email.com',
                'full_name': 'Alex Johnson',
                'phone': '(555) 123-4567',
                'current_address': '123 Tech Street',
                'location': 'San Francisco, CA',
                'citizenship': 'US Citizen',
                'linkedin_url': 'linkedin.com/in/alexjohnson',
                'github_url': 'github.com/alexj-dev',
                'portfolio_url': 'alexjohnson.dev',
                'summary': 'Full Stack Developer with 5 years of experience building scalable web applications. Expertise in Python, JavaScript, and cloud technologies.',
                'education': [{
                    'institution': 'University of California, Berkeley',
                    'degree': 'Bachelor of Science',
                    'field_of_study': 'Computer Science',
                    'start_date': '2015',
                    'end_date': '2019',
                    'gpa': '3.8',
                    'description': 'Focus on Software Engineering and Distributed Systems'
                }],
                'experience': [{
                    'company': 'TechCorp Inc.',
                    'position': 'Senior Software Engineer',
                    'location': 'San Francisco, CA',
                    'start_date': '2021',
                    'end_date': 'Present',
                    'description': 'Lead developer for cloud-based enterprise applications',
                    'achievements': '- Reduced server costs by 40% through microservices optimization\n- Led team of 5 developers in major platform redesign\n- Implemented CI/CD pipeline reducing deployment time by 60%'
                }],
                'skills': [
                    {
                        'category': 'Programming',
                        'name': 'Python',
                        'proficiency': 'Expert'
                    },
                    {
                        'category': 'Programming',
                        'name': 'JavaScript',
                        'proficiency': 'Expert'
                    },
                    {
                        'category': 'Framework',
                        'name': 'React',
                        'proficiency': 'Advanced'
                    },
                    {
                        'category': 'Framework',
                        'name': 'Django',
                        'proficiency': 'Expert'
                    },
                    {
                        'category': 'Cloud',
                        'name': 'AWS',
                        'proficiency': 'Advanced'
                    },
                    {
                        'category': 'Tools',
                        'name': 'Docker',
                        'proficiency': 'Advanced'
                    },
                    {
                        'category': 'Tools',
                        'name': 'Git',
                        'proficiency': 'Expert'
                    }
                ],
                'projects': [{
                    'title': 'Cloud Migration Platform',
                    'description': 'Developed a platform to automate cloud migration processes for enterprise clients',
                    'technologies': 'Python, AWS, Docker, Kubernetes',
                    'url': 'github.com/alexj-dev/cloud-migration',
                    'start_date': '2022',
                    'end_date': '2023'
                }],
                'certifications': [{
                    'name': 'AWS Certified Solutions Architect',
                    'issuer': 'Amazon Web Services',
                    'date_obtained': '2023',
                    'credential_id': 'AWS-123456',
                    'url': 'https://aws.amazon.com/verification'
                }]
            }

            # Convert education list to table format
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
                work_table.append([
                    work['company'],
                    work['position'],
                    work['location'],
                    work['start_date'],
                    work['end_date'],
                    work['description'],
                    work['achievements']
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
                    project['title'],
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
                # Education
                "", "", "", "", "", "", "",  # Reset input fields
                education_table,  # Update table
                # Work Experience
                "", "", "", "", "", "", "",  # Reset input fields
                work_table,  # Update table
                # Skills
                "", "", "",  # Reset input fields
                skills_table,  # Update table
                # Projects
                "", "", "", "", "", "",  # Reset input fields
                projects_table,  # Update table
                # Certifications
                "", "", "", "", "",  # Reset input fields
                certs_table  # Update table
            ]
        except Exception as e:
            import traceback
            traceback.print_exc()
            return [
                # Personal Info
                "", "", "", "", "", "", "", "", "", "", f"Error loading example: {str(e)}",
                # Education
                "", "", "", "", "", "", "", [],
                # Work Experience
                "", "", "", "", "", "", "", [],
                # Skills
                "", "", "", [],
                # Projects
                "", "", "", "", "", "", [],
                # Certifications
                "", "", "", "", "", []
            ]

    def build_profile_dict(self, email, full_name, phone, address, location, citizenship,
                     linkedin, github, portfolio, summary,
                     education_table, work_table, skills_table, projects_table, certs_table):
        """Build a profile dictionary from form values."""
        profile = {
            'email': email,
            'full_name': full_name,
            'phone': phone,
            'current_address': address,
            'location': location,
            'citizenship': citizenship,
            'linkedin_url': linkedin,
            'github_url': github,
            'portfolio_url': portfolio,
            'summary': summary,
            'education': [],  # Use singular form as the standard
            'experience': [],  # Use singular form as the standard
            'skills': {},
            'projects': [],
            'certifications': []
        }

        # Convert education table to list of dictionaries
        try:
            edu_data = self.extract_table_data(education_table)
            for row in edu_data:
                if isinstance(row, list) and len(row) >= 7 and any(str(x).strip() for x in row):
                    education_entry = {
                        'institution': str(row[0]),
                        'degree': str(row[1]),
                        'field_of_study': str(row[2]),
                        'gpa': str(row[3]),
                        'start_date': str(row[4]),
                        'end_date': str(row[5]),
                        'description': str(row[6])
                    }
                    # Add to education field
                    profile['education'].append(education_entry)
        except Exception:
            pass

        # Convert work experience table to list of dictionaries
        try:
            work_data = self.extract_table_data(work_table)
            for row in work_data:
                if isinstance(row, list) and len(row) >= 7 and any(str(x).strip() for x in row):
                    # Get achievements text and process bullet points
                    achievements_text = str(row[6])
                    
                    # Process achievements text to preserve bullet points
                    # If there are bullet points, convert to a list
                    if '-' in achievements_text:
                        achievement_lines = achievements_text.split('\n')
                        bullet_items = []
                        
                        for line in achievement_lines:
                            line = line.strip()
                            if line:
                                if line.startswith('- '):
                                    bullet_items.append(line[2:])  # Remove the "- " prefix
                                elif line.startswith('-'):
                                    bullet_items.append(line[1:].strip())  # Remove the "-" prefix
                                else:
                                    bullet_items.append(line)
                        
                        achievements_value = bullet_items
                    else:
                        # If no bullet points are found, keep as a single string
                        achievements_value = achievements_text
                    
                    work_entry = {
                        'company': str(row[0]),
                        'position': str(row[1]),
                        'location': str(row[2]),
                        'start_date': str(row[3]),
                        'end_date': str(row[4]),
                        'description': str(row[5]),
                        'achievements': achievements_value
                    }
                    # Add to experience field
                    profile['experience'].append(work_entry)
        except Exception as e:
            import traceback
            print(f"Error processing work experience: {str(e)}")
            traceback.print_exc()
        
        # Convert skills table to list of dictionaries
        try:
            skill_data = self.extract_table_data(skills_table)
            skills_list = []
            skills_dict = {}
            
            for row in skill_data:
                if isinstance(row, list) and len(row) >= 3 and any(str(x).strip() for x in row):
                    category = str(row[0])
                    skill_name = str(row[1])
                    proficiency = str(row[2])
                    
                    # Add as a skill object for array format
                    skills_list.append({
                        'category': category,
                        'name': skill_name,
                        'proficiency': proficiency
                    })
                    
                    # Also add to dictionary format
                    if category not in skills_dict:
                        skills_dict[category] = []
                    
                    # Format as either "Name (Proficiency)" or just "Name"
                    skill_text = f"{skill_name} ({proficiency})" if proficiency else skill_name
                    skills_dict[category].append(skill_text)
            
            # Provide both formats for compatibility
            profile['skills'] = skills_list  # Array format (preferred for newer versions)
            if skills_dict:  # Only set if not empty
                profile['skills_dict'] = skills_dict  # Dictionary format (for older versions)
        except Exception:
            pass

        # Convert projects table to list of dictionaries
        try:
            project_data = self.extract_table_data(projects_table)
            for row in project_data:
                if isinstance(row, list) and len(row) >= 6 and any(str(x).strip() for x in row):
                    profile['projects'].append({
                        'title': str(row[0]),
                        'description': str(row[1]),
                        'technologies': str(row[2]),
                        'url': str(row[3]),
                        'start_date': str(row[4]),
                        'end_date': str(row[5])
                    })
        except Exception:
            pass

        # Convert certifications table to list of dictionaries
        try:
            cert_data = self.extract_table_data(certs_table)
            for row in cert_data:
                if isinstance(row, list) and len(row) >= 5 and any(str(x).strip() for x in row):
                    profile['certifications'].append({
                        'name': str(row[0]),
                        'issuer': str(row[1]),
                        'date_obtained': str(row[2]),
                        'credential_id': str(row[3]),
                        'url': str(row[4])
                    })
        except Exception:
            pass

        return profile


def create_app():
    """Create the Gradio application with a modular structure."""
    resume_helper = ResumeHelper()
    
    with gr.Blocks(title="Resume Helper") as app:
        with gr.Row():
            gr.Markdown("# Resume Helper")            
        
        with gr.Tabs() as tabs:
            # Create tabs
            personal_info_tab_wrapper = create_personal_info_tab(resume_helper)
            educations_tab_wrapper = create_educations_tab(resume_helper)
            experiences_tab_wrapper = create_experiences_tab(resume_helper)
            skills_tab_wrapper = create_skills_tab(resume_helper)
            projects_tab_wrapper = create_projects_tab(resume_helper)
            certifications_tab_wrapper = create_certifications_tab(resume_helper)
            
            # Extract actual tab objects for Gradio
            personal_info_tab = personal_info_tab_wrapper.tab
            educations_tab = educations_tab_wrapper.tab
            experiences_tab = experiences_tab_wrapper.tab
            skills_tab = skills_tab_wrapper.tab
            projects_tab = projects_tab_wrapper.tab
            certifications_tab = certifications_tab_wrapper.tab
            
            # Collect components from all tabs
            all_tabs_components = {
                'personal_info_tab': personal_info_tab_wrapper.components,
                'educations_tab': educations_tab_wrapper.components,
                'experiences_tab': experiences_tab_wrapper.components,
                'skills_tab': skills_tab_wrapper.components,
                'projects_tab': projects_tab_wrapper.components,
                'certifications_tab': certifications_tab_wrapper.components,
            }
            
            # Create tabs that depend on components from other tabs
            generate_resume_tab_wrapper = create_generate_resume_tab(resume_helper, all_tabs_components)
            all_tabs_components['generate_resume_tab'] = generate_resume_tab_wrapper.components
            
            ai_resume_helper_tab_wrapper = create_ai_resume_helper_tab(resume_helper, all_tabs_components)
            all_tabs_components['ai_resume_helper_tab'] = ai_resume_helper_tab_wrapper.components
            
            # Extract these tabs as well
            generate_resume_tab = generate_resume_tab_wrapper.tab
            ai_resume_helper_tab = ai_resume_helper_tab_wrapper.tab
            
            # Set up the example button click event
            if 'example1_btn' in personal_info_tab_wrapper.components:
                personal_info_tab_wrapper.components['example1_btn'].click(
                    fn=resume_helper.load_software_developer_example,
                    inputs=[],
                    outputs=[
                        # Personal Info
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
                        certifications_tab_wrapper.components['cert_list']
                    ],
                    show_progress=True
                )
    
    return app

# Launch the app with optimized settings
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

