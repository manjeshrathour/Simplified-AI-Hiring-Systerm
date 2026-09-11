# AI-Powered Recruiting & Talent Screening System

A fully functional, production-ready AI recruiting system powered by multi-agent architecture, featuring automated resume parsing, intelligent candidate matching, interview scheduling, and compliance monitoring.

## 🏗️ Architecture

### Multi-Agent System (Hierarchical Pattern)

This system implements a **hierarchical agent architecture** with 6 specialized agents:

1. **Orchestrator Agent** (Manager) - Coordinates all other agents and manages workflow
2. **Resume Parsing Agent** - Extracts structured data from resumes
3. **Job-Candidate Matching Agent** - Uses RAG for semantic job matching
4. **Interview Scheduling Agent** - Manages calendar and schedules interviews
5. **Communication Agent** - Handles all candidate communications
6. **Compliance Agent** - Ensures fair, unbiased, and compliant recruitment

### Technology Stack

- **Framework**: FastAPI
- **Agent Framework**: CrewAI (with hierarchical process)
- **LLM**: Groq API (Llama3 70B)
- **Embeddings**: sentence-transformers (MiniLM-L6-v2)
- **Vector Store**: FAISS
- **Database**: MongoDB (localhost:27017)
- **MCP**: Model Context Protocol for tool standardization
- **LlamaIndex**: For document processing and RAG

## 🚀 Features

### Core Capabilities

✅ **Automated Resume Processing**
- Parse PDF/DOCX resumes
- Extract skills, experience, education
- Natural language understanding via LLM

✅ **Intelligent Job Matching (RAG)**
- Semantic search using embeddings
- LLM-powered candidate ranking
- Contextual job-candidate alignment

✅ **Interview Automation**
- Calendar integration
- Automatic scheduling
- Meeting link generation

✅ **Communication Management**
- Application confirmations
- Interview invitations
- Follow-up reminders
- Rejection notices

✅ **Compliance & Diversity**
- Bias detection in resumes
- Audit trail logging
- Fair evaluation standards

## 📦 Installation

### Prerequisites

