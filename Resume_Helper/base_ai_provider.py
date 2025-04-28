"""
Base AI Provider - Abstract base class for AI providers.

This module defines the interface that all AI providers must implement.
"""

import abc
import logging
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAIProvider(abc.ABC):
    """
    Abstract base class for AI providers.
    
    All AI providers (OpenAI, Gemini, etc.) should inherit from this class
    and implement its methods.
    """
    
    @abc.abstractmethod
    def set_api_key(self, api_key: str) -> str:
        """
        Set the API key for the provider.
        
        Args:
            api_key: The API key to use.
            
        Returns:
            A message indicating success or failure.
        """
        pass
    
    @abc.abstractmethod
    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description to extract key information.
        
        Args:
            job_description: The job description text.
            
        Returns:
            A dictionary containing the extracted information.
        """
        pass
    
    @abc.abstractmethod
    def identify_relevant_skills(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify skills in the resume that are relevant to the job.
        
        Args:
            resume_data: The resume data.
            job_analysis: The job analysis data.
            
        Returns:
            A dictionary containing the relevant skills.
        """
        pass
    
    @abc.abstractmethod
    def generate_cover_letter(self, resume_data: Dict[str, Any], job_description: str, job_analysis: Dict[str, Any]) -> str:
        """
        Generate a cover letter based on the resume and job description.
        
        Args:
            resume_data: The resume data.
            job_description: The job description text.
            job_analysis: The job analysis data.
            
        Returns:
            The generated cover letter text.
        """
        pass
    
    @abc.abstractmethod
    def validate_and_correct_cover_letter(self, cover_letter: str, resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and correct a cover letter.
        
        Args:
            cover_letter: The cover letter text.
            resume_data: The resume data.
            job_analysis: The job analysis data.
            
        Returns:
            A dictionary containing the corrected cover letter and validation notes.
        """
        pass
    
    @abc.abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the AI provider.
        
        Returns:
            The name of the AI provider.
        """
        pass
    
    @abc.abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models for this provider.
        
        Returns:
            A list of model names.
        """
        pass
    
    @abc.abstractmethod
    def set_model(self, model_name: str) -> str:
        """
        Set the model to use for this provider.
        
        Args:
            model_name: The name of the model to use.
            
        Returns:
            A message indicating success or failure.
        """
        pass
    
    @abc.abstractmethod
    def test_api_key(self, api_key: str, model: str) -> str:
        """
        Test if an API key is valid by making a simple API call.
        
        Args:
            api_key: The API key to test.
            model: The model to use for testing.
            
        Returns:
            A message indicating if the API key is valid.
        """
        pass
    
    @abc.abstractmethod
    def post_process_cover_letter(self, cover_letter: str, request_id: str) -> str:
        """
        Fix common issues in generated cover letters.
        
        Args:
            cover_letter: The generated cover letter text
            request_id: Request ID for logging
            
        Returns:
            Processed cover letter text
        """
        pass
    
    @abc.abstractmethod
    def tailor_resume(self, resume_data: Dict, job_description: str, model: Optional[str] = None) -> Dict:
        """
        Tailor a resume to better match a job description.
        
        Args:
            resume_data: The resume data as a dictionary.
            job_description: The job description to tailor the resume for.
            model: Optional model override for this specific call.
            
        Returns:
            A dictionary containing the tailored resume or an error message.
        """
        pass
    
    @abc.abstractmethod
    def get_improvement_suggestions(self, resume_data: Dict, job_description: str, model: Optional[str] = None) -> str:
        """
        Get suggestions for improving a resume based on a job description.
        
        Args:
            resume_data: The resume data as a dictionary.
            job_description: The job description to compare the resume against.
            model: Optional model override for this specific call.
            
        Returns:
            A string containing improvement suggestions or an error message.
        """
        pass