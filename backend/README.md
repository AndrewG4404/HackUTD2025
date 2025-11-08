# VendorLens Backend

FastAPI backend server for VendorLens.

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file (copy from `.env.example` in root):
```bash
cp ../.env.example ../.env
# Edit .env with your configuration
```

4. Start MongoDB (using Docker Compose from root):
```bash
cd ..
docker-compose up -d
```

5. Run the server:
```bash
python main.py
# Or: uvicorn main:app --reload
```

Server will run on `http://localhost:8000`

## Project Structure

- `api/routes/` - API route handlers
  - `core.py` - Core API endpoints (Teammate 1)
  - `workflows.py` - Workflow API endpoints (Teammate 2)
  - `health.py` - Health check endpoint
- `database/` - MongoDB models and repository
- `services/` - Business logic
  - `agents/` - AI agent implementations
  - `workflows/` - Pipeline orchestration
  - `file_service.py` - File upload handling
  - `nemotron_client.py` - Nemotron API client
- `uploads/` - File upload storage directory
- `main.py` - FastAPI application entry point

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

## Development Notes

- All agents are in `services/agents/` and inherit from `BaseAgent`
- Workflows orchestrate agents in `services/workflows/`
- Database operations use `database/repository.py`
- File uploads are saved to `uploads/` directory

