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

## API Endpoints

### Core API
- `GET /api/health` - Health check
- `POST /api/evaluations/apply` - Create vendor application
- `POST /api/evaluations/assess` - Create vendor assessment
- `GET /api/evaluations/{id}` - Get evaluation
- `GET /api/evaluations` - List evaluations

### Workflow API
- `POST /api/workflows/application/{id}/run` - Run application workflow
- `POST /api/workflows/assessment/{id}/run` - Run assessment workflow

## Environment Variables

See `.env.example` for required environment variables:
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB_NAME` - Database name
- `NEMOTRON_API_URL` - Nemotron API endpoint
- `NEMOTRON_API_KEY` - Nemotron API key
- `UPLOAD_DIR` - Directory for file uploads
- `NEXT_PUBLIC_API_URL` - Backend API URL for frontend

## Notes

- This is a skeleton structure. Most functions have TODO comments indicating what needs to be implemented.
- File uploads are saved to `backend/uploads/` directory
- MongoDB collection name is `evaluations`
- No authentication is implemented for MVP
- Agent workflows run synchronously (can be made async later)

## License

MIT
