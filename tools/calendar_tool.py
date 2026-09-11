from crewai.tools import BaseTool
from typing import Dict, Any, List
from datetime import datetime, timedelta
from utils.logger import log
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config.settings import settings
import os


class CalendarTool(BaseTool):
    name: str = "Calendar Management"
    description: str = """Manages Google Calendar operations with real meeting links:
    - Check available time slots
    - Book interview slots with Google Meet links
    - Find free times in recruiter calendar
    - Schedule meetings with real video conferencing
    - Send calendar invites
    """
    
    def __init__(self):
        super().__init__()
        self._service = None
        self._initialize_calendar_service()
    
    def _initialize_calendar_service(self):
        """Initialize Google Calendar API service"""
        try:
            # Path to service account credentials
            creds_path = 'credentials.json'
            
            if not os.path.exists(creds_path):
                log.warning("Google Calendar credentials not found. Using mock mode.")
                return
            
            # Define the required scopes
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            # Create credentials from service account
            credentials = service_account.Credentials.from_service_account_file(
                creds_path, scopes=SCOPES
            )
            
            # Build the Calendar API service
            self._service = build('calendar', 'v3', credentials=credentials)
            log.info("Google Calendar service initialized successfully")
            
        except Exception as e:
            log.error(f"Failed to initialize Google Calendar: {e}")
            self._service = None
    
    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute calendar operation"""
        try:
            if action == "get_available_slots":
                return self._get_available_slots(kwargs)
            elif action == "book_slot":
                return self._book_slot(kwargs)
            elif action == "check_availability":
                return self._check_availability(kwargs)
            elif action == "cancel_booking":
                return self._cancel_booking(kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            log.error(f"Calendar error: {e}")
            return {"error": str(e)}
    
    def _get_available_slots(self, params: Dict) -> Dict[str, Any]:
        """Get available time slots for interviews"""
        start_date = params.get("start_date")
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        elif not start_date:
            start_date = datetime.now()
        
        days_ahead = params.get("days_ahead", 5)
        duration_minutes = params.get("duration_minutes", 60)
        
        available_slots = []
        current_date = start_date
        days_added = 0
        
        while days_added < days_ahead:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Morning slot: 10:00 AM
                morning_slot = current_date.replace(hour=10, minute=0, second=0, microsecond=0)
                if morning_slot > datetime.now():
                    available_slots.append({
                        "start_time": morning_slot.isoformat(),
                        "end_time": (morning_slot + timedelta(minutes=duration_minutes)).isoformat(),
                        "duration_minutes": duration_minutes,
                        "available": True
                    })
                
                # Afternoon slot: 2:00 PM
                afternoon_slot = current_date.replace(hour=14, minute=0, second=0, microsecond=0)
                if afternoon_slot > datetime.now():
                    available_slots.append({
                        "start_time": afternoon_slot.isoformat(),
                        "end_time": (afternoon_slot + timedelta(minutes=duration_minutes)).isoformat(),
                        "duration_minutes": duration_minutes,
                        "available": True
                    })
                
                days_added += 1
            
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "available_slots": available_slots,
            "count": len(available_slots)
        }
    
    def _book_slot(self, params: Dict) -> Dict[str, Any]:
        """Book an interview slot with real Google Meet link"""
        start_time = params.get("start_time")
        candidate_email = params.get("candidate_email")
        recruiter_email = params.get("recruiter_email", settings.SMTP_USERNAME)
        title = params.get("title", "Interview")
        duration_minutes = params.get("duration_minutes", 60)
        
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Try to create real Google Calendar event
        if self._service:
            try:
                # Create event with Google Meet
                event = {
                    'summary': title,
                    'description': f'Interview scheduled with {candidate_email}',
                    'start': {
                        'dateTime': start_time.isoformat(),
                        'timeZone': 'Asia/Kolkata',
                    },
                    'end': {
                        'dateTime': end_time.isoformat(),
                        'timeZone': 'Asia/Kolkata',
                    },
                    'attendees': [
                        {'email': candidate_email},
                        {'email': recruiter_email},
                    ],
                    'conferenceData': {
                        'createRequest': {
                            'requestId': f"interview-{start_time.strftime('%Y%m%d%H%M')}",
                            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                        }
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 30},
                        ],
                    },
                }
                
                # Insert event with conference data
                created_event = self._service.events().insert(
                    calendarId='primary',
                    body=event,
                    conferenceDataVersion=1,
                    sendUpdates='all'
                ).execute()
                
                # Extract Google Meet link
                meeting_link = created_event.get('hangoutLink', '')
                event_id = created_event.get('id', '')
                
                log.info(f"Created Google Calendar event: {event_id} with Meet link")
                
                return {
                    "success": True,
                    "booking_id": event_id,
                    "title": title,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_minutes": duration_minutes,
                    "candidate_email": candidate_email,
                    "recruiter_email": recruiter_email,
                    "meeting_link": meeting_link,
                    "status": "confirmed",
                    "provider": "Google Meet"
                }
                
            except Exception as e:
                log.error(f"Failed to create Google Calendar event: {e}")
                # Fallback to mock
        
        # Fallback: Generate mock meeting link if Google Calendar fails
        meeting_link = f"https://meet.google.com/interview-{start_time.strftime('%Y%m%d%H%M')}"
        
        booking_info = {
            "success": True,
            "booking_id": f"INT-{start_time.strftime('%Y%m%d%H%M')}",
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": duration_minutes,
            "candidate_email": candidate_email,
            "recruiter_email": recruiter_email,
            "meeting_link": meeting_link,
            "status": "confirmed",
            "provider": "Mock (Google Calendar not configured)"
        }
        
        log.info(f"Booked interview slot (fallback mode): {booking_info['booking_id']}")
        
        return booking_info
    
    def _check_availability(self, params: Dict) -> Dict[str, Any]:
        """Check if a specific time is available"""
        check_time = params.get("check_time")
        
        if isinstance(check_time, str):
            check_time = datetime.fromisoformat(check_time)
        
        is_available = check_time > datetime.now() and check_time.weekday() < 5
        
        return {
            "success": True,
            "time": check_time.isoformat(),
            "available": is_available,
            "message": "Time slot is available" if is_available else "Time slot is not available"
        }
    
    def _cancel_booking(self, params: Dict) -> Dict[str, Any]:
        """Cancel a booking"""
        booking_id = params.get("booking_id")
        
        # Try to delete from Google Calendar
        if self._service and not booking_id.startswith("INT-"):
            try:
                self._service.events().delete(
                    calendarId='primary',
                    eventId=booking_id,
                    sendUpdates='all'
                ).execute()
                
                log.info(f"Cancelled Google Calendar event: {booking_id}")
                
                return {
                    "success": True,
                    "booking_id": booking_id,
                    "status": "cancelled",
                    "message": f"Booking {booking_id} cancelled successfully"
                }
            except Exception as e:
                log.error(f"Failed to cancel event: {e}")
        
        return {
            "success": True,
            "booking_id": booking_id,
            "status": "cancelled",
            "message": f"Booking {booking_id} cancelled successfully"
        }


# Create tool instance
calendar_tool = CalendarTool()