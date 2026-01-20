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

| Category | Features |
|----------|----------|
| **Resume Building** | Personal Info, Education, Experience, Skills, Projects, Certifications |
| **AI Features** | Job Analysis, Resume Tailoring, Cover Letters, Suggestions |
| **Application Tracker** | Track Applications, Interview Management, Outcome Tracking |
| **Multi-AI Support** | Cloud Providers (OpenAI, Anthropic, Google, Groq, xAI, Perplexity) + Local (Ollama, llama.cpp, LM Studio, Lemonade) |
| **PDF Generation** | Resume PDF, Cover Letter PDF, Analysis PDF |
| **Privacy Protection** | Strip Personal Data before AI, Restore after processing |

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

</div>

## Supported AI Providers

<div align="center">

**Cloud Providers**

[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-191919?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Google](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Perplexity](https://img.shields.io/badge/Perplexity-1FB8CD?style=for-the-badge&logo=perplexity&logoColor=white)](https://perplexity.ai)
[![xAI](https://img.shields.io/badge/xAI_Grok-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.ai)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logoColor=white)](https://groq.com)

**Local Providers**

[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logoColor=white)](https://ollama.com)
[![llama.cpp](https://img.shields.io/badge/llama.cpp-00ADD8?style=for-the-badge&logoColor=white)](https://github.com/ggml-org/llama.cpp)
[![LM Studio](https://img.shields.io/badge/LM_Studio-6366F1?style=for-the-badge&logoColor=white)](https://lmstudio.ai)
[![Lemonade](https://img.shields.io/badge/Lemonade-FBBF24?style=for-the-badge&logoColor=black)](https://github.com/lemonade-sdk/lemonade)

</div>

## Quick Start (Windows)

```bash
start_react_ui.bat
```

Access at: `http://localhost:5173`

For manual setup, see [Usage Guide](USAGE_GUIDE.md).

## Requirements

- Windows 10/11
- Python 3.11+
- Node.js 18+

## License

Business Source License 1.1 - See LICENSE file
