# 📁 Complete Project Structure

## Full Directory Tree

```
ai-recruiting-system/
│
├── 📄 main.py                          # FastAPI app entry + frontend serving
├── 📄 requirements.txt                 # Python dependencies
├── 📄 setup.py                         # Setup automation script
├── 📄 test_system.py                   # System testing script
├── 📄 .env                            # Environment variables
├── 📄 README.md                       # Main documentation
├── 📄 QUICKSTART.md                   # Quick start guide
├── 📄 PROJECT_STRUCTURE.md            # This file
│
├── 📁 agents/                          # 6 Intelligent Agents
│   ├── __init__.py
│   ├── 🤖 orchestrator_agent.py       # Hierarchical manager
│   ├── 🤖 resume_parsing_agent.py     # Resume processor
│   ├── 🤖 matching_agent.py           # RAG-based matcher
│   ├── 🤖 scheduling_agent.py         # Interview scheduler
│   ├── 🤖 communication_agent.py      # Email handler
│   └── 🤖 compliance_agent.py         # Bias detection
│
├── 📁 tools/                           # 5 MCP Tools
│   ├── __init__.py
│   ├── 🛠️ resume_parser_tool.py       # PDF/DOCX parser
│   ├── 🛠️ database_tool.py            # MongoDB operations
│   ├── 🛠️ vector_search_tool.py       # FAISS + RAG
│   ├── 🛠️ email_tool.py               # SMTP emailer
│   └── 🛠️ calendar_tool.py            # Calendar API
│
├── 📁 models/                          # Data Models
│   ├── __init__.py
│   ├── 📋 candidate.py                # Candidate schema
│   ├── 📋 job_posting.py              # Job schema
│   └── 📋 interview.py                # Interview schema
│
├── 📁 database/                        # Database Layer
│   ├── __init__.py
│   ├── 💾 mongodb_client.py           # MongoDB async client
│   └── 💾 vector_store.py             # FAISS vector DB
│
├── 📁 llm/                             # LLM Layer
│   ├── __init__.py
│   ├── 🧠 groq_client.py              # Groq API (Llama3-70B)
│   └── 🧠 embeddings.py               # MiniLM embeddings
│
├── 📁 api/                             # FastAPI Routes
│   ├── __init__.py
│   ├── 🔧 middleware.py               # Custom middlewares
│   └── 📁 routes/
│       ├── __init__.py
│       ├── 📡 upload.py               # Resume upload endpoints
│       ├── 📡 jobs.py                 # Job CRUD endpoints
│       ├── 📡 candidates.py           # Candidate endpoints
│       └── 📡 interviews.py           # Interview endpoints
│
├── 📁 mcp/                             # Model Context Protocol
│   ├── __init__.py
│   ├── 🔌 mcp_server.py               # MCP server implementation
│   └── 🔌 mcp_tools.py                # Tool definitions
│
├── 📁 crew/                            # CrewAI Configuration
│   ├── __init__.py
│   └── 👥 crew_config.py              # Hierarchical crew setup
│
├── 📁 config/                          # Configuration
│   ├── __init__.py
│   └── ⚙️ settings.py                  # App settings
│
├── 📁 utils/                           # Utilities
│   ├── __init__.py
│   ├── 📝 logger.py                   # Loguru logging
│   └── 📂 file_handler.py             # File operations
│
├── 📁 frontend/                        # Web Dashboard
│   ├── 🎨 index.html                  # React SPA dashboard
│   └── 📄 README.md                   # Frontend docs
│
├── 📁 uploads/                         # Uploaded resumes
│   └── .gitkeep
│
├── 📁 logs/                            # Application logs
│   └── recruiting_system_*.log
│
└── 📁 data/                            # Data storage
    ├── vector_store/                  # FAISS index
    └── faiss_index                    # Vector index files
```

## 🏗️ Architecture Overview

### Layer 1: API Layer (FastAPI)
```
Frontend (React)
     ↓
FastAPI Routes
     ↓
Middleware (Logging, Rate Limit, CORS)
```

### Layer 2: Agent Layer (CrewAI)
```
Orchestrator Agent (Manager)
     ↓
├── Resume Parsing Agent
├── Matching Agent (RAG)
├── Scheduling Agent
├── Communication Agent
└── Compliance Agent
```

### Layer 3: Tool Layer (MCP)
```
MCP Server
     ↓
├── Resume Parser Tool
├── Database Tool
├── Vector Search Tool
├── Email Tool
└── Calendar Tool
```

### Layer 4: Data Layer
```
MongoDB (Async)          FAISS Vector Store
     ↓                         ↓
Collections:             Embeddings:
- candidates            - Candidate profiles
- jobs                  - Job descriptions
- interviews            - Semantic search
- compliance_logs
- audit_logs
```

