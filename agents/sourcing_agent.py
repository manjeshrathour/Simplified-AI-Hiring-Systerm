# agents/sourcing_agent.py

from crewai import Agent
from langchain_groq import ChatGroq
from config.settings import settings
from tools.database_tool import database_tool
from tools.vector_search_tool import vector_search_tool
from agents.communication_agent import communication_agent
from utils.logger import log
from datetime import datetime, timedelta

class SourcingAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-70b-8192")
        self.agent = Agent(
            role="Proactive Talent Sourcer",
            goal="Identify and re-engage high-quality past candidates from the database for new job openings.",
            backstory="You are an expert AI talent sourcer. You constantly monitor the company's talent pool, looking for hidden gems. When a new role opens up, you are the first to scan the entire history of applicants to find promising candidates who might have been overlooked or applied for a different role in the past.",
            verbose=True,
            llm=self.llm,
        )

    def find_and_engage_past_candidates(self, job_id: str):
        """
        Main workflow for the sourcing agent.
        1. Gets a new job's details.
        2. Searches the vector database for similar resumes.
        3. Filters matches by date (within 1 year) and score.
        4. Sends re-engagement emails to qualified candidates.
        """
        try:
            log.info(f"Sourcing Agent: Starting proactive search for new job ID: {job_id}")
            
            # 1. Get the new job's details and vector
            job = database_tool.get_job_by_id(job_id)
            if not job:
                log.error(f"Sourcing Agent: Could not find job with ID {job_id}. Aborting.")
                return

            job_vector_info = vector_search_tool._run(action="get_vector_by_id", doc_id=f"job_{job_id}")
            if not job_vector_info.get("success"):
                log.error(f"Sourcing Agent: Could not find vector for job ID {job_id}. Aborting.")
                return
            
            job_vector = job_vector_info["vector"]

            # 2. Search FAISS for top 100 most similar candidate resumes
            search_results = vector_search_tool._run(
                action="search",
                query_vector=job_vector,
                top_k=100
            )

            if not search_results.get("success") or not search_results.get("results"):
                log.info("Sourcing Agent: No similar candidates found in the vector database.")
                return
            
            # 3. Filter the results
            one_year_ago = datetime.utcnow() - timedelta(days=365)
            qualified_candidates = []

            for result in search_results["results"]:
                candidate_id = result["doc_id"].replace("candidate_", "")
                score = result["score"] # This is a similarity score, higher is better

                # A. Filter by score threshold
                if score >= 0.50: # Adjust this threshold as needed (FAISS scores are different from LLM scores)
                    # B. Fetch candidate from MongoDB to check the date
                    candidate_doc = database_tool._run("find_one", "candidates", query={"_id": candidate_id}).get("document")
                    
                    if candidate_doc and candidate_doc.get("uploaded_at") >= one_year_ago:
                        qualified_candidates.append(candidate_doc)
                        log.info(f"Sourcing Agent: Found qualified past candidate: {candidate_doc['email']} with score {score}")

            # 4. Engage qualified candidates
            if not qualified_candidates:
                log.info("Sourcing Agent: Found similar candidates, but none met the date/score criteria.")
                return
                
            log.info(f"Sourcing Agent: Sending re-engagement emails to {len(qualified_candidates)} candidates.")
            for candidate in qualified_candidates:
                communication_agent.send_sourcing_invitation(
                    candidate_email=candidate["email"],
                    candidate_name=candidate["name"],
                    job_title=job["title"],
                    job_id=job_id
                )
        
        except Exception as e:
            import traceback
            log.error(f"Sourcing Agent failed: {traceback.format_exc()}")

# Create a singleton instance
sourcing_agent = SourcingAgent()