"""
VendorLens Backend - FastAPI Application
Main entry point for the backend server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
# 1) Load backend/.env (working directory)
load_dotenv()
# 2) Load project root .env to allow rotated keys there to override
root_env_path = (Path(__file__).resolve().parent.parent / ".env")
if root_env_path.exists():
    load_dotenv(dotenv_path=root_env_path, override=True)

# Import routers
from api.routes import core, workflows, health, docs

app = FastAPI(
    title="VendorLens API",
    description="Secure & Intelligent Vendor Onboarding Hub - AI-powered vendor onboarding and assessment platform",
    version="1.0.0",
    contact={
        "name": "VendorLens Team"
    },
    license_info={
        "name": "MIT"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(docs.router, tags=["Documentation"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(core.router, prefix="/api", tags=["Core API"])
app.include_router(workflows.router, prefix="/api", tags=["Workflows"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "VendorLens API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/openapi.yaml")
async def get_openapi_yaml():
    """Serve the OpenAPI YAML specification"""
    openapi_path = Path(__file__).parent / "openapi.yaml"
    if openapi_path.exists():
        return FileResponse(
            openapi_path,
            media_type="application/x-yaml",
            filename="openapi.yaml"
        )
    return {"error": "OpenAPI spec not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )

