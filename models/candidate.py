from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId


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


class Candidate(BaseModel):
    """Candidate data model"""
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_text: str
    skills: List[str] = []
    experience_years: Optional[float] = None
    education: List[Dict] = []
    previous_roles: List[Dict] = []
    score: Optional[float] = None
    matched_jobs: List[str] = []
    status: str = "pending"  # pending, reviewed, shortlisted, rejected, hired
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resume_file_path: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CandidateCreate(BaseModel):
    """Schema for creating a candidate"""
    name: str
    email: EmailStr
    phone: Optional[str] = None


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate"""
    name: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    status: Optional[str] = None
    score: Optional[float] = None


class CandidateResponse(BaseModel):
    """Response model for candidate"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[float] = None
    score: Optional[float] = None
    status: str
    uploaded_at: datetime
    matched_jobs: List[str] = []
    
    # Enrichment fields (GitHub + Public Presence)
    github_url: Optional[str] = None
    github_analysis: Optional[Dict] = None
    enriched_profile: Optional[str] = None
    public_presence: Optional[str] = None
    
    class Config:
        # Allow extra fields that might exist in DB but not defined here
        extra = 'allow'