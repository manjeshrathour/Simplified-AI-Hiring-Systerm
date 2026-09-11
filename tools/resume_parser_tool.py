# Tool: Parse resume files
from crewai.tools import BaseTool
from typing import Dict, Any
import PyPDF2
import docx
import re
from pathlib import Path
from utils.logger import log
from llm.groq_client import groq_client


class ResumeParserTool(BaseTool):
    name: str = "Resume Parser"
    description: str = """Parses resume files (PDF, DOCX) and extracts structured information including:
    - Name, email, phone
    - Skills
    - Work experience
    - Education
    - Years of experience
    """
    
    def _run(self, file_path: str) -> Dict[str, Any]:
        """Parse resume file and extract information"""
        try:
            # Extract text from file
            text = self._extract_text(file_path)
            
            if not text:
                return {"error": "Could not extract text from resume"}
            
            # Use LLM to parse resume
            parsed_data = self._parse_with_llm(text)
            
            # Extract basic contact info with regex
            email = self._extract_email(text)
            phone = self._extract_phone(text)
            github_url = self._extract_github_url(text)
            
            # Combine results
            result = {
                "resume_text": text,
                "email": email or parsed_data.get("email", ""),
                "phone": phone or parsed_data.get("phone", ""),
                "github_url": github_url or parsed_data.get("github_url", ""),
                "name": parsed_data.get("name", ""),
                "skills": parsed_data.get("skills", []),
                "experience_years": parsed_data.get("experience_years", 0),
                "education": parsed_data.get("education", []),
                "previous_roles": parsed_data.get("previous_roles", [])
            }
            
            log.info(f"Successfully parsed resume: {result.get('name', 'Unknown')}")
            return result
            
        except Exception as e:
            log.error(f"Error parsing resume: {e}")
            return {"error": str(e)}
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            log.error(f"Error extracting text: {e}")
            return ""
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _extract_email(self, text: str) -> str:
        """Extract email using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number using regex"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        matches = re.findall(phone_pattern, text)
        return matches[0] if matches else ""
    
    def _extract_github_url(self, text: str) -> str:
        """Extract GitHub profile URL using regex"""
        # Pattern matches: github.com/username or https://github.com/username
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)(?:/)?'
        matches = re.findall(github_pattern, text, re.IGNORECASE)
        
        if matches:
            # Return full URL format
            username = matches[0]
            return f"https://github.com/{username}"
        return ""
    
    def _parse_with_llm(self, text: str) -> Dict[str, Any]:
        """Use LLM to parse resume text"""
        prompt = f"""Parse the following resume and extract structured information. Return a JSON object with these fields:
- name: Full name of the candidate
- skills: List of technical skills
- experience_years: Total years of professional experience (as a number)
- education: List of education entries with degree, institution, and year
- previous_roles: List of previous job roles with title, company, and duration

Resume:
{text}

Return ONLY valid JSON, no other text."""

        try:
            result = groq_client.extract_json(prompt)
            return result
        except Exception as e:
            log.error(f"LLM parsing error: {e}")
            return {}


# Create tool instance
resume_parser_tool = ResumeParserTool()