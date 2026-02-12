"""
Resume Parser Agent
Extracts key information from resumes using AI
"""

import os
import json
from typing import Dict, Any, List
import PyPDF2
import docx
import pdfplumber
from .base_agent import BaseAgent


class ResumeParserAgent(BaseAgent):
    """
    Agent for parsing resumes and extracting structured information
    """

    def __init__(self, agent_id: str = "resume_parser", config: Dict[str, Any] = None):
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

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        text = ""
        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            self.log(f"pdfplumber failed, trying PyPDF2: {e}", "warning")
            try:
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                self.add_error(f"Failed to extract PDF text: {e2}", e2)
                raise

        return text.strip()

    def extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content
        """
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            self.add_error(f"Failed to extract DOCX text: {e}", e)
            raise

    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from resume file (supports PDF and DOCX)

        Args:
            file_path: Path to resume file

        Returns:
            Extracted text content
        """
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    async def parse_resume_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text using AI (Claude or OpenAI)

        Args:
            resume_text: Raw text from resume

        Returns:
            Structured resume data
        """
        prompt_content = """You are an expert HR assistant specialized in analyzing resumes.
Extract the following information from the resume and return it in a structured JSON format:

{
  "name": "Full name of the candidate",
  "email": "Email address",
  "phone": "Phone number",
  "location": "City, State/Country",
  "summary": "Professional summary or objective (if present)",
  "experience": [
    {
      "company": "Company name",
      "title": "Job title",
      "duration": "Start - End date",
      "description": "Brief description of responsibilities"
    }
  ],
  "education": [
    {
      "institution": "School/University name",
      "degree": "Degree name",
      "field": "Field of study",
      "year": "Graduation year"
    }
  ],
  "skills": ["List of skills"],
  "certifications": ["List of certifications"],
  "languages": ["List of languages"],
  "years_of_experience": "Estimated total years of experience (number)"
}

Extract all available information. If a field is not found, use null or empty array.

Resume to parse:

{resume_text}"""

        try:
            if self.ai_provider == 'claude':
                # Use Claude API
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_content.format(resume_text=resume_text)
                        }
                    ]
                )

                # Extract JSON from Claude response
                response_text = response.content[0].text

                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                else:
                    parsed_data = json.loads(response_text)

            else:  # openai
                # Use OpenAI API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert HR assistant. Return valid JSON only."},
                        {"role": "user", "content": prompt_content.format(resume_text=resume_text)}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )

                parsed_data = json.loads(response.choices[0].message.content)

            return parsed_data

        except Exception as e:
            self.add_error(f"AI parsing failed: {e}", e)
            raise

    async def execute(self, file_path: str = None, resume_text: str = None, **kwargs) -> Dict[str, Any]:
        """
        Execute resume parsing

        Args:
            file_path: Path to resume file (PDF, DOCX, TXT)
            resume_text: Raw resume text (alternative to file_path)

        Returns:
            Parsed resume data
        """
        self.log(f"Starting resume parsing for: {file_path or 'text input'}")

        # Extract text from file if file_path is provided
        if file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Resume file not found: {file_path}")
            resume_text = self.extract_text_from_file(file_path)
            self.log(f"Extracted {len(resume_text)} characters from resume")

        if not resume_text:
            raise ValueError("Either file_path or resume_text must be provided")

        # Parse resume using AI
        parsed_data = await self.parse_resume_with_ai(resume_text)

        # Add metadata
        result = {
            'parsed_data': parsed_data,
            'source_file': file_path,
            'text_length': len(resume_text),
            'raw_text': resume_text if kwargs.get('include_raw', False) else None
        }

        self.add_result(result)
        self.log("Resume parsing completed successfully")

        return result
