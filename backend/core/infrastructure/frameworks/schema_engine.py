"""
Schema Engine - Universal data processing framework

This module provides a unified schema-driven approach for data extraction,
validation, and transformation across the entire application.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import date

from backend.core.infrastructure.frameworks.response_types import StandardResponse
from backend.core.utils.logging_helpers import StandardLogger

logger = logging.getLogger(__name__)


class SchemaEngine:
    """Universal schema processing engine used by all data schemas."""
    
    @staticmethod
    def extract_fields(data: dict, schema: dict) -> dict:
        """
        Extract fields from data using schema definition.
        
        Args:
            data: Source data dictionary
            schema: Schema definition with field configurations
            
        Returns:
            Dictionary with extracted and processed fields
        """
        result = {}
        
        for field_name, field_config in schema.items():
            try:
                value = None
                aliases = field_config.get('aliases', [])
                
                if field_name in data:
                    value = data[field_name]
                else:
                    for alias in aliases:
                        if alias in data:
                            value = data[alias]
                            break
                
                if value is None:
                    default = field_config.get('default')
                    if callable(default):
                        value = default()
                    else:
                        value = default
                
                if value is not None and 'type' in field_config:
                    expected_type = field_config['type']
                    if not isinstance(value, expected_type):
                        try:
                            if expected_type == int and isinstance(value, str):
                                value = int(value) if value.strip() else None
                            elif expected_type == str:
                                value = str(value)
                            elif expected_type == list and not isinstance(value, list):
                                value = [value] if value else []
                            elif expected_type == dict and not isinstance(value, dict):
                                value = {}
                            else:
                                value = expected_type(value)
                        except (ValueError, TypeError):
                            default = field_config.get('default')
                            value = default() if callable(default) else default
                
                result[field_name] = value
                
            except Exception as e:
                logger.warning(f"Error extracting field '{field_name}': {e}")
                default = field_config.get('default')
                result[field_name] = default() if callable(default) else default
        
        return result
    
    @staticmethod
    def extract_list_fields(data_list: List[dict], schema: dict) -> List[dict]:
        """
        Extract fields from a list of data dictionaries using schema.
        
        Args:
            data_list: List of source data dictionaries
            schema: Schema definition for each item
            
        Returns:
            List of dictionaries with extracted fields
        """
        result = []
        for item in data_list:
            if item:
                extracted = SchemaEngine.extract_fields(item, schema)
                if any(str(v).strip() for v in extracted.values() if v is not None):
                    result.append(extracted)
        return result
    
    @staticmethod
    def map_form_to_data(form_values: List[Any], field_mapping: List[str], schema: dict) -> dict:
        """
        Map form values to data dictionary using schema.
        
        Args:
            form_values: List of form values
            field_mapping: List of field names in form order
            schema: Schema definition for validation and type conversion
            
        Returns:
            Dictionary with mapped data
        """
        result = {}
        
        for i, field_name in enumerate(field_mapping):
            if i < len(form_values):
                value = form_values[i]
                field_config = schema.get(field_name, {})
                
                if value is not None and 'type' in field_config:
                    expected_type = field_config['type']
                    try:
                        if expected_type == int and value:
                            value = int(value)
                        elif expected_type == str:
                            value = str(value)
                        elif expected_type == list and not isinstance(value, list):
                            value = [value] if value else []
                    except (ValueError, TypeError):
                        default = field_config.get('default')
                        value = default() if callable(default) else default
                
                if value is None or (isinstance(value, str) and not value.strip()):
                    default = field_config.get('default')
                    value = default() if callable(default) else default
                
                result[field_name] = value
        
        return result
    
    @staticmethod
    def convert_to_table_format(data_list: List[dict], schema: dict, field_order: List[str]) -> List[List[str]]:
        """
        Convert list of dictionaries to table format using schema.
        
        Args:
            data_list: List of data dictionaries
            schema: Schema definition
            field_order: Order of fields for table columns
            
        Returns:
            List of lists suitable for table display
        """
        result = []
        
        for item in data_list:
            row = []
            for field_name in field_order:
                value = item.get(field_name, '')
                # Convert to string for table display
                row.append(str(value) if value is not None else '')
            result.append(row)
        
        return result
    
    @staticmethod
    def log_schema_operation(operation: str, schema_name: str, field_count: int, success: bool = True):
        """Log schema operations for debugging and monitoring."""
        status = "✅" if success else "❌"
        logger.info(f"{status} Schema operation: {operation} on {schema_name} ({field_count} fields)")  