- **Python** 3.10 or higher
- **MongoDB** 4.0+ (running on `localhost:27017`)
- **Groq API Key** ([Get it here](https://console.groq.com))
- **Google API Credentials** (optional, for Calendar/Gmail)

### Step-by-Step Setup

#### 1️⃣ Clone Repository

```bash
git clone https://github.com/deepeshyadav760/multiagent_ai_hiring_system.git
cd Agent_Recruiter_langchain
```

#### 2️⃣ Create Virtual Environment

```bash
# Windows
python -m venv lang_venv
lang_venv\Scripts\activate

# macOS/Linux
python3 -m venv lang_venv
source lang_venv/bin/activate
```

#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Download NLP Model

```bash
python -m spacy download en_core_web_sm
```

#### 5️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=recruiting_system

# Optional - Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@recruiting.com

# Optional - Google Calendar (for scheduling)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Optional - GitHub Analysis
GITHUB_API_TOKEN=your_github_token

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://127.0.0.1:5500
```

#### 6️⃣ Create Required Directories

```bash
mkdir -p uploads logs data/vector_store data/faiss_index
mkdir -p uploads/profile_images uploads/interview_verification uploads/interview_snapshots
```

#### 7️⃣ Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use your local MongoDB installation
mongod
```

---

## 🚀 Quick Start

### Start the Application

**Terminal 1** - Start FastAPI backend:
```bash
python main.py
```

**Terminal 2** - Start frontend server:
```bash
python -m http.server 5500
```

### Access Points

- **Frontend UI**: http://127.0.0.1:5500/frontend/index.html
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Quick Test

```bash
# Check system health
curl http://localhost:8000/health

# Get system statistics
curl http://localhost:8000/stats

# Upload a resume
curl -X POST "http://localhost:8000/upload-resume/" \
  -F "file=@sample_resume.pdf"
```

---

## 📡 API Endpoints

### 🏠 System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message and API info |
| `GET` | `/health` | System health check |
| `GET` | `/stats` | Dashboard statistics |

### 📄 Resume & Application Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-resume/` | Upload resume (auto-matches jobs) |
| `POST` | `/apply-for-job/` | Apply for specific job with resume + profile image |

**Example - Upload Resume:**
```bash
curl -X POST "http://localhost:8000/upload-resume/" \
  -F "file=@candidate_resume.pdf"
```

**Example - Apply for Job:**
```bash
curl -X POST "http://localhost:8000/apply-for-job/" \
  -F "job_id=JOB-001" \
  -F "full_name=Deepesh Yadav" \
  -F "email=deepeshyadav760@gmail.com" \
  -F "resume=@resume.pdf" \
  -F "profile_image=@photo.jpg"
```

### 💼 Job Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs/` | Create new job posting |
| `GET` | `/jobs/` | List all jobs |
| `GET` | `/jobs/{job_id}` | Get specific job details |
| `PUT` | `/jobs/{job_id}` | Update job posting |
| `DELETE` | `/jobs/{job_id}` | Delete job posting |
| `GET` | `/jobs/{job_id}/candidates` | Get top matching candidates |

**Example - Create Job:**
```bash
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB-001",
    "title": "Senior Python Developer",
    "description": "We need an expert Python developer with AI/ML experience...",
    "required_skills": ["Python", "FastAPI", "MongoDB", "AI/ML"],
    "experience_required": 5,
    "location": "Remote",
    "employment_type": "full-time"
  }'
```

### 👥 Candidate Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/candidates/` | List all candidates (with filters) |
| `GET` | `/candidates/{email}` | Get candidate details |
| `DELETE` | `/candidates/{email}` | Delete candidate |
| `POST` | `/candidates/{email}/shortlist/{job_id}` | Shortlist candidate (creates interview) |
| `POST` | `/candidates/{email}/reject/{job_id}` | Reject candidate |
| `POST` | `/candidates/{email}/enrich` | Enrich profile (GitHub + public search) |

**Example - Get Candidates:**
```bash
# Get all candidates
curl "http://localhost:8000/candidates/"

# Filter by status and score
curl "http://localhost:8000/candidates/?status=pending&min_score=70"
```

**Example - Shortlist Candidate:**
```bash
curl -X POST "http://localhost:8000/candidates/deepesh@example.com/shortlist/JOB-001"
```

### 🎤 Interview Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/interviews/` | List all interviews |
| `GET` | `/interviews/{interview_id}` | Get interview details |
| `DELETE` | `/interviews/{interview_id}` | Cancel interview |
| `POST` | `/api/interviews/{interview_id}/verification` | Upload ID + photo verification |
| `POST` | `/api/interviews/{interview_id}/snapshot` | Upload proctoring snapshot |
| `POST` | `/api/interviews/{interview_id}/proctoring-event` | Record proctoring event |
| `WS` | `/ws/interview/{interview_id}` | WebSocket AI interview session |

**Example - Upload Verification:**
```bash
curl -X POST "http://localhost:8000/api/interviews/INT-001/verification" \
  -F "id_card=@id_card.jpg" \
  -F "candidate_photo=@photo.jpg"
```

---

## 🎯 Usage Examples

### Example 1: Complete Hiring Flow

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Create a job posting
job_data = {
    "job_id": "PYTHON-SR-001",
    "title": "Senior Python Developer",
    "description": "Looking for 5+ years Python expert with AI/ML background",
    "required_skills": ["Python", "FastAPI", "MongoDB", "Machine Learning", "Docker"],
    "experience_required": 5,
    "location": "Remote",
    "employment_type": "full-time"
}
response = requests.post(f"{BASE_URL}/jobs/", json=job_data)
print("Job created:", response.json())

# 2. Upload candidate resume
files = {"file": open("candidate_resume.pdf", "rb")}
response = requests.post(f"{BASE_URL}/upload-resume/", files=files)
print("Resume uploaded:", response.json())

# Wait for processing
time.sleep(5)

# 3. Get top matching candidates for the job
response = requests.get(f"{BASE_URL}/jobs/PYTHON-SR-001/candidates?top_n=5")
candidates = response.json()
print(f"Found {len(candidates)} matching candidates")

# 4. Shortlist the top candidate
if candidates:
    top_candidate = candidates[0]
    email = top_candidate["email"]
    response = requests.post(f"{BASE_URL}/candidates/{email}/shortlist/PYTHON-SR-001")
    print("Interview scheduled:", response.json())

# 5. Get interview details
response = requests.get(f"{BASE_URL}/interviews/")
interviews = response.json()
print(f"Total interviews: {len(interviews)}")
```

### Example 2: Candidate Profile Enrichment

```python
import requests

BASE_URL = "http://localhost:8000"
candidate_email = "deepesh.Yadav@example.com"
job_id = "JOB-001"

# Trigger profile enrichment (GitHub + public search)
response = requests.post(
    f"{BASE_URL}/candidates/{candidate_email}/enrich",
    params={"job_id": job_id}
)

enrichment_result = response.json()
print("Enrichment complete!")
print(f"GitHub Analysis: {enrichment_result.get('github_analysis')}")
print(f"Public Profile: {enrichment_result.get('public_profile')}")
print(f"Comprehensive Profile: {enrichment_result.get('enriched_profile')}")
```

### Example 3: Bulk Candidate Upload

```python
import requests
import os

BASE_URL = "http://localhost:8000"
resume_folder = "./resumes"

for filename in os.listdir(resume_folder):
    if filename.endswith((".pdf", ".docx")):
        filepath = os.path.join(resume_folder, filename)
        
        with open(filepath, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload-resume/", files=files)
            
            if response.status_code == 200:
                print(f"✅ {filename} uploaded successfully")
            else:
                print(f"❌ {filename} failed: {response.text}")
```

---

## 👥 Agent Details

### 1️⃣ Orchestrator Agent
**Role**: Master Coordinator (Hierarchical Manager)

**Responsibilities**:
- End-to-end workflow coordination
- Delegate tasks to specialized agents
- Monitor process completion
- Handle errors and retries
- Decision routing

**Key Methods**:
- `process_candidate_application()` - Complete resume processing
- `process_job_application()` - Job-specific applications
- `enrich_candidate_profile()` - GitHub + public search enrichment
- `process_candidate_shortlisting()` - Create interviews
- `process_post_interview_decision()` - Final hiring decision
- `reject_candidate()` - Rejection workflow

---

### 2️⃣ Resume Parsing Agent
**Role**: Document Processor

**Tools**: Resume Parser Tool, Database Tool, Vector Search Tool

**Capabilities**:
- Extract text from PDF/DOCX
- Parse using spaCy NLP
- LLM-powered structured extraction
- Validate and normalize data
- Store in MongoDB + FAISS

**Output**:
```json
{
  "name": "deepesh Yadav",
  "email": "deepesh@example.com",
  "phone": "+1234567890",
  "skills": ["Python", "FastAPI", "MongoDB"],
  "experience_years": 5,
  "education": "BS Computer Science",
  "resume_text": "Full extracted text...",
  "github_url": "https://github.com/deepeshYadav"
}
```

---

### 3️⃣ Matching Agent
**Role**: Intelligent Job Matcher

**Tools**: Database Tool, Vector Search Tool (FAISS)

**Algorithm**:
1. Convert job description to embeddings
2. Perform semantic search in FAISS
3. Retrieve top-N similar candidates
4. LLM re-ranks based on context
5. Calculate final match score (0-100)

**Features**:
- Multi-dimensional matching (skills, experience, education)
- Semantic understanding beyond keyword matching
- Context-aware ranking

---

### 4️⃣ Interview Agent
**Role**: AI Interviewer

**Tools**: Database Tool, Groq LLM, Audio Transcription

**Capabilities**:
- Generate contextual questions
- Transcribe candidate audio responses
- Analyze answer quality
- Adaptive questioning based on responses
- Final evaluation and scoring

**Interview Flow**:
1. Fetch job requirements
2. Generate opening question
3. Listen to candidate (WebSocket)
4. Transcribe audio → text
5. Analyze response
6. Generate follow-up question
7. Repeat for 5 rounds
8. Evaluate overall performance

---

### 5️⃣ GitHub Agent
**Role**: Repository Analyzer

**Tools**: GitHub API, LLM Analysis

**Capabilities**:
- Find most relevant repository
- Analyze code quality
- Extract technologies used
- Assess project complexity
- Evaluate contribution patterns

**Output**:
```json
{
  "repo_url": "https://github.com/deepeshYadav/ai-project",
  "technologies": ["Python", "TensorFlow", "FastAPI"],
  "quality_score": 8.5,
  "relevance_to_job": "High - demonstrates ML expertise"
}
```

---

### 6️⃣ Public Search Agent
**Role**: Online Presence Researcher

**Tools**: DuckDuckGo Search, Web Scraping

**Capabilities**:
- Search for candidate's public profiles
- Find LinkedIn, portfolio, blog
- Gather professional achievements
- Assess online reputation

---

### 7️⃣ Synthesizer Agent
**Role**: Profile Consolidator

**Capabilities**:
- Merge resume + GitHub + public data
- Create comprehensive candidate profile
- Generate executive summary
- Highlight key strengths
- Identify red flags

---

### 8️⃣ Scheduling Agent
**Role**: Interview Coordinator

**Tools**: Google Calendar API, Database Tool

**Capabilities**:
- Find available time slots
- Book calendar events
- Generate Google Meet links
- Send calendar invites
- Handle rescheduling

---

### 9️⃣ Communication Agent
**Role**: Candidate Liaison

**Tools**: Email Tool (SMTP), Database Tool

**Email Templates**:
- Application confirmation
- Interview invitation
- Interview reminder
- Offer letter
- Rejection notice

**Features**:
- Personalized messaging
- HTML email formatting
- Attachment support
- Error handling and retries

---

### 🔟 Compliance Agent
**Role**: Ethics & Compliance Officer

**Capabilities**:
- Detect biased language in resumes
- Flag PII (Personally Identifiable Info)
- Monitor fair evaluation standards
- Generate audit logs
- GDPR compliance checks

**Bias Detection**:
- Age discrimination
- Gender bias
- Racial indicators
- Religious references

**Logging**:
All actions logged to `compliance_logs` collection with:
- Timestamp
- Action type
- Bias scan results
- User responsible
- Outcome

---

### 1️⃣1️⃣ Decision Agent
**Role**: Final Decision Maker

**Input**:
- Interview score
- Resume match score
- Compliance flags
- GitHub analysis (if available)

**Output**:
- `HIRE` - Score > 70, no compliance issues
- `REJECT` - Score < 70 or compliance flags
- `UNDER_REVIEW` - Borderline cases

---

### 1️⃣2️⃣ Sourcing Agent
**Role**: Proactive Candidate Finder

**Capabilities** (Future):
- Search job boards
- Scrape LinkedIn
- Find passive candidates
- Build talent pipeline

---

## 🗄️ Database Schema

### MongoDB Collections

#### **candidates**
```javascript
{
  _id: ObjectId("..."),
  name: "deepesh Yadav",
  email: "deepesh@example.com",
  phone: "+1234567890",
  skills: ["Python", "FastAPI", "MongoDB"],
  experience_years: 5,
  education: "BS Computer Science",
  resume_text: "Full resume content...",
  resume_file_path: "/uploads/resume_20240123.pdf",
  profile_image_path: "/uploads/profile_images/deepesh_Yadav.jpg",
  github_url: "https://github.com/deepeshYadav",
  matched_jobs: [
    {
      job_id: "JOB-001",
      match_score: 85.5,
      matched_at: ISODate("2024-01-23T10:00:00Z")
    }
  ],
  status: "pending", // pending, shortlisted, interviewed, hired, rejected
  score: 85,
  enrichment: {
    github_analysis: {...},
    public_profile: {...},
    enriched_summary: "..."
  },
  created_at: ISODate("2024-01-23T10:00:00Z"),
  updated_at: ISODate("2024-01-23T10:00:00Z")
}
```

#### **jobs**
```javascript
{
  _id: ObjectId("..."),
  job_id: "JOB-001",
  title: "Senior Python Developer",
  description: "We are looking for...",
  required_skills: ["Python", "FastAPI", "MongoDB"],
  experience_required: 5,
  location: "Remote",
  employment_type: "full-time",
  status: "active", // active, closed, on_hold
  matched_candidates: [
    {
      email: "deepesh@example.com",
      score: 85.5,
      matched_at: ISODate("2024-01-23T10:00:00Z")
    }
  ],
  created_at: ISODate("2024-01-23T09:00:00Z"),
  updated_at: ISODate("2024-01-23T10:00:00Z")
}
```

#### **interviews**
```javascript
{
  _id: ObjectId("..."),
  interview_id: "INT-001",
  candidate_email: "deepesh@example.com",
  candidate_id: ObjectId("..."),
  job_id: "JOB-001",
  scheduled_time: ISODate("2024-01-25T14:00:00Z"),
  duration_minutes: 30,
  meeting_link: "https://meet.google.com/abc-def-ghi",
  status: "pending_ai_interview", // scheduled, pending_ai_interview, completed_ai_interview, cancelled
  interview_type: "ai_interview",
  evaluation: {
    score: 78,
    strengths: ["Strong Python skills", "Good problem solving"],
    weaknesses: ["Limited MongoDB experience"],
    recommendation: "HIRE"
  },
  interview_score: 78,
  created_at: ISODate("2024-01-23T10:00:00Z"),
  updated_at: ISODate("2024-01-25T14:30:00Z")
}
```

#### **interview_verifications**
```javascript
{
  _id: ObjectId("..."),
  interview_id: "INT-001",
  status: "uploaded", // uploaded, verified, failed
  id_card_path: "/uploads/interview_verification/INT-001/id_card.jpg",
  candidate_photo_path: "/uploads/interview_verification/INT-001/photo.jpg",
  face_match_score: 0.95,
  created_at: ISODate("2024-01-25T13:55:00Z"),
  updated_at: ISODate("2024-01-25T13:55:00Z")
}
```

#### **interview_snapshots**
```javascript
{
  _id: ObjectId("..."),
  interview_id: "INT-001",
  snapshot_path: "/uploads/interview_snapshots/INT-001/snapshot_001.jpg",
  created_at: ISODate("2024-01-25T14:05:00Z")
}
```

#### **compliance_logs**
```javascript
{
  _id: ObjectId("..."),
  action_type: "resume_scan", // resume_scan, proctoring_event, bias_detection
  interview_id: "INT-001",
  event_type: "face_not_detected",
  message: "No face detected for 5 seconds",
  warnings: 1,
  bias_detected: false,
  flagged_content: [],
  timestamp: ISODate("2024-01-25T14:05:00Z"),
  created_at: ISODate("2024-01-25T14:05:00Z")
}
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | Groq API key for LLM |
| `MONGODB_URL` | ✅ Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | No | `recruiting_system` | Database name |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` | Groq model name |
| `EMBEDDING_MODEL` | No | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `SMTP_HOST` | No | `smtp.gmail.com` | Email server |
| `SMTP_PORT` | No | `587` | Email port |
| `SMTP_USERNAME` | No | - | Email username |
| `SMTP_PASSWORD` | No | - | Email password |
| `GOOGLE_CLIENT_ID` | No | - | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | No | - | Google OAuth secret |
| `GITHUB_API_TOKEN` | No | - | GitHub API token |
| `DEBUG` | No | `True` | Debug mode |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `FRONTEND_URL` | No | `http://127.0.0.1:5500` | Frontend URL for CORS |

### Model Configuration

Edit `config/settings.py` to customize:

```python
class Settings(BaseSettings):
    # Change LLM model
    LLM_MODEL: str = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768"
    
    # Change embedding model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Vector store configuration
    VECTOR_STORE_PATH: str = "./data/vector_store"
    FAISS_INDEX_PATH: str = "./data/faiss_index"
```

---

## 🔒 Security & Compliance

### Security Features

✅ **Authentication**
- API key validation
- Google OAuth 2.0 support
- Secure token handling

✅ **Data Protection**
- MongoDB access control
- Encrypted credentials storage
- Secure file upload validation
- HTTPS support (production)

✅ **Privacy**
- GDPR-compliant data handling
- PII detection and masking
- Data retention policies
- Right to be forgotten (delete endpoint)

### Compliance Features

✅ **Bias Detection**
- Scans for discriminatory language
- Flags age/gender/race mentions
- Ensures fair evaluation

✅ **Audit Trail**
- Complete action logging
- Compliance log collection
- Timestamp tracking
- User attribution

✅ **Interview Proctoring**
- Face detection
- Multiple person detection
- ID verification
- Snapshot recording
- Event logging

### GDPR Compliance

```python
# Delete candidate data (Right to be forgotten)
DELETE /candidates/{email}

# Returns all candidate data (Right to access)
GET /candidates/{email}
```

---

## 📈 Monitoring

### Logging

Logs are stored in `logs/` directory with automatic rotation:

- **Application logs**: `logs/app.log`
- **Agent interactions**: Detailed agent task logs
- **Tool executions**: Database, email, calendar operations
- **Error traces**: Full stack traces for debugging

**Log Levels**:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical failures

### System Statistics

```bash
curl http://localhost:8000/stats
```

**Response**:
```json
{
  "success": true,
  "stats": {
    "total_candidates": 127,
    "active_jobs": 15,
    "interviews_scheduled": 42,
    "vector_count": 127,
    "analytics": {
      "interviews_breakdown": {
        "scheduled": 12,
        "completed": 30
      },
      "average_score": 73.5
    }
  }
}
```

### Health Monitoring

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## 🐳 Deployment

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs data/vector_store data/faiss_index

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: recruiting_mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: recruiting_system

  app:
    build: .
    container_name: recruiting_app
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - MONGODB_URL=mongodb://mongodb:27017
      - DEBUG=False
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./data:/app/data

volumes:
  mongodb_data:
```

**Build and Run**:
```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Production Deployment

1. **Set production environment variables**:
```env
DEBUG=False
MONGODB_URL=mongodb://production-server:27017
GROQ_API_KEY=prod_key_here
```

2. **Use a reverse proxy (Nginx)**:
```nginx
server {
    listen 80;
    server_name recruiting.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Use a process manager (systemd)**:
```ini
[Unit]
Description=AI Recruiting System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/recruiting-system
ExecStart=/opt/recruiting-system/lang_venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🤝 Contributing

We welcome contributions! Here are some ways you can help:

### Extension Points

1. **Add New Tools** (MCP-compliant)
   - SMS notification tool
   - Slack integration
   - Video interview analysis

2. **Create Specialized Agents**
   - Salary negotiation agent
   - Onboarding agent
   - Reference check agent

3. **Implement New LLM Providers**
   - OpenAI GPT-4
   - Anthropic Claude
   - Local LLMs (Ollama)

4. **Enhance Matching Algorithm**
   - Add soft skills matching
   - Cultural fit analysis
   - Team compatibility scoring

5. **Add More Communication Channels**
   - SMS notifications (Twilio)
   - Slack/Teams integration
   - WhatsApp messaging

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Troubleshooting

### Common Issues

**Issue**: MongoDB connection failed
```
Solution: Ensure MongoDB is running on localhost:27017
$ mongod
```

**Issue**: Groq API rate limit exceeded
```
Solution: Wait a few minutes or upgrade your Groq API plan
```

**Issue**: Resume parsing fails
```
Solution: 
1. Check file format (PDF, DOCX only)
2. Ensure file size < 10MB
3. Check logs/app.log for details
```

**Issue**: Vector search returns no results
```
Solution:
1. Ensure candidates are processed first
2. Check FAISS index exists in data/faiss_index
3. Rebuild index: Delete data/faiss_index and re-upload resumes
```

### Getting Help

1. **Check API Documentation**: http://localhost:8000/docs
2. **Review Logs**: `logs/app.log`
3. **Test MongoDB Connection**: `curl http://localhost:8000/health`
4. **Verify Environment**: Check `.env` file configuration

### Contact

For issues or questions:
1. Check API docs at `/docs`
2. Review logs in `logs/` directory
3. Check MongoDB connection
4. Verify Groq API key

---

**Built with**: CrewAI, FastAPI, Groq, MongoDB, FAISS, LlamaIndex

**Architecture**: Hierarchical Multi-Agent System with MCP

**Status**: Production Ready ✅
