# Resume Parser Agent
from crewai import Agent
from tools.resume_parser_tool import resume_parser_tool
from tools.database_tool import database_tool
from tools.vector_search_tool import vector_search_tool
from llm.groq_client import groq_client
from utils.logger import log
from langchain_groq import ChatGroq
from config.settings import settings


class ResumeParsingAgent:
    """Agent responsible for parsing resumes and storing candidate data"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.3
        )
        
        self.agent = Agent(
            role="Resume Parser Specialist",
            goal="Parse resumes accurately and extract all relevant candidate information",
            backstory="""You are an expert at analyzing resumes and extracting structured 
            information. You understand various resume formats and can identify key details 
            like skills, experience, education, and contact information. You ensure data 
            quality and completeness.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[resume_parser_tool, database_tool, vector_search_tool]
        )
    
    def process_resume(self, file_path: str) -> dict:
        """Process a resume file and store candidate data
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Dictionary with processing results
        """
        try:
            log.info(f"Processing resume: {file_path}")
            
            # Parse resume
            parsed_data = resume_parser_tool._run(file_path)
            
            if "error" in parsed_data:
                log.error(f"Resume parsing failed: {parsed_data['error']}")
                return {"success": False, "error": parsed_data["error"]}
            
            # Prepare candidate data
            candidate_data = {
                "name": parsed_data.get("name", "Unknown"),
                "email": parsed_data.get("email", ""),
                "phone": parsed_data.get("phone", ""),
                "github_url": parsed_data.get("github_url", ""),
                "resume_text": parsed_data.get("resume_text", ""),
                "skills": parsed_data.get("skills", []),
                "experience_years": parsed_data.get("experience_years", 0),
                "education": parsed_data.get("education", []),
                "previous_roles": parsed_data.get("previous_roles", []),
                "resume_file_path": file_path,
                "score": None,
                "matched_jobs": []
            }
            
            # Save to database
            db_result = database_tool.save_candidate(candidate_data)
            
            if not db_result.get("success"):
                log.error(f"Failed to save candidate: {db_result.get('error')}")
                return {"success": False, "error": db_result.get("error")}
            
            candidate_id = db_result.get("inserted_id")
            
            # Add to vector store for semantic search
            vector_result = vector_search_tool._run(
                action="add_candidate",
                candidate_id=candidate_id,
                text=candidate_data["resume_text"],
                skills=candidate_data["skills"]
            )
            
            log.info(f"Resume processed successfully: {candidate_data['name']}")
            
            return {
                "success": True,
                "candidate_id": candidate_id,
                "candidate_name": candidate_data["name"],
                "candidate_email": candidate_data["email"],
                "skills": candidate_data["skills"],
                "experience_years": candidate_data["experience_years"]
            }
            
        except Exception as e:
            log.error(f"Error processing resume: {e}")
            return {"success": False, "error": str(e)}


# Create agent instance
resume_parsing_agent = ResumeParsingAgent()