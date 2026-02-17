@echo off
REM HR Recruitment Agent System - Windows Setup Script

echo ========================================
echo HR Recruitment Agent System Setup
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

python --version
echo Python detected
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo pip upgraded
echo.

REM Install dependencies
echo Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Error: Failed to install dependencies
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo All dependencies installed
echo.

REM Setup environment file
echo Setting up environment configuration...
if exist ".env" (
    echo .env file already exists. Skipping creation.
) else (
    copy .env.example .env >nul
    echo Created .env file from template
)
echo.

REM Create data directories
echo Creating data directories...
if not exist "backend\data\resumes" mkdir backend\data\resumes
if not exist "backend\data\results" mkdir backend\data\results
echo Data directories created
echo.

REM Final instructions
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Edit the .env file and add your OpenAI API key
echo    notepad .env
echo.
echo 2. Get your OpenAI API key from:
echo    https://platform.openai.com/api-keys
echo.
echo 3. Run the application:
echo    python run.py
echo.
echo 4. Open your browser to:
echo    http://localhost:8000
echo.
echo For more information, see README.md
echo.
echo Happy recruiting!
echo.
pause
