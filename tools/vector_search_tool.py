# Tool: RAG/Vector search
from crewai.tools import BaseTool
from typing import Dict, Any, List
from database.vector_store import vector_store
from llm.embeddings import embedding_model
from utils.logger import log
import numpy as np


class VectorSearchTool(BaseTool):
    name: str = "Vector Search & RAG"
    description: str = """Performs semantic search over candidates and jobs using vector embeddings:
    - Add candidate/job to vector store
    - Search for similar candidates
    - Match jobs to candidates using semantic similarity
    - RAG-based retrieval for context
    """
    
    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute vector search operation"""
        try:
            if action == "add_candidate":
                return self._add_candidate(kwargs)
            elif action == "add_job":
                return self._add_job(kwargs)
            elif action == "search_candidates":
                return self._search_candidates(kwargs)
            elif action == "match_jobs":
                return self._match_jobs(kwargs)
            elif action == "get_stats":
                return vector_store.get_stats()
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            log.error(f"Vector search error: {e}")
            return {"error": str(e)}
    
    def _add_candidate(self, params: Dict) -> Dict[str, Any]:
        """Add candidate to vector store"""
        candidate_id = params.get("candidate_id")
        text = params.get("text", "")
        skills = params.get("skills", [])
        
        # Create searchable text
        searchable_text = f"{text} Skills: {', '.join(skills)}"
        
        # Generate embedding
        embedding = embedding_model.encode(searchable_text)
        
        # Add to vector store
        vector_store.add_vectors(
            vectors=embedding.reshape(1, -1),
            metadata=[{
                "type": "candidate",
                "id": candidate_id,
                "text": searchable_text[:500],
                "skills": skills
            }]
        )
        
        # Save index
        vector_store.save_index()
        
        return {
            "success": True,
            "message": f"Added candidate {candidate_id} to vector store"
        }
    
    def _add_job(self, params: Dict) -> Dict[str, Any]:
        """Add job to vector store"""
        job_id = params.get("job_id")
        title = params.get("title", "")
        description = params.get("description", "")
        required_skills = params.get("required_skills", [])
        
        # Create searchable text
        searchable_text = f"{title}. {description} Required Skills: {', '.join(required_skills)}"
        
        # Generate embedding
        embedding = embedding_model.encode(searchable_text)
        
        # Add to vector store
        vector_store.add_vectors(
            vectors=embedding.reshape(1, -1),
            metadata=[{
                "type": "job",
                "id": job_id,
                "title": title,
                "text": searchable_text[:500],
                "required_skills": required_skills
            }]
        )
        
        # Save index
        vector_store.save_index()
        
        return {
            "success": True,
            "message": f"Added job {job_id} to vector store"
        }
    
    def _search_candidates(self, params: Dict) -> Dict[str, Any]:
        """Search for candidates similar to query"""
        query = params.get("query", "")
        k = params.get("k", 5)
        
        # Generate query embedding
        query_embedding = embedding_model.encode(query)
        
        # Search
        results = vector_store.search(query_embedding, k=k * 2)  # Get more to filter
        
        # Filter for candidates only
        candidate_results = [
            {
                "candidate_id": result[0]["id"],
                "score": result[1],
                "skills": result[0].get("skills", []),
                "text": result[0].get("text", "")
            }
            for result in results
            if result[0].get("type") == "candidate"
        ][:k]
        
        return {
            "success": True,
            "results": candidate_results,
            "count": len(candidate_results)
        }
    
    def _match_jobs(self, params: Dict) -> Dict[str, Any]:
        """Match jobs to a candidate profile"""
        candidate_text = params.get("candidate_text", "")
        skills = params.get("skills", [])
        k = params.get("k", 5)
        
        # Create query from candidate
        query = f"{candidate_text} Skills: {', '.join(skills)}"
        
        # Generate embedding
        query_embedding = embedding_model.encode(query)
        
        # Search
        results = vector_store.search(query_embedding, k=k * 2)
        
        # Filter for jobs only
        job_results = [
            {
                "job_id": result[0]["id"],
                "title": result[0].get("title", ""),
                "match_score": result[1],
                "required_skills": result[0].get("required_skills", [])
            }
            for result in results
            if result[0].get("type") == "job"
        ][:k]
        
        return {
            "success": True,
            "matched_jobs": job_results,
            "count": len(job_results)
        }


# Create tool instance
vector_search_tool = VectorSearchTool()