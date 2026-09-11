# Tool: Email sending
from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config.settings import settings
from utils.logger import log


class EmailTool(BaseTool):
    name: str = "Email Communication"
    description: str = """Sends emails to candidates and recruiters:
    - Send application confirmation
    - Send interview invitation
    - Send rejection notification
    - Send follow-up reminders
    - Send interview reminders
    """
    
    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Send email"""
        try:
            if action == "send_confirmation":
                return self._send_confirmation(kwargs)
            elif action == "send_interview_invitation":
                return self._send_interview_invitation(kwargs)
            elif action == "send_rejection":
                return self._send_rejection(kwargs)
            elif action == "send_follow_up":
                return self._send_follow_up(kwargs)
            elif action == "send_reminder":
                return self._send_reminder(kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            log.error(f"Email error: {e}")
            return {"error": str(e)}
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = True
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Skip if SMTP not configured
            if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
                log.warning("SMTP not configured, skipping email send")
                return {
                    "success": True,
                    "message": "Email skipped (SMTP not configured)",
                    "to": to_email,
                    "subject": subject
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            log.info(f"Email sent to {to_email}: {subject}")
            
            return {
                "success": True,
                "message": f"Email sent to {to_email}",
                "to": to_email,
                "subject": subject
            }
            
        except Exception as e:
            log.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_confirmation(self, params: Dict) -> Dict[str, Any]:
        """Send application confirmation email"""
        to_email = params.get("to_email")
        candidate_name = params.get("candidate_name", "Candidate")
        
        subject = "Application Received - AI Recruiting System"
        body = f"""
        <html>
        <body>
            <h2>Thank You for Your Application!</h2>
            <p>Dear {candidate_name},</p>
            <p>We have received your application and our AI system is currently analyzing your profile.</p>
            <p>You will hear from us soon regarding the next steps.</p>
            <br>
            <p>Best regards,</p>
            <p>The Recruiting Team</p>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_interview_invitation(self, params: Dict) -> Dict[str, Any]:
        """Send interview invitation email"""
        to_email = params.get("to_email")
        candidate_name = params.get("candidate_name", "Candidate")
        job_title = params.get("job_title", "Position")
        interview_time = params.get("interview_time", "")
        meeting_link = params.get("meeting_link", "")
        
        subject = f"Interview Invitation - {job_title}"
        body = f"""
        <html>
        <body>
            <h2>Congratulations! You've Been Shortlisted</h2>
            <p>Dear {candidate_name},</p>
            <p>We are pleased to invite you for an interview for the position of <strong>{job_title}</strong>.</p>
            <p><strong>Interview Details:</strong></p>
            <ul>
                <li>Date & Time: {interview_time}</li>
                {"<li>Meeting Link: <a href='" + meeting_link + "'>" + meeting_link + "</a></li>" if meeting_link else ""}
            </ul>
            <p>Please confirm your availability by replying to this email.</p>
            <br>
            <p>Best regards,</p>
            <p>The Recruiting Team</p>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_rejection(self, params: Dict) -> Dict[str, Any]:
        """Send rejection notification"""
        to_email = params.get("to_email")
        candidate_name = params.get("candidate_name", "Candidate")
        job_title = params.get("job_title", "Position")
        
        subject = f"Application Update - {job_title}"
        body = f"""
        <html>
        <body>
            <h2>Application Update</h2>
            <p>Dear {candidate_name},</p>
            <p>Thank you for your interest in the <strong>{job_title}</strong> position.</p>
            <p>After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.</p>
            <p>We encourage you to apply for future openings that match your skills and experience.</p>
            <br>
            <p>Best regards,</p>
            <p>The Recruiting Team</p>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_follow_up(self, params: Dict) -> Dict[str, Any]:
        """Send follow-up email"""
        to_email = params.get("to_email")
        candidate_name = params.get("candidate_name", "Candidate")
        message = params.get("message", "")
        
        subject = "Follow-up: Your Application"
        body = f"""
        <html>
        <body>
            <h2>Application Follow-up</h2>
            <p>Dear {candidate_name},</p>
            <p>{message}</p>
            <br>
            <p>Best regards,</p>
            <p>The Recruiting Team</p>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_reminder(self, params: Dict) -> Dict[str, Any]:
        """Send interview reminder"""
        to_email = params.get("to_email")
        candidate_name = params.get("candidate_name", "Candidate")
        interview_time = params.get("interview_time", "")
        meeting_link = params.get("meeting_link", "")
        
        subject = "Reminder: Upcoming Interview"
        body = f"""
        <html>
        <body>
            <h2>Interview Reminder</h2>
            <p>Dear {candidate_name},</p>
            <p>This is a reminder about your upcoming interview:</p>
            <p><strong>Time:</strong> {interview_time}</p>
            {"<p><strong>Meeting Link:</strong> <a href='" + meeting_link + "'>" + meeting_link + "</a></p>" if meeting_link else ""}
            <p>Please join on time. We look forward to speaking with you!</p>
            <br>
            <p>Best regards,</p>
            <p>The Recruiting Team</p>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, body)


# Create tool instance
email_tool = EmailTool()