"""
Resume Helper - Backward compatibility alias for ResumeService.

This module provides the ResumeHelper class as an alias for ResumeService
to maintain backward compatibility with existing code.

New code should import from backend.core.services.resume_service directly.
"""

from backend.core.services.resume_service import ResumeService

# Alias for backward compatibility
ResumeHelper = ResumeService

__all__ = ["ResumeHelper", "ResumeService"]
