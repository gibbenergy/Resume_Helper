"""
Logging Helpers Module - Standardized logging utilities

This module provides the StandardLogger class and logging decorators
to ensure consistent logging patterns across the application.
"""

import logging
import time
import uuid
import functools
from typing import Any, Dict, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class StandardLogger:
    """
    Standardized logging utilities for consistent logging patterns.
    
    This class replaces print() statements and inconsistent logging
    with a unified approach that includes request IDs and structured information.
    """
    
    @staticmethod
    def log_operation_start(operation: str, request_id: str, **params):
        """
        Log the start of an operation with parameters.
        
        Args:
            operation: Name of the operation being started
            request_id: Unique identifier for this operation
            **params: Additional parameters to log (sensitive data will be filtered)
        """
        safe_params = {k: v for k, v in params.items() 
                      if k not in ['api_key', 'password', 'token', 'secret'] 
                      and len(str(v)) < 200}
        
        param_str = ', '.join(f"{k}={v}" for k, v in safe_params.items()) if safe_params else ""
        log_message = f"[{request_id}] {operation} started"
        
        if param_str:
            log_message += f" with {param_str}"
        
        logger.info(log_message)
    
    @staticmethod
    def log_operation_success(operation: str, request_id: str, duration: Optional[float] = None, **metadata):
        """
        Log successful completion of an operation.
        
        Args:
            operation: Name of the operation that completed
            request_id: Unique identifier for this operation
            duration: Time taken in seconds (optional)
            **metadata: Additional metadata about the successful operation
        """
        log_message = f"[{request_id}] {operation} completed"
        
        if duration is not None:
            log_message += f" in {duration:.2f}s"
        
        if metadata:
            metadata_str = ', '.join(f"{k}={v}" for k, v in metadata.items())
            log_message += f" - {metadata_str}"
        
        logger.info(log_message)
    
    @staticmethod
    def log_operation_error(operation: str, request_id: str, error: Exception, **context):
        """
        Log operation failure with error details.
        
        Args:
            operation: Name of the operation that failed
            request_id: Unique identifier for this operation
            error: The exception that occurred
            **context: Additional context information
        """
        log_message = f"[{request_id}] {operation} failed: {error}"
        
        if context:
            context_str = ', '.join(f"{k}={v}" for k, v in context.items())
            log_message += f" - Context: {context_str}"
        
        logger.error(log_message, exc_info=True)
    
    @staticmethod
    def log_operation_warning(operation: str, request_id: str, message: str, **context):
        """
        Log operation warning.
        
        Args:
            operation: Name of the operation
            request_id: Unique identifier for this operation
            message: Warning message
            **context: Additional context information
        """
        log_message = f"[{request_id}] {operation} warning: {message}"
        
        if context:
            context_str = ', '.join(f"{k}={v}" for k, v in context.items())
            log_message += f" - Context: {context_str}"
        
        logger.warning(log_message)
    
    @staticmethod
    def log_data_operation(operation: str, request_id: str, data_type: str, count: int, **details):
        """
        Log data processing operations with count information.
        
        Args:
            operation: Name of the data operation
            request_id: Unique identifier for this operation
            data_type: Type of data being processed (e.g., 'applications', 'resume_entries')
            count: Number of items processed
            **details: Additional operation details
        """
        log_message = f"[{request_id}] {operation}: processed {count} {data_type}"
        
        if details:
            details_str = ', '.join(f"{k}={v}" for k, v in details.items())
            log_message += f" - {details_str}"
        
        logger.info(log_message)
    
    @staticmethod
    def log_file_operation(operation: str, request_id: str, file_path: str, file_size: Optional[int] = None, **details):
        """
        Log file operations with file information.
        
        Args:
            operation: Name of the file operation
            request_id: Unique identifier for this operation
            file_path: Path to the file being operated on
            file_size: Size of the file in bytes (optional)
            **details: Additional operation details
        """
        log_message = f"[{request_id}] {operation}: {file_path}"
        
        if file_size is not None:
            log_message += f" ({file_size} bytes)"
        
        if details:
            details_str = ', '.join(f"{k}={v}" for k, v in details.items())
            log_message += f" - {details_str}"
        
        logger.info(log_message)
    
    @staticmethod
    def log_ai_operation(operation: str, request_id: str, model: str, tokens_used: Optional[int] = None, **details):
        """
        Log AI operations with model and token information.
        
        Args:
            operation: Name of the AI operation
            request_id: Unique identifier for this operation
            model: AI model being used
            tokens_used: Number of tokens consumed (optional)
            **details: Additional operation details
        """
        log_message = f"[{request_id}] {operation}: using {model}"
        
        if tokens_used is not None:
            log_message += f" ({tokens_used} tokens)"
        
        if details:
            details_str = ', '.join(f"{k}={v}" for k, v in details.items())
            log_message += f" - {details_str}"
        
        logger.info(log_message)


