"""
Profile Repository - Database operations for resume profiles.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.core.infrastructure.repositories.db import init_database, Profile
from backend.core.infrastructure.frameworks.response_types import StandardResponse

logger = logging.getLogger(__name__)


class ProfileRepository:
    """Repository for managing resume profiles in SQLite database."""
    
    def __init__(self, db_path: str = None):
        """Initialize repository with database connection."""
        self.engine, self.SessionLocal = init_database(db_path)
    
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Get all saved profiles."""
        session = self.SessionLocal()
        try:
            profiles = session.query(Profile).order_by(Profile.updated_at.desc()).all()
            return [p.to_dict() for p in profiles]
        except Exception as e:
            logger.error(f"Error getting profiles: {e}")
            return []
        finally:
            session.close()
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific profile by ID."""
        session = self.SessionLocal()
        try:
            profile = session.query(Profile).filter(Profile.id == profile_id).first()
            return profile.to_dict() if profile else None
        except Exception as e:
            logger.error(f"Error getting profile {profile_id}: {e}")
            return None
        finally:
            session.close()
    
    def get_profile_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a profile by name."""
        session = self.SessionLocal()
        try:
            profile = session.query(Profile).filter(Profile.name == name).first()
            return profile.to_dict() if profile else None
        except Exception as e:
            logger.error(f"Error getting profile by name {name}: {e}")
            return None
        finally:
            session.close()
    
    def save_profile(self, name: str, data: Dict[str, Any], profile_id: str = None) -> StandardResponse:
        """
        Save or update a profile.
        
        If profile_id is provided and exists, updates the profile.
        If a profile with the same name exists, updates that profile.
        Otherwise, creates a new profile.
        """
        session = self.SessionLocal()
        try:
            existing_profile = None
            
            # Check by ID first
            if profile_id:
                existing_profile = session.query(Profile).filter(Profile.id == profile_id).first()
            
            # Check by name if not found by ID
            if not existing_profile:
                existing_profile = session.query(Profile).filter(Profile.name == name).first()
            
            if existing_profile:
                # Update existing profile
                existing_profile.name = name
                existing_profile.data = data
                existing_profile.updated_at = datetime.now()
                session.commit()
                
                logger.info(f"Updated profile: {name} (ID: {existing_profile.id})")
                return StandardResponse.success_response(
                    data=existing_profile.to_dict(),
                    operation="update_profile"
                )
            else:
                # Create new profile
                new_id = profile_id or f"profile_{uuid.uuid4().hex[:12]}"
                new_profile = Profile(
                    id=new_id,
                    name=name,
                    data=data,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(new_profile)
                session.commit()
                
                logger.info(f"Created new profile: {name} (ID: {new_id})")
                return StandardResponse.success_response(
                    data=new_profile.to_dict(),
                    operation="create_profile"
                )
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving profile: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="save_profile"
            )
        finally:
            session.close()
    
    def delete_profile(self, profile_id: str) -> StandardResponse:
        """Delete a profile by ID."""
        session = self.SessionLocal()
        try:
            profile = session.query(Profile).filter(Profile.id == profile_id).first()
            if not profile:
                return StandardResponse.error_response(
                    error=f"Profile not found: {profile_id}",
                    operation="delete_profile"
                )
            
            profile_name = profile.name
            session.delete(profile)
            session.commit()
            
            logger.info(f"Deleted profile: {profile_name} (ID: {profile_id})")
            return StandardResponse.success_response(
                data={"deleted_id": profile_id, "deleted_name": profile_name},
                operation="delete_profile"
            )
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting profile {profile_id}: {e}")
            return StandardResponse.error_response(
                error=str(e),
                operation="delete_profile"
            )
        finally:
            session.close()
