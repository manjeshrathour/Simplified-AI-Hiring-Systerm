# agents/synthesizer_agent.py

from crewai import Agent
from langchain_groq import ChatGroq
from config.settings import settings
from utils.logger import log

class SynthesizerAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name=settings.LLM_MODEL)
        self.agent = Agent(
            role="Senior Recruiting Analyst",
            goal="Combine multiple research reports (GitHub analysis, public presence) into a single, concise, and actionable 'Enriched Candidate Profile'.",
            backstory="You are an expert at synthesizing information. You can take disparate pieces of data from multiple sources and weave them into a clear, holistic narrative that provides a 360-degree view of a candidate's professional persona.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

    def synthesize_reports(self, resume_text: str, github_report: str, public_presence_report: str) -> str:
        """
        Combines the resume text and two research reports into a final summary.
        """
        log.info("Synthesizer Agent: Combining research reports into a final profile.")
        
        prompt = f"""
        As a senior recruiting analyst, your task is to create a final "Enriched Candidate Profile" by synthesizing the information provided below.

        **Source 1: Original Resume Summary**
        {resume_text[:1000]}

        **Source 2: GitHub Profile Analysis Report**
        {github_report}

        **Source 3: Public Presence Report**
        {public_presence_report}

        **Your Task:**
        Combine the key insights from all three sources into a single, easy-to-read summary. The summary should be a short paragraph highlighting the candidate's core technical strengths, their areas of focus based on their public activity, and any notable projects or contributions. Do not simply list the facts; create a holistic professional summary.

        **Enriched Candidate Profile:**
        """
        
        enriched_profile = self.llm.invoke(prompt).content
        log.info("Synthesizer Agent: Successfully created the Enriched Profile.")
        return enriched_profile

# Create a singleton instance
synthesizer_agent = SynthesizerAgent()