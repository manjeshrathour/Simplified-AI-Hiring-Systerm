# Interview Scheduling Agent
from crewai import Agent
from tools.calendar_tool import calendar_tool
from tools.database_tool import database_tool
from utils.logger import log
from langchain_groq import ChatGroq
from config.settings import settings
from typing import Dict
from datetime import datetime


class SchedulingAgent:
    """Agent responsible for scheduling interviews"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.3
        )
        
        self.agent = Agent(
            role="Interview Scheduling Coordinator",
            goal="Schedule interviews efficiently by finding optimal time slots for candidates and recruiters",
            backstory="""You are a professional scheduling coordinator who ensures smooth 
            interview scheduling. You check calendar availability, propose suitable time slots, 
            and coordinate between candidates and recruiters to find the best interview times. 
            You are efficient and considerate of everyone's time.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[calendar_tool, database_tool]
        )
    
    def schedule_interview(
        self,
        candidate_email: str,
        job_id: str,
        recruiter_email: str = "deepesh.y@atriauniversity.edu.in",
        preferred_time: str = None
    ) -> Dict:
        """Schedule an interview for a candidate
        
        Args:
            candidate_email: Candidate's email
            job_id: Job ID
            recruiter_email: Recruiter's email
            preferred_time: Preferred time (optional)
            
        Returns:
            Scheduling results
        """
        try:
            log.info(f"Scheduling interview for {candidate_email} for job {job_id}")
            
            # Get candidate info
            candidate_result = database_tool._run(
                action="find_one",
                collection="candidates",
                query={"email": candidate_email}
            )
            candidate = candidate_result.get("document")
            
            if not candidate:
                return {"success": False, "error": "Candidate not found"}
            
            # Get job info
            job = database_tool.get_job_by_id(job_id)
            if not job:
                return {"success": False, "error": "Job not found"}
            
            # Check if interview already exists
            existing_interview = database_tool._run(
                action="find_one",
                collection="interviews",
                query={
                    "candidate_id": str(candidate["_id"]),
                    "job_id": job_id,
                    "status": {"$in": ["scheduled", "confirmed"]}
                }
            )
            
            if existing_interview.get("document"):
                return {
                    "success": False,
                    "error": "Interview already scheduled for this candidate and job"
                }
            
            # Get available slots
            if preferred_time:
                # Check if preferred time is available
                check_result = calendar_tool._run(
                    action="check_availability",
                    check_time=preferred_time
                )
                
                if not check_result.get("available"):
                    return {
                        "success": False,
                        "error": "Preferred time slot is not available"
                    }
                
                selected_time = preferred_time
            else:
                # Get available slots
                slots_result = calendar_tool._run(
                    action="get_available_slots",
                    days_ahead=7,
                    duration_minutes=60
                )
                
                available_slots = slots_result.get("available_slots", [])
                
                if not available_slots:
                    return {
                        "success": False,
                        "error": "No available time slots found"
                    }
                
                # Select first available slot
                selected_time = available_slots[0]["start_time"]
            
            # Book the slot
            booking_result = calendar_tool._run(
                action="book_slot",
                start_time=selected_time,
                candidate_email=candidate_email,
                recruiter_email=recruiter_email,
                title=f"Interview: {job.get('title', 'Position')}",
                duration_minutes=60
            )
            
            if not booking_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to book time slot"
                }
            
            # Save interview to database
            interview_data = {
                "candidate_id": str(candidate["_id"]),
                "job_id": job_id,
                "recruiter_id": recruiter_email,
                "scheduled_time": datetime.fromisoformat(booking_result["start_time"]),
                "duration_minutes": 60,
                "interview_type": "technical",
                "meeting_link": booking_result.get("meeting_link", ""),
                "status": "scheduled"
            }
            
            db_result = database_tool.save_interview(interview_data)
            
            log.info(f"Interview scheduled: {booking_result['booking_id']}")
            
            return {
                "success": True,
                "interview_id": db_result.get("inserted_id"),
                "booking_id": booking_result["booking_id"],
                "candidate_name": candidate.get("name", ""),
                "candidate_email": candidate_email,
                "job_title": job.get("title", ""),
                "scheduled_time": booking_result["start_time"],
                "meeting_link": booking_result.get("meeting_link", ""),
                "message": "Interview scheduled successfully"
            }
            
        except Exception as e:
            log.error(f"Error scheduling interview: {e}")
            return {"success": False, "error": str(e)}
    
    def get_available_slots(self, days_ahead: int = 7) -> Dict:
        """Get available interview slots
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            Available slots
        """
        return calendar_tool._run(
            action="get_available_slots",
            days_ahead=days_ahead,
            duration_minutes=60
        )


# Create agent instance
scheduling_agent = SchedulingAgent()