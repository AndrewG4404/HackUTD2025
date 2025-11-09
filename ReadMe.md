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
- `GET /api/workflows/{id}/stream` - **Stream real-time agent progress (SSE)**

### Real-Time Agent Visualization
- `GET /api/workflows/{id}/stream` - Server-Sent Events endpoint that streams live agent progress
  - Emits events as agents execute: `agent_start`, `agent_thinking`, `agent_complete`, `workflow_complete`
  - Each event includes: agent name, status, reasoning, outputs, and timestamps
  - Frontend displays live workflow visualization with agent-to-agent communication

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

**Real-Time Agent Visualization** 🎬
- **Live workflow streaming** via Server-Sent Events (SSE)
- **Visual agent-to-agent communication** - see agents reasoning and passing context
- **Synchronous progress updates** - watch analysis happen in real-time
- **Reasoning transparency** - view actual Nemotron model outputs and agent decisions
- **Event stream includes:**
  - Agent start/complete events with timestamps
  - LLM reasoning outputs (actual prompts and responses)
  - Context passing between agents (what each agent sends to the next)
  - Document discoveries and web scraping progress
  - Scoring decisions and findings extraction
  - Final recommendations and reasoning

**Nemotron Client** (`backend/services/nemotron_client.py`)
- OpenAI-compatible client for NVIDIA Nemotron API
- **Supports both cloud API and local NIM deployment**
- Automatically detects endpoint from `NEMOTRON_API_URL`
- Chat completion with JSON support
- **Intelligent documentation discovery** - LLM-powered URL discovery
- Web scraping with content extraction
- Automatic fallback to common documentation patterns

**Document Processor** (`backend/services/document_processor.py`)
- PDF text extraction with PyPDF2
- Simple RAG retrieval (context-based search)
- Text chunking utilities

**7 Specialized Agents** (`backend/services/agents/`)

All agents now feature **intelligent documentation discovery and analysis**:

1. **IntakeAgent** - Normalizes vendor data and extracts basic info
2. **VerificationAgent** - Fact-checks claims against official website
3. **ComplianceAgent** - Evaluates compliance with RAG
   - Automatically discovers privacy/security documentation
   - Analyzes data ownership, retention, usage policies
   - Checks GDPR, CCPA, HIPAA, SOC2, ISO27001 compliance
4. **InteroperabilityAgent** - Assesses technical fit
   - Discovers and analyzes API/technical documentation
   - Evaluates REST, GraphQL, SSO, webhooks, SDKs
   - Estimates integration complexity and dev effort
5. **FinanceAgent** - Analyzes pricing and TCO
   - Discovers official pricing documentation
   - Evaluates pricing models, hidden costs, ROI
   - Estimates TCO for 200-user deployment
6. **AdoptionAgent** - Evaluates support capabilities
   - Discovers support and training documentation
   - Assesses implementation timeline, SLAs, support channels
   - Evaluates training resources and adoption complexity
7. **SummaryAgent** - Aggregates results and provides final recommendation

**Application Pipeline** (`backend/services/workflows/application_pipeline.py`)
- Sequential agent orchestration (ReAct pattern)
- Progress tracking and error handling
- MongoDB integration

### 🔍 Key Features - Intelligent RAG on Live Documentation

Each agent now **automatically discovers and analyzes official vendor documentation**:

1. **Documentation Discovery**: LLM intelligently finds relevant docs (privacy, pricing, API, support)
2. **Live Web Scraping**: Fetches and analyzes current official documentation
3. **RAG-Enhanced Analysis**: Retrieves relevant context from discovered docs
4. **Comprehensive Evaluation**: Enterprise-grade compliance and technical assessments

**Example workflow:**
- User provides: `company_name="ServiceNow"`, `website="https://servicenow.com"`
- Compliance Agent:
  - Discovers: `/privacy-policy`, `/trust`, `/security`
  - Fetches and analyzes official documentation
  - Performs GDPR, SOC2, data retention analysis
