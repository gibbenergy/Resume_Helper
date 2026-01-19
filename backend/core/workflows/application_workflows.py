"""
Application Manager - Business logic for job application tracking

This module provides the ApplicationManager class that handles all CRUD operations
for job applications, including interview tracking and document management.
"""

import logging
from datetime import date
from typing import Dict, Any, List, Optional

from backend.core.infrastructure.repositories.sql_application_repository import (
    SQLApplicationRepository, 
    create_job_url_hash, 
    validate_application_data
)
from backend.core.infrastructure.frameworks.response_types import StandardResponse

logger = logging.getLogger(__name__)

class ApplicationWorkflows:
    """Business logic for job application management workflows."""
    
    def __init__(self, repository: Optional[SQLApplicationRepository] = None):
        """Initialize the application workflows."""
        self.repository = repository if repository else SQLApplicationRepository()
        logger.info("ApplicationWorkflows initialized")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get application settings."""
        return self.repository.load_settings()
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update application settings."""
        result = self.repository.save_settings(settings)
        return result.is_success()
    
    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Get all applications as a list with IDs included."""
        try:
            applications = self.repository.get_all_applications()
            
            applications.sort(
                key=lambda x: x.get("date_applied", "1900-01-01"), 
                reverse=True
            )
            
            return applications
            
        except Exception as e:
            logger.error(f"Error getting all applications: {e}")
            return []
    
    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get a single application by ID."""
        try:
            return self.repository.get_application(app_id)
        except Exception as e:
            logger.error(f"Error getting application {app_id}: {e}")
            return None
    
    def create_application(self, app_data: Dict[str, Any]) -> StandardResponse:
        """
        Create a new job application.
        
        Args:
            app_data: Dictionary containing application information
        
        Returns:
            StandardResponse with success/error status and application ID in data
        """
        try:
            validation_result = validate_application_data(app_data)
            if not validation_result.is_success():
                return StandardResponse.error_response(
                    error=validation_result.get_error_message(),
                    operation="create_application",
                    validation_field=getattr(validation_result, 'validation_field', None)
                )
            
            from infrastructure.frameworks.schema_engine import SchemaEngine
            from models.application import ApplicationSchema
            
            new_app = SchemaEngine.extract_fields(app_data, ApplicationSchema.FIELDS)
            
            if new_app.get("description"):
                new_app["description"] = ApplicationSchema.truncate_description(
                    new_app["description"], 
                    ApplicationSchema.FIELDS["description"]["max_length"]
                )
            
            new_app["timeline"] = ApplicationSchema.create_default_timeline(app_data)
            
            validation_result = validate_application_data(new_app)
            if not validation_result.is_success():
                return validation_result
            
            result = self.repository.create_application(new_app)
            
            if result.is_success():
                logger.info(f"Created new application: {result.get_data().get('id')}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error creating application: {e}")
            return StandardResponse.error_response(
                error=f"Error creating application: {str(e)}",
                operation="create_application",
                error_type=type(e).__name__
            )
    
    def update_application(self, app_id: str, updates: Dict[str, Any]) -> StandardResponse:
        """
        Update an existing application.
        
        Args:
            app_id: Application ID to update
            updates: Dictionary of fields to update
        
        Returns:
            StandardResponse with success/error status
        """
        try:
            current_app = self.repository.get_application(app_id)
            if current_app:
                timeline = current_app.get("timeline", [])
                timeline.append({
                    "date": date.today().isoformat(),
                    "event": f"Updated: {', '.join(updates.keys())}",
                    "notes": ""
                })
                updates["timeline"] = timeline
            
            result = self.repository.update_application(app_id, updates)
            
            if result.is_success():
                logger.info(f"Updated application: {app_id}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error updating application {app_id}: {e}")
            return StandardResponse.error_response(
                error=f"Error updating application: {str(e)}",
                operation="update_application",
                error_type=type(e).__name__
            )
    
    def delete_application(self, app_id: str) -> StandardResponse:
        """
        Delete an application.
        
        Args:
            app_id: Application ID to delete
        
        Returns:
            StandardResponse with success/error status
        """
        try:
            result = self.repository.delete_application(app_id)
            
            if result.is_success():
                logger.info(f"Deleted application: {app_id}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error deleting application {app_id}: {e}")
            return StandardResponse.error_response(
                error=f"Error deleting application: {str(e)}",
                operation="delete_application",
                error_type=type(e).__name__
            )
    
    def update_interview_round(self, app_id: str, round_name: str, round_data: Dict[str, Any]) -> StandardResponse:
        """
        Update a specific interview round.
        
        Note: Status field should only be: Applied, Offered, Accepted, Rejected, Withdrawn
        Interview stages (Phone Screen, Interview, Technical, etc.) are tracked in the 
        interview_pipeline, NOT in the status field. The status remains "Applied" during 
        all interview stages and only changes when manually updated or when an offer/rejection occurs.
        
        Args:
            app_id: Application ID
            round_name: Interview round name
            round_data: Dictionary containing round information
        
        Returns:
            StandardResponse with success/error status
        """
        try:
            app = self.repository.get_application(app_id)
            if not app:
                return StandardResponse.error_response(
                    error="Application not found",
                    operation="update_interview_round",
                    app_id=app_id
                )
            
            interview_pipeline = app.get("interview_pipeline", {})
            interview_pipeline[round_name] = round_data
            
            timeline = app.get("timeline", [])
            status = round_data.get("status", "")
            round_display = round_name.replace("_", " ").title()
            
            if status == "scheduled":
                event = f"{round_display} interview scheduled"
            elif status == "completed":
                event = f"{round_display} interview completed"
            else:
                event = f"{round_display} interview {status}"
            
            timeline.append({
                "date": round_data.get("date", date.today().isoformat()),
                "event": event,
                "notes": round_data.get("notes", "")
            })
            
            # NOTE: We do NOT update the status field here - status should only be:
            # Applied, Offered, Accepted, Rejected, Withdrawn (not interview stage names)
            result = self.repository.update_application(app_id, {
                "interview_pipeline": interview_pipeline,
                "timeline": timeline
            })
            
            if result.is_success():
                logger.info(f"Updated interview round {round_name} for application {app_id}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error updating interview round: {e}")
            return StandardResponse.error_response(
                error=f"Error updating interview round: {str(e)}",
                operation="update_interview_round",
                error_type=type(e).__name__
            )
    
 