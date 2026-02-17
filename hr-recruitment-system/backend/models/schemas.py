"""
Pydantic Schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class JobRequirements(BaseModel):
    """Job requirements for candidate matching"""
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Job description")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    min_years_experience: Optional[int] = Field(None, description="Minimum years of experience")
    education_requirements: Optional[str] = Field(None, description="Education requirements")
    location: Optional[str] = Field(None, description="Job location")
    salary_range: Optional[str] = Field(None, description="Salary range")
    additional_requirements: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional requirements")


class SearchRequest(BaseModel):
    """Request to search for candidates"""
    job_title: str = Field(..., description="Job title to search for")
    location: Optional[str] = Field("", description="Location filter")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Additional keywords")
    search_linkedin: bool = Field(True, description="Search LinkedIn")
    search_indeed: bool = Field(True, description="Search Indeed")
    max_candidates: int = Field(50, description="Maximum number of candidates per source")
    linkedin_email: Optional[str] = Field(None, description="LinkedIn email for authenticated search")
    linkedin_password: Optional[str] = Field(None, description="LinkedIn password for authenticated search")


class ResumeUploadRequest(BaseModel):
    """Request for resume parsing"""
    file_paths: List[str] = Field(..., description="Paths to resume files")
    include_raw_text: bool = Field(False, description="Include raw text in response")


class OrchestrationRequest(BaseModel):
    """Request for full orchestration workflow"""
    mode: str = Field("full_search", description="Operation mode: full_search, parse_only, search_only, rank_only")
    job_requirements: Optional[JobRequirements] = Field(None, description="Job requirements for ranking")
    resume_files: Optional[List[str]] = Field(default_factory=list, description="Resume files to parse")
    job_title: Optional[str] = Field(None, description="Job title for searching")
    location: Optional[str] = Field("", description="Location filter")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Search keywords")
    search_linkedin: bool = Field(True, description="Search LinkedIn")
    search_indeed: bool = Field(True, description="Search Indeed")
    linkedin_email: Optional[str] = Field(None, description="LinkedIn credentials")
    linkedin_password: Optional[str] = Field(None, description="LinkedIn credentials")
    rank_candidates: bool = Field(True, description="Rank candidates")
    shortlist_size: int = Field(10, description="Shortlist size")


class CandidateResponse(BaseModel):
    """Response containing candidate information"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    source: Optional[str] = None
    profile_url: Optional[str] = None
    overall_score: Optional[float] = None
    rank: Optional[int] = None
    scoring: Optional[Dict[str, Any]] = None


class RankingResponse(BaseModel):
    """Response containing ranking results"""
    total_candidates: int
    ranked_candidates: List[Dict[str, Any]]
    top_score: float
    average_score: float
    shortlist: Optional[Dict[str, Any]] = None


class AgentStatusResponse(BaseModel):
    """Response containing agent status"""
    agent_id: str
    agent_type: str
    status: str
    created_at: str
    last_run: Optional[str] = None
    results_count: int
    errors_count: int
    config: Dict[str, Any]


class OrchestrationResponse(BaseModel):
    """Response from orchestration workflow"""
    mode: str
    total_candidates_found: int
    candidates: List[Dict[str, Any]]
    ranked_results: Optional[Dict[str, Any]] = None
    sources: Dict[str, int]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