### Layer 5: LLM Layer
```
Groq API (Llama3-70B)    MiniLM Embeddings
     ↓                         ↓
- Resume parsing         - Vector generation
- Job matching          - Similarity search
- Reasoning             - RAG retrieval
- Scoring
```

## 🔄 Data Flow

### Resume Upload Flow
```
1. Frontend → POST /upload/resume
2. FastAPI → Orchestrator Agent
3. Orchestrator → Resume Parsing Agent
4. Resume Parser Tool → Extract text
5. Groq LLM → Parse structured data
6. Database Tool → Save candidate
7. MiniLM → Generate embeddings
8. Vector Store → Add to FAISS
9. Compliance Agent → Bias scan
10. Matching Agent → Find jobs (RAG)
11. Database Tool → Update scores
12. Communication Agent → Send email
13. FastAPI → Return result
14. Frontend → Show notification
```

### Job Matching Flow (RAG)
```
1. Candidate profile → MiniLM → Vector
2. FAISS → Semantic search → Top jobs
3. Vector Search Tool → Retrieve context
4. Groq LLM → Refine matches + reasoning
5. Matching Agent → Calculate scores
6. Database Tool → Update candidate
7. Return ranked job matches
```

### Interview Scheduling Flow
```
1. Recruiter → Shortlist candidate
2. Orchestrator → Scheduling Agent
3. Calendar Tool → Find available slots
4. Calendar Tool → Book slot
5. Database Tool → Save interview
6. Communication Agent → Send invitation
7. Email Tool → Send email
8. Return confirmation
```

## 📊 Component Responsibilities

### Agents (What they do)
| Agent | Responsibility | Tools Used |
|-------|---------------|------------|
| **Orchestrator** | Workflow coordination | All agents |
| **Resume Parsing** | Extract resume data | Resume Parser, Database, Vector Search |
| **Matching** | Match candidates to jobs | Database, Vector Search, LLM |
| **Scheduling** | Book interviews | Calendar, Database |
| **Communication** | Send emails | Email, Database |
| **Compliance** | Bias detection, auditing | Database, LLM |

### Tools (What they provide)
| Tool | Capability | Used By |
|------|-----------|---------|
| **Resume Parser** | Extract text from PDF/DOCX | Resume Parsing Agent |
| **Database** | CRUD operations | All agents |
| **Vector Search** | Semantic search, RAG | Matching Agent |
| **Email** | Send notifications | Communication Agent |
| **Calendar** | Schedule management | Scheduling Agent |

### Models (What they store)
| Model | Fields | Collections |
|-------|--------|-------------|
| **Candidate** | name, email, skills, score, resume_text | candidates |
| **Job** | title, description, required_skills | jobs |
| **Interview** | candidate_id, job_id, time, status | interviews |

## 🔌 API Endpoints Map

### Upload Endpoints
```
POST   /upload/resume           # Upload single resume
POST   /upload/resume/batch     # Upload multiple resumes
```

### Job Endpoints
```
POST   /jobs/                   # Create job
GET    /jobs/                   # List jobs
GET    /jobs/{job_id}           # Get job details
PUT    /jobs/{job_id}           # Update job
DELETE /jobs/{job_id}           # Delete job
GET    /jobs/{job_id}/candidates # Top candidates for job
```

### Candidate Endpoints
```
GET    /candidates/             # List candidates
GET    /candidates/{email}      # Get candidate
PUT    /candidates/{email}      # Update candidate
DELETE /candidates/{email}      # Delete candidate
POST   /candidates/{email}/rematch # Re-match jobs
POST   /candidates/{email}/shortlist/{job_id} # Shortlist
POST   /candidates/{email}/reject/{job_id}    # Reject
```

### Interview Endpoints
```
POST   /interviews/             # Create interview
GET    /interviews/             # List interviews
GET    /interviews/{id}         # Get interview
PUT    /interviews/{id}         # Update interview
DELETE /interviews/{id}         # Cancel interview
POST   /interviews/{id}/send-reminder # Send reminder
GET    /interviews/available-slots/   # Get slots
```

### System Endpoints
```
GET    /                        # Dashboard (frontend)
GET    /health                  # Health check
GET    /stats                   # System statistics
GET    /agents/status           # Agent status
GET    /mcp/tools               # MCP tools list
```

## 🧩 Integration Points

### External Services
```
┌─────────────────────────────────────────┐
│          AI Recruiting System           │
├─────────────────────────────────────────┤
│  Groq API        → LLM reasoning        │
│  MongoDB         → Data persistence     │
│  SMTP Server     → Email sending        │
│  Google Calendar → Interview scheduling │
└─────────────────────────────────────────┘
```

