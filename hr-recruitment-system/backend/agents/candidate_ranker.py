"""
Candidate Ranker Agent
Scores and ranks candidates based on job requirements using AI
"""

from typing import Dict, Any, List
import json
import re
from .base_agent import BaseAgent


class CandidateRankerAgent(BaseAgent):
    """
    Agent for scoring and ranking candidates against job requirements
    """

    def __init__(self, agent_id: str = "candidate_ranker", config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        self.ai_provider = config.get('ai_provider', 'claude')

        if self.ai_provider == 'claude':
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=config.get('anthropic_api_key'))
            self.model = config.get('claude_model', 'claude-3-5-sonnet-20241022')
        else:  # openai
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=config.get('openai_api_key'))
            self.model = config.get('openai_model', 'gpt-4-turbo-preview')

    async def score_candidate(self, candidate: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single candidate against job requirements

        Args:
            candidate: Candidate information dictionary
            job_requirements: Job requirements dictionary

        Returns:
            Scoring results with breakdown
        """
        system_prompt = """You are an expert HR recruiter specialized in matching candidates to job requirements.
Analyze the candidate's profile against the job requirements and provide a detailed scoring.

Return your analysis in the following JSON format:
{
  "overall_score": 85,  // Score from 0-100
  "match_quality": "Excellent",  // Excellent, Good, Fair, Poor
  "strengths": ["List of candidate's key strengths matching the role"],
  "weaknesses": ["List of gaps or areas of concern"],
  "skill_match": {
    "required_skills_matched": ["List of required skills the candidate has"],
    "required_skills_missing": ["List of required skills the candidate lacks"],
    "bonus_skills": ["Additional relevant skills the candidate has"]
  },
  "experience_analysis": {
    "years_match": true,  // Whether experience level matches requirements
    "relevant_experience": "Brief description of relevant experience",
    "experience_score": 80  // Score from 0-100
  },
  "education_match": {
    "meets_requirements": true,
    "details": "Brief analysis of education match"
  },
  "cultural_fit_indicators": ["Indicators that suggest good cultural fit"],
  "red_flags": ["Any concerning aspects if present"],
  "recommendation": "Detailed recommendation on whether to proceed with this candidate",
  "suggested_next_steps": ["Recommended next steps if moving forward"]
}

Be thorough, objective, and provide actionable insights."""

        user_prompt = f"""Job Requirements:
{json.dumps(job_requirements, indent=2)}

Candidate Profile:
{json.dumps(candidate, indent=2)}

Analyze this candidate and provide a detailed scoring and recommendation."""

        try:
            if self.ai_provider == 'claude':
                # Use Claude API
                full_prompt = system_prompt + "\n\n" + user_prompt
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.2,
                    messages=[
                        {
                            "role": "user",
                            "content": full_prompt
                        }
                    ]
                )

                # Extract JSON from Claude response
                response_text = response.content[0].text

                # Try to extract JSON from the response
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    scoring = json.loads(json_match.group())
                else:
                    scoring = json.loads(response_text)

            else:  # openai
                # Use OpenAI API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )

                scoring = json.loads(response.choices[0].message.content)

            return scoring

        except Exception as e:
            self.add_error(f"Candidate scoring failed: {e}", e)
            # Return a basic fallback score
            return {
                "overall_score": 50,
                "match_quality": "Unknown",
                "error": str(e)
            }

    async def rank_candidates(self, candidates: List[Dict[str, Any]],
                            job_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score and rank multiple candidates

        Args:
            candidates: List of candidate dictionaries
            job_requirements: Job requirements dictionary

        Returns:
            List of candidates with scores, sorted by score (highest first)
        """
        self.log(f"Ranking {len(candidates)} candidates")

        scored_candidates = []

        for idx, candidate in enumerate(candidates):
            self.log(f"Scoring candidate {idx + 1}/{len(candidates)}: {candidate.get('name', 'Unknown')}")

            scoring = await self.score_candidate(candidate, job_requirements)

            scored_candidate = {
                **candidate,
                'scoring': scoring,
                'overall_score': scoring.get('overall_score', 0),
                'rank': None  # Will be assigned after sorting
            }

            scored_candidates.append(scored_candidate)

        # Sort by overall score (descending)
        scored_candidates.sort(key=lambda x: x['overall_score'], reverse=True)

        # Assign ranks
        for rank, candidate in enumerate(scored_candidates, start=1):
            candidate['rank'] = rank

        return scored_candidates

    async def generate_shortlist(self, ranked_candidates: List[Dict[str, Any]],
                                top_n: int = 10) -> Dict[str, Any]:
        """
        Generate a shortlist summary of top candidates

        Args:
            ranked_candidates: List of ranked candidates with scores
            top_n: Number of top candidates to include in shortlist

        Returns:
            Shortlist summary
        """
        shortlist = ranked_candidates[:top_n]

        summary_prompt = f"""Based on the following top {len(shortlist)} candidates who have been scored and ranked,
provide an executive summary for the hiring manager.

Candidates:
{json.dumps(shortlist, indent=2)}

Provide a JSON response with:
{{
  "summary": "Brief overview of the candidate pool quality",
  "top_recommendations": [
    {{
      "name": "Candidate name",
      "rank": 1,
      "key_reason": "Primary reason to interview this candidate"
    }}
  ],
  "diversity_analysis": "Brief note on diversity of the candidate pool",
  "hiring_timeline_suggestion": "Suggested timeline based on candidate quality",
  "additional_notes": "Any other important observations"
}}"""

        try:
            if self.ai_provider == 'claude':
                # Use Claude API
                full_prompt = "You are an expert HR recruiter providing hiring recommendations.\n\n" + summary_prompt
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    temperature=0.3,
                    messages=[
                        {
                            "role": "user",
                            "content": full_prompt
                        }
                    ]
                )

                # Extract JSON from Claude response
                response_text = response.content[0].text

                # Try to extract JSON from the response
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    summary = json.loads(json_match.group())
                else:
                    summary = json.loads(response_text)

            else:  # openai
                # Use OpenAI API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert HR recruiter providing hiring recommendations."},
                        {"role": "user", "content": summary_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                summary = json.loads(response.choices[0].message.content)

            return {
                'shortlist': shortlist,
                'summary': summary,
                'total_candidates_reviewed': len(ranked_candidates),
                'shortlist_size': len(shortlist)
            }

        except Exception as e:
            self.add_error(f"Shortlist generation failed: {e}", e)
            return {
                'shortlist': shortlist,
                'total_candidates_reviewed': len(ranked_candidates),
                'shortlist_size': len(shortlist),
                'error': str(e)
            }

    async def execute(self, candidates: List[Dict[str, Any]],
                     job_requirements: Dict[str, Any],
                     generate_shortlist: bool = True,
                     shortlist_size: int = 10,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute candidate ranking

        Args:
            candidates: List of candidates to rank
            job_requirements: Job requirements to match against
            generate_shortlist: Whether to generate a shortlist summary
            shortlist_size: Number of candidates in shortlist

        Returns:
            Ranking results
        """
        self.log(f"Starting candidate ranking for {len(candidates)} candidates")

        if not candidates:
            return {
                'ranked_candidates': [],
                'message': 'No candidates to rank'
            }

        # Rank all candidates
        ranked_candidates = await self.rank_candidates(candidates, job_requirements)

        result = {
            'total_candidates': len(candidates),
            'ranked_candidates': ranked_candidates,
            'top_score': ranked_candidates[0]['overall_score'] if ranked_candidates else 0,
            'average_score': sum(c['overall_score'] for c in ranked_candidates) / len(ranked_candidates) if ranked_candidates else 0
        }

        # Generate shortlist if requested
        if generate_shortlist:
            shortlist_data = await self.generate_shortlist(ranked_candidates, shortlist_size)
            result['shortlist'] = shortlist_data

        self.add_result(result)
        self.log(f"Candidate ranking completed. Top score: {result['top_score']}")

        return result
