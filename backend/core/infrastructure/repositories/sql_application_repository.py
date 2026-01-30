"""
SQL Application Repository - Database access layer using SQLAlchemy

Replaces JSON file storage with SQLite database.
"""

import logging
import os
import shutil
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.core.infrastructure.repositories.db import Application, Document, Settings, init_database, get_default_settings
from backend.core.infrastructure.frameworks.response_types import StandardResponse
from backend.core.utils.constants import ErrorMessages

logger = logging.getLogger(__name__)


class SQLApplicationRepository:
    """Database access layer for job applications using SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQL repository.
        
        Args:
            db_path: Path to SQLite database file. Defaults to data/applications.db
        """
        self.engine, self.SessionLocal = init_database(db_path)
        self._initialize_default_settings()
        logger.info(f"SQLApplicationRepository initialized with database")
    
    def _initialize_default_settings(self):
        """Initialize default settings if not exists, and update status_options to match current defaults."""
        session = self.SessionLocal()
        try:
            default_settings = get_default_settings()
            for key, value in default_settings.items():
                existing = session.query(Settings).filter_by(key=key).first()
                if not existing:
                    session.add(Settings(key=key, value=value))
                elif key == 'status_options':
                    # Always update status_options to match current defaults (remove invalid options)
                    existing.value = value
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error initializing settings: {e}")
        finally:
            session.close()
    
    # ========== APPLICATION CRUD ==========
    
    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Get all applications as list of dictionaries."""
        session = self.SessionLocal()
        try:
            applications = session.query(Application).all()
            return [app.to_dict() for app in applications]
        except Exception as e:
            logger.error(f"Error loading applications: {e}")
            return []
        finally:
            session.close()
    
    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get single application by ID."""
        session = self.SessionLocal()
        try:
            app = session.query(Application).filter_by(id=app_id).first()
            return app.to_dict() if app else None
        except Exception as e:
            logger.error(f"Error loading application {app_id}: {e}")
            return None
        finally:
            session.close()
    
    def create_application(self, app_data: Dict[str, Any]) -> StandardResponse:
        """
        Create new application.
        
        Args:
            app_data: Application data dictionary
            
        Returns:
            StandardResponse with created application data
        """
        session = self.SessionLocal()
        try:
            job_url = app_data.get('job_url', '')
            app_id = app_data.get('id') or create_job_url_hash(job_url)
            
            existing = session.query(Application).filter_by(id=app_id).first()
            if existing:
                return StandardResponse.error_response(
                    error=f"Application for this job URL already exists (Company: {existing.company}, Position: {existing.position}). Use the Application Tracker to modify it.",
                    operation="create_application"
                )
            
            app = Application(
                id=app_id,
                job_url=app_data.get('job_url', ''),
                company=app_data.get('company', ''),
                position=app_data.get('position', ''),
                location=app_data.get('location'),
                salary_min=app_data.get('salary_min'),
                salary_max=app_data.get('salary_max'),
                date_applied=app_data.get('date_applied'),
                application_source=app_data.get('application_source', 'Other'),
                priority=app_data.get('priority', 'Medium'),
                status=app_data.get('status', 'Applied'),
                description=app_data.get('description'),
                notes=app_data.get('notes'),
                match_score=app_data.get('match_score'),
                hr_contact=app_data.get('hr_contact'),
                hiring_manager=app_data.get('hiring_manager'),
                recruiter=app_data.get('recruiter'),
                referral=app_data.get('referral'),
                requirements=app_data.get('requirements', []),
                analysis_data=app_data.get('analysis_data', {}),
                interview_pipeline=app_data.get('interview_pipeline', {}),
                timeline=app_data.get('timeline', []),
                next_actions=app_data.get('next_actions', []),
                tags=app_data.get('tags', [])
            )
            
            session.add(app)
            session.commit()
            session.refresh(app)
            
            logger.info(f"Created application: {app_id}")
            return StandardResponse.success_response(
                data=app.to_dict(),
                operation="create_application"
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating application: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="create_application"
            )
        finally:
            session.close()
    
    def update_application(self, app_id: str, updates: Dict[str, Any]) -> StandardResponse:
        """
        Update existing application.
        
        Args:
            app_id: Application ID
            updates: Dictionary of fields to update
            
        Returns:
            StandardResponse with updated application data
        """
        session = self.SessionLocal()
        try:
            app = session.query(Application).filter_by(id=app_id).first()
            if not app:
                return StandardResponse.error_response(
                    error=f"Application {app_id} not found",
                    operation="update_application"
                )
            
            for key, value in updates.items():
                if key not in ['id', 'created_date'] and hasattr(app, key):
                    setattr(app, key, value)
            
            app.last_updated = datetime.now()
            session.commit()
            session.refresh(app)
            
            logger.info(f"Updated application: {app_id}")
            return StandardResponse.success_response(
                data=app.to_dict(),
                operation="update_application"
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating application {app_id}: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="update_application"
            )
        finally:
            session.close()
    
    def delete_application(self, app_id: str) -> StandardResponse:
        """Delete application, its documents from DB, and physical files from disk."""
        session = self.SessionLocal()
        try:
            app = session.query(Application).filter_by(id=app_id).first()
            if not app:
                return StandardResponse.error_response(
                    error=f"Application {app_id} not found",
                    operation="delete_application"
                )
            
            # Delete physical files from disk
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            docs_dir = os.path.join(base_dir, "data", "documents", app_id)
            
            if os.path.exists(docs_dir):
                try:
                    shutil.rmtree(docs_dir)
                    logger.info(f"Deleted documents folder: {docs_dir}")
                except Exception as e:
                    logger.warning(f"Could not delete documents folder {docs_dir}: {e}")
            
            # Delete from database (CASCADE will handle documents table)
            session.delete(app)
            session.commit()
            
            logger.info(f"Deleted application: {app_id}")
            return StandardResponse.success_response(
                data={"deleted_id": app_id},
                operation="delete_application"
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting application {app_id}: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="delete_application"
            )
        finally:
            session.close()
    
    # ========== DOCUMENT OPERATIONS ==========
    
    def add_document(self, app_id: str, doc_data: Dict[str, Any]) -> StandardResponse:
        """Add document to application."""
        session = self.SessionLocal()
        try:
            app = session.query(Application).filter_by(id=app_id).first()
            if not app:
                return StandardResponse.error_response(
                    error=f"Application {app_id} not found",
                    operation="add_document"
                )
            
            doc = Document(
                application_id=app_id,
                name=doc_data.get('name', ''),
                type=doc_data.get('type', ''),
                path=doc_data.get('path', ''),
                size=doc_data.get('size', 0)
            )
            
            session.add(doc)
            session.commit()
            session.refresh(doc)
            
            logger.info(f"Added document to application {app_id}")
            return StandardResponse.success_response(
                data=doc.to_dict(),
                operation="add_document"
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding document: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="add_document"
            )
        finally:
            session.close()
    
    def delete_document(self, doc_id: int) -> StandardResponse:
        """Delete document by ID."""
        session = self.SessionLocal()
        try:
            doc = session.query(Document).filter_by(id=doc_id).first()
            if not doc:
                return StandardResponse.error_response(
                    error=f"Document {doc_id} not found",
                    operation="delete_document"
                )
            
            session.delete(doc)
            session.commit()
            
            logger.info(f"Deleted document: {doc_id}")
            return StandardResponse.success_response(
                data={"deleted_id": doc_id},
                operation="delete_document"
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting document: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="delete_document"
            )
        finally:
            session.close()
    
    # ========== SETTINGS OPERATIONS ==========
    
    def load_settings(self) -> Dict[str, Any]:
        """Load all settings as dictionary."""
        session = self.SessionLocal()
        try:
            settings = session.query(Settings).all()
            result = {s.key: s.value for s in settings}
            
            default_settings = get_default_settings()
            if 'status_options' in result:
                valid_statuses = set(default_settings.get('status_options', []))
                current_statuses = result.get('status_options', [])
                filtered_statuses = [s for s in current_statuses if s in valid_statuses]
                if len(filtered_statuses) != len(current_statuses):
                    result['status_options'] = default_settings['status_options']
                    setting = session.query(Settings).filter_by(key='status_options').first()
                    if setting:
                        setting.value = default_settings['status_options']
                        session.commit()
                else:
                    result['status_options'] = default_settings['status_options']
            else:
                result['status_options'] = default_settings['status_options']
            
            return result
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return get_default_settings()
        finally:
            session.close()
    
    def save_settings(self, settings: Dict[str, Any]) -> StandardResponse:
        """Save settings to database."""
        session = self.SessionLocal()
        try:
            for key, value in settings.items():
                setting = session.query(Settings).filter_by(key=key).first()
                if setting:
                    setting.value = value
                    setting.updated_at = datetime.now()
                else:
                    session.add(Settings(key=key, value=value))
            
            session.commit()
            
            logger.info("Settings saved successfully")
            return StandardResponse.success_response(
                data={"settings_count": len(settings)},
                operation="save_settings"
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving settings: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="save_settings"
            )
        finally:
            session.close()
    
    # ========== STATISTICS ==========
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get application statistics."""
        session = self.SessionLocal()
        try:
            total = session.query(Application).count()
            
            stats = {
                'total_applications': total,
                'by_status': {},
                'by_priority': {},
                'by_source': {}
            }
            
            from sqlalchemy import func
            status_counts = session.query(
                Application.status, func.count(Application.id)
            ).group_by(Application.status).all()
            stats['by_status'] = {status: count for status, count in status_counts}
            
            priority_counts = session.query(
                Application.priority, func.count(Application.id)
            ).group_by(Application.priority).all()
            stats['by_priority'] = {priority: count for priority, count in priority_counts}
            
            source_counts = session.query(
                Application.application_source, func.count(Application.id)
            ).group_by(Application.application_source).all()
            stats['by_source'] = {source: count for source, count in source_counts}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'total_applications': 0, 'by_status': {}, 'by_priority': {}, 'by_source': {}}
        finally:
            session.close()
    
    def load_applications(self) -> Dict[str, Any]:
        """
        Load applications in JSON format.
        
        Returns:
            Dict with 'applications' and 'metadata' keys
        """
        apps = self.get_all_applications()
        return {
            'applications': {app['id']: app for app in apps},
            'metadata': {
                'version': '2.0',
                'storage_type': 'sqlite',
                'total_applications': len(apps),
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def save_applications(self, data: Dict[str, Any]) -> StandardResponse:
        """
        Save applications. Use create_application or update_application instead.
        """
        return StandardResponse.success_response(
            data={"message": "Use create_application or update_application instead"},
            operation="save_applications"
        )


# ========== UTILITY FUNCTIONS ==========

def create_job_url_hash(job_url: str) -> str:
    """Create a unique hash from a job URL for use as application ID."""
    if not job_url or not job_url.strip():
        import uuid
        return str(uuid.uuid4()).replace('-', '')[:16]
    
    hash_object = hashlib.sha256(job_url.encode('utf-8'))
    return hash_object.hexdigest()[:16]


def validate_application_data(app_data: Dict[str, Any]) -> StandardResponse:
    """
    Basic validation for application data - just required fields.
    """
    try:
        required_fields = ['company', 'position', 'job_url']

        for field in required_fields:
            value = app_data.get(field)
            # Handle None, empty string, whitespace-only, or non-string values
            if value is None:
                return StandardResponse.error_response(
                    error=f"Required field '{field}' is missing",
                    validation_field=field
                )
            # Convert to string if needed (handles dicts, lists, etc.)
            str_value = str(value) if not isinstance(value, str) else value
            if not str_value.strip():
                return StandardResponse.error_response(
                    error=f"Required field '{field}' is missing",
                    validation_field=field
                )

        return StandardResponse.success_response(
            data={"validation_status": "Valid"},
            validated_fields=len(app_data)
        )

    except Exception as e:
        logger.error(f"Error in application validation: {e}")
        return StandardResponse.error_response(
            error=f"Validation error: {str(e)}",
            operation="validate_application_data"
        )


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations."""
    import re
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_name = ''.join(char for char in safe_name if ord(char) >= 32)
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
    return safe_name.strip()

 