### Internal Communication
```
Frontend ←→ FastAPI ←→ Agents ←→ Tools ←→ Services
   ↓          ↓          ↓         ↓         ↓
 React    REST API   CrewAI     MCP    Groq/MongoDB
```

## 📦 Package Dependencies

### Core Frameworks
- **FastAPI**: Web framework
- **CrewAI**: Multi-agent orchestration
- **LangChain**: LLM framework
- **LlamaIndex**: Document processing

### AI/ML
- **Groq**: LLM API client
- **Sentence-Transformers**: Embeddings
- **FAISS**: Vector search
- **spaCy**: NLP processing

### Database
- **PyMongo**: MongoDB sync client
- **Motor**: MongoDB async client

### Utilities
- **Pydantic**: Data validation
- **Loguru**: Logging
- **Python-dotenv**: Environment variables

## 🔐 Security Layers

### Authentication & Authorization
- API key authentication (future)
- Role-based access control (future)
- JWT tokens (future)

### Data Protection
- Environment variables for secrets
- MongoDB access control
- HTTPS for production
- Rate limiting middleware

### Compliance
- Bias detection in AI
- Audit logging
- GDPR-compliant data handling
- Secure file uploads

## 🚀 Deployment Architecture

### Development
```
localhost:8000 (FastAPI)
localhost:27017 (MongoDB)
File system (Uploads, Logs)
```

### Production (Recommended)
```
┌──────────────────────────────────────┐
│         Load Balancer (Nginx)        │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│    FastAPI (Uvicorn/Gunicorn)       │
│    Docker Container × N              │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│    MongoDB Cluster (Atlas/Self-host) │
└──────────────────────────────────────┘
```

## 📈 Scalability

### Horizontal Scaling
- Multiple FastAPI instances
- Load balancer distribution
- Stateless API design
- Shared MongoDB cluster

### Vertical Scaling
- Increase MongoDB resources
- GPU for embeddings
- Redis caching layer
- CDN for frontend

## 🧪 Testing Structure

### Unit Tests
```
tests/
├── test_agents.py
├── test_tools.py
├── test_models.py
└── test_api.py
```

### Integration Tests
```
test_system.py  # Full workflow tests
```

### Performance Tests
```
tests/
└── test_performance.py  # Load testing
```

## 📝 Configuration Files

### Environment (.env)
```
GROQ_API_KEY=xxx
MONGODB_URL=mongodb://localhost:27017
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Settings (config/settings.py)
```python
- API configuration
- Database URLs
- Model parameters
- File upload limits
```

## 🔄 Workflow Patterns

### Hierarchical Pattern (CrewAI)
```
Orchestrator (Manager)
    ↓ delegates to
Sub-Agents (Workers)
    ↓ use
Tools (Executors)
    ↓ interact with
Services (External)
```

### MCP Pattern
```
Agent Request
    ↓
MCP Server (Standardization)
    ↓
Tool Execution
    ↓
Standardized Response
```

### RAG Pattern
```
Query
    ↓
Generate Embedding
    ↓
Vector Search (FAISS)
    ↓
Retrieve Context
    ↓
LLM Processing
    ↓
Refined Result
```

## 💡 Key Features by File

| File | Key Feature |
|------|-------------|
| `orchestrator_agent.py` | Hierarchical workflow coordination |
| `matching_agent.py` | RAG-based semantic matching |
| `vector_search_tool.py` | FAISS semantic search |
| `mcp_server.py` | Standardized tool protocol |
| `groq_client.py` | Llama3-70B integration |
| `embeddings.py` | MiniLM-L6-v2 vectors |
| `frontend/index.html` | React dashboard UI |

## 🎯 System Capabilities

✅ **Automated**: End-to-end resume processing
✅ **Intelligent**: AI-powered matching with RAG
✅ **Scalable**: Microservices-ready architecture
✅ **Compliant**: Bias detection & audit trails
✅ **User-Friendly**: Beautiful web dashboard
✅ **Extensible**: Plugin-based tool system (MCP)
✅ **Production-Ready**: Error handling, logging, monitoring

## 📚 Documentation Files

- `README.md` - Main documentation
- `QUICKSTART.md` - 5-minute setup guide
- `PROJECT_STRUCTURE.md` - This file
- `frontend/README.md` - Frontend guide
- API Docs - http://localhost:8000/docs (auto-generated)

---

**Total Files**: 40+ Python files, 1 HTML frontend, 5 documentation files
**Total Lines**: ~8,000+ lines of production-ready code
**Architecture**: Multi-agent, hierarchical, MCP-compliant, RAG-enabled