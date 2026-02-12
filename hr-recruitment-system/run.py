#!/usr/bin/env python3
"""
HR Recruitment Agent System
Main entry point for running the application
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('hr_recruitment.log')
    ]
)

logger = logging.getLogger(__name__)


def check_environment():
    """
    Check if the environment is properly configured
    """
    logger.info("Checking environment configuration...")

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning(".env file not found. Creating from .env.example...")
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            logger.info("Created .env file. Please update it with your configuration.")
        else:
            logger.error(".env.example not found!")
            return False

    # Check for AI API key
    from dotenv import load_dotenv
    load_dotenv()

    ai_provider = os.getenv("AI_PROVIDER", "claude").lower()

    if ai_provider == "claude":
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key or anthropic_key == "your_anthropic_api_key_here":
            logger.error("❌ Claude (Anthropic) API key not configured!")
            logger.error("Please set ANTHROPIC_API_KEY in your .env file")
            logger.error("Get your API key from: https://console.anthropic.com/")
            logger.error("")
            logger.error("Or switch to OpenAI by setting AI_PROVIDER=openai in .env")
            return False
        logger.info("✓ Claude API key found")
    else:  # openai
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key == "your_openai_api_key_here":
            logger.error("❌ OpenAI API key not configured!")
            logger.error("Please set OPENAI_API_KEY in your .env file")
            logger.error("Get your API key from: https://platform.openai.com/api-keys")
            logger.error("")
            logger.error("Or switch to Claude by setting AI_PROVIDER=claude in .env")
            return False
        logger.info("✓ OpenAI API key found")

    # Check if required directories exist
    data_dir = Path("backend/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "resumes").mkdir(exist_ok=True)
    (data_dir / "results").mkdir(exist_ok=True)

    logger.info("✓ Data directories verified")

    return True


def main():
    """
    Main function to run the application
    """
    logger.info("=" * 60)
    logger.info("HR Recruitment Agent System")
    logger.info("=" * 60)

    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Please fix the issues above and try again.")
        sys.exit(1)

    logger.info("Starting application server...")

    # Import and run the FastAPI application
    try:
        import uvicorn
        from backend.utils.config import get_settings

        settings = get_settings()

        logger.info(f"Server will start at: http://{settings.app_host}:{settings.app_port}")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("")
        logger.info("📊 Web Dashboard: http://localhost:8000")
        logger.info("📚 API Docs: http://localhost:8000/docs")
        logger.info("🔍 Health Check: http://localhost:8000/api/health")
        logger.info("")

        uvicorn.run(
            "backend.api.main:app",
            host=settings.app_host,
            port=settings.app_port,
            reload=settings.debug_mode,
            log_level="info"
        )

    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
