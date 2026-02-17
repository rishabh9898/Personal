# 🤖 HR Recruitment Agent System

An intelligent, multi-agent system for automating candidate sourcing and resume analysis. This system leverages AI (Claude or GPT-4) and web scraping to help HR professionals find and evaluate the best candidates quickly and efficiently.

## ✨ Features

### 🎯 Core Capabilities

- **Multi-Source Candidate Search**
  - LinkedIn candidate scraping
  - Indeed job posting analysis
  - Automated profile extraction

- **Intelligent Resume Parsing**
  - AI-powered resume analysis using Claude or GPT-4
  - Supports PDF, DOCX, DOC, and TXT formats
  - Extracts structured information (name, email, skills, experience, etc.)

- **AI-Powered Candidate Ranking**
  - Automatic scoring against job requirements using advanced AI
  - Detailed match analysis with strengths and weaknesses
  - Intelligent shortlist generation
  - Personalized recommendations

- **Web Dashboard**
  - Easy-to-use interface for managing recruitment
  - Real-time agent status monitoring
  - One-click deployment of recruitment searches
  - Visual candidate comparison

### 🤖 Agent Architecture

The system uses specialized agents that work together:

1. **Resume Parser Agent** - Extracts structured data from resumes using AI
2. **LinkedIn Scraper Agent** - Searches LinkedIn for matching candidates
3. **Indeed Scraper Agent** - Searches Indeed for relevant job postings and candidates
4. **Candidate Ranker Agent** - Scores and ranks candidates using AI
5. **Orchestrator Agent** - Coordinates all agents for seamless workflow

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- **Claude API key (Recommended)** - Get from https://console.anthropic.com/
  - OR OpenAI API key - Get from https://platform.openai.com/api-keys
- Chrome/Chromium browser (for web scraping)

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd hr-recruitment-system
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your API key:

**Option 1: Claude (Recommended)**
```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional: LinkedIn credentials for authenticated searches
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
```

**Option 2: OpenAI**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Optional: LinkedIn credentials for authenticated searches
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Application settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG_MODE=True

# Scraping settings
HEADLESS_BROWSER=True
SCRAPE_DELAY=2
MAX_CANDIDATES_PER_SEARCH=50
```

5. **Run the application:**
```bash
python run.py
```

6. **Open your browser:**
Navigate to `http://localhost:8000`

## 📖 Usage Guide

### Searching for Candidates

1. Go to the **"Search Candidates"** tab
2. Fill in the job details:
   - Job title (required)
   - Location (optional)
   - Keywords (optional)
3. Configure search options:
   - Select LinkedIn and/or Indeed
   - Set maximum candidates per source
4. (Optional) Add job requirements for AI ranking:
   - Job description
   - Required skills
   - Minimum experience
5. Click **"Start Recruitment Search"**

### Uploading & Parsing Resumes

1. Go to the **"Upload Resumes"** tab
2. Select one or more resume files (PDF, DOCX, DOC, TXT)
3. Click **"Upload & Parse Resumes"**
4. View parsed results in the **"Results"** tab

### Viewing Results

1. Go to the **"Results"** tab after a search or upload
2. Review the summary statistics
3. Browse through candidate cards showing:
   - Contact information
   - Skills and experience
   - AI match score (if ranked)
   - Strengths and weaknesses analysis
   - Recommendations

### Monitoring Agent Status

1. Go to the **"Agent Status"** tab
2. Click **"Refresh Status"** to see current agent states
3. View execution history and error logs

## 🏗️ Architecture

```
hr-recruitment-system/
├── backend/
│   ├── agents/               # Agent implementations
│   │   ├── base_agent.py    # Base agent class
│   │   ├── resume_parser.py # Resume parsing agent
│   │   ├── linkedin_scraper.py
│   │   ├── indeed_scraper.py
│   │   ├── candidate_ranker.py
│   │   └── orchestrator.py  # Agent coordinator
│   ├── api/
│   │   └── main.py          # FastAPI application
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── utils/
│   │   └── config.py        # Configuration management
│   └── data/
│       ├── resumes/         # Uploaded resume files
│       └── results/         # Search results cache
├── frontend/
│   ├── index.html           # Web dashboard
│   ├── styles.css           # Styling
│   └── app.js               # Frontend logic
├── requirements.txt
├── .env.example
├── run.py                   # Application entry point
└── README.md
```

