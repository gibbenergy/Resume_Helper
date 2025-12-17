"""
Resume Helper Business Logic - AI-powered workflows and tasks

This module contains all the specialized AI workflows for resume and job application tasks.
It uses the LiteLLM provider as a foundation but focuses on business logic rather than provider management.
"""

import json
import re
import hashlib
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ResumeAIWorkflows:
    """
    Business logic class for AI-powered resume and job application workflows.
    
    This class handles the high-level business operations while delegating
    LLM calls to the LiteLLMProvider for clean separation of concerns.
    """
    
    def __init__(self, llm_provider):
        """Initialize with an LLM provider instance."""
        self.llm_provider = llm_provider
        # Cache to avoid duplicate API calls for same job description
        self._job_analysis_cache = {}
        
    # ===== JOB ANALYSIS WORKFLOWS =====
    
    def _create_cache_key(self, job_description: str, resume_data: Optional[Dict] = None) -> str:
        """Create a cache key for job description and optionally resume data."""
        content = job_description
        if resume_data:
            content += json.dumps(resume_data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from response, handling markdown code blocks if present."""
        if not content:
            return content
        
        content = content.strip()
        
        # Remove markdown code block markers if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first line if it's a code block marker
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line if it's a code block marker
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        
        return content
    
    def analyze_job_description(self, job_description: str, model: Optional[str] = None, resume_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a job description comprehensively with insights and recommendations, 
        including match score calculation against the candidate's resume.
        Uses caching to avoid duplicate API calls."""
        
        if not resume_data:
            logger.error("❌ Resume data is required for job analysis")
            return {"success": False, "error": "Resume data is required for job analysis"}
        
        from utils.privacy_manager import PrivacyManager
        sanitized_resume, _ = PrivacyManager.sanitize_resume_data(resume_data)
        cache_key = self._create_cache_key(job_description + json.dumps(sanitized_resume))
        
        if cache_key in self._job_analysis_cache:
            logger.info("🚀 Using cached job analysis - NO API call needed!")
            return self._job_analysis_cache[cache_key]
        
        logger.info("🤖 Making API call for comprehensive job analysis + match score")
        
        prompt = f"""
        Perform a COMPREHENSIVE ANALYSIS of this job description and calculate how well the candidate's resume matches.
        
        Job Description:
        {job_description}
        
        CANDIDATE RESUME:
        {json.dumps(sanitized_resume, indent=2)}
        
        Return JSON with these keys (use snake_case):
        
        1. "position_title": The job title/position
        2. "company_name": The company name (or "Not Specified" if unclear)
        3. "location": Location/remote status
        4. "employment_type": Full-time/Contract/etc
        5. "experience_level": Junior/Mid/Senior level
        
        6. "required_skills": List of must-have technical and soft skills
        7. "preferred_skills": Nice-to-have skills and qualifications
        8. "education_requirements": Degree requirements and certifications
        
        9. "responsibilities": Main duties and accountabilities
        10. "role_insights": What this role really entails (2-3 sentences analyzing the actual day-to-day work, level of autonomy, collaboration requirements)
        
        11. "company_culture_indicators": What the job posting reveals about company culture, values, and work environment (2-3 sentences)
        12. "growth_opportunities": Career progression potential and learning opportunities mentioned or implied (2-3 sentences)
        
        13. "red_flags_or_considerations": Any concerns or things to investigate further (e.g., unrealistic expectations, vague descriptions, excessive requirements). List 2-3 items or "None apparent"
        14. "unique_selling_points": What makes this opportunity attractive or distinctive (2-3 points)
        
        15. "strategic_application_tips": Specific advice for applying to THIS role (3-4 actionable tips based on what they emphasize)
        16. "keywords_for_ats": Critical keywords to include in resume/cover letter for ATS screening
        
        17. "estimated_salary_range": Educated guess based on role, skills, and seniority (include reasoning)
        18. "interview_preparation_focus": Key areas to prepare for interviews based on requirements
        
        RESUME MATCH SCORING:
        Calculate how well the candidate's resume matches this job description.
        
        19. "match_score": Overall match score (integer 0-100)
        20. "skills_match": Skills alignment percentage (0-100)
        21. "experience_match": Experience relevance percentage (0-100)
        22. "education_match": Education requirements match percentage (0-100)
        23. "match_summary": Brief explanation of the match score (2-3 sentences analyzing strengths and gaps)
        
        Analyze how well the resume aligns with: required_skills, experience_level, education_requirements, responsibilities.
        
        Provide thorough, insightful analysis - not just data extraction. Be specific and actionable.
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = self.llm_provider.prompt_function(messages, model=model, response_format={"type": "json_object"})
        
        if result["success"]:
            try:
                # Extract JSON from response (handles markdown code blocks)
                json_content = self._extract_json_from_response(result["content"])
                analysis = json.loads(json_content)
                
                if not isinstance(analysis, dict):
                    logger.error(f"❌ LLM returned non-dict: {type(analysis)}")
                    return {"success": False, "error": f"Invalid response format: expected dict, got {type(analysis).__name__}"}
                
                required_fields = [
                    "position_title", "company_name", "required_skills", 
                    "keywords_for_ats", "strategic_application_tips",
                    "match_score", "skills_match", "experience_match", 
                    "education_match", "match_summary"
                ]
                
                missing_fields = [f for f in required_fields if f not in analysis]
                if missing_fields:
                    logger.error(f"❌ LLM response missing required fields: {missing_fields}")
                    return {
                        "success": False, 
                        "error": f"Invalid job analysis: missing required fields: {', '.join(missing_fields)}"
                    }
                
                response = {"success": True, "analysis": analysis, "usage": result.get("usage", {})}
                self._job_analysis_cache[cache_key] = response
                logger.info(f"✅ Validated and cached job analysis with key: {cache_key[:8]}...")
                
                return response
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed for job analysis")
                logger.error(f"Raw response (first 500 chars): {result['content'][:500]}")
                logger.error(f"JSON decode error: {e}")
                
                # Try with extracted JSON
                try:
                    json_content = self._extract_json_from_response(result["content"])
                    analysis = json.loads(json_content)
                    
                    # Continue with validation
                    if not isinstance(analysis, dict):
                        return {"success": False, "error": f"Invalid response format: expected dict, got {type(analysis).__name__}"}
                    
                    required_fields = [
                        "position_title", "company_name", "required_skills", 
                        "keywords_for_ats", "strategic_application_tips",
                        "match_score", "skills_match", "experience_match", 
                        "education_match", "match_summary"
                    ]
                    
                    missing_fields = [f for f in required_fields if f not in analysis]
                    if missing_fields:
                        return {
                            "success": False, 
                            "error": f"Invalid job analysis: missing required fields: {', '.join(missing_fields)}"
                        }
                    
                    response = {"success": True, "analysis": analysis, "usage": result.get("usage", {})}
                    self._job_analysis_cache[cache_key] = response
                    logger.info(f"✅ Validated and cached job analysis with key: {cache_key[:8]}...")
                    return response
                except json.JSONDecodeError:
                    return {"success": False, "error": f"Failed to parse JSON: {str(e)}. Raw response: {result['content'][:200]}"}
        return {"success": False, "error": result["error"]}
    
    # ===== COVER LETTER WORKFLOWS =====
    
    def generate_cover_letter(self, resume_data: Dict[str, Any], job_description: str, 
                            model: Optional[str] = None, user_prompt: Optional[str] = None,
                            job_analysis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a cover letter."""
        from utils.privacy_manager import PrivacyManager
        sanitized_resume, personal_info = PrivacyManager.sanitize_resume_data(resume_data)
        
        if not job_analysis_data:
            logger.error("❌ Cover letter generation requires job analysis data")
            return {
                "body_content": "Error: Please analyze the job first before generating a cover letter.",
                "company_name": "",
                "job_position": "",
                "letter_title": "Cover Letter",
                "recipient_greeting": "",
                "request_id": "",
                "usage": {}
            }
        
        name = personal_info.get("personal_info", {}).get("name", "the candidate")
        job_info = json.dumps(job_analysis_data, indent=2)
        
        base_requirements = """
        Resume: {resume}
        
        Job Analysis (Structured):
        {job_data}
        
        REQUIREMENTS:
        - Write 5-6 natural, flowing paragraphs with substantial detail
        - Connect the candidate's specific experience to required_skills and responsibilities
        - Be professional yet engaging, matching the company_culture_indicators
        - 500-700 words total (significantly longer and more comprehensive)
        - Start with expressing interest in the specific position_title at company_name
        - Include detailed examples of relevant projects, achievements, and experiences
        - Highlight relevant skills from keywords_for_ats with specific context
        - Apply strategic_application_tips to demonstrate fit with concrete examples
        - Show deep understanding of the role and company
        - End with enthusiasm for next steps
        - Use "I" perspective but avoid mentioning specific personal details
        
        IMPORTANT: Generate ONLY the body paragraphs of the cover letter, not the header, greeting, or closing.
        The template already includes the header (name, contact info), greeting (Dear Hiring Manager), and footer (Sincerely, signature).
        
        Generate actual paragraph content, not structural descriptions. Write the complete cover letter body that would impress a hiring manager with its depth and detail.
        """
        
        if user_prompt:
            prompt = f"""
            ⚠️ ADDITIONAL USER REQUIREMENTS - MUST FOLLOW THESE INSTRUCTIONS:
            {user_prompt}
            ⚠️ END OF ADDITIONAL REQUIREMENTS
            
            {base_requirements.format(resume=json.dumps(sanitized_resume), job_data=job_info)}
            
            REMEMBER: Follow ALL requirements above, INCLUDING the additional user requirements.
            """
        else:
            prompt = base_requirements.format(resume=json.dumps(sanitized_resume), job_data=job_info)
        
        messages = [{"role": "user", "content": prompt}]
        
        # Set appropriate max_tokens based on provider
        # Ollama: Lower limit for local resource constraints
        # API providers: High limit for reasoning models (GPT-5, o1, o3) that use tokens for internal reasoning
        provider = getattr(self.llm_provider, 'provider', '').lower()
        max_tokens = 1500 if provider == 'ollama' else 25000
        
        result = self.llm_provider.prompt_function(messages, model=model, max_tokens=max_tokens)
        
        if result["success"]:
            cover_letter_content = self.post_process_cover_letter(result["content"], result["request_id"])
            
            company_name = job_analysis_data.get("company_name", "") if job_analysis_data else ""
            job_position = job_analysis_data.get("position_title", "") if job_analysis_data else ""
            
            return {
                "body_content": cover_letter_content,
                "company_name": company_name,
                "job_position": job_position,
                "letter_title": "",  # Let template generate proper title based on job_position and company_name
                "recipient_greeting": "Dear Hiring Manager,",
                "request_id": result.get("request_id", ""),
                "usage": result.get("usage", {})
            }
        
        return {
            "body_content": f"Error: {result['error']}",
            "company_name": "",
            "job_position": "",
            "letter_title": "Cover Letter",
            "recipient_greeting": "",
            "request_id": result.get("request_id", ""),
            "usage": {}
        }
    
    def post_process_cover_letter(self, cover_letter: str, request_id: str) -> str:
        """Fix common issues in generated cover letters and ensure it's body content only."""
        processed = cover_letter.strip()
        
        greeting_patterns = [
            r'^Dear\s+[^,\n]+,?\s*\n?',  # Dear [Name],
            r'^Dear\s+Hiring\s+Manager,?\s*\n?',  # Dear Hiring Manager,
            r'^To\s+Whom\s+It\s+May\s+Concern,?\s*\n?',  # To Whom It May Concern,
            r'^Hello,?\s*\n?',  # Hello,
            r'^Hi,?\s*\n?',  # Hi,
        ]
        
        for pattern in greeting_patterns:
            processed = re.sub(pattern, '', processed, flags=re.IGNORECASE | re.MULTILINE)
        
        # Don't remove "thank you" phrases in the middle of the letter!
        if processed.strip():
            lines = processed.split('\n')
            closing_keywords = ['sincerely', 'best regards', 'yours truly', 'kind regards', 'respectfully', 'warmly', 'regards']
            while lines and any(keyword in lines[-1].lower() for keyword in closing_keywords):
                lines.pop()
            processed = '\n'.join(lines)
        
        processed = re.sub(r'\u2014', '; ', processed)
        processed = re.sub(r'\n\s*\n\s*\n+', '\n\n', processed)
        processed = re.sub(r' +', ' ', processed)
        processed = re.sub(r'^\s+', '', processed)
        processed = re.sub(r'\s+$', '', processed)
        processed = re.sub(r'\n\n+', '\n\n', processed)
        
        return processed
    
    # ===== RESUME OPTIMIZATION WORKFLOWS =====
    
    def tailor_resume(self, resume_data: Dict, job_description: str, model: Optional[str] = None, user_prompt: Optional[str] = None, job_analysis_data: Optional[Dict[str, Any]] = None) -> Dict:
        """Tailor a resume to better match a job description."""
        from utils.privacy_manager import PrivacyManager
        sanitized_resume, personal_info = PrivacyManager.sanitize_resume_data(resume_data)
        
        if not job_analysis_data:
            logger.error("❌ Resume tailoring requires job analysis data")
            return {
                "success": False,
                "error": "Please analyze the job first before tailoring the resume.",
                "tailored_resume": {},
                "request_id": "",
                "usage": {}
            }
        
        job_requirements = json.dumps(job_analysis_data, indent=2)
        
        prompt = f"""
        GOAL: Maximize ATS score by optimizing how EXISTING qualifications are presented.
        
        INPUT RESUME:
        {json.dumps(sanitized_resume, indent=2)}
        
        JOB REQUIREMENTS (Structured Analysis):
        {job_requirements}
        
        LEGAL CONSTRAINTS (CRITICAL - DO NOT VIOLATE):
        - DO NOT add skills, certifications, or technologies not in the original resume
        - DO NOT fabricate experience, achievements, or responsibilities
        - DO NOT invent job titles, companies, projects, or education
        - ONLY rephrase and optimize EXISTING content
        
        OPTIMIZATION STRATEGY:
        1. Rephrase existing skills/experience using keywords from required_skills and keywords_for_ats
        2. Reorder and emphasize content most relevant to this role based on responsibilities
        3. Rewrite existing achievements to highlight measurable impact
        4. Align summary with position requirements using existing qualifications
        5. Use industry-standard terminology for existing skills
        6. Apply strategic_application_tips to highlight relevant experience
        
        OUTPUT: Return same JSON structure with optimized wording of EXISTING content only.
        """
        
        if user_prompt and user_prompt.strip():
            prompt += f"""
        
        ADDITIONAL USER REQUIREMENTS:
        {user_prompt.strip()}
        """
        
        prompt += "\n\nReturn ONLY valid JSON."
        
        messages = [{"role": "user", "content": prompt}]
        result = self.llm_provider.prompt_function(messages, model=model, response_format={"type": "json_object"})
        
        if result["success"]:
            try:
                tailored_professional_content = json.loads(result["content"])
                
                # 🔧 NORMALIZE & VALIDATE: Use schema to fix structure issues
                from infrastructure.frameworks.schema_engine import SchemaEngine
                from models.resume import ResumeSchema
                
                normalized_content = {}
                
                for section_name, section_schema in [
                    ('education', ResumeSchema.EDUCATION),
                    ('experience', ResumeSchema.EXPERIENCE),
                    ('skills', ResumeSchema.SKILLS),
                    ('projects', ResumeSchema.PROJECTS),
                    ('certifications', ResumeSchema.CERTIFICATIONS)
                ]:
                    if section_name in sanitized_resume:
                        ai_data = tailored_professional_content.get(section_name)
                        if ai_data is None:
                            ai_data = tailored_professional_content.get(section_name + 's')
                        if ai_data is None:
                            ai_data = tailored_professional_content.get(section_name[:-1]) if section_name.endswith('s') else None
                        
                        if ai_data is None or not isinstance(ai_data, list):
                            logger.warning(f"AI output missing or invalid '{section_name}', using original")
                            normalized_content[section_name] = sanitized_resume[section_name]
                        else:
                            # For experience: convert achievements list → string (to match GUI format)
                            if section_name == 'experience':
                                pre_normalized = []
                                for item in ai_data:
                                    if isinstance(item, dict):
                                        item_copy = dict(item)
                                        if 'achievements' in item_copy:
                                            achievements = item_copy['achievements']
                                            if isinstance(achievements, list):
                                                # ["item1", "item2"] → "- item1\n- item2"
                                                item_copy['achievements'] = '\n'.join([f"- {a}" for a in achievements if a])
                                            elif not isinstance(achievements, str):
                                                item_copy['achievements'] = ''
                                        pre_normalized.append(item_copy)
                                
                                normalized_items = SchemaEngine.extract_list_fields(pre_normalized, section_schema)
                            else:
                                normalized_items = SchemaEngine.extract_list_fields(ai_data, section_schema)
                            
                            normalized_content[section_name] = normalized_items
                
                if 'summary' in sanitized_resume:
                    ai_summary = tailored_professional_content.get('summary')
                    if ai_summary is None:
                        ai_summary = tailored_professional_content.get('professional_summary', {}).get('summary') if isinstance(tailored_professional_content.get('professional_summary'), dict) else tailored_professional_content.get('professional_summary')
                    
                    if ai_summary and isinstance(ai_summary, str):
                        normalized_content['summary'] = ai_summary
                    else:
                        logger.warning(f"AI output missing or invalid 'summary', using original")
                        normalized_content['summary'] = sanitized_resume.get('summary', '')
                
                if 'others' in sanitized_resume:
                    ai_others = tailored_professional_content.get('others')
                    if isinstance(ai_others, dict):
                        normalized_content['others'] = ai_others
                    else:
                        normalized_content['others'] = sanitized_resume.get('others', {})
                
                logger.info(f"✅ AI output normalized using schema - all sections validated")
                
                complete_tailored_resume = PrivacyManager.merge_personal_info_for_documents(
                    normalized_content, personal_info
                )
                
                if complete_tailored_resume.get('email') and '@' in str(complete_tailored_resume.get('full_name', '')):
                    logger.error(f"Personal info corrupted! full_name contains '@': {complete_tailored_resume.get('full_name')}")
                    complete_tailored_resume = PrivacyManager.merge_personal_info_for_documents(
                        sanitized_resume, personal_info
                    )
                
                original_metadata = resume_data.get("metadata", {})
                if original_metadata and "metadata" not in complete_tailored_resume:
                    complete_tailored_resume["metadata"] = original_metadata.copy()
                
                return {
                    "success": True, 
                    "tailored_resume": complete_tailored_resume, 
                    "usage": result.get("usage", {}),
                    "privacy_protected": True
                }
            except json.JSONDecodeError:
                return {"success": False, "error": "Failed to parse JSON"}
        return {"success": False, "error": result["error"]}
    
    def get_improvement_suggestions(self, resume_data: Dict, job_description: str, 
                                  model: Optional[str] = None, job_analysis_data: Optional[Dict[str, Any]] = None) -> str:
        """Get suggestions for improving a resume."""
        from utils.privacy_manager import PrivacyManager
        sanitized_resume, personal_info = PrivacyManager.sanitize_resume_data(resume_data)
        
        if not job_analysis_data:
            logger.error("❌ Improvement suggestions require job analysis data")
            return {
                "content": "Error: Please analyze the job first before requesting improvement suggestions.",
                "usage": {}
            }
        
        job_info = json.dumps(job_analysis_data, indent=2)
        
        prompt = f"""
        Analyze this resume against the job requirements and provide specific, actionable improvement suggestions.
        
        Resume: {json.dumps(sanitized_resume)}
        
        Job Analysis (Structured):
        {job_info}
        
        Return a JSON object with the following structure:
        {{
            "skills_enhancement": ["suggestion 1", "suggestion 2", ...],
            "experience_optimization": ["suggestion 1", "suggestion 2", ...],
            "content_improvements": ["suggestion 1", "suggestion 2", ...],
            "formatting_presentation": ["suggestion 1", "suggestion 2", ...],
            "keyword_optimization": ["suggestion 1", "suggestion 2", ...],
            "cultural_fit": ["suggestion 1", "suggestion 2", ...]
        }}
        
        Guidelines:
        - skills_enhancement: Compare against required_skills and preferred_skills, provide specific skill recommendations based on gaps
        - experience_optimization: How to better align with responsibilities and role_insights, keywords from keywords_for_ats to incorporate
        - content_improvements: Apply strategic_application_tips, quantifiable achievements to highlight based on experience_level
        - formatting_presentation: Layout and organization suggestions
        - keyword_optimization: Industry-specific terms from keywords_for_ats, ATS-friendly improvements
        - cultural_fit: Suggestions based on company_culture_indicators, how to demonstrate alignment with company values
        
        Make each suggestion specific and actionable. Focus on improvements that will increase the match score with this particular job.
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = self.llm_provider.prompt_function(messages, model=model, response_format={"type": "json_object"})
        
        if result["success"]:
            try:
                # Extract JSON from response (handles markdown code blocks)
                json_content = self._extract_json_from_response(result["content"])
                suggestions_json = json.loads(json_content)
                
                # Convert JSON to formatted text with bold section headers
                formatted_sections = []
                section_headers = {
                    "skills_enhancement": "SKILLS ENHANCEMENT",
                    "experience_optimization": "EXPERIENCE OPTIMIZATION",
                    "content_improvements": "CONTENT IMPROVEMENTS",
                    "formatting_presentation": "FORMATTING & PRESENTATION",
                    "keyword_optimization": "KEYWORD OPTIMIZATION",
                    "cultural_fit": "CULTURAL FIT"
                }
                
                for key, header in section_headers.items():
                    if key in suggestions_json and suggestions_json[key]:
                        suggestions = suggestions_json[key]
                        if isinstance(suggestions, list) and suggestions:
                            formatted_sections.append(f"**{header}:**")
                            for suggestion in suggestions:
                                if suggestion:
                                    formatted_sections.append(f"- {suggestion}")
                            formatted_sections.append("")
                
                content = "\n".join(formatted_sections).strip()
                
                return {
                    "content": content,
                    "usage": result.get("usage", {})
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse improvement suggestions JSON: {e}")
                logger.error(f"Raw response: {result['content'][:500]}")
                
                # Try to extract JSON from markdown code blocks if present
                json_content = self._extract_json_from_response(result["content"])
                
                # Try parsing again after cleanup
                try:
                    suggestions_json = json.loads(json_content)
                    
                    # Continue with processing the successfully parsed JSON
                    formatted_sections = []
                    section_headers = {
                        "skills_enhancement": "SKILLS ENHANCEMENT",
                        "experience_optimization": "EXPERIENCE OPTIMIZATION",
                        "content_improvements": "CONTENT IMPROVEMENTS",
                        "formatting_presentation": "FORMATTING & PRESENTATION",
                        "keyword_optimization": "KEYWORD OPTIMIZATION",
                        "cultural_fit": "CULTURAL FIT"
                    }
                    
                    for key, header in section_headers.items():
                        if key in suggestions_json and suggestions_json[key]:
                            suggestions = suggestions_json[key]
                            if isinstance(suggestions, list) and suggestions:
                                formatted_sections.append(f"**{header}:**")
                                for suggestion in suggestions:
                                    if suggestion:
                                        formatted_sections.append(f"- {suggestion}")
                                formatted_sections.append("")
                    
                    content = "\n".join(formatted_sections).strip()
                    
                    return {
                        "content": content,
                        "usage": result.get("usage", {})
                    }
                except json.JSONDecodeError:
                    return {
                        "content": f"ERROR: Failed to parse suggestions. Raw response: {result['content'][:200]}",
                        "usage": result.get("usage", {})
                    }
        else:
            return {
                "content": f"ERROR GENERATING SUGGESTIONS:\n\n{result['error']}",
                "usage": {}
            } 