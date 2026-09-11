# CrewAI configuration
"""
CrewAI Configuration for Multi-Agent Coordination
"""
from crewai import Crew, Process
from agents.orchestrator_agent import orchestrator
from agents.resume_parsing_agent import resume_parsing_agent
from agents.matching_agent import matching_agent
from agents.scheduling_agent import scheduling_agent
from agents.communication_agent import communication_agent
from agents.compliance_agent import compliance_agent
from utils.logger import log


class RecruitingCrew:
    """CrewAI configuration for recruiting system"""
    
    def __init__(self):
        self.orchestrator = orchestrator
        self.resume_agent = resume_parsing_agent
        self.matching_agent = matching_agent
        self.scheduling_agent = scheduling_agent
        self.communication_agent = communication_agent
        self.compliance_agent = compliance_agent
        
        log.info("Recruiting Crew initialized")
    
    def create_hierarchical_crew(self) -> Crew:
        """Create a hierarchical crew with orchestrator as manager
        
        Returns:
            Configured Crew instance
        """
        crew = Crew(
            agents=[
                self.orchestrator.agent,
                self.resume_agent.agent,
                self.matching_agent.agent,
                self.scheduling_agent.agent,
                self.communication_agent.agent,
                self.compliance_agent.agent
            ],
            process=Process.hierarchical,
            manager_llm=self.orchestrator.llm,
            verbose=True
        )
        
        log.info("Hierarchical crew created with orchestrator as manager")
        return crew
    
    def create_sequential_crew(self) -> Crew:
        """Create a sequential crew for simple workflows
        
        Returns:
            Configured Crew instance
        """
        crew = Crew(
            agents=[
                self.resume_agent.agent,
                self.matching_agent.agent,
                self.compliance_agent.agent,
                self.scheduling_agent.agent,
                self.communication_agent.agent
            ],
            process=Process.sequential,
            verbose=True
        )
        
        log.info("Sequential crew created")
        return crew
    
    def get_all_agents(self):
        """Get all agent instances
        
        Returns:
            Dictionary of all agents
        """
        return {
            "orchestrator": self.orchestrator,
            "resume_parsing": self.resume_agent,
            "matching": self.matching_agent,
            "scheduling": self.scheduling_agent,
            "communication": self.communication_agent,
            "compliance": self.compliance_agent
        }


# Global crew instance
recruiting_crew = RecruitingCrew()