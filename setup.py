"""
Setup script for AI Recruiting System
Run this after installing requirements.txt
"""
import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'logs',
        'data',
        'data/vector_store',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def check_env_file():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print("\n⚠️  .env file not found!")
        print("Creating .env from template...")
        
        env_template = """# Groq API
GROQ_API_KEY=your_groq_api_key_here

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=recruiting_system

# LLM Configuration
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Google Calendar API (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@recruiting.com

# Application Settings
APP_NAME=AI Recruiting System
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Vector Store
VECTOR_STORE_PATH=./data/vector_store
FAISS_INDEX_PATH=./data/faiss_index

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
"""
        
        with open('.env', 'w') as f:
            f.write(env_template)
        
        print("✓ Created .env file")
        print("\n⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY!")
    else:
        print("✓ .env file exists")


def check_mongodb():
    """Check MongoDB connection"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✓ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("\n  Please ensure MongoDB is running:")
        print("  - Install MongoDB: https://www.mongodb.com/try/download/community")
        print("  - Start MongoDB: mongod --dbpath /path/to/data")
        print("  - Or use Docker: docker run -d -p 27017:27017 mongo:latest")
        return False


def download_spacy_model():
    """Download spaCy model"""
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
            print("✓ spaCy model already downloaded")
        except:
            print("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            print("✓ spaCy model downloaded")
    except ImportError:
        print("⚠️  spaCy not installed. Install requirements.txt first")


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'crewai',
        'groq',
        'pymongo',
        'motor',
        'faiss',
        'sentence-transformers',
        'langchain',
        'llama-index'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"✗ {package}")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def test_imports():
    """Test if all modules can be imported"""
    print("\nTesting module imports...")
    
    try:
        from config.settings import settings
        print("✓ config.settings")
        
        from utils.logger import log
        print("✓ utils.logger")
        
        from database.mongodb_client import mongodb
        print("✓ database.mongodb_client")
        
        from llm.groq_client import groq_client
        print("✓ llm.groq_client")
        
        from llm.embeddings import embedding_model
        print("✓ llm.embeddings")
        
        print("\n✓ All core modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        return False


def create_sample_job():
    """Create a sample job posting"""
    print("\nCreating sample job posting...")
    
    sample_job = """
{
    "job_id": "SAMPLE-001",
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer with expertise in FastAPI, MongoDB, and AI/ML technologies. The ideal candidate will have strong experience building scalable backend systems and working with LLMs.",
    "requirements": [
        "5+ years of Python development experience",
        "Experience with FastAPI or similar frameworks",
        "Knowledge of MongoDB and database design",
        "Familiarity with AI/ML concepts and LLMs",
        "Strong problem-solving skills"
    ],
    "required_skills": [
        "Python",
        "FastAPI",
        "MongoDB",
        "RESTful APIs",
        "Machine Learning",
        "Docker"
    ],
    "experience_required": 5,
    "location": "Remote",
    "salary_range": "$120,000 - $160,000",
    "department": "Engineering",
    "employment_type": "full-time"
}
"""
    
    with open('sample_job.json', 'w') as f:
        f.write(sample_job)
    
    print("✓ Created sample_job.json")
    print("  Use this to test job creation via API")


def print_next_steps():
    """Print next steps for user"""
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    
    print("\nNext Steps:")
    print("\n1. Configure your Groq API key in .env file:")
    print("   GROQ_API_KEY=your_actual_key_here")
    
    print("\n2. Ensure MongoDB is running:")
    print("   mongod --dbpath /path/to/data")
    print("   OR")
    print("   docker run -d -p 27017:27017 --name mongodb mongo:latest")
    
    print("\n3. (Optional) Configure email settings in .env for notifications")
    
    print("\n4. Start the application:")
    print("   python main.py")
    
    print("\n5. Access the API:")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - Health: http://localhost:8000/health")
    
    print("\n6. Test the system:")
    print("   - Upload a resume: POST /upload/resume")
    print("   - Create a job: POST /jobs/")
    print("   - View candidates: GET /candidates/")
    
    print("\n" + "="*60)


def main():
    """Main setup function"""
    print("="*60)
    print("AI Recruiting System - Setup")
    print("="*60)
    
    print("\n[1/7] Checking dependencies...")
    if not check_dependencies():
        print("\n⚠️  Please install dependencies first:")
        print("    pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n[2/7] Creating directories...")
    create_directories()
    
    print("\n[3/7] Checking .env file...")
    check_env_file()
    
    print("\n[4/7] Checking MongoDB connection...")
    check_mongodb()
    
    print("\n[5/7] Downloading spaCy model...")
    download_spacy_model()
    
    print("\n[6/7] Testing module imports...")
    test_imports()
    
    print("\n[7/7] Creating sample data...")
    create_sample_job()
    
    print_next_steps()


if __name__ == "__main__":
    main()