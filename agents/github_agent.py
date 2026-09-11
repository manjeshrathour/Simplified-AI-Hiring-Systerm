# agents/github_agent.py

from crewai import Agent
from langchain_groq import ChatGroq
from config.settings import settings
from utils.logger import log
import requests
import json
from typing import Dict, List, Optional


class GitHubAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name=settings.LLM_MODEL)
        self.github_token = settings.GITHUB_API_TOKEN
        self.headers = {}
        
        # Add authentication header if token is available
        if self.github_token and self.github_token != "your_github_token_here":
            self.headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        else:
            log.warning("GitHub API token not configured. Using unauthenticated requests (rate limited to 60/hour)")
            self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        self.agent = Agent(
            role="GitHub Profile Analyst",
            goal="Analyze a candidate's GitHub profile to assess their repositories, programming languages, project quality, and contribution activity using the GitHub API.",
            backstory="You are a senior engineering manager who is an expert at evaluating developer talent by analyzing their code repositories. You can quickly understand a developer's strengths and technical expertise by examining their GitHub projects.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )

    def get_user_repositories(self, username: str) -> Optional[List[Dict]]:
        """
        Fetches all public repositories for a GitHub user using the GitHub API.
        
        Args:
            username: GitHub username
            
        Returns:
            List of repository dictionaries or None if error
        """
        try:
            log.info(f"GitHub Agent: Fetching repositories for user '{username}'")
            
            url = f"https://api.github.com/users/{username}/repos"
            params = {
                "sort": "updated",
                "per_page": 100  # Get up to 100 repos
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 404:
                log.warning(f"GitHub user '{username}' not found")
                return None
            elif response.status_code == 403:
                log.error("GitHub API rate limit exceeded. Please add GITHUB_API_TOKEN to .env")
                return None
            elif response.status_code != 200:
                log.error(f"GitHub API error: {response.status_code} - {response.text}")
                return None
            
            repos = response.json()
            log.info(f"GitHub Agent: Found {len(repos)} repositories for '{username}'")
            
            return repos
            
        except requests.exceptions.RequestException as e:
            log.error(f"GitHub Agent: Network error fetching repositories: {e}")
            return None
        except Exception as e:
            log.error(f"GitHub Agent: Error fetching repositories: {e}")
            return None

    def analyze_repositories(self, repos: List[Dict], job_requirements: Dict = None) -> Dict:
        """
        Analyzes repositories and evaluates them against job requirements.
        
        Args:
            repos: List of repository dictionaries from GitHub API
            job_requirements: Job details including required skills
            
        Returns:
            Analysis dictionary with rankings and insights
        """
        try:
            if not repos:
                return {
                    "success": False,
                    "message": "No repositories to analyze"
                }
            
            log.info(f"GitHub Agent: Analyzing {len(repos)} repositories")
            
            # Extract key information from repos
            repo_summaries = []
            for repo in repos[:20]:  # Analyze top 20 repos
                summary = {
                    "name": repo.get("name", "Unknown"),
                    "description": repo.get("description", "No description"),
                    "language": repo.get("language", "N/A"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "url": repo.get("html_url", ""),
                    "updated_at": repo.get("updated_at", ""),
                    "topics": repo.get("topics", [])
                }
                repo_summaries.append(summary)
            
            # Use LLM to analyze repositories
            job_skills = job_requirements.get("required_skills", []) if job_requirements else []
            job_title = job_requirements.get("title", "General Technical Role") if job_requirements else "General Technical Role"
            
            prompt = f"""
            Analyze the following GitHub repositories for a candidate applying for a '{job_title}' position.
            
            Required Skills for the Job: {', '.join(job_skills) if job_skills else 'General programming skills'}
            
            Repositories (JSON format):
            {json.dumps(repo_summaries, indent=2)}
            
            **Your Task:**
            1. Identify the candidate's primary programming languages (top 3)
            2. Find the BEST FIT repository that matches the job requirements
            3. Evaluate the overall quality of the portfolio (stars, activity, variety)
            4. Provide a 2-3 sentence professional summary
            
            Return ONLY valid JSON in this exact format:
            {{
              "primary_languages": ["Python", "JavaScript", "Go"],
              "best_fit_repo": {{
                "name": "repository-name",
                "url": "https://github.com/user/repo",
                "reason": "This repository demonstrates strong Python skills with machine learning, directly relevant to the data science role."
              }},
              "portfolio_quality": "high/medium/low",
              "total_stars": 150,
              "professional_summary": "Brief 2-3 sentence summary of the candidate's GitHub profile and technical expertise."
            }}
            """
            
            analysis_text = self.llm.invoke(prompt).content
            
            # Clean and parse JSON
            cleaned_response = analysis_text.strip().replace("```json", "").replace("```", "").strip()
            analysis = json.loads(cleaned_response)
            
            log.info(f"GitHub Agent: Analysis complete. Best fit repo: {analysis.get('best_fit_repo', {}).get('name', 'None')}")
            
            return {
                "success": True,
                "analysis": analysis,
                "total_repos": len(repos)
            }
            
        except json.JSONDecodeError as e:
            log.error(f"GitHub Agent: Failed to parse LLM response as JSON: {e}")
            log.error(f"Raw response: {analysis_text}")
            return {
                "success": False,
                "error": "Failed to parse analysis results",
                "raw_response": analysis_text
            }
        except Exception as e:
            log.error(f"GitHub Agent: Error analyzing repositories: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def find_best_fit_repository(self, username: str, job_requirements: Dict = None) -> Dict:
        """
        Main method: Finds the best-fit repository for a candidate based on job requirements.
        
        Args:
            username: GitHub username
            job_requirements: Job details including required skills and title
            
        Returns:
            Dictionary with best fit repository and analysis
        """
        try:
            log.info(f"GitHub Agent: Finding best fit repository for '{username}'")
            
            # Step 1: Fetch repositories
            repos = self.get_user_repositories(username)
            
            if not repos:
                return {
                    "success": False,
                    "message": f"Could not fetch repositories for user '{username}'"
                }
            
            # Step 2: Analyze repositories
            analysis_result = self.analyze_repositories(repos, job_requirements)
            
            if not analysis_result.get("success"):
                return analysis_result
            
            return {
                "success": True,
                "username": username,
                "analysis": analysis_result.get("analysis", {}),
                "total_repos": analysis_result.get("total_repos", 0)
            }
            
        except Exception as e:
            log.error(f"GitHub Agent: Error in find_best_fit_repository: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_profile(self, github_url: str, job_requirements: Dict = None) -> Dict:
        """
        Analyzes a GitHub profile given a URL.
        
        Args:
            github_url: Full GitHub profile URL (e.g., https://github.com/username)
            job_requirements: Optional job requirements for matching
            
        Returns:
            Analysis results dictionary
        """
        log.info(f"GitHub Agent: Analyzing profile at {github_url}")
        
        if not github_url or "github.com" not in github_url:
            return {
                "success": False,
                "message": "No valid GitHub URL provided"
            }
        
        try:
            # Extract username from URL
            # Handles: https://github.com/username or github.com/username
            parts = github_url.rstrip('/').split('/')
            username = parts[-1]
            
            if not username:
                return {
                    "success": False,
                    "message": "Could not extract username from GitHub URL"
                }
            
            # Use the new API-based method
            result = self.find_best_fit_repository(username, job_requirements)
            
            if result.get("success"):
                analysis = result.get("analysis", {})
                return {
                    "success": True,
                    "username": username,
                    "primary_languages": analysis.get("primary_languages", []),
                    "best_fit_repo": analysis.get("best_fit_repo", {}),
                    "portfolio_quality": analysis.get("portfolio_quality", "unknown"),
                    "total_stars": analysis.get("total_stars", 0),
                    "professional_summary": analysis.get("professional_summary", ""),
                    "total_repos": result.get("total_repos", 0)
                }
            else:
                return result
            
        except Exception as e:
            log.error(f"GitHub Agent: Error analyzing profile: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Create a singleton instance
github_agent = GitHubAgent()