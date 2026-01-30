# Changelog

All notable changes to Resume Helper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-01-30

### Added
- **Reorder functionality** - Up/down move buttons on all form sections (Education, Experience, Skills, Projects, Certifications, Others)
- **Custom profile names** - SaveProfileDialog component allowing users to name multiple resume versions with duplicate detection
- **Test infrastructure** - 198 automated tests with CI integration
- **Playwright auto-install** - Start script now automatically installs browser dependencies for PDF generation

### Fixed
- **PersonalInfo auto-sync** - Form changes no longer lost when switching tabs; all field changes now sync to store automatically
- **PDF contact separators** - Fixed missing separators between citizenship, phone, and email when address fields are empty
- **Application tracker validation** - Fixed import paths, URL validation, error handling, and AI response parsing
- **Salary parsing** - Added support for `base` property and made parsing LLM-agnostic (works regardless of AI response format)
- **Settings endpoint 404** - Fixed FastAPI route ordering so `/api/applications/settings` resolves correctly
- **UV hardlink error** - Added `--link-mode copy` to support cloud-synced folders (OneDrive, Dropbox, etc.)

### Changed
- **Start script** - Now 5-step automated setup (UV check, Python deps, Playwright browsers, Node deps, server start)
- **Test isolation** - Tests now use separate SQLite database in temp directory to prevent production data pollution

### Developer Notes
- CI workflows updated: `frontend-ci.yml` and `code-quality.yml` now execute vitest and pytest
- Test fixtures include profile cleanup to prevent ghost data

---

## [3.0.0] - 2026-01-01

**Frontend rewrite: Migrated from Gradio to React + TypeScript**

### Changed
- **Complete frontend rewrite** - Migrated from Gradio to React 18 + TypeScript
- **Modern state management** - Zustand replacing Gradio's built-in state
- **Component library** - Tailwind CSS + Radix UI for accessible, polished UI
- **Build tooling** - Vite for fast development and builds

### Added
- **Additional local LLM support** - llama.cpp, LM Studio, Lemonade

### Technical Stack (v3)
- Frontend: React 18, TypeScript, Vite, Zustand, Tailwind CSS, Radix UI
- Backend: FastAPI, SQLAlchemy, LiteLLM, Playwright (unchanged from v2)

---

## [2.0.0] - 2025-11-01

**Major architecture rewrite: CLEAN architecture + Multi-provider LLM support**

### Added
- **Multi-provider LLM support** via LiteLLM - OpenAI, Anthropic Claude, Google Gemini, Groq, Perplexity, xAI
- **Local-first LLM support** - Ollama integration for privacy-focused users
- **Application tracker** - Track job applications with status and interview pipeline
- **Cost tracking** - Monitor API usage costs across all LLM providers
- **SQLite database** - Persistent storage replacing JSON files

### Changed
- **Complete code rewrite** - Restructured using CLEAN architecture principles
- **Backend architecture** - FastAPI with SQLAlchemy ORM
- **LLM abstraction** - Unified interface via LiteLLM replacing individual SDKs

### Technical Stack (v2)
- Frontend: Gradio (Python)
- Backend: FastAPI, SQLAlchemy, LiteLLM, Playwright
- Database: SQLite

---

## [1.0.0] - 2025-06-01

**Initial Release**

### Added
- **AI-powered resume analysis** - Job description analysis with match scoring
- **Resume tailoring** - AI-generated resume customization for specific jobs
- **Cover letter generation** - AI-powered cover letter creation
- **PDF generation** - Export resumes to PDF format
- **Profile management** - Save and load resume profiles

### Technical Stack (v1)
- Frontend: Gradio (Python)
- Backend: Python with OpenAI SDK, Google Gemini SDK
- Storage: JSON files

---

[3.1.0]: https://github.com/gibbenergy/Resume_Helper/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/gibbenergy/Resume_Helper/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/gibbenergy/Resume_Helper/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/gibbenergy/Resume_Helper/releases/tag/v1.0.0
