"""
Agent Orchestrator
Coordinates multiple agents to complete the full recruitment workflow
"""

import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from .resume_parser import ResumeParserAgent
from .linkedin_scraper import LinkedInScraperAgent
from .indeed_scraper import IndeedScraperAgent
from .candidate_ranker import CandidateRankerAgent


class AgentOrchestrator(BaseAgent):
    """
    Orchestrator that coordinates multiple recruitment agents
    """

    def __init__(self, agent_id: str = "orchestrator", config: Dict[str, Any] = None):
        super().__init__(agent_id, config)

        # Initialize all agents
        self.resume_parser = ResumeParserAgent(
            agent_id="resume_parser_1",
            config=config
        )

        self.linkedin_scraper = LinkedInScraperAgent(
            agent_id="linkedin_scraper_1",
            config=config
        )

        self.indeed_scraper = IndeedScraperAgent(
            agent_id="indeed_scraper_1",
            config=config
        )

        self.candidate_ranker = CandidateRankerAgent(
            agent_id="candidate_ranker_1",
            config=config
        )

    async def parse_resumes(self, resume_files: List[str]) -> List[Dict[str, Any]]:
        """
        Parse multiple resumes in parallel

        Args:
            resume_files: List of resume file paths

        Returns:
            List of parsed resume data
        """
        self.log(f"Parsing {len(resume_files)} resumes")

        tasks = []
        for file_path in resume_files:
            task = self.resume_parser.run(file_path=file_path)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        parsed_resumes = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                self.log(f"Failed to parse resume {resume_files[idx]}: {result}", "error")
            elif result.get('success'):
                parsed_data = result['data']['parsed_data']
                parsed_data['source_file'] = resume_files[idx]
                parsed_data['source'] = 'uploaded_resume'
                parsed_resumes.append(parsed_data)

        return parsed_resumes

    async def search_candidates(self, job_title: str, location: str = "",
                               keywords: List[str] = None,
                               search_linkedin: bool = True,
                               search_indeed: bool = True,
                               linkedin_credentials: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Search for candidates across multiple platforms

        Args:
            job_title: Job title to search for
            location: Location filter
            keywords: Additional search keywords
            search_linkedin: Whether to search LinkedIn
            search_indeed: Whether to search Indeed
            linkedin_credentials: Optional LinkedIn credentials

        Returns:
            Combined list of candidates from all sources
        """
        self.log(f"Searching for candidates: {job_title}")

        tasks = []

        # LinkedIn search
        if search_linkedin:
            linkedin_task = self.linkedin_scraper.run(
                job_title=job_title,
                location=location,
                keywords=keywords,
                linkedin_email=linkedin_credentials.get('email') if linkedin_credentials else None,
                linkedin_password=linkedin_credentials.get('password') if linkedin_credentials else None
            )
            tasks.append(('linkedin', linkedin_task))

        # Indeed search
        if search_indeed:
            indeed_task = self.indeed_scraper.run(
                job_title=job_title,
                location=location
            )
            tasks.append(('indeed', indeed_task))

        # Execute searches in parallel
        all_candidates = []

        for source, task in tasks:
            try:
                result = await task
                if result.get('success'):
                    candidates = result['data'].get('candidates', result['data'].get('results', []))
                    all_candidates.extend(candidates)
                    self.log(f"Found {len(candidates)} candidates from {source}")
            except Exception as e:
                self.log(f"Search failed for {source}: {e}", "error")

        return all_candidates

    async def execute(self,
                     mode: str = "full_search",
                     job_requirements: Optional[Dict[str, Any]] = None,
                     resume_files: Optional[List[str]] = None,
                     job_title: Optional[str] = None,
                     location: str = "",
                     keywords: Optional[List[str]] = None,
                     search_linkedin: bool = True,
                     search_indeed: bool = True,
                     linkedin_credentials: Optional[Dict[str, str]] = None,
                     rank_candidates: bool = True,
                     shortlist_size: int = 10,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute the full recruitment workflow

        Args:
            mode: Operation mode - "full_search", "parse_only", "search_only", "rank_only"
            job_requirements: Job requirements for ranking
            resume_files: List of resume files to parse
            job_title: Job title for searching
            location: Location filter
            keywords: Search keywords
            search_linkedin: Search LinkedIn
            search_indeed: Search Indeed
            linkedin_credentials: LinkedIn login credentials
            rank_candidates: Whether to rank candidates
            shortlist_size: Size of shortlist

        Returns:
            Complete recruitment results
        """
        self.log(f"Starting orchestrator in mode: {mode}")

        all_candidates = []

        # Mode: Parse uploaded resumes
        if mode in ["full_search", "parse_only"] and resume_files:
            self.log("Parsing uploaded resumes...")
            parsed_resumes = await self.parse_resumes(resume_files)
            all_candidates.extend(parsed_resumes)
            self.log(f"Parsed {len(parsed_resumes)} resumes")

        # Mode: Search for candidates
        if mode in ["full_search", "search_only"] and job_title:
            self.log("Searching for candidates online...")
            search_results = await self.search_candidates(
                job_title=job_title,
                location=location,
                keywords=keywords,
                search_linkedin=search_linkedin,
                search_indeed=search_indeed,
                linkedin_credentials=linkedin_credentials
            )
            all_candidates.extend(search_results)
            self.log(f"Found {len(search_results)} candidates from searches")

        # Mode: Rank candidates
        ranked_results = None
        if rank_candidates and job_requirements and all_candidates:
            self.log("Ranking candidates...")
            ranking_result = await self.candidate_ranker.run(
                candidates=all_candidates,
                job_requirements=job_requirements,
                generate_shortlist=True,
                shortlist_size=shortlist_size
            )

            if ranking_result.get('success'):
                ranked_results = ranking_result['data']
                self.log(f"Ranking completed. Top score: {ranked_results.get('top_score', 0)}")

        # Compile final results
        result = {
            'mode': mode,
            'total_candidates_found': len(all_candidates),
            'candidates': all_candidates,
            'ranked_results': ranked_results,
            'sources': {
                'uploaded_resumes': len([c for c in all_candidates if c.get('source') == 'uploaded_resume']),
                'linkedin': len([c for c in all_candidates if c.get('source') == 'LinkedIn']),
                'indeed': len([c for c in all_candidates if c.get('source') == 'Indeed'])
            }
        }

        self.add_result(result)
        self.log(f"Orchestrator completed. Total candidates: {len(all_candidates)}")

        return result

    def get_agents_status(self) -> Dict[str, Any]:
        """
        Get status of all managed agents

        Returns:
            Status dictionary for all agents
        """
        return {
            'orchestrator': self.get_summary(),
            'resume_parser': self.resume_parser.get_summary(),
            'linkedin_scraper': self.linkedin_scraper.get_summary(),
            'indeed_scraper': self.indeed_scraper.get_summary(),
            'candidate_ranker': self.candidate_ranker.get_summary()
        }
