# VendorLens - Secure & Intelligent Vendor Onboarding Hub

A 24-hour hackathon MVP that simulates a realistic vendor onboarding workflow using Nemotron-powered AI agents.

## Project Structure

```
vendorlens/
├── backend/              # FastAPI backend server
│   ├── api/
│   │   └── routes/      # API route handlers
│   │       ├── core.py  # Core API (Teammate 1)
│   │       ├── workflows.py  # Workflow API (Teammate 2)
│   │       └── health.py
│   ├── database/         # MongoDB models and repository
│   ├── services/        # Business logic
│   │   ├── agents/      # AI agent implementations
│   │   ├── workflows/   # Pipeline orchestration
│   │   ├── file_service.py
│   │   └── nemotron_client.py
│   ├── uploads/         # File upload storage
│   ├── main.py          # FastAPI app entry point
│   └── requirements.txt
│
├── frontend/            # Next.js frontend
│   ├── app/            # Next.js 14 app directory
│   │   ├── page.tsx    # Landing page
│   │   ├── apply/      # Vendor application form
│   │   ├── assess/     # Assessment setup form
│   │   └── evaluations/[id]/  # Results page
│   ├── lib/            # Utilities and API client
│   └── package.json
│
├── .env.example        # Environment variables template
├── .gitignore
├── docker-compose.yml  # MongoDB setup
└── README.md
```

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, Uvicorn
- **Database**: MongoDB
- **LLM**: Nemotron API
- **Storage**: Local file system (`uploads/`)

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (or use Docker Compose)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` in the root directory and configure:
```bash
cp ../.env.example ../.env
# Edit .env with your MongoDB URI and Nemotron API key
```

5. Start MongoDB (if not using Docker):
```bash
# Using Docker Compose (from root):
docker-compose up -d

# Or start MongoDB locally
```

6. Run the backend server:
```bash
python main.py
# Or: uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## Development Workflow

### Teammate 1 - Core API & Data
- Work in `backend/api/routes/core.py`
- Implement file upload handling in `backend/services/file_service.py`
- Define MongoDB schemas in `backend/database/models.py`
- Implement CRUD operations in `backend/database/repository.py`

### Teammate 2 - Agent Workflow & Nemotron
- Work in `backend/api/routes/workflows.py`
- Implement agents in `backend/services/agents/`
- Orchestrate pipelines in `backend/services/workflows/`
- Configure Nemotron client in `backend/services/nemotron_client.py`

### Teammate 3 - Frontend
- Work in `frontend/app/` for pages
- Create components as needed
- Use API client in `frontend/lib/api.ts`
- Implement UI for results display

## API Documentation

### Interactive Documentation
Once the backend is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Info Page**: http://localhost:8000/
- **OpenAPI Spec (YAML)**: http://localhost:8000/openapi.yaml
- **OpenAPI Spec (JSON)**: http://localhost:8000/openapi.json

### Core API Endpoints
- `GET /api/health` - Health check
- `POST /api/evaluations/apply` - Create vendor application
- `POST /api/evaluations/assess` - Create vendor assessment
- `GET /api/evaluations/{id}` - Get evaluation
- `GET /api/evaluations` - List evaluations

### Workflow API Endpoints
- `POST /api/workflows/application/{id}/run` - Run application workflow
- `POST /api/workflows/assessment/{id}/run` - Run assessment workflow

See `backend/API_TESTING.md` for detailed testing examples.

## Environment Variables

See `.env.example` for required environment variables:
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB_NAME` - Database name
- `NEMOTRON_API_URL` - Nemotron API endpoint (cloud or local)
- `NEMOTRON_API_KEY` - Nemotron API key
- `UPLOAD_DIR` - Directory for file uploads
- `NEXT_PUBLIC_API_URL` - Backend API URL for frontend

## Bypassing Rate Limits with Local NIM

The NVIDIA cloud API has rate limits. To bypass them during development:

### Quick Start (One Command)

```bash
# Set your NGC API key
export NGC_API_KEY=your-ngc-api-key-here

