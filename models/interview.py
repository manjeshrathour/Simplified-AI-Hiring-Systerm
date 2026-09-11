# models/interview.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

# This is a helper class for ObjectId handling. No changes needed here.
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# This is your main internal data model. No changes needed here.
class Interview(BaseModel):
    """Interview data model"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    candidate_id: str
    job_id: str
    recruiter_id: Optional[str] = None
    scheduled_time: datetime
    duration_minutes: int = 60
    interview_type: str = "technical"
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    status: str = "scheduled"
    notes: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reminder_sent: bool = False
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# These models for creating/updating data can remain as they are.
class InterviewCreate(BaseModel):
    """Schema for creating an interview"""
    candidate_id: str
    job_id: str
    scheduled_time: datetime
    duration_minutes: int = 60
    interview_type: str = "technical"
    meeting_link: Optional[str] = None
    location: Optional[str] = None

class InterviewUpdate(BaseModel):
    """Schema for updating an interview"""
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    feedback: Optional[str] = None


### FIX: This is the corrected response model ###
# It is now flexible enough to handle both human-scheduled and AI interviews.
class InterviewResponse(BaseModel):
    """Response model for interview"""
    id: str = Field(alias="_id")
    candidate_id: str
    job_id: str
    status: str
    meeting_link: Optional[str] = None
    created_at: datetime
    
    # These fields are now OPTIONAL, as they won't exist for pending AI interviews
    scheduled_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    interview_type: Optional[str] = None
    
    # These fields are OPTIONAL and will be populated after an AI interview is complete
    evaluation: Optional[Dict] = None
    interview_score: Optional[int] = None

    class Config:
        populate_by_name = True # Allows using alias="_id"
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}