## 🔧 API Endpoints

The system provides a REST API:

- `GET /api/health` - Health check
- `POST /api/upload-resumes` - Upload resume files
- `POST /api/parse-resumes` - Parse uploaded resumes
- `POST /api/search-candidates` - Search for candidates
- `POST /api/rank-candidates` - Rank candidates
- `POST /api/orchestrate` - Full workflow orchestration
- `GET /api/agents/status` - Get agent status
- `GET /api/resumes` - List uploaded resumes
- `DELETE /api/resumes/{filename}` - Delete a resume

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_PROVIDER` | AI provider to use: "claude" or "openai" | claude |
| `ANTHROPIC_API_KEY` | Claude (Anthropic) API key | - |
| `CLAUDE_MODEL` | Claude model to use | claude-3-5-sonnet-20241022 |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI) | - |
| `OPENAI_MODEL` | GPT model to use (if using OpenAI) | gpt-4-turbo-preview |
| `LINKEDIN_EMAIL` | LinkedIn email (optional) | - |
| `LINKEDIN_PASSWORD` | LinkedIn password (optional) | - |
| `APP_HOST` | Server host | 0.0.0.0 |
| `APP_PORT` | Server port | 8000 |
| `HEADLESS_BROWSER` | Run browser in headless mode | True |
| `SCRAPE_DELAY` | Delay between scraping requests (seconds) | 2 |
| `MAX_CANDIDATES_PER_SEARCH` | Maximum candidates per source | 50 |

### Customization

You can customize agent behavior by modifying the configuration in `backend/utils/config.py` or creating custom agents by extending the `BaseAgent` class.

## 🛡️ Important Notes

### LinkedIn & Indeed Scraping

- **Rate Limiting**: Be respectful of platform rate limits. The system includes delays to avoid being blocked.
- **Terms of Service**: Scraping may violate LinkedIn/Indeed ToS. Use at your own risk.
- **Authentication**: LinkedIn login provides better access but requires valid credentials.
- **Alternatives**: Consider using official APIs when available (LinkedIn Talent Solutions, Indeed API).

### Data Privacy

- All uploaded resumes are stored locally in `backend/data/resumes/`
- No data is sent to third parties except OpenAI for AI analysis
- Delete sensitive data regularly using the dashboard

### AI Accuracy

- AI analysis is a tool to assist, not replace, human judgment
- Always review AI recommendations before making hiring decisions
- Scores are relative and should be calibrated to your specific needs

## 🧪 Testing

To test the system:

1. **Upload sample resumes**: Use the upload tab to test resume parsing
2. **Run a search**: Try searching for "Software Engineer" to see the scraping in action
3. **Check agent status**: Verify all agents are working correctly

## 🐛 Troubleshooting

### Common Issues

**Issue**: Selenium/ChromeDriver errors
- **Solution**: Ensure Chrome/Chromium is installed. The system auto-downloads ChromeDriver.

**Issue**: OpenAI API errors
- **Solution**: Check your API key and ensure you have credits/quota available.

**Issue**: LinkedIn/Indeed blocking
- **Solution**: Reduce `SCRAPE_DELAY`, enable `HEADLESS_BROWSER=False`, or use VPN.

**Issue**: Resume parsing fails
- **Solution**: Ensure the resume is in a supported format (PDF, DOCX, DOC, TXT) and not corrupted.

## 📈 Future Enhancements

Potential improvements for the system:

- [ ] Database integration for persistent storage
- [ ] Email notification system
- [ ] Interview scheduling integration
- [ ] More job boards (Glassdoor, ZipRecruiter, etc.)
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Browser extension for quick candidate capture
- [ ] Integration with ATS systems
- [ ] Candidate communication automation

## 🤝 Contributing

This is a demonstration project. Feel free to fork and customize for your needs.

## 📄 License

MIT License - Feel free to use and modify as needed.

## ⚠️ Disclaimer

This system is for educational and demonstration purposes. Users are responsible for:
- Complying with website Terms of Service
- Respecting data privacy laws (GDPR, CCPA, etc.)
- Obtaining proper consent for data processing
- Using AI responsibly in hiring decisions

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the agent status dashboard
3. Check application logs in the console

---

**Built with**: Python, FastAPI, OpenAI GPT-4, Selenium, BeautifulSoup, and LangChain

**Made with ❤️ for HR professionals who want to work smarter, not harder**
