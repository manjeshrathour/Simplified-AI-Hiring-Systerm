# api/routes/candidates.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from models.candidate import CandidateUpdate, CandidateResponse
from tools.database_tool import database_tool
from agents.orchestrator_agent import orchestrator
from agents.matching_agent import matching_agent
from utils.logger import log

router = APIRouter(prefix="/candidates", tags=["Candidates"])


# Define a Pydantic model for the list response to ensure proper serialization
class CandidateListResponse(BaseModel):
    success: bool = True
    count: int
    candidates: List[CandidateResponse]

# Define a Pydantic model for the single item response
class SingleCandidateResponse(BaseModel):
    success: bool = True
    candidate: CandidateResponse


@router.get("/", response_model=CandidateListResponse)
async def get_candidates(
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 50
):
    """Get all candidates with optional filters"""
    try:
        query = {}
        if status:
            query["status"] = status
        if min_score is not None:
            query["score"] = {"$gte": min_score}
        
        result = database_tool._run(
            action="find",
            collection="candidates",
            query=query
        )
        
        db_candidates = result.get("documents", [])[:limit]
        
        # Transform DB data to match the CandidateResponse model
        # Pydantic will handle datetime serialization automatically
        candidates_list = []
        for cand in db_candidates:
            cand["id"] = str(cand["_id"])  # Convert ObjectId to string for the 'id' field
            candidates_list.append(cand)

        # Return a dictionary that matches the response_model. FastAPI does the rest.
        return {
            "count": len(candidates_list),
            "candidates": candidates_list
        }
        
    except Exception as e:
        log.error(f"Error fetching candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{candidate_email}", response_model=SingleCandidateResponse)
async def get_candidate(candidate_email: str):
    """Get a specific candidate by email"""
    try:
        result = database_tool._run(
            action="find_one",
            collection="candidates",
            query={"email": candidate_email}
        )
        
        candidate = result.get("document")
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Transform DB data to match the CandidateResponse model
        candidate["id"] = str(candidate["_id"])

        # Return a dictionary matching the response_model
        return {"candidate": candidate}
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{candidate_email}", response_model=dict)
async def update_candidate(candidate_email: str, update: CandidateUpdate):
    """Update candidate information"""
    try:
        update_data = update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = database_tool._run(
            action="update",
            collection="candidates",
            query={"email": candidate_email},
            data=update_data
        )
        
        if result.get("matched_count", 0) == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        log.info(f"Candidate updated: {candidate_email}")
        
        return {
            "success": True,
            "message": "Candidate updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{candidate_email}/rematch", response_model=dict)
async def rematch_candidate(candidate_email: str):
    """Re-run job matching for a candidate"""
    try:
        result = matching_agent.match_candidate_to_jobs(candidate_email)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Matching failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error rematching candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{candidate_email}/shortlist/{job_id}", response_model=dict)
async def shortlist_candidate(candidate_email: str, job_id: str):
    """Shortlist a candidate for a job and schedule interview"""
    try:
        result = orchestrator.process_candidate_shortlisting(
            candidate_email=candidate_email,
            job_id=job_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("errors", ["Shortlisting failed"])
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error shortlisting candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{candidate_email}/reject/{job_id}", response_model=dict)
async def reject_candidate(candidate_email: str, job_id: str):
    """Reject a candidate for a job"""
    try:
        result = orchestrator.reject_candidate(
            candidate_email=candidate_email,
            job_id=job_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Rejection failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error rejecting candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{candidate_email}", response_model=dict)
async def delete_candidate(candidate_email: str):
    """Delete a candidate"""
    try:
        result = database_tool._run(
            action="delete",
            collection="candidates",
            query={"email": candidate_email}
        )
        
        if result.get("deleted_count", 0) == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        log.info(f"Candidate deleted: {candidate_email}")
        
        return {
            "success": True,
            "message": "Candidate deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))