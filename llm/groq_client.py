# Groq API client
from groq import Groq
from typing import Optional, List, Dict
from config.settings import settings
from utils.logger import log


class GroqClient:
    """Groq API client for LLM interactions"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text using Groq LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            log.error(f"Groq API error: {e}")
            raise
    
    def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate text with additional context
        
        Args:
            prompt: User prompt
            context: Additional context
            system_prompt: System prompt
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        full_prompt = f"Context:\n{context}\n\nQuery: {prompt}"
        return self.generate(full_prompt, system_prompt, temperature)
    
    def extract_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """Extract structured JSON from LLM response
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            
        Returns:
            Parsed JSON dict
        """
        import json
        
        if not system_prompt:
            system_prompt = "You are a helpful assistant that returns responses in valid JSON format."
        
        response = self.generate(prompt, system_prompt, temperature=0.3)
        
        try:
            # Try to find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON from LLM response: {e}")
            log.debug(f"Response was: {response}")
            return {}


# Global instance
groq_client = GroqClient()