def log_operation(operation_name: str, log_params: bool = True, log_duration: bool = True):
    """
    Decorator for automatic operation logging with timing.
    
    Args:
        operation_name: Name of the operation for logging
        log_params: Whether to log function parameters
        log_duration: Whether to log operation duration
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = time.time()
            
            if log_params:
                safe_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ['api_key', 'password', 'token', 'secret'] 
                              and len(str(v)) < 100}
                StandardLogger.log_operation_start(operation_name, request_id, **safe_kwargs)
            else:
                StandardLogger.log_operation_start(operation_name, request_id)
            
            try:
                result = func(*args, **kwargs)
                
                if log_duration:
                    duration = time.time() - start_time
                    StandardLogger.log_operation_success(operation_name, request_id, duration)
                else:
                    StandardLogger.log_operation_success(operation_name, request_id)
                
                return result
                
            except Exception as e:
                StandardLogger.log_operation_error(operation_name, request_id, e)
                raise
        
        return wrapper
    return decorator


def log_file_operation(operation_name: str):
    """
    Specialized decorator for file operations with file-specific logging.
    
    Args:
        operation_name: Name of the file operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            
            file_path = None
            if args and isinstance(args[0], str):
                file_path = args[0]
            elif 'file_path' in kwargs:
                file_path = kwargs['file_path']
            elif 'path' in kwargs:
                file_path = kwargs['path']
            
            if file_path:
                StandardLogger.log_file_operation(operation_name, request_id, file_path)
            else:
                StandardLogger.log_operation_start(operation_name, request_id)
            
            try:
                result = func(*args, **kwargs)
                StandardLogger.log_operation_success(operation_name, request_id)
                return result
                
            except Exception as e:
                StandardLogger.log_operation_error(operation_name, request_id, e, file_path=file_path)
                raise
        
        return wrapper
    return decorator


def log_ai_operation(operation_name: str):
    """
    Specialized decorator for AI operations with model-specific logging.
    
    Args:
        operation_name: Name of the AI operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            
            model = kwargs.get('model', 'default')
            
            StandardLogger.log_ai_operation(operation_name, request_id, model)
            
            try:
                result = func(*args, **kwargs)
                
                tokens_used = None
                if isinstance(result, dict):
                    usage = result.get('usage', {})
                    if isinstance(usage, dict):
                        tokens_used = usage.get('total_tokens')
                
                if tokens_used:
                    StandardLogger.log_operation_success(operation_name, request_id, tokens_used=tokens_used)
                else:
                    StandardLogger.log_operation_success(operation_name, request_id)
                
                return result
                
            except Exception as e:
                StandardLogger.log_operation_error(operation_name, request_id, e, model=model)
                raise
        
        return wrapper
    return decorator


class OperationTimer:
    """Context manager for timing operations with automatic logging."""
    
    def __init__(self, operation_name: str, request_id: Optional[str] = None, **context):
        self.operation_name = operation_name
        self.request_id = request_id or str(uuid.uuid4())
        self.context = context
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        StandardLogger.log_operation_start(self.operation_name, self.request_id, **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            StandardLogger.log_operation_success(self.operation_name, self.request_id, duration)
        else:
            StandardLogger.log_operation_error(self.operation_name, self.request_id, exc_val)
    
    def get_duration(self) -> float:
        """Get the duration of the operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


def log_debug(message: str, request_id: Optional[str] = None, **context):
    """Log a debug message with optional context."""
    req_id = request_id or str(uuid.uuid4())
    context_str = ', '.join(f"{k}={v}" for k, v in context.items()) if context else ""
    log_message = f"[{req_id}] DEBUG: {message}"
    if context_str:
        log_message += f" - {context_str}"
    logger.debug(log_message)


def log_info(message: str, request_id: Optional[str] = None, **context):
    """Log an info message with optional context."""
    req_id = request_id or str(uuid.uuid4())
    context_str = ', '.join(f"{k}={v}" for k, v in context.items()) if context else ""
    log_message = f"[{req_id}] INFO: {message}"
    if context_str:
        log_message += f" - {context_str}"
    logger.info(log_message)


def log_warning(message: str, request_id: Optional[str] = None, **context):
    """Log a warning message with optional context."""
    req_id = request_id or str(uuid.uuid4())
    context_str = ', '.join(f"{k}={v}" for k, v in context.items()) if context else ""
    log_message = f"[{req_id}] WARNING: {message}"
    if context_str:
        log_message += f" - {context_str}"
    logger.warning(log_message)


def log_error(message: str, request_id: Optional[str] = None, **context):
    """Log an error message with optional context."""
    req_id = request_id or str(uuid.uuid4())
    context_str = ', '.join(f"{k}={v}" for k, v in context.items()) if context else ""
    log_message = f"[{req_id}] ERROR: {message}"
    if context_str:
        log_message += f" - {context_str}"
    logger.error(log_message)


def replace_print(message: str, level: str = "info", **context):
    """
    Replacement for print() statements throughout the codebase.
    
    Args:
        message: The message to log
        level: Log level ('debug', 'info', 'warning', 'error')
        **context: Additional context information
    """
    request_id = str(uuid.uuid4())
    
    if level.lower() == "debug":
        log_debug(message, request_id, **context)
    elif level.lower() == "warning":
        log_warning(message, request_id, **context)
    elif level.lower() == "error":
        log_error(message, request_id, **context)
    else:
        log_info(message, request_id, **context)  
