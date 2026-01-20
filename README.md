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

<div align="center">

```mermaid
flowchart TB
    subgraph Core["Core Features"]
        A[Resume Building]
        A1[Personal Info]
        A2[Education]
        A3[Experience]
        A4[Skills]
        A5[Projects]
        A6[Certifications]
        A --> A1
        A --> A2
        A --> A3
        A --> A4
        A --> A5
        A --> A6
    end
    
    subgraph AI["AI-Powered Features"]
        B[Job Analysis]
        C[Resume Tailoring]
        D[Cover Letter Generation]
        E[Improvement Suggestions]
    end
    
    subgraph Tracking["Application Management"]
        F[Application Tracker]
        F1[Track Applications]
        F2[Interview Management]
        F3[Outcome Tracking]
        F --> F1
        F --> F2
        F --> F3
    end
    
    subgraph Providers["Multi-AI Support"]
        G[Cloud Providers]
        G1[OpenAI]
        G2[Anthropic Claude]
        G3[Google Gemini]
        G4[Groq]
        G5[Perplexity]
        G6[xAI Grok]
        G --> G1
        G --> G2
        G --> G3
        G --> G4
        G --> G5
        G --> G6
        
        H[Local Providers]
        H1[Ollama]
        H2[llama.cpp]
        H3[LM Studio]
        H4[Lemonade]
        H --> H1
        H --> H2
        H --> H3
        H --> H4
    end
    
    subgraph Output["Export & Generation"]
        I[PDF Generation]
        I1[Resume PDF]
        I2[Cover Letter PDF]
        I3[Job Analysis PDF]
        I --> I1
        I --> I2
        I --> I3
    end
    
    subgraph Privacy["Privacy Protection"]
        J[Privacy-Preserving Workflow]
        J1[Strip Personal Data]
        J2[AI Processing]
        J3[Restore Personal Data]
        J --> J1
        J1 --> J2
        J2 --> J3
    end
    
    A --> B
    A --> C
    A --> D
    B --> C
    B --> D
    C --> I
    D --> I
    B --> F
    C --> F
    D --> F
    B --> G
    B --> H
    C --> G
    C --> H
    D --> G
    D --> H
    B --> J
    C --> J
    D --> J
    
    style A fill:#1e3a5f,stroke:#4a90d9,color:#fff
    style B fill:#166534,stroke:#22c55e,color:#fff
    style C fill:#166534,stroke:#22c55e,color:#fff
    style D fill:#166534,stroke:#22c55e,color:#fff
    style E fill:#166534,stroke:#22c55e,color:#fff
    style F fill:#7c2d12,stroke:#f97316,color:#fff
    style G fill:#0369a1,stroke:#38bdf8,color:#fff
    style H fill:#0369a1,stroke:#38bdf8,color:#fff
    style I fill:#6b21a8,stroke:#a855f7,color:#fff
    style J fill:#991b1b,stroke:#ef4444,color:#fff
```

</div>

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
