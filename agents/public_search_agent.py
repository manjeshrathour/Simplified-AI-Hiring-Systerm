# agents/public_search_agent.py

from crewai import Agent
from langchain_groq import ChatGroq
from config.settings import settings
from utils.logger import log
from ddgs import DDGS  # Updated package name

class PublicSearchAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name=settings.LLM_MODEL)
        self.search_tool = DDGS()
        self.agent = Agent(
            role="Public Presence Analyst",
            goal="Scan the public web to find a candidate's technical contributions, such as blogs, articles, and conference talks.",
            backstory="You are an expert investigative researcher. You are skilled at using search engines to uncover a person's professional and technical footprint on the internet, focusing on high-quality, relevant content.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

    def search_for_contributions(self, candidate_name: str) -> str:
        """
        Searches for a candidate's technical articles, blogs, or talks and returns a summary.
        """
        log.info(f"Public Search Agent: Searching for contributions from '{candidate_name}'")
        
        try:
            # Create a series of targeted search queries
            queries = [
                f'"{candidate_name}" technical blog post',
                f'"{candidate_name}" Medium article data science',
                f'"{candidate_name}" towards data science',
                f'"{candidate_name}" conference talk machine learning',
                f'"{candidate_name}" Stack Overflow contributions'
            ]
            
            # Use the search tool to get results
            # For this example, we'll just search the first query for simplicity
            search_results_list = list(self.search_tool.text(queries[0], max_results=5))
            
            # Format results as text
            if not search_results_list:
                search_results = "No results found"
            else:
                search_results = "\n\n".join([
                    f"Title: {result.get('title', 'N/A')}\nSnippet: {result.get('body', 'N/A')}\nURL: {result.get('href', 'N/A')}"
                    for result in search_results_list
                ])
            
            if not search_results or "No good DuckDuckGo Search Result was found" in search_results:
                log.info(f"Public Search Agent: No significant public contributions found for '{candidate_name}'.")
                return "No significant public technical contributions were found."

            # Use an LLM to summarize the findings
            prompt = f"""
            Based on the following search results, please summarize the key technical contributions (blogs, talks, articles) found for the candidate named '{candidate_name}'.
            Focus on the topics they write or speak about. If the results seem irrelevant, please state that no relevant contributions were found.

            Search Results:
            {search_results[:3000]}

            Summary:
            """
            
            summary = self.llm.invoke(prompt).content
            log.info(f"Public Search Agent: Found and summarized contributions for '{candidate_name}'.")
            return summary

        except Exception as e:
            log.error(f"Public Search Agent failed for '{candidate_name}': {e}")
            return "An error occurred during the public search."

# Create a singleton instance
public_search_agent = PublicSearchAgent()