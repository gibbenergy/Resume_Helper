<div align="center">
  <img src="Resume_Helper/assets/logo.jpg" alt="Resume Helper Logo" width="200"/>
  

  
  **AI-powered resume builder with multi-provider LLM support**
  
  [![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![Code Quality](https://github.com/gibbenergy/Resume_Helper/actions/workflows/code-quality.yml/badge.svg)](https://github.com/gibbenergy/Resume_Helper/actions/workflows/code-quality.yml)
  
  📖 [Usage Guide](USAGE_GUIDE.md) | 📄 [License](LICENSE)
  
</div>

## 📺 App Demo

<div align="center">

[![Resume Helper Demo](https://img.youtube.com/vi/SQgfXfSYLac/0.jpg)](https://www.youtube.com/watch?v=SQgfXfSYLac)

</div>

---

---

## ✨ Features

🎯 **Resume Building** - Create resumes with personal info, education, experience, skills, projects, certifications

🤖 **AI Resume Tailoring** - Adapt your resume to match job descriptions

✉️ **AI Cover Letters** - Generate personalized cover letters

📊 **Job Analysis** - Analyze job postings with AI insights

📋 **Application Tracker** - Track applications, interviews, and outcomes

🔌 **Multi-AI Support** - OpenAI, Anthropic, Google, Groq, Ollama, Perplexity, xAI, llama.cpp, LM Studio, Lemonade

📄 **PDF Generation** - Export professional resumes and cover letters

## Quick Start (Windows)

```bash
install_run_windows.bat
```

Or manually:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cd Resume_Helper
python app.py
```

Access at: `http://localhost:53441`

## Configuration

API keys are configured directly in the app:
1. Launch the app
2. Go to "AI Resume Helper" tab
3. Expand "AI Configuration" 
4. Select provider, enter API key, click "Set"

Keys are auto-saved and remembered for next session.

## Supported AI Models

**🦙 Recommended: Local Models (Free)**

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

**☁️ Cloud Providers (API key required)**
- **OpenAI**: GPT-4.1, GPT-5, GPT-5-mini
- **Anthropic**: Claude Opus 4, Claude 3.5 Sonnet
- **Google**: Gemini 2.5 Pro, Gemini 2.5 Flash
- **Groq**: Llama 3.3
- **Perplexity**: Sonar Pro, Sonar Reasoning
- **xAI**: Grok 4, Grok 3

## Requirements

- Windows 10/11
- Python 3.11+
- For Ollama: ~14GB disk space for gpt-oss model

## License

Business Source License 1.1 - See LICENSE file
Free for personal/educational use. Commercial use requires a license.

