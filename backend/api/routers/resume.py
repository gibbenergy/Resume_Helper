"""
Resume CRUD operations router.
"""

import json
import os
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse

from backend.api.dependencies import get_resume_helper
from backend.api.models import BuildProfileRequest, ResumeData
from backend.core.services import ResumeService as ResumeHelper

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/build-profile")
async def build_profile(
    request: BuildProfileRequest,
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Build resume profile dictionary from form data."""
    try:
        profile = resume_helper.build_profile_dict(
            name_prefix=request.name_prefix or "",
            email=request.email or "",
            full_name=request.full_name or "",
            phone=request.phone or "",
            current_address=request.current_address or "",
            location=request.location or "",
            citizenship=request.citizenship or "",
            linkedin_url=request.linkedin_url or "",
            github_url=request.github_url or "",
            portfolio_url=request.portfolio_url or "",
            summary=request.summary or "",
            education_table=request.education_table or [],
            experience_table=request.experience_table or [],
            skills_table=request.skills_table or [],
            projects_table=request.projects_table or [],
            certifications_table=request.certifications_table or [],
            others_sections_data=request.others_sections_data or {}
        )
        return {"success": True, "data": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building profile: {str(e)}")


def _convert_form_values_to_resume_data(form_values: list, resume_helper: ResumeHelper) -> Dict[str, Any]:
    """Convert form values (from load_from_json) to ResumeData format."""
    from backend.core.utils.constants import UIConstants
    from backend.core.models.resume import ResumeSchema
    from backend.core.infrastructure.adapters.table_data_extractor import TableDataExtractor
    
    if not form_values or len(form_values) < UIConstants.FORM_BASE_COUNT:
        raise ValueError("Invalid form values format")
    
    # Extract personal info (indices 0-11)
    personal_order = ResumeSchema.get_field_order('personal_info')
    personal_info = {}
    for i, field_name in enumerate(personal_order):
        if i < len(form_values):
            personal_info[field_name] = form_values[i] or ""
    
    # Extract education table (index 20 = EDUCATION_TABLE_INDEX)
    education_table = form_values[UIConstants.EDUCATION_TABLE_INDEX] if UIConstants.EDUCATION_TABLE_INDEX < len(form_values) else []
    
    education = []
    if isinstance(education_table, list):
        edu_data = TableDataExtractor.extract_table_data(education_table)
        for row in edu_data:
            if isinstance(row, list) and len(row) >= UIConstants.EDUCATION_INPUT_FIELDS and any(str(x).strip() for x in row):
                education.append({
                    'institution': str(row[0]) if len(row) > 0 else '',
                    'degree': str(row[1]) if len(row) > 1 else '',
                    'field_of_study': str(row[2]) if len(row) > 2 else '',
                    'gpa': str(row[3]) if len(row) > 3 else '',
                    'start_date': str(row[4]) if len(row) > 4 else '',
                    'end_date': str(row[5]) if len(row) > 5 else '',
                    'description': str(row[6]) if len(row) > 6 else ''
                })
    
    # Extract experience table (index 28 = WORK_TABLE_INDEX)
    experience_table = form_values[UIConstants.WORK_TABLE_INDEX] if UIConstants.WORK_TABLE_INDEX < len(form_values) else []
    
    experience = []
    if isinstance(experience_table, list):
        work_data = TableDataExtractor.extract_table_data(experience_table)
        for row in work_data:
            if isinstance(row, list) and len(row) >= UIConstants.WORK_INPUT_FIELDS and any(str(x).strip() for x in row):
                achievements_str = str(row[6]) if len(row) > 6 else ''
                achievements = [a.strip('- ').strip() for a in achievements_str.split('\n') if a.strip()] if achievements_str else []
                experience.append({
                    'company': str(row[0]) if len(row) > 0 else '',
                    'position': str(row[1]) if len(row) > 1 else '',
                    'location': str(row[2]) if len(row) > 2 else '',
                    'start_date': str(row[3]) if len(row) > 3 else '',
                    'end_date': str(row[4]) if len(row) > 4 else '',
                    'description': str(row[5]) if len(row) > 5 else '',
                    'achievements': achievements
                })
    
    # Extract skills table (index 32 = SKILLS_TABLE_INDEX)
    skills_table = form_values[UIConstants.SKILLS_TABLE_INDEX] if UIConstants.SKILLS_TABLE_INDEX < len(form_values) else []
    
    skills = []
    if isinstance(skills_table, list):
        skill_data = TableDataExtractor.extract_table_data(skills_table)
        for row in skill_data:
            if isinstance(row, list) and len(row) >= UIConstants.SKILLS_INPUT_FIELDS and any(str(x).strip() for x in row):
                skills.append({
                    'category': str(row[0]) if len(row) > 0 else '',
                    'name': str(row[1]) if len(row) > 1 else '',
                    'proficiency': str(row[2]) if len(row) > 2 else ''
                })
    
    # Extract projects table (index 39 = PROJECTS_TABLE_INDEX)
    projects_table = form_values[UIConstants.PROJECTS_TABLE_INDEX] if UIConstants.PROJECTS_TABLE_INDEX < len(form_values) else []
    
    projects = []
    if isinstance(projects_table, list):
        project_data = TableDataExtractor.extract_table_data(projects_table)
        for row in project_data:
            if isinstance(row, list) and len(row) >= UIConstants.PROJECTS_INPUT_FIELDS and any(str(x).strip() for x in row):
                projects.append({
                    'name': str(row[0]) if len(row) > 0 else '',
                    'description': str(row[1]) if len(row) > 1 else '',
                    'technologies': str(row[2]) if len(row) > 2 else '',
                    'url': str(row[3]) if len(row) > 3 else '',
                    'start_date': str(row[4]) if len(row) > 4 else '',
                    'end_date': str(row[5]) if len(row) > 5 else ''
                })
    
    # Extract certifications table (index 45 = CERTIFICATIONS_TABLE_INDEX)
    certifications_table = form_values[UIConstants.CERTIFICATIONS_TABLE_INDEX] if UIConstants.CERTIFICATIONS_TABLE_INDEX < len(form_values) else []
    
    certifications = []
    if isinstance(certifications_table, list):
        cert_data = TableDataExtractor.extract_table_data(certifications_table)
        for row in cert_data:
            if isinstance(row, list) and len(row) >= UIConstants.CERTIFICATIONS_INPUT_FIELDS and any(str(x).strip() for x in row):
                certifications.append({
                    'name': str(row[0]) if len(row) > 0 else '',
                    'issuer': str(row[1]) if len(row) > 1 else '',
                    'date_obtained': str(row[2]) if len(row) > 2 else '',
                    'credential_id': str(row[3]) if len(row) > 3 else '',
                    'url': str(row[4]) if len(row) > 4 else ''
                })
    
    # Extract others (index 46 = OTHERS_SECTIONS_DATA_INDEX)
    others = form_values[UIConstants.OTHERS_SECTIONS_DATA_INDEX] if UIConstants.OTHERS_SECTIONS_DATA_INDEX < len(form_values) else {}
    if not isinstance(others, dict):
        others = {}
    
    # Build ResumeData structure
    resume_data = {
        'personal_info': {
            'name_prefix': personal_info.get('name_prefix', ''),
            'email': personal_info.get('email', ''),
            'full_name': personal_info.get('full_name', ''),
            'phone': personal_info.get('phone', ''),
            'current_address': personal_info.get('current_address', ''),
            'location': personal_info.get('location', ''),
            'citizenship': personal_info.get('citizenship', ''),
            'linkedin_url': personal_info.get('linkedin_url', ''),
            'github_url': personal_info.get('github_url', ''),
            'portfolio_url': personal_info.get('portfolio_url', ''),
            'summary': personal_info.get('summary', '')
        },
        'education': education,
        'experience': experience,
        'skills': skills,
        'projects': projects,
        'certifications': certifications,
        'others': others
    }
    
    return resume_data


@router.post("/load-from-json")
async def load_from_json(
    file: UploadFile = File(...),
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Load resume data from JSON file."""
    try:
        # Save uploaded file temporarily
        import tempfile
        content = await file.read()
        
        # Try to decode with multiple encodings
        text_content = None
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if text_content is None:
            raise HTTPException(status_code=400, detail="Could not decode file - unsupported encoding")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as tmp_file:
            tmp_file.write(text_content)
            tmp_path = tmp_file.name
        
        try:
            form_values = resume_helper.load_from_json(tmp_path)
            resume_data = _convert_form_values_to_resume_data(form_values, resume_helper)
            return {"success": True, "data": resume_data}
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading JSON: {str(e)}")


@router.post("/generate-json")
async def generate_json(
    resume_data: ResumeData,
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> JSONResponse:
    """Generate and return resume as JSON file."""
    try:
        # Convert Pydantic model to dict
        resume_dict = resume_data.dict()
        
        # Return as JSON response
        return JSONResponse(
            content=resume_dict,
            headers={
                "Content-Disposition": "attachment; filename=resume.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JSON: {str(e)}")


@router.get("/example/software-developer")
async def load_software_developer_example(
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Load software developer example profile."""
    try:
        result = resume_helper.load_software_developer_example()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading example: {str(e)}")


@router.get("/example/process-engineer")
async def load_process_engineer_example(
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Load process engineer example profile."""
    try:
        result = resume_helper.load_process_engineer_example()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading example: {str(e)}")


def _extract_json_from_pdf(pdf_path: str, resume_helper: ResumeHelper):
    """Extract embedded JSON metadata from PDF file."""
    try:
        import pypdf
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            metadata = pdf_reader.metadata
            
            if metadata and '/ResumeData' in metadata:
                json_data = str(metadata['/ResumeData'])
                profile_data = json.loads(json_data)
                
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(profile_data, temp_file, indent=2)
                    temp_path = temp_file.name
                
                try:
                    result = resume_helper.load_from_json(temp_path)
                    return result
                finally:
                    os.unlink(temp_path)
            else:
                return None
    except ImportError:
        return None
    except Exception:
        return None


def _extract_json_from_docx(docx_path: str, resume_helper: ResumeHelper):
    """Extract embedded JSON metadata from DOCX file."""
    try:
        import base64
        from zipfile import ZipFile
        import xml.etree.ElementTree as ET
        
        with ZipFile(docx_path, 'r') as zip_file:
            if 'docProps/custom.xml' in zip_file.namelist():
                custom_props = zip_file.read('docProps/custom.xml')
                root = ET.fromstring(custom_props)
                
                for prop in root.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/custom-properties}property'):
                    prop_name = prop.get('name')
                    
                    if prop_name == 'ResumeHelperData':
                        text_elem = prop.find('.//{http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes}lpwstr')
                        if text_elem is not None and text_elem.text:
                            try:
                                encoded_data = text_elem.text
                                json_str = base64.b64decode(encoded_data).decode('utf-8')
                                profile_data = json.loads(json_str)
                                
                                import tempfile
                                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                                    json.dump(profile_data, temp_file, indent=2)
                                    temp_path = temp_file.name
                                
                                try:
                                    result = resume_helper.load_from_json(temp_path)
                                    return result
                                finally:
                                    os.unlink(temp_path)
                            except Exception:
                                pass
        
        return None
    except ImportError as e:
        return None
    except Exception as e:
        return None


@router.post("/load-from-pdf")
async def load_from_pdf(
    file: UploadFile = File(...),
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Load resume data from PDF file (extracts embedded JSON metadata)."""
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            form_values = _extract_json_from_pdf(tmp_path, resume_helper)
            if form_values is None:
                raise HTTPException(
                    status_code=400, 
                    detail="No resume data found in PDF. The PDF must have been generated by Resume Helper with embedded metadata."
                )
            resume_data = _convert_form_values_to_resume_data(form_values, resume_helper)
            return {"success": True, "data": resume_data}
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading PDF: {str(e)}")


@router.post("/load-from-docx")
async def load_from_docx(
    file: UploadFile = File(...),
    resume_helper: ResumeHelper = Depends(get_resume_helper)
) -> Dict[str, Any]:
    """Load resume data from DOCX file (extracts embedded JSON metadata)."""
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            form_values = _extract_json_from_docx(tmp_path, resume_helper)
            if form_values is None:
                raise HTTPException(
                    status_code=400, 
                    detail="No resume data found in DOCX. The DOCX must have been generated by Resume Helper with embedded metadata."
                )
            resume_data = _convert_form_values_to_resume_data(form_values, resume_helper)
            return {"success": True, "data": resume_data}
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading DOCX: {str(e)}")

 
