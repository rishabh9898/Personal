"""
Resume Parser Agent
Extracts key information from resumes using AI
"""

import os
from typing import Dict, Any, List
import PyPDF2
import docx
import pdfplumber
from openai import AsyncOpenAI
from .base_agent import BaseAgent


class ResumeParserAgent(BaseAgent):
    """
    Agent for parsing resumes and extracting structured information
    """

    def __init__(self, agent_id: str = "resume_parser", config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
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
        Parse resume text using OpenAI GPT

        Args:
            resume_text: Raw text from resume

        Returns:
            Structured resume data
        """
        system_prompt = """You are an expert HR assistant specialized in analyzing resumes.
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

Extract all available information. If a field is not found, use null or empty array."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this resume:\n\n{resume_text}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            import json
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
