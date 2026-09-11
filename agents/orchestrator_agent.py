# agents/orchestrator_agent.py

from crewai import Agent
from utils.logger import log
from langchain_groq import ChatGroq
from config.settings import settings
from typing import Dict
from bson import ObjectId
from datetime import datetime

# Import other agents and tools
from agents.resume_parsing_agent import resume_parsing_agent
from agents.matching_agent import matching_agent
from agents.communication_agent import communication_agent
from agents.compliance_agent import compliance_agent
from agents.github_agent import github_agent
from agents.public_search_agent import public_search_agent
from agents.synthesizer_agent import synthesizer_agent
from tools.database_tool import database_tool


class OrchestratorAgent:
    """Hierarchical orchestrator that coordinates all other agents"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.5
        )
        self.agent = Agent(
            role="Recruitment Process Orchestrator",
            goal="Coordinate the entire recruitment workflow efficiently and ensure all steps are completed correctly",
            backstory="You are the master coordinator of the AI recruitment system. You oversee the entire hiring process from resume submission to interview scheduling. You delegate tasks to specialized agents and ensure smooth workflow execution.",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
        
        self.resume_agent = resume_parsing_agent
        self.matching_agent = matching_agent
        self.communication_agent = communication_agent
        self.compliance_agent = compliance_agent
    
    def process_candidate_application(self, resume_file_path: str) -> Dict:
        """Complete end-to-end processing of a candidate application"""
        try:
            log.info(f"Orchestrator: Starting candidate application processing for {resume_file_path}")
            
            workflow_result = {"success": True, "steps": [], "errors": [], "decision": None}
            
            parse_result = self.resume_agent.process_resume(resume_file_path)
            if not parse_result.get("success"):
                raise ValueError(f"Resume parsing failed: {parse_result.get('error')}")
            
            candidate_email = parse_result["candidate_email"]
            
            # NEW: Enrich candidate profile with GitHub + public presence
            log.info(f"Orchestrator: Enriching candidate profile for {candidate_email}")
            enrichment_result = self.enrich_candidate_profile(candidate_email)
            
            if enrichment_result.get("success"):
                log.info(f"Enrichment successful. GitHub: {enrichment_result.get('has_github')}, Public: {enrichment_result.get('has_public_presence')}")
            else:
                log.warning(f"Enrichment failed, proceeding without: {enrichment_result.get('error', 'Unknown')}")
            
            self.communication_agent.send_application_confirmation(candidate_email)
            self.compliance_agent.scan_for_bias(candidate_email)
            match_result = self.matching_agent.match_candidate_to_jobs(candidate_email)
            
            overall_score = match_result.get("overall_score", 0)
            matched_jobs = match_result.get("matched_jobs", [])
            
            if overall_score >= 50 and matched_jobs: # Using a threshold of 50
                workflow_result["decision"] = "shortlisted_for_ai_interview"
                top_job_id = matched_jobs[0]["job_id"]
                
                log.info(f"AUTO-SHORTLIST: Score {overall_score} >= 50. Scheduling AI interview for job {top_job_id}")
                
                shortlist_result = self.process_candidate_shortlisting(
                    candidate_email=candidate_email,
                    job_id=top_job_id
                )
                
                workflow_result["message"] = f"SHORTLISTED! Score: {overall_score:.2f}. AI interview link sent."
                workflow_result["ai_interview_link"] = shortlist_result.get("ai_interview_link", "")
            else:
                workflow_result["decision"] = "rejected"
                log.info(f"AUTO-REJECT: Score {overall_score} < 50. Sending rejection email")
                job_id_for_rejection = matched_jobs[0]["job_id"] if matched_jobs else "GENERAL"
                self.reject_candidate(candidate_email, job_id_for_rejection)
                workflow_result["message"] = f"REJECTED. Score: {overall_score:.2f}. Rejection email sent."
            
            return workflow_result
            
        except Exception as e:
            log.error(f"Orchestrator error in application processing: {e}")
            return {"success": False, "error": str(e)}
    
    def enrich_candidate_profile(self, candidate_email: str, job_id: str = None) -> Dict:
        """
        Enriches a candidate's profile with GitHub analysis and public presence research.
        This creates a comprehensive "Enriched Profile" by:
        1. Analyzing GitHub repositories (if URL exists)
        2. Searching for public contributions (blogs, articles, talks)
        3. Synthesizing all data into a comprehensive professional summary
        
        Args:
            candidate_email: Candidate's email
            job_id: Optional job ID for matching analysis
            
        Returns:
            Enrichment results dictionary
        """
        try:
            log.info(f"Orchestrator: Starting enrichment for candidate {candidate_email}")
            
            # Get candidate data
            candidate_result = database_tool._run(
                action="find_one",
                collection="candidates",
                query={"email": candidate_email}
            )
            
            candidate = candidate_result.get("document")
            if not candidate:
                return {"success": False, "error": "Candidate not found"}
            
            candidate_name = candidate.get("name", "Candidate")
            github_url = candidate.get("github_url", "")
            resume_text = candidate.get("resume_text", "")
            
            # Get job requirements if job_id provided
            job_requirements = None
            if job_id:
                job = database_tool.get_job_by_id(job_id)
                if job:
                    job_requirements = {
                        "title": job.get("title", ""),
                        "required_skills": job.get("required_skills", [])
                    }
            
            # Step 1: GitHub Analysis (if URL exists)
            github_analysis = None
            if github_url and github_url.strip():
                log.info(f"Orchestrator: Running GitHub analysis for {candidate_email}")
                github_result = github_agent.analyze_profile(github_url, job_requirements)
                
                if github_result.get("success"):
                    github_analysis = github_result
                    log.info(f"GitHub analysis complete: {github_result.get('professional_summary', 'N/A')[:100]}")
                else:
                    log.warning(f"GitHub analysis failed: {github_result.get('message', 'Unknown error')}")
            else:
                log.info(f"No GitHub URL found for {candidate_email}, skipping GitHub analysis")
            
            # Step 2: Public Presence Search
            log.info(f"Orchestrator: Searching for public contributions for {candidate_name}")
            public_presence = public_search_agent.search_for_contributions(candidate_name)
            
            # Step 3: Synthesize all data
            log.info(f"Orchestrator: Synthesizing enriched profile for {candidate_email}")
            
            github_report = "No GitHub profile provided."
            if github_analysis:
                # Format GitHub analysis as readable text
                best_repo = github_analysis.get("best_fit_repo", {})
                github_report = f"""Primary Languages: {', '.join(github_analysis.get('primary_languages', []))}
