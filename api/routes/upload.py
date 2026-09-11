# Resume upload endpoints
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from config.settings import settings
from utils.logger import log
from agents.orchestrator_agent import orchestrator
import os
import shutil
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume and process it through the complete pipeline
    
    Args:
        file: Resume file (PDF or DOCX)
        
    Returns:
        Processing results
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        log.info(f"File uploaded: {file_path}")
        
        # Process through orchestrator
        result = orchestrator.process_candidate_application(file_path)
        
        return JSONResponse(content={
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "candidate_email": result.get("candidate_email", ""),
            "candidate_name": result.get("candidate_name", ""),
            "overall_score": result.get("overall_score", 0),
            "workflow_steps": result.get("steps", []),
            "file_path": file_path
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        log.error(f"Resume upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume/batch")
async def upload_resumes_batch(files: list[UploadFile] = File(...)):
    """Upload multiple resumes in batch
    
    Args:
        files: List of resume files
        
    Returns:
        Batch processing results
    """
    try:
        results = []
        
        for file in files:
            try:
                # Validate and save each file
                file_ext = os.path.splitext(file.filename)[1].lower()
                
                if file_ext not in ['.pdf', '.docx', '.doc']:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "Invalid file type"
                    })
                    continue
                
                # Save file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Process
                result = orchestrator.process_candidate_application(file_path)
                
                results.append({
                    "filename": file.filename,
                    "success": result.get("success", False),
                    "candidate_email": result.get("candidate_email", ""),
                    "candidate_name": result.get("candidate_name", ""),
                    "overall_score": result.get("overall_score", 0)
                })
                
            except Exception as e:
                log.error(f"Error processing {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        return JSONResponse(content={
            "total_files": len(files),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "results": results
        })
        
    except Exception as e:
        log.error(f"Batch upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))