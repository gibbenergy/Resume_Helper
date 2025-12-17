"""
CRUD Operations - Unified CRUD operations for resume sections

This module provides standardized Create, Read, Update, Delete operations
for all resume sections, eliminating code duplication.
"""

from typing import List, Any, Optional
from infrastructure.adapters.table_data_extractor import TableDataExtractor
from utils.constants import UIConstants


class CRUDOperations:
    """Unified CRUD operations for resume sections."""
    
    @staticmethod
    def reset_section(section_type: str) -> List[str]:
        """
        Reset fields for a specific section.
        
        Args:
            section_type: Type of section ('personal_info', 'education', 'experience', 'skills', 'projects', 'certifications')
            
        Returns:
            List of empty strings for the section's input fields
        """
        field_counts = {
            'personal_info': UIConstants.PERSONAL_INFO_FIELDS,
            'education': UIConstants.EDUCATION_INPUT_FIELDS,
            'experience': UIConstants.WORK_INPUT_FIELDS,
            'skills': UIConstants.SKILLS_INPUT_FIELDS,
            'projects': UIConstants.PROJECTS_INPUT_FIELDS,
            'certifications': UIConstants.CERTIFICATIONS_INPUT_FIELDS
        }
        
        field_count = field_counts.get(section_type, 0)
        return TableDataExtractor.create_empty_row(field_count)
    
    @staticmethod
    def add_to_section(section_type: str, data: List[Any], existing_table: Any = None) -> List[List[Any]]:
        """
        Add data to a section table.
        
        Args:
            section_type: Type of section
            data: List of values to add
            existing_table: Existing table data
            
        Returns:
            Updated table data
        """
        return TableDataExtractor.add_row_to_table(data, existing_table)
    
    @staticmethod
    def remove_from_section(table_data: List[List[Any]], selected_rows: List[int]) -> List[List[Any]]:
        """
        Remove selected rows from a section table.
        
        Args:
            table_data: Current table data
            selected_rows: List of row indices to remove
            
        Returns:
            Updated table data with selected rows removed
        """
        return TableDataExtractor.remove_rows_from_table(table_data, selected_rows)
    
    @staticmethod
    def clear_section() -> List[List[Any]]:
        """
        Clear all data from a section table.
        
        Returns:
            Empty table
        """
        return TableDataExtractor.clear_table()


# Convenience functions for specific sections
class EducationCRUD:
    """CRUD operations specifically for education section."""
    
    @staticmethod
    def reset() -> List[str]:
        return CRUDOperations.reset_section('education')
    
    @staticmethod
    def add(institution: str, degree: str, field: str, start_date: str, end_date: str, 
            gpa: str, description: str, existing_table: Any = None) -> List[List[Any]]:
        data = [institution, degree, field, gpa, start_date, end_date, description]
        return CRUDOperations.add_to_section('education', data, existing_table)
    
    @staticmethod
    def remove(table_data: List[List[Any]], selected_rows: List[int]) -> List[List[Any]]:
        return CRUDOperations.remove_from_section(table_data, selected_rows)
    
    @staticmethod
    def clear() -> List[List[Any]]:
        return CRUDOperations.clear_section()


class ExperienceCRUD:
    """CRUD operations specifically for experience section."""
    
    @staticmethod
    def reset() -> List[str]:
        return CRUDOperations.reset_section('experience')
    
    @staticmethod
    def add(company: str, position: str, location: str, start_date: str, end_date: str,
            description: str, achievements: str, existing_table: Any = None) -> List[List[Any]]:
        data = [company, position, location, start_date, end_date, description, achievements]
        return CRUDOperations.add_to_section('experience', data, existing_table)
    
    @staticmethod
    def remove(table_data: List[List[Any]], selected_rows: List[int]) -> List[List[Any]]:
        return CRUDOperations.remove_from_section(table_data, selected_rows)
    
    @staticmethod
    def clear() -> List[List[Any]]:
        return CRUDOperations.clear_section()


class SkillsCRUD:
    """CRUD operations specifically for skills section."""
    
    @staticmethod
    def reset() -> List[str]:
        return CRUDOperations.reset_section('skills')
    
    @staticmethod
    def add(category: str, skill_name: str, proficiency: str, existing_table: Any = None) -> List[List[Any]]:
        data = [category, skill_name, proficiency]
        return CRUDOperations.add_to_section('skills', data, existing_table)
    
    @staticmethod
    def remove(table_data: List[List[Any]], selected_rows: List[int]) -> List[List[Any]]:
        return CRUDOperations.remove_from_section(table_data, selected_rows)
    
    @staticmethod
    def clear() -> List[List[Any]]:
        return CRUDOperations.clear_section()


class ProjectsCRUD:
    """CRUD operations specifically for projects section."""
    
    @staticmethod
    def reset() -> List[str]:
        return CRUDOperations.reset_section('projects')
    
    @staticmethod
    def add(title: str, description: str, technologies: str, url: str, start_date: str,
            end_date: str, existing_table: Any = None) -> List[List[Any]]:
        data = [title, description, technologies, url, start_date, end_date]
        return CRUDOperations.add_to_section('projects', data, existing_table)
    
    @staticmethod
    def remove(table_data: List[List[Any]], selected_rows: List[int]) -> List[List[Any]]:
        return CRUDOperations.remove_from_section(table_data, selected_rows)
    
    @staticmethod
    def clear() -> List[List[Any]]:
        return CRUDOperations.clear_section()


class CertificationsCRUD:
    """CRUD operations specifically for certifications section."""
    
    @staticmethod
    def reset() -> List[str]:
        return CRUDOperations.reset_section('certifications')
    
    @staticmethod
    def add(name: str, issuer: str, date_obtained: str, credential_id: str, url: str,
            existing_table: Any = None) -> List[List[Any]]:
        data = [name, issuer, date_obtained, credential_id, url]
        return CRUDOperations.add_to_section('certifications', data, existing_table)
    
    @staticmethod
    def remove(table_data: List[List[Any]], selected_rows: List[int]) -> List[List[Any]]:
        return CRUDOperations.remove_from_section(table_data, selected_rows)
    
    @staticmethod
    def clear() -> List[List[Any]]:
        return CRUDOperations.clear_section()


class PersonalInfoCRUD:
    """CRUD operations specifically for personal info section."""
    
    @staticmethod
    def reset() -> List[str]:
        return CRUDOperations.reset_section('personal_info') 