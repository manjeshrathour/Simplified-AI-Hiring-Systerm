# config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # --- Keys and Secrets ---
    GROQ_API_KEY: str
    SECRET_API_KEY: Optional[str] = None # For Google Forms integration
    GITHUB_API_TOKEN: Optional[str] = None # For GitHub API integration
    
    # --- Database ---
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "recruiting_system"
    
    # --- AI Models ---
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # --- Google Services (Optional) ---
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # --- Email ---
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@recruiting.com"
    
    # --- Application ---
    APP_NAME: str = "AI Recruiting System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "development" # Environment (e.g., development, production)
    # FRONTEND_URL: str = "http://127.0.0.1:5500"   # Add this line with a default value
    
    FRONTEND_URL: str = "https://multiagent-ai-hiring-system.vercel.app"


    # --- File Paths ---
    VECTOR_STORE_PATH: str = "./data/vector_store"
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    UPLOAD_DIR: str = "./uploads"
    
    # --- Other ---
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # This is the Pydantic V2 way to configure the class
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # FIX: This tells Pydantic to ignore any extra variables
    )


# Create settings instance
settings = Settings()

# Create necessary directories
# It's good practice to handle potential errors here
try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
except OSError as e:
    print(f"Error creating directories: {e}")