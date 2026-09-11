# api/routes/interviews.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from models.interview import InterviewCreate, InterviewUpdate, InterviewResponse
from tools.database_tool import database_tool
from agents.scheduling_agent import scheduling_agent
from agents.communication_agent import communication_agent
from utils.logger import log

router = APIRouter(prefix="/interviews", tags=["Interviews"])


# Define Pydantic models for structured, serialized responses
class InterviewListResponse(BaseModel):
    success: bool = True
    count: int
    interviews: List[InterviewResponse]

class SingleInterviewResponse(BaseModel):
    success: bool = True
    interview: InterviewResponse


@router.post("/", response_model=dict)
async def create_interview(interview: InterviewCreate):
    """Create and schedule an interview"""
    try:
        result = scheduling_agent.schedule_interview(
            candidate_email=interview.candidate_id,
            job_id=interview.job_id,
            preferred_time=interview.scheduled_time.isoformat()
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Scheduling failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=InterviewListResponse)
async def get_interviews(
    status: Optional[str] = None,
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
    limit: int = 50
):
    """Get interviews with optional filters"""
    try:
        query = {}
        if status:
            query["status"] = status
        if candidate_id:
            query["candidate_id"] = candidate_id
        if job_id:
            query["job_id"] = job_id
        
        result = database_tool._run(
            action="find",
            collection="interviews",
            query=query
        )
        
        db_interviews = result.get("documents", [])[:limit]

        # Transform DB data to match InterviewResponse model
        interview_list = []
        for interview in db_interviews:
            interview["id"] = str(interview["_id"])
            interview_list.append(interview)
        
        # Return a dictionary, FastAPI will handle serialization
        return {
            "count": len(interview_list),
            "interviews": interview_list
        }
        
    except Exception as e:
        log.error(f"Error fetching interviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interview_id}", response_model=SingleInterviewResponse)
async def get_interview(interview_id: str):
    """Get a specific interview"""
    try:
        result = database_tool._run(
            action="find_one",
            collection="interviews",
            query={"_id": interview_id}
        )
        
        interview = result.get("document")
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Transform DB data to match InterviewResponse model
        interview["id"] = str(interview["_id"])
        
        return {"interview": interview}
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{interview_id}", response_model=dict)
async def update_interview(interview_id: str, update: InterviewUpdate):
    """Update an interview"""
    try:
        update_data = update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = database_tool._run(
            action="update",
            collection="interviews",
            query={"_id": interview_id},
            data=update_data
        )
        
        if result.get("matched_count", 0) == 0:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        log.info(f"Interview updated: {interview_id}")
        
        return {
            "success": True,
            "message": "Interview updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/send-reminder", response_model=dict)
async def send_interview_reminder(interview_id: str):
    """Send interview reminder to candidate"""
    try:
        interview_result = database_tool._run(
            action="find_one",
            collection="interviews",
            query={"_id": interview_id}
        )
        
        interview = interview_result.get("document")
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        result = communication_agent.send_interview_reminder(
            candidate_email=interview.get("candidate_id"),
            interview_time=str(interview.get("scheduled_time")),
            meeting_link=interview.get("meeting_link", "")
        )
        
        database_tool._run(
            action="update",
            collection="interviews",
            query={"_id": interview_id},
            data={"reminder_sent": True}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error sending reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{interview_id}", response_model=dict)
async def cancel_interview(interview_id: str):
    """Cancel/Delete an interview"""
    try:
        # Try finding by direct ID first (could be string UUID or MongoDB ObjectId string)
        query = {"_id": interview_id}
        
        # If the database tool supports intelligent ID handling (which it does), 
        # we can just pass the string. The tool converts to ObjectId if needed.
        
        result = database_tool._run(
            action="delete",
            collection="interviews",
            query=query
        )
        
        if result.get("deleted_count", 0) == 0:
            # If not found, try forcing ObjectId conversion just in case the tool didn't catch it
            # This is a fallback
            try: 
                from bson import ObjectId
                oid = ObjectId(interview_id)
                result = database_tool._run(
                    action="delete",
                    collection="interviews",
                    query={"_id": oid}
                )
            except:
                pass # Invalid ObjectId, original query failure stands

        if result.get("deleted_count", 0) == 0:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        log.info(f"Interview deleted: {interview_id}")
        
        return {
            "success": True,
            "message": "Interview deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-slots/", response_model=dict)
async def get_available_slots(days_ahead: int = 7):
    """Get available interview slots"""
    try:
        result = scheduling_agent.get_available_slots(days_ahead=days_ahead)
        
        return result
        
    except Exception as e:
        log.error(f"Error fetching available slots: {e}")
        raise HTTPException(status_code=500, detail=str(e))