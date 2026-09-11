# Compliance & Diversity Agent
from crewai import Agent
from tools.database_tool import database_tool
from llm.groq_client import groq_client
from utils.logger import log
from langchain_groq import ChatGroq
from config.settings import settings
from typing import Dict, List
from datetime import datetime


class ComplianceAgent:
    """Agent responsible for ensuring compliance and diversity"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL,
            temperature=0.2
        )
        
        self.agent = Agent(
            role="Compliance and Diversity Officer",
            goal="Ensure fair, unbiased, and compliant recruitment practices",
            backstory="""You are a compliance expert focused on ensuring ethical AI-powered 
            recruitment. You monitor for potential bias, ensure equal opportunity, maintain 
            audit logs, and verify that the recruitment process complies with employment laws 
            and diversity standards. You protect both candidates and the organization.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[database_tool]
        )
    
    def scan_for_bias(self, candidate_email: str) -> Dict:
        """Scan candidate profile for potential bias markers
        
        Args:
            candidate_email: Candidate's email
            
        Returns:
            Bias scan results
        """
        try:
            log.info(f"Scanning for bias: {candidate_email}")
            
            # Get candidate data
            candidate_result = database_tool._run(
                action="find_one",
                collection="candidates",
                query={"email": candidate_email}
            )
            
            candidate = candidate_result.get("document")
            if not candidate:
                return {"success": False, "error": "Candidate not found"}
            
            resume_text = candidate.get("resume_text", "")
            
            # Use LLM to detect potential bias indicators
            prompt = f"""Analyze this resume for potential bias markers that should NOT influence 
hiring decisions. Look for mentions of:
- Gender or gender identity
- Age or graduation years that reveal age
- Ethnicity, race, or nationality (unless directly relevant to job)
- Religious affiliations
- Marital status or family situation
- Physical characteristics or disabilities (unless job-relevant accommodations)
- Personal photos or descriptions

Resume excerpt:
{resume_text[:1000]}

Return JSON with:
- has_bias_markers: boolean
- detected_markers: list of found markers
- recommendations: suggestions to ensure fair evaluation
- risk_level: low/medium/high
"""
            
            scan_result = groq_client.extract_json(prompt)
            
            # Log compliance check
            compliance_log = {
                "candidate_id": str(candidate["_id"]),
                "candidate_email": candidate_email,
                "scan_type": "bias_detection",
                "timestamp": datetime.utcnow(),
                "has_bias_markers": scan_result.get("has_bias_markers", False),
                "detected_markers": scan_result.get("detected_markers", []),
                "risk_level": scan_result.get("risk_level", "low"),
                "recommendations": scan_result.get("recommendations", [])
            }
            
            # Save to compliance log
            database_tool._run(
                action="insert",
                collection="compliance_logs",
                data=compliance_log
            )
            
            log.info(f"Bias scan completed for {candidate_email}: {scan_result.get('risk_level', 'low')} risk")
            
            return {
                "success": True,
                "candidate_email": candidate_email,
                "scan_result": scan_result
            }
            
        except Exception as e:
            log.error(f"Error in bias scan: {e}")
            return {"success": False, "error": str(e)}
    
    def audit_selection_process(self, job_id: str) -> Dict:
        """Audit the candidate selection process for a job
        
        Args:
            job_id: Job ID
            
        Returns:
            Audit results
        """
        try:
            log.info(f"Auditing selection process for job: {job_id}")
            
            # Get all candidates for this job
            candidates_result = database_tool._run(
                action="find",
                collection="candidates",
                query={"matched_jobs": job_id}
            )
            
            candidates = candidates_result.get("documents", [])
            
            if not candidates:
                return {
                    "success": True,
                    "message": "No candidates found for this job",
                    "audit_passed": True
                }
            
            # Analyze diversity metrics
            total_candidates = len(candidates)
            shortlisted = [c for c in candidates if c.get("status") == "shortlisted"]
            rejected = [c for c in candidates if c.get("status") == "rejected"]
            
            # Check score distribution
            scores = [c.get("score", 0) for c in candidates if c.get("score")]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Create audit report
            audit_report = {
                "job_id": job_id,
                "timestamp": datetime.utcnow(),
                "total_candidates": total_candidates,
                "shortlisted_count": len(shortlisted),
                "rejected_count": len(rejected),
                "average_score": avg_score,
                "score_range": {
                    "min": min(scores) if scores else 0,
                    "max": max(scores) if scores else 0
                },
                "audit_passed": True,
                "notes": []
            }
            
            # Check for concerning patterns
            if shortlisted and avg_score > 0:
                shortlisted_avg = sum(c.get("score", 0) for c in shortlisted) / len(shortlisted)
                if shortlisted_avg < avg_score * 0.8:
                    audit_report["notes"].append("Warning: Shortlisted candidates have lower average scores than overall pool")
            
            # Save audit report
            database_tool._run(
                action="insert",
                collection="audit_logs",
                data=audit_report
            )
            
            log.info(f"Audit completed for job {job_id}")
            
            return {
                "success": True,
                "audit_report": audit_report
            }
            
        except Exception as e:
            log.error(f"Error in audit: {e}")
            return {"success": False, "error": str(e)}
    
    def log_action(self, action_type: str, details: Dict) -> Dict:
        """Log a compliance-relevant action
        
        Args:
            action_type: Type of action
            details: Action details
            
        Returns:
            Logging result
        """
        try:
            log_entry = {
                "action_type": action_type,
                "timestamp": datetime.utcnow(),
                "details": details
            }
            
            result = database_tool._run(
                action="insert",
                collection="compliance_logs",
                data=log_entry
            )
            
            return result
            
        except Exception as e:
            log.error(f"Error logging action: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_compliance_report(self, start_date: str = None, end_date: str = None) -> Dict:
        """Generate compliance report for a time period
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            Compliance report
        """
        try:
            query = {}
            if start_date:
                query["timestamp"] = {"$gte": datetime.fromisoformat(start_date)}
            if end_date:
                if "timestamp" in query:
                    query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)
                else:
                    query["timestamp"] = {"$lte": datetime.fromisoformat(end_date)}
            
            # Get compliance logs
            logs_result = database_tool._run(
                action="find",
                collection="compliance_logs",
                query=query
            )
            
            logs = logs_result.get("documents", [])
            
            # Generate summary
            report = {
                "period": {
                    "start": start_date or "beginning",
                    "end": end_date or "now"
                },
                "total_scans": len([l for l in logs if l.get("scan_type") == "bias_detection"]),
                "high_risk_findings": len([l for l in logs if l.get("risk_level") == "high"]),
                "medium_risk_findings": len([l for l in logs if l.get("risk_level") == "medium"]),
                "recommendations": [],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Add recommendations if high-risk findings exist
            if report["high_risk_findings"] > 0:
                report["recommendations"].append("Review high-risk candidates manually")
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            log.error(f"Error generating compliance report: {e}")
            return {"success": False, "error": str(e)}


# Create agent instance
compliance_agent = ComplianceAgent()