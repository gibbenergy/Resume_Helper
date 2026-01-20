"""
Unified table data extraction and manipulation utilities.
Replaces duplicated table handling logic across all tabs.
"""

import logging
from typing import Any, List, Optional, Union

logger = logging.getLogger(__name__)


class TableDataExtractor:
    """Unified class for handling table data extraction and manipulation."""
    
    @staticmethod
    def extract_table_data(table: Any) -> List[List[Any]]:
        """
        Extract data from various table formats (DataFrame, list).
        
        Args:
            table: Table data in various formats
            
        Returns:
            List of lists representing table rows
        """
        try:
            if table is None:
                return []
            
            # If it's a pandas DataFrame
            if hasattr(table, 'values') and hasattr(table, 'to_dict'):
                return table.values.tolist()
            
            # If it's a dict with 'data' key
            if isinstance(table, dict) and 'data' in table:
                return table['data']
            
            # If it's already a list
            if isinstance(table, list):
                return table
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting table data: {str(e)}")
            return []
    
    @staticmethod
    def add_row_to_table(new_row: List[Any], existing_table: Any = None) -> List[List[Any]]:
        """
        Add a new row to an existing table.
        
        Args:
            new_row: List of values for the new row
            existing_table: Existing table data in various formats
            
        Returns:
            Updated table data as list of lists
        """
        try:
            if existing_table is None or not existing_table:
                return [new_row]
            
            existing_data = TableDataExtractor.extract_table_data(existing_table)
            result = list(existing_data)
            result.append(new_row)
            return result
            
        except Exception as e:
            logger.error(f"Error adding row to table: {str(e)}")
            return TableDataExtractor.extract_table_data(existing_table) if existing_table is not None else []
    
    @staticmethod
    def remove_rows_from_table(table_data: List[List[Any]], selected_rows: List[int]) -> List[List[Any]]:
        """
        Remove selected rows from table data.
        
        Args:
            table_data: Table data as list of lists
            selected_rows: List of row indices to remove
            
        Returns:
            Updated table data with selected rows removed
        """
        try:
            if not table_data or not selected_rows:
                return table_data
            return [row for i, row in enumerate(table_data) if i not in selected_rows]
        except Exception as e:
            logger.error(f"Error removing rows from table: {str(e)}")
            return table_data
    
    @staticmethod
    def clear_table() -> List[List[Any]]:
        """
        Clear all table data.
        
        Returns:
            Empty list
        """
        return []
    
    @staticmethod
    def create_empty_row(field_count: int) -> List[str]:
        """
        Create an empty row with the specified number of fields.
        
        Args:
            field_count: Number of empty fields to create
            
        Returns:
            List of empty strings
        """
        try:
            return [""] * field_count
        except Exception as e:
            logger.error(f"Error creating empty row: {str(e)}")
            return [""] * field_count