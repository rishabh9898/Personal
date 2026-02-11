# 🚀 Quick Start Guide

Get up and running with the HR Recruitment Agent System in 5 minutes!

## Step 1: Install Python Dependencies

```bash
cd hr-recruitment-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Get your OpenAI API key**: https://platform.openai.com/api-keys

## Step 3: Run the Application

```bash
python run.py
```

## Step 4: Open the Dashboard

Navigate to: **http://localhost:8000**

## 🎯 First Actions

### Option 1: Upload Resumes
1. Click "Upload Resumes" tab
2. Select PDF/DOCX resume files
3. Click "Upload & Parse Resumes"
4. View results in "Results" tab

### Option 2: Search Candidates
1. Click "Search Candidates" tab
2. Enter job title (e.g., "Software Engineer")
3. (Optional) Enter location and keywords
4. (Optional) Fill job requirements for AI ranking
5. Click "Start Recruitment Search"
6. View results in "Results" tab

## 📊 Example Searches

**Software Engineer:**
- Job Title: `Senior Software Engineer`
- Location: `San Francisco, CA`
- Keywords: `Python, React, AWS`
- Required Skills: `Python, JavaScript, SQL, REST APIs`
- Min Experience: `5 years`

**Product Manager:**
- Job Title: `Product Manager`
- Location: `New York, NY`
- Keywords: `Agile, Scrum, B2B SaaS`
- Required Skills: `Product Strategy, Roadmap Planning, Stakeholder Management`
- Min Experience: `3 years`

**Data Scientist:**
- Job Title: `Data Scientist`
- Location: `Remote`
- Keywords: `Machine Learning, Python, TensorFlow`
- Required Skills: `Python, Machine Learning, Statistics, SQL`
- Min Experience: `4 years`

## 🔍 What Each Agent Does

1. **Resume Parser** - Extracts structured data from uploaded resumes using GPT-4
2. **LinkedIn Scraper** - Searches LinkedIn for matching profiles
3. **Indeed Scraper** - Searches Indeed for relevant job postings and candidates
4. **Candidate Ranker** - Scores candidates against job requirements using AI
5. **Orchestrator** - Coordinates all agents seamlessly

## ⚡ Tips for Best Results

### For Searching:
- Be specific with job titles (use common industry terms)
- Add relevant keywords to narrow down results
- Use location filters to find local candidates
- Provide detailed job requirements for better AI ranking

### For Resume Parsing:
- Use clear, well-formatted PDF or DOCX files
- Ensure resumes have standard sections (Experience, Education, Skills)
- Multiple files can be uploaded at once

### For LinkedIn Scraping:
- LinkedIn login is optional but provides better results
- Start with broader searches, then refine
- Be patient - scraping takes time to avoid rate limits

## 🛠️ Troubleshooting

**"OpenAI API key not configured"**
- Edit `.env` file and add your API key
- Make sure there are no quotes around the key
- Restart the application

**"ChromeDriver not found"**
- The system auto-downloads ChromeDriver
- Ensure Chrome/Chromium is installed
- Check your internet connection

**"No candidates found"**
- Try a broader search term
- Remove location filters
- Check if the job title is common (e.g., use "Software Engineer" not "Code Ninja")

**Slow performance**
- Scraping takes time to avoid detection
- Reduce MAX_CANDIDATES_PER_SEARCH in .env
- Disable one of the search sources

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API docs at http://localhost:8000/docs
- Check agent status in the dashboard
- Customize agents in `backend/agents/`

## 🎓 Learn More

**Understanding the Results:**
- Scores range from 0-100 (higher is better)
- 80+ = Excellent match
- 65-79 = Good match
- 50-64 = Fair match
- Below 50 = Poor match

**AI Analysis Includes:**
- Match quality assessment
- Strengths and weaknesses
- Skills gap analysis
- Personalized recommendations

## 🆘 Need Help?

1. Check the [README.md](README.md) troubleshooting section
2. Review the agent status dashboard
3. Check the console logs for errors
4. Ensure your .env file is configured correctly

---

**Happy recruiting! 🎉**