Total Repositories: {github_analysis.get('total_repos', 0)}
Portfolio Quality: {github_analysis.get('portfolio_quality', 'unknown')}
Total Stars: {github_analysis.get('total_stars', 0)}
Best Fit Repository: {best_repo.get('name', 'N/A')} ({best_repo.get('url', 'N/A')})
Reason: {best_repo.get('reason', 'N/A')}
Professional Summary: {github_analysis.get('professional_summary', 'N/A')}"""
            
            enriched_profile = synthesizer_agent.synthesize_reports(
                resume_text=resume_text[:1000],
                github_report=github_report,
                public_presence_report=public_presence
            )
            
            # Step 4: Save enriched data back to candidate record
            update_data = {
                "enriched_profile": enriched_profile,
                "public_presence": public_presence,
                "updated_at": datetime.utcnow()
            }
            
            if github_analysis:
                update_data["github_analysis"] = github_analysis
            
            database_tool._run(
                action="update",
                collection="candidates",
                query={"email": candidate_email},
                data=update_data
            )
            
            log.info(f"Orchestrator: Enrichment complete for {candidate_email}")
            
            return {
                "success": True,
                "enriched_profile": enriched_profile,
                "has_github": github_analysis is not None,
                "has_public_presence": bool(public_presence and "No significant" not in public_presence)
            }
            
        except Exception as e:
            log.error(f"Orchestrator error in enrichment: {e}")
            return {"success": False, "error": str(e)}
    
    def process_candidate_shortlisting(self, candidate_email: str, job_id: str) -> Dict:
        """
        Processes shortlisting by creating an AI interview record with the CORRECT status.
        """
        try:
            log.info(f"Orchestrator: Processing AI interview shortlisting for {candidate_email} for job {job_id}")
            
            unique_interview_id = str(ObjectId())
            base_url = settings.FRONTEND_URL.strip('/')
            ai_interview_link = f"{base_url}/interview.html?interview_id={unique_interview_id}"

            ### FIX: Using the generic _run method to save the interview ###
            # This ensures that we have full control over the data being inserted and
            # that the 'status' is correctly set to 'pending_ai_interview'.
            database_tool._run(
                action="insert",
                collection="interviews",
                data={
                    "_id": unique_interview_id,
                    "job_id": job_id,
                    "candidate_id": candidate_email,
                    "status": "pending_ai_interview", # The correct status
                    "meeting_link": ai_interview_link,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )
            log.info(f"Successfully created AI interview record {unique_interview_id} in database.")

            self.communication_agent.send_interview_invitation(
                candidate_email=candidate_email,
                job_id=job_id,
                interview_time="at your convenience within the next 48 hours",
                meeting_link=ai_interview_link
            )
            
            return {
                "success": True,
                "message": "AI interview scheduled and invitation sent.",
                "ai_interview_link": ai_interview_link
            }
            
        except Exception as e:
            log.error(f"Orchestrator error in AI interview shortlisting: {e}")
            return {"success": False, "error": str(e)}
    
    def process_post_interview_decision(self, interview_id: str):
        """
        Makes a final hiring decision after an AI interview is complete.
        """
        try:
            log.info(f"Orchestrator: Processing post-interview decision for {interview_id}")
            interview = database_tool.get_interview_by_id(interview_id)
            if not interview:
                raise ValueError("Interview not found")

            score = interview.get("interview_score", 0)
            candidate_email = interview["candidate_id"]
            job_id = interview["job_id"]

            if score >= 70: # Decision threshold
                log.info(f"HIRE DECISION: Score {score} >= 70. Sending offer/next steps email.")
                self.communication_agent.send_rejection_notice(candidate_email, job_id, is_rejection=False)
            else:
                log.info(f"REJECT DECISION: Score {score} < 70. Sending rejection email.")
                self.communication_agent.send_rejection_notice(candidate_email, job_id, is_rejection=True)

            return {"success": True, "decision": "hire" if score >= 70 else "reject"}
            
        except Exception as e:
            log.error(f"Orchestrator error in post-interview decision: {e}")
            return {"success": False, "error": str(e)}

    def reject_candidate(self, candidate_email: str, job_id: str) -> Dict:
        """Processes an immediate candidate rejection."""
        try:
            log.info(f"Orchestrator: Processing rejection for {candidate_email}")
            return self.communication_agent.send_rejection_notice(candidate_email, job_id)
        except Exception as e:
            log.error(f"Orchestrator error in rejection: {e}")
            return {"success": False, "error": str(e)}


# =====================================this is the new method to sync with the google form applications=========================================
    def process_job_application(self, resume_path: str, applied_job_id: str, full_name: str, email: str = None, profile_image_path: str = None) -> Dict:
        """
        NEW: Specifically handles applications coming from the Google Form 
        matched against a specific job selected by the candidate.
        """
        try:
            log.info(f"Orchestrator: Processing specific application for {full_name} to Job {applied_job_id}")

            # 1. Parse Resume
            parse_result = self.resume_agent.process_resume(resume_path)
            if not parse_result.get("success"):
                return {"success": False, "error": "Resume parsing failed"}

            # Use email from form if available, otherwise from resume
            candidate_email = email or parse_result.get("candidate_email")
            
            # Update candidate record with full name from form if it was missing
            database_tool._run(
                action="update",
                collection="candidates",
                query={"email": candidate_email},
                data={"name": full_name, "profile_image": profile_image_path}
            )

            # 2. Enrich Profile (GitHub + Public Search)
            self.enrich_candidate_profile(candidate_email, job_id=applied_job_id)

            # 3. Run Specific Match with Tips (Using the new Matching Agent method)
            match_result = self.matching_agent.get_match_and_tips(candidate_email, applied_job_id)
            
            if not match_result.get("success"):
                return {"success": False, "error": "Matching process failed"}

            score = match_result.get("score", 0)
            is_shortlisted = match_result.get("is_shortlisted", False)
            tips = match_result.get("tips", [])

            # 4. Handle Decision
            if is_shortlisted:
                log.info(f"Candidate {candidate_email} SHORTLISTED for {applied_job_id} with score {score}")
                
                # Create interview link and record
                shortlist_data = self.process_candidate_shortlisting(candidate_email, applied_job_id)
                
                # Note: You might want to update your communication_agent to mention 
                # the score even in the success email!
                return {
                    "success": True, 
                    "message": f"Shortlisted! Score: {score}", 
                    "applied_job_score": score
                }
            else:
                log.info(f"Candidate {candidate_email} REJECTED for {applied_job_id} with score {score}")
                
                # Send rejection with score and tips
                # Note: We call a specific rejection method that includes feedback
                self.communication_agent.send_rejection_notice(
                    candidate_email=candidate_email, 
                    job_id=applied_job_id,
                    score=score,
                    tips=tips
                )
                
                return {
                    "success": True, 
                    "message": f"Processed. Rejected with score: {score}", 
                    "applied_job_score": score
                }

        except Exception as e:
            log.error(f"Orchestrator error in job-specific application: {e}")
            return {"success": False, "error": str(e)}

# Create a singleton instance
orchestrator = OrchestratorAgent()