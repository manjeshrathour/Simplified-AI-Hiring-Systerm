# agents/decision_agent.py

from agents.communication_agent import communication_agent
from tools.database_tool import database_tool
from utils.logger import log

class DecisionAgent:
    def process_post_interview_decision(self, interview_id: str):
        try:
            log.info(f"Decision Agent: Processing post-interview decision for {interview_id}")
            interview = database_tool.get_interview_by_id(interview_id)
            if not interview:
                raise ValueError("Interview not found for decision.")

            score = interview.get("interview_score", 0)
            candidate_email = interview["candidate_id"]
            job_id = interview["job_id"]

            if score >= 70:
                log.info(f"HIRE DECISION: Score {score} >= 70. Sending next steps email.")
                communication_agent.send_rejection_notice(candidate_email, job_id, is_rejection=False)
            else:
                log.info(f"REJECT DECISION: Score {score} < 70. Sending rejection email.")
                communication_agent.send_rejection_notice(candidate_email, job_id, is_rejection=True)

            return {"success": True}
        except Exception as e:
            log.error(f"Decision Agent error: {e}")
            return {"success": False, "error": str(e)}

decision_agent = DecisionAgent()