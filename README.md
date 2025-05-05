<h1 align="center">💼 Resume Helper AI</h1>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="Apache-2.0 License">
  </a>
</p>

**Resume Helper AI** is a desktop application leveraging state-of-the-art AI models (**Google Gemini** and **OpenAI GPT-4o**) to generate personalized resumes and cover letters. The application intelligently tailors your documents based on your provided information and selected job descriptions, simplifying the job-application process.

---

## 📖 Quick Start  
See the 👉 [Usage Guide](USAGE_GUIDE.md) for installation and step-by-step usage details

## ✨ Key Features

- **Automated Resume Generation**: Create professional, tailored resumes quickly.
- **Customized Cover Letters**: Generate compelling, personalized cover letters instantly.
- **AI-Powered Content**: Uses **Google Gemini** and **OpenAI GPT-4o** for accurate, context-sensitive outputs.
- **Easy-to-use Interface**: Tab-based GUI simplifies data entry and document management.

---

## 🕓 Version History

| Date | Version | Highlights |
|------|:------:|-----------|
| **2025-05-05** | **0.2.0** | **One-Click installer** overhauled<br>• now uses **Miniconda** to install Python 3.11+ if absent<br>• auto-installs GTK runtime (tschoonj build) for WeasyPrint |
| 2025-04-29 | 0.1.0 | Initial public release on GitHub |

## 📌 Prerequisites

- **Operating System**: Windows 10 or Windows 11
- **Internet Connection**: Required for installing dependencies and accessing AI models.

> **Note:** API keys for **Google Gemini** and **OpenAI GPT-4o** can be configured directly within the application's GUI (**AI Resume Helper** tab).

---

## 🚀 Installation & Run (Windows 10/11)

### ⚡ One-Click Windows Installation

1.  **Download or Clone** this repository and open the project folder.
2.  **Double-click `install_run_windows.bat`** (or run from command prompt):

```cmd
install_run_windows.bat
```

The script will automatically:

✅ Check and install Python 3.11+ if it's missing.
✅ Create and activate a local virtual environment (`venv`).
✅ Install all required dependencies (`pip install -r requirements.txt`).
✅ Free port `53630` automatically if currently in use.
✅ Launch the Resume Helper application at: `http://localhost:53630`
✅ Keep the console window open to clearly display any messages or errors.

⚠️ **SmartScreen or Antivirus Warning?**
Right-click on the batch file → `Properties` → `Unblock`, then run it again.
(The script is plain text and safe to inspect with Notepad.)

🖱️ **Starting the App Later**
Whenever you want to start Resume Helper AI again, simply double-click `install_run_windows.bat`.
If the application is already set up, the script will skip installation steps and immediately launch the app.
(Tip: Create a desktop shortcut to the batch file for even quicker access.)

---

## 📁 Project Structure

```text
.
├── .gitignore
├── app.py                     # Main application entry point
├── base_ai_provider.py        # Base class for AI integrations
├── cover_letter_generator.py  # Logic for generating cover letters
├── resume_generator.py        # Logic for generating resumes
├── sample_resume.json         # Example resume data structure
├── unified_ai_features.py     # Core AI feature integration
├── Resume_Templates/          # HTML templates for output
│   ├── classic_cover_letter.html
│   └── classic_template.html
├── tabs/                      # GUI tabs/modules
│   ├── __init__.py
│   ├── ai_resume_helper_tab.py
│   ├── certifications_tab.py
│   ├── educations_tab.py
│   ├── experiences_tab.py
│   ├── generate_resume_tab.py
│   ├── personal_info_tab.py
│   ├── projects_tab.py
│   └── skills_tab.py
├── utils/                     # Utility functions
│   ├── __init__.py
│   └── file_utils.py

```

---

## 🛠️ Troubleshooting

*   **Missing API Key:** The app requires API keys for the AI models. You can easily input your keys within the application's GUI (**AI Resume Helper** tab).
*   **Rate Limits:** AI providers set limits on API calls. If you encounter limit issues, consider upgrading your plan or waiting briefly before trying again.
*   **Windows Antivirus or SmartScreen Warning:** Antivirus software or SmartScreen might flag the `install_run_windows.bat` file. Right-click on the batch file → `Properties` → `Unblock`, then re-run.

---

## 📄 License

This project is licensed under the Apache License, Version 2.0. 
