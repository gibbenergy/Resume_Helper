"""
Application tracker router - CRUD operations for job applications.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, File
from fastapi.responses import FileResponse

from backend.api.dependencies import get_resume_helper
from backend.api.models import ApplicationCreateRequest, ApplicationUpdateRequest
from backend.core.services import ResumeService as ResumeHelper
from backend.core.workflows.application_workflows import ApplicationWorkflows

router = APIRouter(prefix="/api/applications", tags=["applications"])


def get_app_workflows(resume_helper: ResumeHelper = Depends(get_resume_helper)) -> ApplicationWorkflows:
    """Get ApplicationWorkflows instance."""
    # ApplicationWorkflows is initialized separately, not from ResumeHelper
    from backend.core.workflows.application_workflows import ApplicationWorkflows
    return ApplicationWorkflows()


@router.get("")
async def get_applications(
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Get all job applications."""
    try:
        applications = workflows.get_all_applications()
        return {"success": True, "data": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting applications: {str(e)}")


@router.get("/settings")
async def get_application_settings(
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Get application settings (interview rounds, statuses, etc.)."""
    try:
        settings = workflows.get_settings()
        return {"success": True, "data": settings}
    except FileNotFoundError:
        # Return default settings if file doesn't exist yet
        default_settings = {
            "interview_rounds": ["Phone Screen", "Technical", "Behavioral", "Final"],
            "statuses": ["Not Started", "Applied", "Interview", "Offer", "Rejected", "Withdrawn"],
            "priorities": ["Low", "Medium", "High"]
        }
        return {"success": True, "data": default_settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")


@router.get("/{app_id}")
async def get_application(
    app_id: str = Path(..., description="Application ID"),
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Get a single application by ID."""
    try:
        application = workflows.get_application(app_id)
        if application is None:
            raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
        return {"success": True, "data": application}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting application: {str(e)}")


@router.post("")
async def create_application(
    request: ApplicationCreateRequest,
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Create a new job application."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        app_data = request.dict(exclude_none=True)
        logger.info(f"Creating application with data: company={app_data.get('company')}, position={app_data.get('position')}, job_url={app_data.get('job_url', '')[:50]}...")
        result = workflows.create_application(app_data)

        if result.is_success():
            return {
                "success": True,
                "data": result.get_data(),
                "message": result.get_data().get("message", "Application created successfully")
            }
        else:
            error_msg = result.get_error_message()
            logger.warning(f"Application creation failed: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception creating application: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")


@router.put("/{app_id}")
async def update_application(
    app_id: str = Path(..., description="Application ID"),
    request: ApplicationUpdateRequest = ...,
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Update an existing application."""
    try:
        updates = request.dict(exclude_none=True)
        result = workflows.update_application(app_id, updates)
        
        if result.is_success():
            return {
                "success": True,
                "data": result.get_data(),
                "message": result.get_data().get("message", "Application updated successfully")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get_error_message()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating application: {str(e)}")


@router.delete("/{app_id}")
async def delete_application(
    app_id: str = Path(..., description="Application ID"),
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Delete an application."""
    try:
        result = workflows.delete_application(app_id)
        
        if result.is_success():
            return {
                "success": True,
                "message": result.get_data().get("message", "Application deleted successfully")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get_error_message()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting application: {str(e)}")


@router.post("/{app_id}/interview-rounds/{round_name}")
async def update_interview_round(
    app_id: str = Path(..., description="Application ID"),
    round_name: str = Path(..., description="Interview round name"),
    round_data: Dict[str, Any] = ...,
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Update a specific interview round."""
    try:
        result = workflows.update_interview_round(app_id, round_name, round_data)
        
        if result.is_success():
            return {
                "success": True,
                "data": result.get_data(),
                "message": result.get_data().get("message", "Interview round updated successfully")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get_error_message()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating interview round: {str(e)}")


@router.post("/{app_id}/documents")
async def upload_document(
    app_id: str = Path(..., description="Application ID"),
    file: UploadFile = File(...),
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Upload a document for an application."""
    try:
        import os
        import re
        import time
        import shutil
        from pathlib import Path
        
        # Verify application exists
        app = workflows.get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
        
        # Get project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        
        # Create documents directory
        docs_dir = os.path.join(project_root, "data", "documents", app_id)
        os.makedirs(docs_dir, exist_ok=True)
        
        # Sanitize filename
        original_filename = file.filename or "document"
        doc_name, file_ext = os.path.splitext(original_filename)
        doc_name = re.sub(r'[^a-zA-Z0-9_\-\s]', '', doc_name).strip()
        if not doc_name:
            doc_name = "Document"
        
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', doc_name)
        new_filename = f"{safe_name}_{int(time.time())}{file_ext}"
        dest_path = os.path.join(docs_dir, new_filename)
        
        # Save file
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(dest_path)
        
        # Determine document type
        doc_type = "other"
        if file_ext.lower() in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            doc_type = "document"
        elif file_ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']:
            doc_type = "image"
        elif file_ext.lower() in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs']:
            doc_type = "code"
        elif file_ext.lower() in ['.zip', '.tar', '.gz', '.rar']:
            doc_type = "archive"
        
        # Create document record
        doc_data = {
            "name": original_filename,
            "type": doc_type,
            "path": dest_path,
            "size": file_size
        }
        
        result = workflows.repository.add_document(app_id, doc_data)
        
        if result.is_success():
            return {
                "success": True,
                "data": result.get_data(),
                "message": f"Document '{original_filename}' uploaded successfully"
            }
        else:
            # Clean up file if database insert failed
            try:
                os.remove(dest_path)
            except:
                pass
            raise HTTPException(
                status_code=400,
                detail=result.get_error_message()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/{app_id}/documents/{doc_id}/download")
async def download_document(
    app_id: str = Path(..., description="Application ID"),
    doc_id: int = Path(..., description="Document ID"),
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> FileResponse:
    """Download a document file."""
    try:
        import os
        import mimetypes
        
        # Verify application exists
        app = workflows.get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
        
        # Find document in application's documents
        documents = app.get("documents", [])
        doc = None
        for d in documents:
            if d.get("id") == doc_id:
                doc = d
                break
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        file_path = doc.get("path", "")
        doc_name = doc.get("name", "document")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document file not found on disk")
        
        # Detect MIME type from file extension
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        return FileResponse(
            file_path,
            media_type=mime_type,
            filename=doc_name,
            headers={"Content-Disposition": f"attachment; filename={doc_name}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")


@router.delete("/{app_id}/documents/{doc_id}")
async def delete_document(
    app_id: str = Path(..., description="Application ID"),
    doc_id: int = Path(..., description="Document ID"),
    workflows: ApplicationWorkflows = Depends(get_app_workflows)
) -> Dict[str, Any]:
    """Delete a document."""
    try:
        import os
        
        # Verify application exists
        app = workflows.get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
        
        # Find document to get file path before deletion
        documents = app.get("documents", [])
        doc = None
        for d in documents:
            if d.get("id") == doc_id:
                doc = d
                break
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        # Delete from database
        result = workflows.repository.delete_document(doc_id)
        
        if result.is_success():
            # Delete file from disk
            file_path = doc.get("path", "")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    import logging
                    logging.warning(f"Could not delete file {file_path}: {e}")
            
            return {
                "success": True,
                "message": f"Document '{doc.get('name', 'Unknown')}' deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get_error_message()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

 
