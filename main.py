# main.py

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,  # Added for job application endpoint
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Body
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import shutil
import os
import tempfile
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId
import uuid

# Your existing imports
from config.settings import settings
from utils.logger import log
from database.mongodb_client import mongodb
from mcp.mcp_server import initialize_mcp_server
from api.routes import upload, jobs, candidates, interviews
from agents.orchestrator_agent import orchestrator
from agents.interview_agent import interview_agent
from tools.database_tool import database_tool
from fastapi import Header, Form # Ensure Header and Form are imported

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await mongodb.connect()
    initialize_mcp_server()
    log.info("Application startup complete")
    yield
    log.info("Shutting down application")
    await mongodb.close()
    log.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Recruiting & Talent Screening System with Multi-Agent Architecture",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://multiagent-ai-hiring-system.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "https://mac-interlunar-nonancestrally.ngrok-free.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Serve the uploads folder so resumes can be opened in the browser
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Routers
app.include_router(upload.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(interviews.router)

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)


# ============================================================
# ✅ Resume Upload Endpoint
# ============================================================
@app.post("/upload-resume/", tags=["Resume"])
async def handle_resume_upload(file: UploadFile = File(...)):
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOADS_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        log.info(f"Resume uploaded and saved to: {file_path}")

        result = orchestrator.process_candidate_application(file_path)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to process resume."))

        return {"success": True, "message": result.get("message", "Resume processed successfully.")}

    except Exception as e:
        log.error(f"Error during resume upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()


# ============================================================
# ✅ Job Application Endpoint (NEW - Candidate selects job)
# ============================================================
PROFILE_IMAGES_DIR = os.path.join(UPLOADS_DIR, "profile_images")
os.makedirs(PROFILE_IMAGES_DIR, exist_ok=True)


# ============================================================
# ✅ Verification Upload Endpoint
# ============================================================
VERIFICATION_DIR = os.path.join(UPLOADS_DIR, "interview_verification")
os.makedirs(VERIFICATION_DIR, exist_ok=True)


@app.post("/api/interviews/{interview_id}/verification", tags=["Interview Proctoring"])
async def upload_interview_verification(
    interview_id: str,
    id_card: UploadFile = File(...),
    candidate_photo: UploadFile = File(...)
):
    try:
        interview_folder = os.path.join(VERIFICATION_DIR, str(interview_id))
        os.makedirs(interview_folder, exist_ok=True)

        id_card_filename = f"id_card_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{id_card.filename}"
        id_card_path = os.path.join(interview_folder, id_card_filename)
        with open(id_card_path, "wb") as buffer:
            shutil.copyfileobj(id_card.file, buffer)

        candidate_photo_filename = f"candidate_photo_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{candidate_photo.filename}"
        candidate_photo_path = os.path.join(interview_folder, candidate_photo_filename)
        with open(candidate_photo_path, "wb") as buffer:
            shutil.copyfileobj(candidate_photo.file, buffer)

        verification_doc = {
            "interview_id": interview_id,
            "status": "uploaded",
            "id_card_path": id_card_path,
            "candidate_photo_path": candidate_photo_path,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = database_tool._run(
            action="insert",
            collection="interview_verifications",
            data=verification_doc
        )

        log.info(f"✅ Verification uploaded successfully for interview_id={interview_id}")

        return {
            "success": True,
            "message": "Verification uploaded successfully",
            "verification_id": result.get("inserted_id"),
            "interview_id": interview_id,
        }

    except Exception as e:
        log.error(f"Error uploading verification for interview {interview_id}: {e}")
        raise HTTPException(status_code=500, detail="Verification upload failed")


# ============================================================
# ✅ Snapshot Upload Endpoint
# ============================================================
SNAPSHOT_DIR = os.path.join(UPLOADS_DIR, "interview_snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


@app.post("/api/interviews/{interview_id}/snapshot", tags=["Interview Proctoring"])
async def upload_interview_snapshot(interview_id: str, snapshot: UploadFile = File(...)):
    try:
        interview_folder = os.path.join(SNAPSHOT_DIR, str(interview_id))
        os.makedirs(interview_folder, exist_ok=True)

        filename = f"snapshot_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(interview_folder, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(snapshot.file, buffer)

        snapshot_doc = {
            "interview_id": interview_id,
            "snapshot_path": file_path,
            "created_at": datetime.utcnow()
        }

        result = database_tool._run(
            action="insert",
            collection="interview_snapshots",
            data=snapshot_doc
        )

        log.info(f"✅ Snapshot saved for interview_id={interview_id} -> {file_path}")

        return {"success": True, "message": "Snapshot uploaded", "snapshot_id": result.get("inserted_id")}

    except Exception as e:
        log.error(f"Snapshot upload failed for interview {interview_id}: {e}")
        raise HTTPException(status_code=500, detail="Snapshot upload failed")


# ============================================================
# ✅ Proctoring Event Endpoint
# ============================================================
@app.post("/api/interviews/{interview_id}/proctoring-event", tags=["Interview Proctoring"])
async def record_proctoring_event(interview_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        event_doc = {
            "interview_id": interview_id,
            "event_type": payload.get("event_type"),
            "message": payload.get("message", ""),
            "warnings": payload.get("warnings", 0),
            "timestamp": payload.get("timestamp", datetime.utcnow().isoformat()),
            "created_at": datetime.utcnow(),
        }

        database_tool._run(action="insert", collection="compliance_logs", data=event_doc)

        return {"success": True, "message": "Proctoring event recorded"}

    except Exception as e:
        log.error(f"Error recording proctoring event for interview {interview_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to record proctoring event")




# ============================================================
# ✅ WebSocket Interview Endpoint
# ============================================================
@app.websocket("/ws/interview/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: str):
    await websocket.accept()
    log.info(f"✅ WebSocket connection established for AI interview: {interview_id}")

    try:
        log.info(f"🔍 DEBUG: Starting WebSocket logic for {interview_id}")

        # ✅ must exist
        interview = database_tool.get_interview_by_any_id(interview_id)
        log.info(f"🔍 DEBUG: Interview lookup result: {interview}")

        if not interview:
            log.error(f"❌ DEBUG: Interview not found for ID {interview_id}")
            await websocket.send_json({"type": "error", "text": "Interview not found."})
            await websocket.close()
            return

        # ✅ verification must exist
        verification = database_tool._run(
            action="find_one",
            collection="interview_verifications",
            query={"interview_id": interview_id}
        ).get("document")
        log.info(f"🔍 DEBUG: Verification lookup result: {verification}")

        if not verification:
            log.error(f"❌ DEBUG: Verification not found for interview {interview_id}")
            await websocket.send_json({"type": "error", "text": "Verification not uploaded. Please upload ID + photo first."})
            await websocket.close()
            return

        # ✅ START question immediately
        log.info(f"Generating opening question for job {interview['job_id']}")
        try:
             start_data = interview_agent.get_opening_question(interview["job_id"])
             if not start_data.get("success"):
                 raise Exception(start_data.get("error", "Failed to generate question"))
        except Exception as e:
             log.error(f"Error generating opening question: {e}")
             await websocket.send_json({"type": "error", "text": "Failed to start interview. AI error."})
             await websocket.close()
             return

        log.info(f"Sending opening question: {start_data['question']}")
        
        job_details = start_data["job_details"]
        first_question = start_data["question"]

        await websocket.send_json({"type": "question", "text": first_question})
        conversation_history = [{"speaker": "AI", "text": first_question}]
        
        # ✅ interview loop
        for _ in range(5):
            audio_bytes = await websocket.receive_bytes()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_audio:
                tmp_audio.write(audio_bytes)
                audio_file_path = tmp_audio.name

            candidate_text = interview_agent.transcribe_audio(audio_file_path)

            try:
                os.remove(audio_file_path)
            except Exception:
                pass

            log.info(f"Candidate said: {candidate_text}")
            conversation_history.append({"speaker": "Candidate", "text": candidate_text})

            next_question = interview_agent.get_next_question(conversation_history, job_details)
            conversation_history.append({"speaker": "AI", "text": next_question})

            await websocket.send_json({"type": "question", "text": next_question})

        # ✅ evaluate
        await websocket.send_json({"type": "status", "text": "Interview complete. Evaluating..."})
        evaluation = interview_agent.evaluate_interview(conversation_history, job_details)

        database_tool._run(
            action="update",
            collection="interviews",
            query={"_id": interview["_id"]},  # ✅ converted inside _run()
            data={
                "status": "completed_ai_interview",
                "evaluation": evaluation,
                "interview_score": evaluation.get("score", 0),
                "updated_at": datetime.utcnow()
            }
        )

        log.info(f"✅ Interview completed. Score: {evaluation.get('score')}")

        # ✅ orchestrator must use MongoDB _id
        orchestrator.process_post_interview_decision(interview["_id"])

        await websocket.send_json({"type": "thank_you", "text": "Thanks! HR will contact you soon."})
        await asyncio.sleep(2)
        await websocket.close()

    except WebSocketDisconnect:
        log.warning(f"⚠️ Interview {interview_id} disconnected by client.")

    except Exception as e:
        import traceback
        log.error(f"❌ Critical WebSocket error: {traceback.format_exc()}")
        try:
            await websocket.send_json({"type": "error", "text": "Server error occurred."})
            await websocket.close()
        except Exception:
            pass



# ============================================================
# Utility Endpoints
# ============================================================
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }

# ==============================================================this is new =======================================
# --- ENDPOINT FOR GOOGLE FORM SUBMISSION ---
@app.post("/apply-for-job/", tags=["Resume"])
async def handle_job_application_final(
    file: UploadFile = File(...),              # Matches "file" in Google Script
    full_name: str = Form(...),                # Matches "full_name" in Google Script
    email: str = Form(...),                    # Matches "email" in Google Script
    job_id: str = Form(...),                   # Matches "job_id" in Google Script
    profile_image: Optional[UploadFile] = File(None), # Optional - No error if missing
    x_secret_key: str = Header(None)           # Security check
):
    # 1. Security Check
    if x_secret_key != settings.SECRET_API_KEY:
        log.error(f"Security Alert: Unauthorized key: {x_secret_key}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        # 2. Save the uploaded Resume
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOADS_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        log.info(f"🚀 Form Received: {full_name} for Job {job_id}")

        # 3. Trigger the Orchestrator
        # This starts the AI Parsing -> Matching -> Emailing workflow
        result = orchestrator.process_job_application(
            resume_path=file_path,
            applied_job_id=job_id,
            full_name=full_name,
            email=email
        )

        return {
            "success": True, 
            "message": "AI Agents have started processing your application.",
            "score": result.get("applied_job_score")
        }

    except Exception as e:
        log.error(f"Error in application processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/health")
async def health_check():
    try:
        await mongodb.client.admin.command("ping")
        db_status = "connected"
    except:
        db_status = "disconnected"

    return {"status": "healthy", "database": db_status, "version": settings.APP_VERSION}


@app.get("/stats")
async def get_stats():
    """Get high-level system statistics for the dashboard."""
    try:
        # Get counts from MongoDB collections
        candidates_count = await mongodb.db.candidates.count_documents({})
        jobs_count = await mongodb.db.jobs.count_documents({})
        interviews_count = await mongodb.db.interviews.count_documents({})
        
        # --- Advanced Analytics ---
        # 1. Interview Breakdown
        scheduled_count = await mongodb.db.interviews.count_documents({"status": {"$in": ["scheduled", "pending_ai_interview"]}})
        completed_count = await mongodb.db.interviews.count_documents({"status": {"$in": ["completed", "completed_ai_interview"]}})
        
        # 2. Average Score (of candidates who have a score > 0)
        pipeline = [
            {"$match": {"score": {"$gt": 0}}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}}
        ]
        avg_score_result = await mongodb.db.candidates.aggregate(pipeline).to_list(length=1)
        avg_score = round(avg_score_result[0]["avg_score"], 1) if avg_score_result else 0
        
        # Import the vector_store instance directly
        from database.vector_store import vector_store
        
        vector_count = 0
        if vector_store.index:
            vector_count = vector_store.index.ntotal
        
        log.info(f"Fetching stats: Candidates={candidates_count}, Jobs={jobs_count}, Interviews={interviews_count}, AvgScore={avg_score}")

        return {
            "success": True,
            "stats": {
                "total_candidates": candidates_count,
                "active_jobs": jobs_count,
                "interviews_scheduled": interviews_count,
                "vector_count": vector_count,
                "analytics": {
                    "interviews_breakdown": {
                        "scheduled": scheduled_count,
                        "completed": completed_count
                    },
                    "average_score": avg_score
                }
            }
        }
    except Exception as e:
        log.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch system statistics.")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"❌ VALIDATION ERROR: {exc.errors()}") # This will print the exact missing field in your terminal
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


if __name__ == "__main__":
    import uvicorn
    log.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG, log_level="info")