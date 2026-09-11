# api/routes/jobs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Import the corrected models
from models.job_posting import JobPostingCreate, JobPostingUpdate, JobPostingResponse
from tools.database_tool import database_tool
from tools.vector_search_tool import vector_search_tool
from agents.sourcing_agent import sourcing_agent
from utils.logger import log

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Define a wrapper model for the list response for better serialization
class JobListResponse(BaseModel):
    success: bool = True
    count: int
    jobs: List[JobPostingResponse]


@router.post("/", response_model=dict)
async def create_job(job: JobPostingCreate):
    """Create a new job posting"""
    try:
        job_data = job.model_dump()
        result = database_tool._run(action="insert", collection="jobs", data=job_data)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        job_id = result.get("inserted_id")
        
        vector_search_tool._run(
            action="add_job",
            job_id=job_data["job_id"],
            title=job_data["title"],
            description=job_data["description"],
            required_skills=job_data["required_skills"]
        )
        log.info(f"Job created: {job_data['job_id']}")
        
        # NEW: Trigger sourcing agent to find past candidates
        try:
            log.info(f"Triggering sourcing agent for new job: {job_data['job_id']}")
            sourcing_agent.find_and_engage_past_candidates(job_data["job_id"])
        except Exception as sourcing_error:
            log.warning(f"Sourcing agent failed for job {job_data['job_id']}: {sourcing_error}")
            # Don't fail job creation if sourcing fails
        
        return {
            "success": True,
            "job_id": job_data["job_id"],
            "id": job_id,
            "message": "Job posting created successfully"
        }
    except Exception as e:
        log.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


### FIX: Corrected get_jobs endpoint ###
@router.get("/", response_model=JobListResponse)
async def get_jobs(limit: int = 50):
    """Get all job postings"""
    try:
        # The incorrect 'status' filter has been removed.
        # This now fetches ALL jobs.
        query = {}
        
        result = database_tool._run(
            action="find",
            collection="jobs",
            query=query
        )
        
        db_jobs = result.get("documents", [])[:limit]

        # Transform the _id to id to match the Pydantic model
        jobs_list = []
        for job in db_jobs:
            job["id"] = str(job["_id"])
            jobs_list.append(job)
        
        # Return a dictionary that FastAPI will serialize using the response_model
        return {
            "count": len(jobs_list),
            "jobs": jobs_list
        }
        
    except Exception as e:
        log.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================== Additional Endpoints =======================================google form====
@router.get("/list-names")
async def list_job_names():
    try:
        jobs = database_tool.get_active_jobs()
        # Format for Google Form: "Software Engineer (JOB-AI-001)"
        job_list = [f"{j['title']} ({j['job_id']})" for j in jobs]
        return {"success": True, "jobs": job_list}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{job_id}", response_model=dict)
async def get_job(job_id: str):
    """Get a specific job posting"""
    # NOTE: This assumes `get_job_by_id` handles ObjectId conversion.
    # If not, this might also need adjustment.
    try:
        job = database_tool.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"success": True, "job": job}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{job_id}", response_model=dict)
async def update_job(job_id: str, job_update: JobPostingUpdate):
    """Update a job posting"""
    try:
        update_data = job_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = database_tool._run(
            action="update", collection="jobs", query={"job_id": job_id}, data=update_data
        )
        if result.get("matched_count", 0) == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        log.info(f"Job updated: {job_id}")
        return {
            "success": True,
            "message": "Job updated successfully",
            "modified_count": result.get("modified_count", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}", response_model=dict)
async def delete_job(job_id: str):
    """Delete a job posting"""
    try:
        result = database_tool._run(
            action="delete", collection="jobs", query={"job_id": job_id}
        )
        if result.get("deleted_count", 0) == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        log.info(f"Job deleted: {job_id}")
        return {"success": True, "message": "Job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/candidates", response_model=dict)
async def get_job_candidates(job_id: str, top_n: int = 10):
    """Get top candidates for a job"""
    try:
        candidates = database_tool.get_top_candidates(job_id, limit=top_n)
        return {
            "success": True,
            "job_id": job_id,
            "count": len(candidates),
            "candidates": candidates
        }
    except Exception as e:
        log.error(f"Error fetching job candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))