# MCP tool definitions
"""
MCP Tool Definitions and Configurations
Model Context Protocol standardized tool interface
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MCPToolDefinition(BaseModel):
    """Standard tool definition for MCP"""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    examples: Optional[List[Dict]] = None


# Tool Definitions for MCP

RESUME_PARSER_TOOL = MCPToolDefinition(
    name="resume_parser",
    description="Parses resume files (PDF, DOCX) and extracts structured candidate information",
    parameters={
        "file_path": {
            "type": "string",
            "description": "Path to the resume file",
            "required": True
        }
    },
    returns={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "phone": {"type": "string"},
            "skills": {"type": "array", "items": {"type": "string"}},
            "experience_years": {"type": "number"},
            "education": {"type": "array"},
            "resume_text": {"type": "string"}
        }
    },
    examples=[
        {
            "input": {"file_path": "/uploads/resume.pdf"},
            "output": {
                "name": "John Doe",
                "email": "john@example.com",
                "skills": ["Python", "Machine Learning"],
                "experience_years": 5
            }
        }
    ]
)


DATABASE_TOOL = MCPToolDefinition(
    name="database",
    description="Performs database operations on MongoDB collections",
    parameters={
        "action": {
            "type": "string",
            "enum": ["insert", "find", "find_one", "update", "delete", "count"],
            "required": True
        },
        "collection": {
            "type": "string",
            "description": "Collection name (candidates, jobs, interviews)",
            "required": True
        },
        "data": {
            "type": "object",
            "description": "Data to insert or update",
            "required": False
        },
        "query": {
            "type": "object",
            "description": "Query filter",
            "required": False
        }
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "documents": {"type": "array"},
            "inserted_id": {"type": "string"},
            "modified_count": {"type": "integer"}
        }
    },
    examples=[
        {
            "input": {
                "action": "find",
                "collection": "candidates",
                "query": {"status": "pending"}
            },
            "output": {
                "success": True,
                "documents": [],
                "count": 0
            }
        }
    ]
)


VECTOR_SEARCH_TOOL = MCPToolDefinition(
    name="vector_search",
    description="Performs semantic search using vector embeddings and RAG",
    parameters={
        "action": {
            "type": "string",
            "enum": ["add_candidate", "add_job", "search_candidates", "match_jobs"],
            "required": True
        },
        "candidate_id": {"type": "string", "required": False},
        "job_id": {"type": "string", "required": False},
        "text": {"type": "string", "required": False},
        "skills": {"type": "array", "items": {"type": "string"}, "required": False},
        "query": {"type": "string", "required": False},
        "k": {"type": "integer", "default": 5, "required": False}
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "results": {"type": "array"},
            "matched_jobs": {"type": "array"}
        }
    },
    examples=[
        {
            "input": {
                "action": "match_jobs",
                "candidate_text": "Python developer with 5 years experience",
                "skills": ["Python", "FastAPI"],
                "k": 5
            },
            "output": {
                "success": True,
                "matched_jobs": [
                    {"job_id": "JOB-001", "match_score": 0.85}
                ]
            }
        }
    ]
)


EMAIL_TOOL = MCPToolDefinition(
    name="email",
    description="Sends emails to candidates and recruiters",
    parameters={
        "action": {
            "type": "string",
            "enum": [
                "send_confirmation",
                "send_interview_invitation",
                "send_rejection",
                "send_follow_up",
                "send_reminder"
            ],
            "required": True
        },
        "to_email": {"type": "string", "required": True},
        "candidate_name": {"type": "string", "required": False},
        "job_title": {"type": "string", "required": False},
        "interview_time": {"type": "string", "required": False},
        "meeting_link": {"type": "string", "required": False},
        "message": {"type": "string", "required": False}
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "to": {"type": "string"}
        }
    },
    examples=[
        {
            "input": {
                "action": "send_confirmation",
                "to_email": "candidate@example.com",
                "candidate_name": "John Doe"
            },
            "output": {
                "success": True,
                "message": "Email sent",
                "to": "candidate@example.com"
            }
        }
    ]
)


CALENDAR_TOOL = MCPToolDefinition(
    name="calendar",
    description="Manages calendar operations and interview scheduling",
    parameters={
        "action": {
            "type": "string",
            "enum": [
                "get_available_slots",
                "book_slot",
                "check_availability",
                "cancel_booking"
            ],
            "required": True
        },
        "start_date": {"type": "string", "format": "date-time", "required": False},
        "days_ahead": {"type": "integer", "default": 5, "required": False},
        "duration_minutes": {"type": "integer", "default": 60, "required": False},
        "start_time": {"type": "string", "format": "date-time", "required": False},
        "candidate_email": {"type": "string", "required": False},
        "recruiter_email": {"type": "string", "required": False},
        "title": {"type": "string", "required": False},
        "booking_id": {"type": "string", "required": False}
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "available_slots": {"type": "array"},
            "booking_id": {"type": "string"},
            "meeting_link": {"type": "string"}
        }
    },
    examples=[
        {
            "input": {
                "action": "get_available_slots",
                "days_ahead": 7
            },
            "output": {
                "success": True,
                "available_slots": [
                    {
                        "start_time": "2025-10-03T10:00:00",
                        "end_time": "2025-10-03T11:00:00",
                        "available": True
                    }
                ]
            }
        }
    ]
)


# Tool Registry
MCP_TOOL_REGISTRY = {
    "resume_parser": RESUME_PARSER_TOOL,
    "database": DATABASE_TOOL,
    "vector_search": VECTOR_SEARCH_TOOL,
    "email": EMAIL_TOOL,
    "calendar": CALENDAR_TOOL
}


def get_tool_definition(tool_name: str) -> Optional[MCPToolDefinition]:
    """Get tool definition by name"""
    return MCP_TOOL_REGISTRY.get(tool_name)


def get_all_tool_definitions() -> Dict[str, MCPToolDefinition]:
    """Get all tool definitions"""
    return MCP_TOOL_REGISTRY


def validate_tool_parameters(tool_name: str, parameters: Dict[str, Any]) -> bool:
    """Validate parameters against tool definition"""
    tool_def = get_tool_definition(tool_name)
    if not tool_def:
        return False
    
    # Check required parameters
    for param_name, param_def in tool_def.parameters.items():
        if param_def.get("required") and param_name not in parameters:
            return False
    
    return True


def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """Get OpenAPI-compatible schema for a tool"""
    tool_def = get_tool_definition(tool_name)
    if not tool_def:
        return {}
    
    return {
        "name": tool_def.name,
        "description": tool_def.description,
        "parameters": {
            "type": "object",
            "properties": tool_def.parameters,
            "required": [
                k for k, v in tool_def.parameters.items()
                if v.get("required", False)
            ]
        },
        "returns": tool_def.returns
    }