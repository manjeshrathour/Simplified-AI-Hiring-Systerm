# agents/communication_agent.py

from crewai import Agent
from tools.email_tool import email_tool
from tools.database_tool import database_tool
from utils.logger import log
from langchain_groq import ChatGroq
from config.settings import settings
from typing import Dict, List, Optional


class CommunicationAgent:
    """Agent responsible for candidate communication with transparent feedback"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.7
        )
        
        self.agent = Agent(
            role="Candidate Communication Specialist",
            goal="Communicate recruitment outcomes clearly, including scores and constructive feedback",
            backstory="""You are a professional and empathetic communicator. You believe in 
            hiring transparency, ensuring every candidate knows their match score and 
            receives actionable advice on how to improve if they are not selected.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[email_tool, database_tool]
        )
    
    def send_application_confirmation(self, candidate_email: str) -> Dict:
        """Send application received confirmation"""
        try:
            candidate_result = database_tool._run(action="find_one", collection="candidates", query={"email": candidate_email})
            candidate = candidate_result.get("document")
            if not candidate:
                return {"success": False, "error": "Candidate not found"}
            
            return email_tool._run(
                action="send_confirmation",
                to_email=candidate_email,
                candidate_name=candidate.get("name", "Candidate")
            )
        except Exception as e:
            log.error(f"Error sending confirmation: {e}")
            return {"success": False, "error": str(e)}

    def send_interview_invitation(
        self,
        candidate_email: str,
        job_id: str,
        interview_time: str,
        meeting_link: str = None,
        score: float = None  # Added score for transparency
    ) -> Dict:
        """Send interview invitation including the match score"""
        try:
            candidate_result = database_tool._run(action="find_one", collection="candidates", query={"email": candidate_email})
            candidate = candidate_result.get("document")
            job = database_tool.get_job_by_id(job_id)
            
            if not candidate or not job:
                return {"success": False, "error": "Candidate or job not found"}

            score_text = f" You achieved an impressive match score of {score}/100!" if score else ""
            
            # Using the email tool to send the notification
            # We customize the invitation message to include the score
            result = email_tool._run(
                action="send_interview_invitation",
                to_email=candidate_email,
                candidate_name=candidate.get("name", "Candidate"),
                job_title=job.get("title", "Position"),
                interview_time=interview_time,
                meeting_link=meeting_link or "",
                additional_text=f"Congratulations!{score_text} Our AI matching system identified you as a top fit for this role."
            )
            
            log.info(f"Sent shortlisted invitation to {candidate_email} (Score: {score})")
            return result
        except Exception as e:
            log.error(f"Error sending invitation: {e}")
            return {"success": False, "error": str(e)}

    def send_rejection_notice(
        self, 
        candidate_email: str, 
        job_id: str, 
        score: float = None, 
        tips: List[str] = None
    ) -> Dict:
        """
        Send rejection notification including match score and improvement recommendations.
        """
        try:
            candidate_result = database_tool._run(action="find_one", collection="candidates", query={"email": candidate_email})
            candidate = candidate_result.get("document")
            
            job_title = "Position"
            if job_id != "GENERAL":
                job = database_tool.get_job_by_id(job_id)
                if job:
                    job_title = job.get("title", "Position")
            
            if not candidate:
                return {"success": False, "error": "Candidate not found"}

            # Update status in DB
            database_tool._run(
                action="update",
                collection="candidates",
                query={"email": candidate_email},
                data={"status": "rejected"}
            )

            # Construct the specialized feedback body
            tips_html = ""
            if tips:
                tips_list = "".join([f"<li>{tip}</li>" for tip in tips])
                tips_html = f"""
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #4f46e5; margin-top: 20px;">
                    <h4 style="margin-top: 0; color: #4f46e5;">How to improve for next time:</h4>
                    <p>Based on our AI analysis of the {job_title} requirements, we recommend focusing on these areas:</p>
                    <ul>{tips_list}</ul>
                </div>
                """

            score_html = f"<p>Your application match score was: <strong>{score}/100</strong></p>" if score is not None else ""

            full_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h3>Application Update: {job_title}</h3>
                <p>Dear {candidate.get('name', 'Candidate')},</p>
                <p>Thank you for your interest in the {job_title} role. After careful review of your profile against our specific requirements, we have decided to move forward with other candidates at this time.</p>
                
                {score_html}
                
                <p>We believe in providing transparency to all our applicants. While you weren't selected for this specific role, we want to help you in your professional journey.</p>
                
                {tips_html}
                
                <p>We will keep your profile in our database for future opportunities that may be a better fit.</p>
                <br>
                <p>Best regards,</p>
                <p><strong>The Recruiting Team</strong></p>
            </body>
            </html>
            """

            # Send via custom email action or standard rejection (depending on tool capability)
            # Here we use a generic send action if available, or override the rejection body
            result = email_tool._run(
                action="send_rejection", # Or use a generic "send_custom_email"
                to_email=candidate_email,
                candidate_name=candidate.get("name", "Candidate"),
                job_title=job_title,
                custom_body=full_body # Assuming tool is updated to handle custom_body
            )
            
            log.info(f"Sent detailed rejection to {candidate_email} (Score: {score})")
            return result
            
        except Exception as e:
            log.error(f"Error sending rejection: {e}")
            return {"success": False, "error": str(e)}

    def send_follow_up(self, candidate_email: str, message: str) -> Dict:
        """Send follow-up message"""
        try:
            candidate_result = database_tool._run(action="find_one", collection="candidates", query={"email": candidate_email})
            candidate = candidate_result.get("document")
            if not candidate: return {"success": False, "error": "Candidate not found"}
            
            return email_tool._run(
                action="send_follow_up",
                to_email=candidate_email,
                candidate_name=candidate.get("name", "Candidate"),
                message=message
            )
        except Exception as e:
            log.error(f"Error sending follow-up: {e}")
            return {"success": False, "error": str(e)}

    def send_interview_reminder(self, candidate_email: str, interview_time: str, meeting_link: str = None) -> Dict:
        """Send interview reminder"""
        try:
            candidate_result = database_tool._run(action="find_one", collection="candidates", query={"email": candidate_email})
            candidate = candidate_result.get("document")
            if not candidate: return {"success": False, "error": "Candidate not found"}
            
            return email_tool._run(
                action="send_reminder",
                to_email=candidate_email,
                candidate_name=candidate.get("name", "Candidate"),
                interview_time=interview_time,
                meeting_link=meeting_link or ""
            )
        except Exception as e:
            log.error(f"Error sending reminder: {e}")
            return {"success": False, "error": str(e)}


# Create agent instance
communication_agent = CommunicationAgent()