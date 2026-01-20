<div align="center">
  <img src="assets/logo.jpg" alt="Resume Helper Logo" width="200"/>
  

  
  **AI-powered resume builder with multi-provider LLM support**
  
  [![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![Code Quality](https://github.com/gibbenergy/Resume_Helper/actions/workflows/code-quality.yml/badge.svg)](https://github.com/gibbenergy/Resume_Helper/actions/workflows/code-quality.yml)
  
  [Usage Guide](USAGE_GUIDE.md) | [License](LICENSE)
  
</div>

## App Demo

### AI Resume Helper

https://github.com/user-attachments/assets/857c7162-8baa-4eda-854a-9f30fff3caf0

### Application Tracking System

https://github.com/user-attachments/assets/ea617f6f-fb20-44fa-9bba-d45a1c36756d

---

## Features

```mermaid
flowchart LR
    R[Resume Helper]
    
    R --> A[Resume Building]
    A --> A1[Personal Info]
    A --> A2[Education]
    A --> A3[Experience]
    A --> A4[Skills]
    A --> A5[Projects]
    A --> A6[Certifications]
    
    R --> B[AI Features]
    B --> B1[Job Analysis]
    B --> B2[Resume Tailoring]
    B --> B3[Cover Letters]
    B --> B4[Suggestions]
    
    R --> C[Application Tracker]
    C --> C1[Track Applications]
    C --> C2[Interview Management]
    C --> C3[Outcome Tracking]
    
    R --> D[Multi-AI Support]
    D --> D1[Cloud Providers]
    D --> D2[Local Providers]
    
    R --> E[PDF Generation]
    E --> E1[Resume PDF]
    E --> E2[Cover Letter PDF]
    E --> E3[Analysis PDF]
    
    R --> F[Privacy Protection]
    F --> F1[Strip Personal Data]
    F --> F2[Process with AI]
    F --> F3[Restore Data]
    
    style R fill:#0ea5e9,stroke:#0ea5e9,color:#fff
    style A fill:#3b82f6,stroke:#3b82f6,color:#fff
    style B fill:#8b5cf6,stroke:#8b5cf6,color:#fff
    style C fill:#f59e0b,stroke:#f59e0b,color:#fff
    style D fill:#10b981,stroke:#10b981,color:#fff
    style E fill:#ef4444,stroke:#ef4444,color:#fff
    style F fill:#ec4899,stroke:#ec4899,color:#fff
    style A1 fill:#60a5fa,stroke:#60a5fa,color:#fff
    style A2 fill:#60a5fa,stroke:#60a5fa,color:#fff
    style A3 fill:#60a5fa,stroke:#60a5fa,color:#fff
    style A4 fill:#60a5fa,stroke:#60a5fa,color:#fff
    style A5 fill:#60a5fa,stroke:#60a5fa,color:#fff
    style A6 fill:#60a5fa,stroke:#60a5fa,color:#fff
    style B1 fill:#a78bfa,stroke:#a78bfa,color:#fff
    style B2 fill:#a78bfa,stroke:#a78bfa,color:#fff
    style B3 fill:#a78bfa,stroke:#a78bfa,color:#fff
    style B4 fill:#a78bfa,stroke:#a78bfa,color:#fff
    style C1 fill:#fbbf24,stroke:#fbbf24,color:#000
    style C2 fill:#fbbf24,stroke:#fbbf24,color:#000
    style C3 fill:#fbbf24,stroke:#fbbf24,color:#000
    style D1 fill:#34d399,stroke:#34d399,color:#000
    style D2 fill:#34d399,stroke:#34d399,color:#000
    style E1 fill:#f87171,stroke:#f87171,color:#fff
    style E2 fill:#f87171,stroke:#f87171,color:#fff
    style E3 fill:#f87171,stroke:#f87171,color:#fff
    style F1 fill:#f472b6,stroke:#f472b6,color:#fff
    style F2 fill:#f472b6,stroke:#f472b6,color:#fff
    style F3 fill:#f472b6,stroke:#f472b6,color:#fff
```

### Privacy-Preserving Workflow

<div align="center">

```mermaid
flowchart TD
    A[Resume<br/>Original Document] --> B[Strip Info<br/>Remove Personal Data]
    B -->|send| C[Work Content<br/>Anonymized Resume]
    B -->|remove| D[Personal Info<br/>Stored Locally]
    C --> E[Cloud AI<br/>Process Content]
    E --> F[AI Results<br/>Resume, Cover Letter,<br/>Suggestions, Skill Gaps]
    F --> G[Restore Info<br/>Merge Personal Data]
    D -->|append back| G
    G --> H[Final Output<br/>Complete Document]
    
    style A fill:#1e3a5f,stroke:#4a90d9,color:#fff
    style B fill:#6b21a8,stroke:#a855f7,color:#fff
    style C fill:#166534,stroke:#22c55e,color:#fff
    style D fill:#991b1b,stroke:#ef4444,color:#fff
    style E fill:#0369a1,stroke:#38bdf8,color:#fff
    style F fill:#1d4ed8,stroke:#60a5fa,color:#fff
    style G fill:#6b21a8,stroke:#a855f7,color:#fff
    style H fill:#1e3a5f,stroke:#4a90d9,color:#fff
```

**Before sending anything to AI, remove personal information. After getting the AI response, put it back.**

</div>

## Quick Start (Windows)

```bash
start_react_ui.bat
```

Or manually:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cd backend
uvicorn backend.api.main:app --host 0.0.0.0 --port 5000
```

In another terminal:
```bash
cd frontend
npm install
npm run dev
```

Access at: `http://localhost:5173`

## Configuration

API keys are configured directly in the app:
1. Launch the app
2. Go to "AI Resume Helper" tab
3. Expand "AI Configuration" 
4. Select provider, enter API key, click "Set"

Keys are auto-saved and remembered for next session.

## Supported AI Models

**Recommended: Local Models (Free)**

**Ollama** - Easiest local setup
- **gpt-oss** - OpenAI's open-weight model (14GB, 128K context) - best for reasoning
- Qwen2.5, Llama 3.3, DeepSeek-R1 - smaller alternatives

**llama.cpp** - High-performance C++ inference
- Run any GGUF model with OpenAI-compatible API
- Lower memory usage, faster inference
- Default: `http://localhost:8080/v1`

**LM Studio** - User-friendly GUI
- Easy model downloads and management
- Built-in OpenAI-compatible server
- Default: `http://localhost:1234/v1`

**Lemonade** - Advanced LLM router/proxy
- Route requests to multiple local backends
- Smart model selection and load balancing
- OpenAI-compatible API with extended features
- Default: `http://localhost:8000/v1`
- **Recommended:** Use `--ctx-size 8192` or higher for job analysis

**Cloud Providers (API key required)**
- **OpenAI**: GPT-4.1, GPT-5, GPT-5-mini
- **Anthropic**: Claude Opus 4, Claude 3.5 Sonnet
- **Google**: Gemini 2.5 Pro, Gemini 2.5 Flash
- **Groq**: Llama 3.3
- **Perplexity**: Sonar Pro, Sonar Reasoning
- **xAI**: Grok 4, Grok 3

## Requirements

- Windows 10/11
- Python 3.11+
- Node.js 18+ (for frontend)
- For Ollama: ~14GB disk space for gpt-oss model

## License

Business Source License 1.1 - See LICENSE file
Free for personal/educational use. Commercial use requires a license.
