# agents/interview_agent.py

from crewai import Agent
from langchain_groq import ChatGroq
from config.settings import settings
from tools.database_tool import database_tool
from faster_whisper import WhisperModel
from utils.logger import log
import json
import re


class InterviewAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile"
        )

        # ✅ STT Whisper model (fast + accurate)
        self.stt_model = WhisperModel("base.en", device="cpu", compute_type="int8")

        self.agent = Agent(
            role="Senior Technical Interviewer",
            goal="Conduct a professional, short-question technical interview that fairly evaluates the candidate.",
            backstory=(
                "Your name is PrashnaAI. You are an expert AI interviewer. "
                "You ask ONLY ONE short question at a time. "
                "You never ask multi-part questions. "
                "You never explain the answer or provide long context. "
                "You repeat the same question if the candidate asks to repeat or if the candidate does not answer."
            ),
            verbose=True,
            llm=self.llm,
        )

    # ✅ ------------------------------
    # Speech to Text
    # ✅ ------------------------------
    def transcribe_audio(self, audio_file_path: str) -> str:
        """Converts audio file to text."""
        segments, _ = self.stt_model.transcribe(audio_file_path, beam_size=5)
        text = " ".join([segment.text for segment in segments]).strip()
        return text

    # ✅ ------------------------------
    # Helper Utilities
    # ✅ ------------------------------
    def _clean_question(self, raw: str) -> str:
        """
        ✅ Ensures the interviewer outputs only 1 short question.
        Removes long paragraphs and trims output.
        """
        if not raw:
            return "Can you explain your experience related to this role?"

        raw = raw.strip()

        # Remove markdown blocks if any
        raw = re.sub(r"```.*?```", "", raw, flags=re.DOTALL).strip()

        # If model returns multiple lines, keep first meaningful question line
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        if len(lines) > 1:
            raw = lines[0]

        # Force a question mark at end if missing
        if not raw.endswith("?"):
            raw = raw.rstrip(".") + "?"

        # Keep question short
        if len(raw) > 180:
            raw = raw[:175].rstrip() + "?"

        return raw

    def _is_repeat_request(self, candidate_text: str) -> bool:
        """Detect if candidate asks to repeat the question."""
        if not candidate_text:
            return False
        text = candidate_text.lower()
        repeat_keywords = [
            "repeat", "can you repeat", "say again",
            "come again", "please repeat", "what was the question",
            "i didn't hear", "again please"
        ]
        return any(k in text for k in repeat_keywords)

    def _is_no_answer(self, candidate_text: str) -> bool:
        """Detect empty, silence, unclear, or missing response."""
        if not candidate_text:
            return True

        text = candidate_text.strip().lower()

        if len(text) < 3:
            return True

        useless = ["", "no", "nothing", "i don't know", "not sure", "skip", "na", "n/a", "dont know"]
        if text in useless:
            return True

        return False

    # ✅ ------------------------------
    # Interview Flow Methods
    # ✅ ------------------------------
    def get_opening_question(self, job_id: str) -> dict:
        """Prepares the first opening question."""
        job = database_tool.get_job_by_id(job_id)

        if not job:
            return {"success": False, "error": "Job not found"}

        required_skills = job.get("required_skills", [])

        try:
            prompt = f"""
You are PrashnaAI, a professional technical interviewer.

Interview role: {job.get('title')}

Required skills: {required_skills}

Rules you MUST follow:
- Ask ONLY ONE question.
- The question must be short (max 1 sentence).
- Do not give explanations.
- Do not ask multiple parts.
- Do not include greetings longer than 1 line.

Return ONLY the question text.
"""

            question = self.llm.invoke(prompt).content
            question = self._clean_question(question)

            return {"success": True, "question": question, "job_details": job}
        except Exception as e:
            log.error(f"Error generating opening question: {e}")
            return {"success": False, "error": str(e)}

    def get_next_question(self, conversation_history: list, job_details: dict) -> str:
        """
        ✅ Generates next question:
        - repeats last question if candidate asked repeat
        - repeats last question if candidate gave no answer
        - otherwise asks 1 follow-up question (only once)
        - then moves to next new topic question
        """

        required_skills = job_details.get("required_skills", [])

        # ✅ Find last AI question
        last_ai_question = None
        for entry in reversed(conversation_history):
            if entry["speaker"] == "AI":
                last_ai_question = entry["text"]
                break

        # ✅ Find last candidate response
        last_candidate_answer = None
        for entry in reversed(conversation_history):
            if entry["speaker"] == "Candidate":
                last_candidate_answer = entry["text"]
                break

        if last_ai_question is None:
            return self._clean_question("Can you introduce yourself briefly?")

        # ✅ If candidate requests repetition
        if self._is_repeat_request(last_candidate_answer or ""):
            return self._clean_question(last_ai_question)

        # ✅ If candidate gave no answer
        if self._is_no_answer(last_candidate_answer or ""):
            return self._clean_question(last_ai_question)

        # ✅ Check if we already asked follow-up for last answer
        # We look at last 2 AI messages: if one contains "follow-up" style
        recent_ai_questions = [e["text"] for e in conversation_history if e["speaker"] == "AI"]
        follow_up_already_asked = False

        if len(recent_ai_questions) >= 2:
            # If last question seems like follow-up (very simple check)
            if "why" in recent_ai_questions[-1].lower() or "how" in recent_ai_questions[-1].lower():
                follow_up_already_asked = True

        # ✅ If no follow-up asked yet → ask ONE follow-up question
        if not follow_up_already_asked:
            prompt_followup = f"""
You are PrashnaAI, a technical interviewer for role: {job_details.get("title")}

Candidate Answer:
"{last_candidate_answer}"

Rules:
- Ask ONLY ONE short follow-up question based on the candidate answer.
- Question must be max 1 sentence.
- Do not add explanations.
- Do not include long context.
Return ONLY the question.
"""
            followup = self.llm.invoke(prompt_followup).content
            return self._clean_question(followup)

        # ✅ After follow-up, move to new topic question
        history_str = "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in conversation_history])

        prompt_next = f"""
You are PrashnaAI, conducting a technical interview for role: {job_details.get("title")}

Required skills: {required_skills}

Conversation so far:
{history_str}

Rules:
- Ask ONLY ONE new question.
- It must be short (max 1 sentence).
- It must be relevant to required skills.
- It must NOT repeat any previous question.
- Do not add explanations.
Return ONLY the question.
"""

        next_q = self.llm.invoke(prompt_next).content
        return self._clean_question(next_q)

    def evaluate_interview(self, conversation_history: list, job_details: dict) -> dict:
        """Evaluates the full transcript and provides a score and summary."""
        transcript = "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in conversation_history])

        prompt = f"""
As an expert technical recruiter, evaluate the following interview transcript for a '{job_details.get("title")}' role.
Required skills: {job_details.get("required_skills", [])}

Transcript:
{transcript}

Return ONLY valid JSON.
JSON keys required: summary, strengths, weaknesses, score.

Rules:
- summary: max 2 sentences
- strengths: 2-3 bullet points
- weaknesses: 1-2 bullet points
- score: integer 0-100
"""

        evaluation_text = self.llm.invoke(prompt).content.strip()

        try:
            if evaluation_text.startswith("```json"):
                evaluation_text = evaluation_text[7:]
            if evaluation_text.endswith("```"):
                evaluation_text = evaluation_text[:-3]

            eval_data = json.loads(evaluation_text)
            eval_data["transcript"] = transcript

            log.info(f"✅ Interview evaluation parsed successfully. Score: {eval_data.get('score')}")
            return eval_data

        except Exception as e:
            log.error(f"❌ Failed to parse evaluation JSON. Raw: '{evaluation_text}'. Error: {e}")
            return {
                "summary": "Failed to parse evaluation from LLM.",
                "strengths": [],
                "weaknesses": [],
                "score": 0,
                "transcript": transcript
            }

interview_agent = InterviewAgent()