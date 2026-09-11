# models/job_posting.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# This is a helper class for ObjectId handling in Pydantic V1
# You can keep it as is.
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


# This model seems to be your ideal internal representation. No changes needed here.
class JobPosting(BaseModel):
    """Job posting data model"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    job_id: str
    title: str
    description: str
    requirements: List[str] = []
    required_skills: List[str] = []
    experience_required: Optional[float] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    department: Optional[str] = None
    employment_type: str = "full-time"
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    recruiter_id: Optional[str] = None
    matched_candidates: List[str] = []
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# These models are for creating/updating data. They can remain as they are.
class JobPostingCreate(BaseModel):
    """Schema for creating a job posting"""
    job_id: str
    title: str
    description: str
    requirements: List[str] = []
    required_skills: List[str] = []
    experience_required: Optional[float] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    department: Optional[str] = None
    employment_type: str = "full-time"

class JobPostingUpdate(BaseModel):
    """Schema for updating a job posting"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    status: Optional[str] = None


### FIX: This is the corrected response model ###
# It now accurately reflects the fields present in your MongoDB 'jobs' collection.
class JobPostingResponse(BaseModel):
    """Response model for job posting"""
    id: str = Field(alias="_id") # The response will have 'id', mapped from '_id'
    job_id: str
    title: str
    description: str
    location: str
    employment_type: str      # This field exists in your DB
    required_skills: List[str] = []
    department: Optional[str] = None
    salary_range: Optional[str] = None
    # 'requirements' also exists if you want to send it to the frontend
    requirements: List[str] = []

    class Config:
        populate_by_name = True # Allows using alias="_id"
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}