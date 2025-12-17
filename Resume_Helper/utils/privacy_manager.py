"""
Privacy Manager - Protect personal information from being sent to LLM providers

This module provides data sanitization and personal information management
to ensure user privacy while maintaining AI functionality.
"""

import copy
import logging
from typing import Dict, Any, Tuple, List, Optional

logger = logging.getLogger(__name__)

class PrivacyManager:
    """Manages privacy protection for resume data sent to LLM providers."""
    
    SENSITIVE_PERSONAL_FIELDS = [
        'name_prefix', 'full_name', 'name', 'email', 'phone', 'current_address', 
        'address', 'location', 'citizenship', 'linkedin_url', 
        'github_url', 'portfolio_url'
    ]
    

    
    @classmethod
    def sanitize_resume_data(cls, resume_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Sanitize resume data by completely removing personal information for LLM processing.
        
        This follows the user's privacy-first approach:
        1. Remove ALL personal info before sending to LLM
        2. LLM processes only professional content 
        3. Personal info gets added back during document generation
        
        Args:
            resume_data: Complete resume data dictionary
            
        Returns:
            Tuple of (sanitized_data, personal_info)
            - sanitized_data: Professional content only - SAFE for LLM providers
            - personal_info: Complete personal data for document generation
        """
        if not isinstance(resume_data, dict):
            logger.warning("Invalid resume data format for sanitization")
            return {}, {}
        
        sanitized_data = copy.deepcopy(resume_data)
        personal_info = {}
        
        if 'personal_info' in sanitized_data:
            personal_section = sanitized_data.pop('personal_info', {})
            personal_info['personal_info'] = personal_section
            
            safe_professional = {}
            if 'summary' in personal_section:
                safe_professional['summary'] = personal_section['summary']
            if 'objective' in personal_section:
                safe_professional['objective'] = personal_section['objective']
            
            if safe_professional:
                sanitized_data['professional_summary'] = safe_professional
        
        for field in cls.SENSITIVE_PERSONAL_FIELDS:
            if field in sanitized_data:
                personal_info[field] = sanitized_data.pop(field, None)
        
        cls._sanitize_work_experience(sanitized_data, personal_info)
        
        removed_fields = list(personal_info.keys())
        if removed_fields:
            logger.info(f"🛡️ PRIVACY PROTECTION: Removed {len(removed_fields)} personal fields - LLM will receive ONLY professional content")
            logger.debug(f"🛡️ Removed personal fields: {removed_fields}")
        else:
            logger.info("🛡️ PRIVACY PROTECTION: No personal fields found to remove")
        
        is_safe, violations = cls.validate_sanitized_data(sanitized_data)
        if not is_safe:
            logger.error(f"🚨 PRIVACY BREACH DETECTED! Personal data still present: {violations}")
            for violation in violations:
                if '.' in violation:
                    section, field = violation.split('.', 1)
                    if section in sanitized_data and isinstance(sanitized_data[section], dict):
                        sanitized_data[section].pop(field, None)
                else:
                    sanitized_data.pop(violation, None)
            logger.info("🛡️ Emergency cleanup completed - personal data removed")
        
        return sanitized_data, personal_info
    
    @classmethod
    def _sanitize_work_experience(cls, sanitized_data: Dict[str, Any], personal_info: Dict[str, Any]) -> None:
        """Sanitize work experience to remove personally identifiable information."""
        experience_fields = ['experience', 'work_experience', 'experiences']
        
        for field in experience_fields:
            if field in sanitized_data and isinstance(sanitized_data[field], list):
                for i, exp in enumerate(sanitized_data[field]):
                    if isinstance(exp, dict):
                        if 'manager' in exp:
                            personal_info.setdefault('work_contacts', []).append({
                                'company': exp.get('company', ''),
                                'manager': exp.pop('manager', '')
                            })
    
    @classmethod
    def merge_personal_info_for_documents(cls, professional_content: Dict[str, Any], personal_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge personal information back with professional content for document generation.
        
        This is the final step in the privacy-first workflow:
        1. LLM processed only professional content (no personal info)
        2. Now we merge personal info back for PDF/document generation
        
        Args:
            professional_content: LLM-processed professional content (sanitized)
            personal_info: Personal information extracted earlier
            
        Returns:
            Complete resume data ready for document generation
        """
        complete_resume = copy.deepcopy(professional_content)
        
        if 'personal_info' in personal_info:
            complete_resume['personal_info'] = personal_info['personal_info']
        
        for field in cls.SENSITIVE_PERSONAL_FIELDS:
            if field in personal_info:
                complete_resume[field] = personal_info[field]
        
        if 'work_contacts' in personal_info:
            logger.debug(f"🔐 Work contacts available for restoration: {len(personal_info['work_contacts'])}")
        
        logger.info(f"🔐 DOCUMENT GENERATION: Merged personal info back with professional content")
        logger.debug(f"🔐 Personal fields restored: {[k for k in personal_info.keys() if k != 'work_contacts']}")
        
        return complete_resume
    

    

    
    @classmethod
    def validate_sanitized_data(cls, sanitized_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that sanitized data doesn't contain personal information.
        
        Args:
            sanitized_data: Data that should be safe for LLM processing
            
        Returns:
            Tuple of (is_safe, violations_found)
        """
        violations = []
        
        if 'personal_info' in sanitized_data:
            personal_section = sanitized_data['personal_info']
            for field in cls.SENSITIVE_PERSONAL_FIELDS:
                if field in personal_section:
                    violations.append(f"personal_info.{field}")
        
        for field in cls.SENSITIVE_PERSONAL_FIELDS:
            if field in sanitized_data:
                violations.append(field)
        
        is_safe = len(violations) == 0
        
        if not is_safe:
            logger.error(f"🚨 Privacy violation detected! Sensitive fields found in sanitized data: {violations}")
        else:
            logger.info("✅ Privacy validation passed - no sensitive data detected")
        
        return is_safe, violations


class PrivacyAwareWorkflowMixin:
    """Mixin class to add privacy-aware methods to workflow classes."""
    
    def _prepare_safe_resume_data(self, resume_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Prepare resume data for safe LLM processing.
        
        Returns:
            Tuple of (sanitized_data, personal_info)
        """
        sanitized_data, personal_info = PrivacyManager.sanitize_resume_data(resume_data)
        
        is_safe, violations = PrivacyManager.validate_sanitized_data(sanitized_data)
        if not is_safe:
            logger.error(f"🚨 PRIVACY BREACH PREVENTED! Violations: {violations}")
            for violation in violations:
                if '.' in violation:
                    section, field = violation.split('.', 1)
                    if section in sanitized_data and isinstance(sanitized_data[section], dict):
                        sanitized_data[section].pop(field, None)
                else:
                    sanitized_data.pop(violation, None)
        
        return sanitized_data, personal_info 