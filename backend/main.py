"""
VendorLens Backend - FastAPI Application
Main entry point for the backend server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routers
from api.routes import core, workflows, health

app = FastAPI(
    title="VendorLens API",
    description="Secure & Intelligent Vendor Onboarding Hub",
    version="1.0.0"
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
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(core.router, prefix="/api", tags=["Core API"])
app.include_router(workflows.router, prefix="/api", tags=["Workflows"])


@app.get("/")
async def root():
    return {"message": "VendorLens API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )

