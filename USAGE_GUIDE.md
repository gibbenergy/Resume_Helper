# Resume Helper Usage Guide

Complete guide for downloading, installing, configuring, and using the Resume Helper application.

## Table of Contents

1. [Download](#1-download)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Resume Building](#4-resume-building)
5. [AI Features](#5-ai-features)
6. [Application Tracker](#6-application-tracker)
7. [Local AI Setup](#7-local-ai-setup)
8. [Cloud AI Setup](#8-cloud-ai-setup)

---

## 1. Download

Clone the repository:

```bash
git clone https://github.com/gibbenergy/Resume_Helper.git
cd Resume_Helper
```

Or download as ZIP from the [GitHub releases page](https://github.com/gibbenergy/Resume_Helper/releases).

---

## 2. Installation

### Windows (Recommended)

**Option A: One-Click Start**
```bash
start_react_ui.bat
```

**Option B: Manual Setup**

Terminal 1 (Backend):
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.api.main:app --host 0.0.0.0 --port 5000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm install
npm run dev
```

Access the app at: `http://localhost:5173`

---

## 3. Configuration

### AI Provider Setup

1. Launch the app and navigate to **AI Resume Helper** tab
2. Expand **AI Configuration** section
3. Select your provider from the dropdown
4. For cloud providers: Enter your API key
5. For local providers: Leave API key empty
6. Select a model from the Model dropdown
7. Click **Test Connection** to verify

API keys are automatically saved for future sessions.

### Supported Providers

| Provider | Type | API Key Required |
|----------|------|------------------|
| OpenAI | Cloud | Yes |
| Anthropic | Cloud | Yes |
| Google Gemini | Cloud | Yes |
| Groq | Cloud | Yes |
| Perplexity | Cloud | Yes |
| xAI | Cloud | Yes |
| Ollama | Local | No |
| llama.cpp | Local | No |
| LM Studio | Local | No |
| Lemonade | Local | No |

---

## 4. Resume Building

The app uses a tabbed interface for resume sections:

### Personal Info
- Name, contact details, summary
- LinkedIn, GitHub, Portfolio URLs
- Load example profiles or saved profiles

### Education
- Institution, degree, field of study
- GPA, dates, description

### Experience
- Company, position, location
- Start/end dates, description
- Achievements (use bullet points)

### Skills
- Category (Programming, Framework, etc.)
- Skill name and proficiency level

### Projects
- Project name and description
- Technologies used, URL
- Start/end dates

### Certifications
- Certification name and issuer
- Date obtained, credential ID, URL

### Saving Profiles

Profiles are saved to the database (not browser storage):
- Click **Save** in any section to save the entire profile
- Profiles persist across browsers on the same computer
- Load saved profiles from the **Assets** panel

---

## 5. AI Features

### Workflow

1. **Update Resume** - Sync your current resume data
2. **Paste Job Description** - Enter the full job posting
3. **Analyze Job** - Extract requirements and get match score
4. **Tailor Resume** - Adapt resume to job requirements
5. **Generate Cover Letter** - Create personalized cover letter
6. **Get Suggestions** - Receive improvement recommendations

### AI Operations

| Button | Action |
|--------|--------|
| Analyze Job | Extract skills, requirements, calculate match score |
| Tailor Resume | Rewrite resume aligned to job requirements |
| Cover Letter | Generate personalized cover letter |
| Suggestions | Get targeted improvement advice |

### PDF Generation

After AI processing:
1. Click **Preview** on any result card
2. Review the content
3. Click **Download PDF** to save

---

## 6. Application Tracker

### Adding Applications

1. Click **Add Application**
2. Fill required fields: Job URL, Company, Position
3. Optional: Location, salary, match score, notes
4. Click **Save**

### Managing Applications

| Action | How To |
|--------|--------|
| View | Click any row |
| Edit | Click row, then Edit button |
| Delete | Click row, then Delete button |
| Search | Use search box |
| Filter | Use status filter dropdown |
| Sort | Use sort dropdown |

### Interview Management

1. Open application details
2. Click **Manage Interviews**
3. Track rounds: Phone Screen, Technical, Panel, etc.
4. Update status: Scheduled, Completed, Passed, Failed

### Documents

Attach documents to applications:
- Resume versions
- Cover letters
- Portfolios
- Reference letters

---

## 7. Local AI Setup

### Ollama (Recommended for Beginners)

1. Download from: https://ollama.com/download
2. Install and run Ollama
3. Download a model
  
4. In Resume Helper: Select **Ollama (Local)**, leave API key empty

### llama.cpp (High Performance)

1. Download from: https://github.com/ggerganov/llama.cpp/releases
2. Download a GGUF model from HuggingFace
3. Start the server:
   ```bash
   llama-server -m model.gguf --port 8080
   ```
4. In Resume Helper: Select **llama.cpp**, use `http://localhost:8080/v1`

### LM Studio (User-Friendly GUI)

1. Download from: https://lmstudio.ai/
2. Install and open LM Studio
3. Download a model from the Discover tab
4. Go to **Local Server** tab, start server
5. In Resume Helper: Select **LM Studio**, use `http://localhost:1234/v1`

### Lemonade (AMD GPU / Advanced)

Lemonade is an LLM server optimized for AMD GPUs with advanced features.

1. Install Lemonade:
   ```bash
   pip install lemonade-server
   ```

2. Start the server:
   ```bash
   lemonade-server serve --ctx-size 8192
   ```
   
   **Important:** Use `--ctx-size 8192` or higher for job analysis (default 4096 may be too small).

3. In Resume Helper: Select **Lemonade**, use `http://localhost:8000/api/v1`

**Features:**
- AMD GPU optimization (ROCm)
- Smart caching and batching
- OpenAI-compatible API

**Troubleshooting:**
- If you see "context size exceeded" error, restart with larger context:
  ```bash
  lemonade-server serve --ctx-size 16384
  ```

---

## 8. Cloud AI Setup

### Getting API Keys

| Provider | Get API Key |
|----------|-------------|
| OpenAI | https://platform.openai.com/api-keys |
| Anthropic | https://console.anthropic.com/ |
| Google | https://aistudio.google.com/apikey |
| Groq | https://console.groq.com/keys |
| Perplexity | https://www.perplexity.ai/settings/api |
| xAI | https://console.x.ai/ |

### Tested Configuration

This app has been tested with **gpt-oss:20b** (OpenAI's open-weight model) running locally via Ollama and produces satisfactory results for job analysis, resume tailoring, and cover letter generation.

```bash
ollama pull gpt-oss:20b
```

For other models, check your provider's documentation for the latest available options.

---

## Stopping the Application

- Press `Ctrl+C` in each terminal window
- Or close the terminal windows

---

This concludes the Resume Helper usage guide.
