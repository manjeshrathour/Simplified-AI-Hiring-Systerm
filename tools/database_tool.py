# tools/database_tool.py

from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional
from database.mongodb_client import mongodb_sync
from datetime import datetime
from utils.logger import log
from bson import ObjectId


class DatabaseTool(BaseTool):
    name: str = "Database Operations"
    description: str = """Performs database operations:
    - Save candidate data
    - Retrieve job postings
    - Update candidate scores
    - Query candidates by criteria
    - Save interview records
    - Save interview verification images
    - Save proctoring logs
    """

    # =========================================================
    # ✅ INTERNAL HELPERS
    # =========================================================
    def _id_query(self, _id_value: Any) -> Dict[str, Any]:
        """
        Always return a correct MongoDB query for _id field.
        Supports: ObjectId, str(ObjectId)
        """
        if isinstance(_id_value, ObjectId):
            return {"_id": _id_value}

        if isinstance(_id_value, str):
            try:
                # ✅ Check BOTH ObjectId and String types to handle data inconsistency
                return {"_id": {"$in": [ObjectId(_id_value), _id_value]}}
            except Exception:
                return {"_id": _id_value}

        return {"_id": _id_value}

    # =========================================================
    # ✅ CORE DB RUN METHOD
    # =========================================================
    def _run(
        self,
        action: str,
        collection: str,
        data: Optional[Dict] = None,
        query: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute database operation

        Args:
            action: insert, find, find_one, update, update_many, delete, count
            collection: collection name
            data: data for insert/update
            query: filter query
        """
        try:
            coll = mongodb_sync.get_collection(collection)

            # ✅ Convert _id automatically if query uses it
            if query and "_id" in query:
                query["_id"] = self._id_query(query["_id"])["_id"]

            if action == "insert":
                result = coll.insert_one(data)
                return {
                    "success": True,
                    "inserted_id": str(result.inserted_id),
                    "message": f"Document inserted in {collection}"
                }

            elif action == "find":
                documents = list(coll.find(query or {}).limit(100))
                for doc in documents:
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])
                return {
                    "success": True,
                    "documents": documents,
                    "count": len(documents)
                }

            elif action == "find_one":
                document = coll.find_one(query or {})
                if document and "_id" in document:
                    document["_id"] = str(document["_id"])
                return {"success": True, "document": document}

            elif action == "update":
                result = coll.update_one(query, {"$set": data})
                return {
                    "success": True,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "message": f"Updated {result.modified_count} document(s)"
                }

            elif action == "update_many":
                result = coll.update_many(query, {"$set": data})
                return {
                    "success": True,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count
                }

            elif action == "delete":
                result = coll.delete_one(query)
                return {"success": True, "deleted_count": result.deleted_count}

            elif action == "count":
                count = coll.count_documents(query or {})
                return {"success": True, "count": count}

            return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            log.error(f"Database operation error: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================
    # ✅ REQUIRED METHODS (USED BY YOUR AGENTS)
    # =========================================================

    def save_candidate(self, candidate_data: Dict) -> Dict[str, Any]:
        """
        ✅ Used by resume_parsing_agent / orchestrator
        """
        candidate_data["uploaded_at"] = datetime.utcnow()
        candidate_data["updated_at"] = datetime.utcnow()
        candidate_data["status"] = "pending"

        return self._run(
            action="insert",
            collection="candidates",
            data=candidate_data
        )

    def update_candidate_score(self, email: str, score: float, matched_jobs: List[str]) -> Dict[str, Any]:
        """
        ✅ Used by job matching logic
        """
        return self._run(
            action="update",
            collection="candidates",
            query={"email": email},
            data={
                "score": score,
                "matched_jobs": matched_jobs,
                "updated_at": datetime.utcnow()
            }
        )

    def get_active_jobs(self) -> List[Dict]:
        """
        ✅ Fetch all job postings (status filter removed)
        """
        log.info("Fetching all job postings from the database.")
        result = self._run(
            action="find",
            collection="jobs",
            query={}
        )
        return result.get("documents", [])

    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """
        ✅ Used by interview_agent.get_opening_question()
        """
        result = self._run(
            action="find_one",
            collection="jobs",
            query={"job_id": job_id}
        )
        return result.get("document")

    def get_top_candidates(self, job_id: str, limit: int = 10) -> List[Dict]:
        """
        ✅ Used by dashboard ranking logic
        """
        result = self._run(
            action="find",
            collection="candidates",
            query={"matched_jobs": job_id}
        )

        candidates = result.get("documents", [])
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        return candidates[:limit]

    def save_interview(self, interview_data: Dict) -> Dict[str, Any]:
        """
        ✅ This MUST NOT force status="scheduled" always.
        It should respect passed status (AI interview vs scheduled).
        """
        interview_data["created_at"] = datetime.utcnow()
        interview_data["updated_at"] = datetime.utcnow()

        # ✅ Only set default status if not provided
        if "status" not in interview_data:
            interview_data["status"] = "scheduled"

        return self._run(
            action="insert",
            collection="interviews",
            data=interview_data
        )

    # =========================================================
    # ✅ INTERVIEW LOOKUP FIXES
    # =========================================================

    def get_interview_by_id(self, interview_id: str) -> Optional[Dict]:
        """
        ✅ Fetch by MongoDB _id properly (ObjectId conversion happens inside _run)
        """
        log.info(f"Fetching interview by MongoDB _id: {interview_id}")
        result = self._run(
            action="find_one",
            collection="interviews",
            query={"_id": interview_id}
        )
        return result.get("document")

    def get_interview_by_any_id(self, interview_id: str) -> Optional[Dict]:
        """
        ✅ Tries both:
        - Mongo ObjectId _id
        - interview_id field
        """
        log.info(f"Fetching interview by ANY ID: {interview_id}")

        doc = self.get_interview_by_id(interview_id)
        if doc:
            return doc

        result = self._run(
            action="find_one",
            collection="interviews",
            query={"interview_id": interview_id}
        )
        return result.get("document")

    # =========================================================
    # ✅ PROCTORING HELPERS (used by main.py endpoints)
    # =========================================================

    def append_proctoring_event(self, interview_id: str, event_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store all proctoring logs in compliance_logs
        """
        return self._run(
            action="insert",
            collection="compliance_logs",
            data={
                "interview_id": interview_id,
                "event": event_doc,
                "created_at": datetime.utcnow()
            }
        )

    def mark_interview_failed_proctoring(self, interview_id: str, reason: str, warnings: int) -> Dict[str, Any]:
        """
        Mark interview status as cheating_detected
        """
        interview = self.get_interview_by_any_id(interview_id)
        if not interview:
            return {"success": False, "error": "Interview not found"}

        return self._run(
            action="update",
            collection="interviews",
            query={"_id": interview["_id"]},
            data={
                "status": "cheating_detected",
                "proctoring_fail_reason": reason,
                "warnings": warnings,
                "updated_at": datetime.utcnow()
            }
        )


database_tool = DatabaseTool()