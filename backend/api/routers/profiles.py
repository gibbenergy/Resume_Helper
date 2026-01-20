"""
Profile router - API endpoints for resume profile management.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.infrastructure.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profiles", tags=["profiles"])

# Initialize repository
_profile_repo: ProfileRepository = None


def get_profile_repo() -> ProfileRepository:
    """Get or create ProfileRepository instance."""
    global _profile_repo
    if _profile_repo is None:
        _profile_repo = ProfileRepository()
    return _profile_repo


class ProfileSaveRequest(BaseModel):
    """Request model for saving a profile."""
    name: str
    data: Dict[str, Any]
    id: Optional[str] = None


@router.get("")
async def get_all_profiles() -> Dict[str, Any]:
    """Get all saved profiles."""
    try:
        repo = get_profile_repo()
        profiles = repo.get_all_profiles()
        return {
            "success": True,
            "profiles": profiles
        }
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{profile_id}")
async def get_profile(profile_id: str) -> Dict[str, Any]:
    """Get a specific profile by ID."""
    try:
        repo = get_profile_repo()
        profile = repo.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Profile not found: {profile_id}")
        return {
            "success": True,
            "profile": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def save_profile(request: ProfileSaveRequest) -> Dict[str, Any]:
    """Save or update a profile."""
    try:
        repo = get_profile_repo()
        result = repo.save_profile(
            name=request.name,
            data=request.data,
            profile_id=request.id
        )
        
        if result.success:
            return {
                "success": True,
                "profile": result.data,
                "message": "Profile saved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{profile_id}")
async def delete_profile(profile_id: str) -> Dict[str, Any]:
    """Delete a profile by ID."""
    try:
        repo = get_profile_repo()
        result = repo.delete_profile(profile_id)
        
        if result.success:
            return {
                "success": True,
                "message": f"Profile deleted successfully",
                "deleted": result.data
            }
        else:
            raise HTTPException(status_code=404, detail=result.error)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