- Finance Agent:
  - Discovers: `/pricing`, `/plans`
  - Analyzes pricing models and TCO
- Interoperability Agent:
  - Discovers: `/developers`, `/api-docs`
  - Evaluates REST API, SSO, webhooks

### 🧪 Testing

```bash
# Test the agent workflow
python backend/test_agent_workflow.py

# Test with a real vendor (e.g., ServiceNow, Salesforce)
# Agents will automatically discover and analyze their documentation!

# Or test via API after starting the backend
curl -X POST "http://localhost:8000/api/workflows/application/{evaluation_id}/run"

# Watch real-time agent progress (SSE stream)
curl -N -H "Accept: text/event-stream" \
  "http://localhost:8000/api/workflows/{evaluation_id}/stream"
```

### 🎬 Real-Time Workflow Visualization

The frontend displays a **live agentic workflow visualization** showing:

1. **Agent Pipeline View**
   - Sequential agent execution flow (Intake → Verification → Compliance → etc.)
   - Current active agent highlighted with pulsing animation
   - Completed agents show checkmarks with execution time
   - Failed agents show error indicators

2. **Agent Communication Panel**
   - Live LLM reasoning outputs from Nemotron
   - Context being passed between agents
   - Document discoveries and analysis snippets
   - Real-time score calculations and findings

3. **Event Timeline**
   - Chronological log of all agent activities
   - Timestamps and durations for each step
   - Expandable details for each event (prompts, responses, context)

**For Judges**: Navigate to `/evaluations/{id}` immediately after starting a workflow to see the live visualization in action. The page will show agents reasoning, discovering documentation, and building the evaluation in real-time.

### 🏗️ Implementation Architecture

**Backend (Python/FastAPI):**
- **SSE Endpoint**: `GET /api/workflows/{evaluation_id}/stream`
  - Uses `fastapi.responses.StreamingResponse` with `text/event-stream` media type
  - Yields SSE-formatted events during workflow execution
  - Event format: `event: {type}\ndata: {json}\n\n`

- **Agent Event Emitter**: Base class method for agents to emit events
  - `emit_event(event_type, data)` - publishes event to SSE stream
  - Called at key points: start, LLM calls, discoveries, completion
  - Includes timestamps, agent name, role, and context

- **Modified Pipeline**: Workflows stream events in real-time
  - Before agent execution: emit `agent_start`
  - During LLM calls: emit `agent_thinking` with prompt preview
  - During processing: emit `agent_progress` for discoveries/analysis
  - After agent execution: emit `agent_complete` with outputs
  - At workflow end: emit `workflow_complete` with final results

**Frontend (Next.js/React):**
- **EventSource API**: Native browser SSE client
  - Connects to `/api/workflows/{id}/stream` when evaluation page loads
  - Listens for event types and updates UI state
  - Automatically reconnects on connection loss

- **Live Visualization Components**:
  - `<AgentPipeline>` - Shows agent flow with current status
  - `<AgentReasoningPanel>` - Displays live LLM outputs and context
  - `<EventTimeline>` - Chronological log with expandable details

- **State Management**: React state hooks for real-time updates
  - Current active agent, completed agents, event history
  - Auto-scrolling to latest event, pulsing animations
  - Preserves events after workflow completion for review

**Event Examples:**
```typescript
// agent_start
{ agent_name: "ComplianceAgent", role: "Compliance Officer", timestamp: "..." }

// agent_thinking
{ agent_name: "ComplianceAgent", action: "Discovering privacy docs", 
  prompt_preview: "Find privacy documentation for...", llm_model: "nemotron" }

// agent_progress  
{ agent_name: "ComplianceAgent", message: "Found 3 documentation URLs",
  urls: ["https://vendor.com/privacy", ...], timestamp: "..." }

// agent_complete
{ agent_name: "ComplianceAgent", outputs: { score: 4.2, findings: [...] },
  duration_ms: 5432, timestamp: "..." }
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