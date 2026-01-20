"""
Response Types Module - Standardized response formats and error handling

This module provides the StandardResponse class and error handling decorators
to ensure consistent error fallback behavior across all function operations.
"""

import json
import uuid
import logging
from typing import Any, Optional, Dict, List, Union, Tuple
from dataclasses import dataclass, field
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StandardResponse:
    """
    Standardized response format for all operations.
    
    This ensures consistent error fallback behavior across the entire application.
    All functions should return this format instead of tuples, dicts, or exceptions.
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'request_id': self.request_id,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def success_response(cls, data: Any = None, request_id: Optional[str] = None, **metadata) -> 'StandardResponse':
        """Create a successful response."""
        return cls(
            success=True,
            data=data,
            request_id=request_id,
            metadata=metadata
        )
    
    @classmethod
    def error_response(cls, error: str, request_id: Optional[str] = None, **metadata) -> 'StandardResponse':
        """Create an error response."""
        return cls(
            success=False,
            error=error,
            request_id=request_id,
            metadata=metadata
        )
    
    def add_metadata(self, key: str, value: Any) -> 'StandardResponse':
        """Add metadata to the response."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
        return self
    
    def is_success(self) -> bool:
        return self.success
    
    def is_error(self) -> bool:
        return not self.success
    
    def get_error_message(self) -> str:
        """Get the error message, or empty string if successful."""
        return self.error or ""
    
    def get_data(self) -> Any:
        """Get the response data, or None if error."""
        return self.data if self.success else None


class ResponseHandler:
    """Utility class for handling StandardResponse objects."""
    
    @staticmethod
    def handle_response(response: StandardResponse, on_success=None, on_error=None):
        """Handle a StandardResponse with optional callbacks."""
        if response.is_success():
            if on_success:
                return on_success(response.data)
            return response.data
        else:
            if on_error:
                return on_error(response.error, response.request_id)
            logger.error(f"[{response.request_id}] Operation failed: {response.error}")
            return None
    
    @staticmethod
    def extract_data(response: StandardResponse, default=None):
        """Extract data from response, returning default if error."""
        return response.data if response.is_success() else default
    
    @staticmethod
    def log_response(response: StandardResponse, operation_name: str = "operation"):
        """Log a StandardResponse appropriately."""
        if response.is_success():
            logger.info(f"[{response.request_id}] {operation_name} completed successfully")
        else:
            logger.error(f"[{response.request_id}] {operation_name} failed: {response.error}")


# Error handling decorators
def handle_errors(operation_name: str, return_data_on_success: bool = True):
    """
    Decorator for standardized error handling.
    
    Args:
        operation_name: Name of the operation for logging
        return_data_on_success: If True, returns only the data on success; if False, returns full StandardResponse
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, StandardResponse):
                    return result.data if (return_data_on_success and result.is_success()) else result
                
                response = StandardResponse.success_response(data=result, request_id=request_id)
                return response.data if return_data_on_success else response
                
            except Exception as e:
                logger.error(f"[{request_id}] {operation_name} failed: {e}", exc_info=True)
                response = StandardResponse.error_response(error=str(e), request_id=request_id)
                return response if not return_data_on_success else None
        
        return wrapper
    return decorator


def handle_file_operations(operation_name: str):
    """Specialized decorator for file operations with enhanced error handling."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, StandardResponse):
                    return result
                
                return StandardResponse.success_response(
                    data=result,
                    request_id=request_id,
                    operation=operation_name
                )
                
            except FileNotFoundError as e:
                error_msg = f"File not found: {str(e)}"
                logger.error(f"[{request_id}] {operation_name} failed: {error_msg}")
                return StandardResponse.error_response(
                    error=error_msg,
                    request_id=request_id,
                    error_type="FileNotFoundError"
                )
            except PermissionError as e:
                error_msg = f"Permission denied: {str(e)}"
                logger.error(f"[{request_id}] {operation_name} failed: {error_msg}")
                return StandardResponse.error_response(
                    error=error_msg,
                    request_id=request_id,
                    error_type="PermissionError"
                )
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON format: {str(e)}"
                logger.error(f"[{request_id}] {operation_name} failed: {error_msg}")
                return StandardResponse.error_response(
                    error=error_msg,
                    request_id=request_id,
                    error_type="JSONDecodeError"
                )
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"[{request_id}] {operation_name} failed: {error_msg}", exc_info=True)
                return StandardResponse.error_response(
                    error=error_msg,
                    request_id=request_id,
                    error_type=type(e).__name__
                )
        
        return wrapper
    return decorator


def handle_ai_operations(operation_name: str):
    """Specialized decorator for AI operations with timeout and API error handling."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, StandardResponse):
                    return result
                
                if isinstance(result, dict):
                    if result.get("success") is False:
                        return StandardResponse.error_response(
                            error=result.get("error", "Unknown AI operation error"),
                            request_id=request_id,
                            operation=operation_name
                        )
                    else:
                        return StandardResponse.success_response(
                            data=result,
                            request_id=request_id,
                            operation=operation_name
                        )
                
                return StandardResponse.success_response(
                    data=result,
                    request_id=request_id,
                    operation=operation_name
                )
                
            except TimeoutError as e:
                error_msg = f"Operation timed out: {str(e)}"
                logger.error(f"[{request_id}] {operation_name} failed: {error_msg}")
                return StandardResponse.error_response(
                    error=error_msg,
                    request_id=request_id,
                    error_type="TimeoutError"
                )
            except Exception as e:
                error_msg = str(e)
                if "api" in error_msg.lower() or "key" in error_msg.lower():
                    error_type = "APIError"
                elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    error_type = "RateLimitError"
                else:
                    error_type = type(e).__name__
                
                logger.error(f"[{request_id}] {operation_name} failed: {error_msg}", exc_info=True)
                return StandardResponse.error_response(
                    error=error_msg,
                    request_id=request_id,
                    error_type=error_type
                )
        
        return wrapper
    return decorator


# Utility functions for common response patterns
def success(data: Any = None, **metadata) -> StandardResponse:
    """Create a success response quickly."""
    return StandardResponse.success_response(data=data, **metadata)


def error(message: str, **metadata) -> StandardResponse:
    """Create an error response quickly."""
    return StandardResponse.error_response(error=message, **metadata)


def from_exception(e: Exception, operation: str = "operation") -> StandardResponse:
    """Create an error response from an exception."""
    return StandardResponse.error_response(
        error=str(e),
        error_type=type(e).__name__,
        operation=operation
    ) 