# agents/matching_agent.py

from crewai import Agent
from langchain_groq import ChatGroq
from config.settings import settings
from tools.database_tool import database_tool
from utils.logger import log
import json
import re

class MatchingAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile",
            temperature=0.2
        )
        self.agent = Agent(
            role="Candidate-Job Matching Specialist",
            goal="Accurately assess a candidate's resume against job postings and provide constructive feedback.",
            backstory="You are an expert AI recruiter. You not only find the best talent but also provide career-path guidance by identifying skill gaps in candidates.",
            verbose=True,
            llm=self.llm,
        )

    def get_match_and_tips(self, candidate_email: str, applied_job_id: str) -> dict:
        """
        Matches a candidate against a SPECIFIC job and generates improvement tips.
        Used for the Google Form application workflow.
        """
        log.info(f"Matching agent generating specific report for {candidate_email} against {applied_job_id}")
        
        try:
            # 1. Fetch Data
            candidate_result = database_tool._run("find_one", "candidates", query={"email": candidate_email})
            candidate = candidate_result.get("document")
            job = database_tool.get_job_by_id(applied_job_id)

            if not candidate or not job:
                return {"success": False, "error": "Candidate or Job not found."}

            # 2. Construct Prompt
            prompt = f"""
            As an expert recruiter, compare the candidate's profile to the applied job requirements.
            
            **Job Title:** {job.get('title')}
            **Job Requirements:** {', '.join(job.get('required_skills', []))}
            **Job Description:** {job.get('description', '')[:500]}

            **Candidate Skills:** {', '.join(candidate.get('skills', []))}
            **Candidate Experience:** {candidate.get('experience_years', 0)} years
            **Resume Text:** {candidate.get('resume_text', '')[:1500]}

            **Your Task:**
            1. Calculate a match score (0-100).
            2. Decide if they are shortlisted (is_shortlisted = true if score >= 70).
            3. If the score is below 70, provide 3 VERY SPECIFIC improvement tips as bullet points. These should be technical skills or certifications they are missing for THIS specific role.
            4. If the score is above 70, provide 3 strengths they demonstrated.

            **Output Format (ONLY JSON):**
            {{
              "score": 65,
              "is_shortlisted": false,
              "reasoning": "Brief explanation of the score.",
              "tips": [
                "Tip 1: Learn...",
                "Tip 2: Gain experience in...",
                "Tip 3: Consider getting certified in..."
              ]
            }}
            """

            # 3. Get LLM Response
            response = self.llm.invoke(prompt).content
            
            # Clean and parse JSON
            cleaned_response = re.sub(r"```json|```", "", response).strip()
            result = json.loads(cleaned_response)

            # 4. Save the score back to the candidate record
            database_tool.update_candidate_score(
                email=candidate_email,
                score=result.get("score", 0),
                matched_jobs=[applied_job_id]
            )

            return {
                "success": True,
                "score": result.get("score", 0),
                "is_shortlisted": result.get("is_shortlisted", False),
                "tips": result.get("tips", []),
                "reasoning": result.get("reasoning", "")
            }

        except Exception as e:
            log.error(f"Error in get_match_and_tips: {e}")
            return {"success": False, "error": str(e)}

    def match_candidate_to_jobs(self, candidate_email: str) -> dict:
        """
        Original method: Fetches a candidate and matches against ALL jobs.
        """
        log.info(f"Matching agent starting general process for candidate: {candidate_email}")
        
        try:
            candidate_result = database_tool._run("find_one", "candidates", query={"email": candidate_email})
            candidate = candidate_result.get("document")
            if not candidate: return {"success": False, "error": "Candidate not found."}

            all_jobs = database_tool.get_active_jobs()
            if not all_jobs: return {"success": False, "error": "No jobs found."}

            candidate_summary = f"Skills: {', '.join(candidate.get('skills', []))}\nResume: {candidate.get('resume_text', '')[:1000]}"
            jobs_summary = json.dumps([{"job_id": j["job_id"], "title": j["title"], "skills": j.get("required_skills", [])} for j in all_jobs])

            prompt = f"""
            Evaluate the candidate against these jobs. 
            Candidate: {candidate_summary}
            Jobs: {jobs_summary}
            Return ONLY JSON: {{"best_match_job_id": "ID", "best_match_score": 85, "reasoning": "...", "all_scores": []}}
            """
            
            response_text = self.llm.invoke(prompt).content
            cleaned_response = re.sub(r"```json|```", "", response_text).strip()
            match_data = json.loads(cleaned_response)

            top_score = match_data.get("best_match_score", 0)
            best_job_id = match_data.get("best_match_job_id")
            
            database_tool.update_candidate_score(
                email=candidate_email,
                score=top_score,
                matched_jobs=[best_job_id] if best_job_id else []
            )

            return {
                "success": True,
                "overall_score": top_score,
                "matched_jobs": [{"job_id": best_job_id, "score": top_score}] if best_job_id else []
            }

        except Exception as e:
            log.error(f"Error in general matching: {e}")
            return {"success": False, "error": str(e)}

# Create a singleton instance
matching_agent = MatchingAgent()
