"""
FastAPI Main Application
REST API for HR Recruitment Agent System
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, Dict, Any
import os
import shutil
import logging
from pathlib import Path

from backend.agents import AgentOrchestrator
from backend.models.schemas import (
    JobRequirements,
    SearchRequest,
    OrchestrationRequest,
    OrchestrationResponse,
    ErrorResponse,
    AgentStatusResponse
)
from backend.utils.config import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HR Recruitment Agent System",
    description="Multi-agent system for automated candidate sourcing and resume analysis",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get settings
settings = get_settings()

# Create data directories
UPLOAD_DIR = Path("backend/data/resumes")
RESULTS_DIR = Path("backend/data/results")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Global orchestrator instance
orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        config = {
            'openai_api_key': settings.openai_api_key,
            'openai_model': settings.openai_model,
            'headless': settings.headless_browser,
            'scrape_delay': settings.scrape_delay,
            'max_candidates': settings.max_candidates_per_search
        }
        orchestrator = AgentOrchestrator(config=config)
        logger.info("Orchestrator initialized")
    return orchestrator


@app.get("/")
async def root():
    """Root endpoint - serves the web dashboard"""
    return FileResponse("frontend/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents": ["resume_parser", "linkedin_scraper", "indeed_scraper", "candidate_ranker"]
    }


@app.post("/api/upload-resumes")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Upload resume files for parsing

    Returns:
        List of uploaded file paths
    """
    try:
        uploaded_files = []

        for file in files:
            # Validate file type
            if not file.filename.endswith(('.pdf', '.docx', '.doc', '.txt')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Supported types: PDF, DOCX, DOC, TXT"
                )

            # Save file
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded_files.append(str(file_path))
            logger.info(f"Uploaded file: {file.filename}")

        return {
            "success": True,
            "files_uploaded": len(uploaded_files),
            "file_paths": uploaded_files
        }

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parse-resumes")
async def parse_resumes(file_paths: List[str]):
    """
    Parse uploaded resumes

    Args:
        file_paths: List of file paths to parse

    Returns:
        Parsed resume data
    """
    try:
        orch = get_orchestrator()

        result = await orch.run(
            mode="parse_only",
            resume_files=file_paths
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

        return result['data']

    except Exception as e:
        logger.error(f"Resume parsing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search-candidates")
async def search_candidates(request: SearchRequest):
    """
    Search for candidates on LinkedIn and Indeed

    Args:
        request: Search parameters

    Returns:
        List of found candidates
    """
    try:
        orch = get_orchestrator()

        linkedin_creds = None
        if request.linkedin_email and request.linkedin_password:
            linkedin_creds = {
                'email': request.linkedin_email,
                'password': request.linkedin_password
            }

        result = await orch.run(
            mode="search_only",
            job_title=request.job_title,
            location=request.location,
            keywords=request.keywords,
            search_linkedin=request.search_linkedin,
            search_indeed=request.search_indeed,
            linkedin_credentials=linkedin_creds
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

        return result['data']

    except Exception as e:
        logger.error(f"Candidate search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rank-candidates")
async def rank_candidates(
    candidates: List[Dict[str, Any]],
    job_requirements: JobRequirements,
    shortlist_size: int = 10
):
    """
    Rank candidates against job requirements

    Args:
        candidates: List of candidates to rank
        job_requirements: Job requirements
        shortlist_size: Size of shortlist

    Returns:
        Ranked candidates with scores
    """
    try:
        orch = get_orchestrator()

        result = await orch.candidate_ranker.run(
            candidates=candidates,
            job_requirements=job_requirements.dict(),
            generate_shortlist=True,
            shortlist_size=shortlist_size
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

        return result['data']

    except Exception as e:
        logger.error(f"Candidate ranking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_workflow(request: OrchestrationRequest):
    """
    Execute full recruitment workflow with orchestrator

    Args:
        request: Orchestration parameters

    Returns:
        Complete workflow results
    """
    try:
        orch = get_orchestrator()

        # Prepare LinkedIn credentials
        linkedin_creds = None
        if request.linkedin_email and request.linkedin_password:
            linkedin_creds = {
                'email': request.linkedin_email,
                'password': request.linkedin_password
            }

        # Prepare job requirements
        job_reqs = None
        if request.job_requirements:
            job_reqs = request.job_requirements.dict()

        result = await orch.run(
            mode=request.mode,
            job_requirements=job_reqs,
            resume_files=request.resume_files,
            job_title=request.job_title,
            location=request.location,
            keywords=request.keywords,
            search_linkedin=request.search_linkedin,
            search_indeed=request.search_indeed,
            linkedin_credentials=linkedin_creds,
            rank_candidates=request.rank_candidates,
            shortlist_size=request.shortlist_size
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

        return result['data']

    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/status")
async def get_agents_status():
    """
    Get status of all agents

    Returns:
        Status information for all agents
    """
    try:
        orch = get_orchestrator()
        return orch.get_agents_status()

    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/resumes/{filename}")
async def delete_resume(filename: str):
    """
    Delete an uploaded resume file

    Args:
        filename: Name of file to delete

    Returns:
        Success message
    """
    try:
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return {"success": True, "message": f"Deleted {filename}"}
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resumes")
async def list_resumes():
    """
    List all uploaded resume files

    Returns:
        List of resume filenames
    """
    try:
        files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
        return {
            "success": True,
            "count": len(files),
            "files": files
        }

    except Exception as e:
        logger.error(f"Failed to list resumes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug_mode
    )