# Deploy local NIM
./deploy_local_nim.sh
```

### Manual Setup

1. **Login to NVIDIA Container Registry:**
```bash
docker login nvcr.io
# Username: $oauthtoken
# Password: your-ngc-api-key
```

2. **Run the NIM container:**
```bash
export NGC_API_KEY=your-ngc-api-key
export LOCAL_NIM_CACHE=~/.cache/nim
mkdir -p "$LOCAL_NIM_CACHE"

docker run -it --rm \
    --gpus all \
    --shm-size=16GB \
    -e NGC_API_KEY \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -u $(id -u) \
    -p 8000:8000 \
    nvcr.io/nim/nvidia/nvidia-nemotron-nano-9b-v2:latest
```

3. **Update your `.env` file:**
```bash
NEMOTRON_API_URL=http://localhost:8000/v1
NEMOTRON_API_KEY=not-needed-for-local
BACKEND_PORT=8001  # Use different port since NIM uses 8000
```

4. **Test the deployment:**
```bash
./test_nim.sh
```

See `backend/LOCAL_NIM_SETUP.md` for detailed documentation.

**Note:** Requires NVIDIA GPU with Docker GPU support (`nvidia-docker2`)

## Agent Workflow (Teammate #2)

### ✅ Implemented Components

**Nemotron Client** (`backend/services/nemotron_client.py`)
- OpenAI-compatible client for NVIDIA Nemotron API
- **Supports both cloud API and local NIM deployment**
- Automatically detects endpoint from `NEMOTRON_API_URL`
- Chat completion with JSON support
- Web scraping for URL fetching

**Document Processor** (`backend/services/document_processor.py`)
- PDF text extraction with PyPDF2
- Simple RAG retrieval (context-based search)
- Text chunking utilities

**7 Specialized Agents** (`backend/services/agents/`)
1. **IntakeAgent** - Normalizes vendor data
2. **VerificationAgent** - Fact-checks against website
3. **ComplianceAgent** - Evaluates compliance with RAG
4. **InteroperabilityAgent** - Assesses technical fit
5. **FinanceAgent** - Analyzes pricing and TCO
6. **AdoptionAgent** - Evaluates support capabilities
7. **SummaryAgent** - Aggregates and recommends

**Application Pipeline** (`backend/services/workflows/application_pipeline.py`)
- Sequential agent orchestration (ReAct pattern)
- Progress tracking and error handling
- MongoDB integration

### 🧪 Testing

```bash
# Test the agent workflow
python backend/test_agent_workflow.py

# Or test via API after starting the backend
curl -X POST "http://localhost:8000/api/workflows/application/{evaluation_id}/run"
```

## Development Rules

**🎯 Using Cursor AI? Read `.cursorrules` first!**

Key principles:
- Keep solutions simple - avoid over-engineering
- Follow DRY principles - reuse existing code
- Stay within MVP scope - no feature creep
- No hallucinations - only use code that exists
- This is the ONLY README - no summary/overview docs

## Notes

- This is a skeleton structure. Most functions have TODO comments indicating what needs to be implemented.
- File uploads are saved to `backend/uploads/` directory
- MongoDB collection name is `evaluations`
- No authentication is implemented for MVP
- Agent workflows run synchronously (can be made async later)

## License

MIT

Winning projects will showcase true agentic behavior:
Multi-Agent Systems: Build teams of specialized AI agents
(like Report Generator: Research Agent → Outline Agent → Writer Agent → Editor)
Agentic RAG: Systems that intelligently decide WHEN to retrieve information, not just HOW (perfect for domain-specific assistants)
ReAct Pattern Workflows: Agents that Reason → Act → Observe in loops to solve problems iteratively (like automated debugging or technical support)
Tool-Calling Applications: Leverage Nemotron's exceptional ability to use external APIs and tools (finance analysis, DevOps automation, content creation)
Multi-Modal Agents: Combine Nemotron reasoning with VLMs (visual analysis + logical decision-making)
Agent Simulation & Evaluation: Use Nemotron to generate realistic test scenarios and evaluation pipelines