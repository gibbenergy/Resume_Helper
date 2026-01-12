# Resume Helper Usage Guide

This guide explains how to download, install, and use the Resume Helper application.

## 1. Download the Application

First, download the application code from the GitHub repository:

```bash
git clone https://github.com/gibbenergy/Resume_Helper.git
cd Resume_Helper
```

Alternatively, you can download the repository as a ZIP file from the GitHub page (https://github.com/gibbenergy/Resume_Helper) and extract it to a folder on your computer. Navigate into the extracted folder using your terminal or command prompt.

## 2. Installation and Running the Application

The application includes scripts to simplify the installation and running process. Choose the script appropriate for your operating system.

### Windows Users

1.  Navigate to the `Resume_Helper` folder you downloaded or extracted.
2.  Double-click the `install_run_windows.bat` file.
3.  This script will:
    *   Check if Python 3.11+ is installed. If not found, it will display an error message and exit.
    *   Ensure `pip` (Python package installer) is available.
    *   Create a Python virtual environment (`.venv`) if it doesn't exist.
    *   Install the required dependencies listed in `requirements.txt`.
    *   Install Playwright Chromium browser.
    *   Check if the default port (53441) is busy and attempt to free it if necessary.
    *   Start the Resume Helper application.
4.  Your default web browser should automatically open to `http://localhost:53441`, displaying the application interface.

## 3. Using the Application Interface

The application uses a tabbed interface to organize resume sections:

*   **Personal Info:** Enter your name, contact details, summary, and links (LinkedIn, GitHub, Portfolio). You can also load an example profile from here.
*   **Educations:** Add details about your educational background (institution, degree, dates, GPA, description).
*   **Experiences:** Add your work history (company, position, dates, description, achievements). Use bullet points (starting with `- `) for achievements.
*   **Skills:** List your skills, categorized (e.g., Programming, Framework) with proficiency levels.
*   **Projects:** Detail personal or professional projects (title, description, technologies, URL, dates).
*   **Certifications:** Add any relevant certifications (name, issuer, date, ID, URL).

**Common Actions in Tabs:**

*   **Add:** Fill in the fields and click "Add" to add an entry to the list/table below.
*   **Remove Selected:** Select one or more rows in the table and click "Remove Selected" to delete them.
*   **Clear All:** Click "Clear All" to remove all entries from the current section's table.
*   **Reset Fields:** Click "Reset" to clear the input fields in the current section.

**Saving and Loading:**

*   Use the "Generate JSON" and "Download JSON" buttons (in the "Import & Export" tab) to save all your entered data to a `.json` file.
*   Use the "Load from JSON" button (in the "Import & Export" tab) to load data from a previously saved `.json` file.

## 4. Generating Your Resume

1.  Navigate to the **Import & Export** tab.
2.  Click the **Generate Resume (PDF)** button.
3.  A PDF file of your resume will be generated and saved. Click the **Download PDF** button to download the file.

## 4.5 Setting Up Local AI Models (Recommended - Free) 🦙

You have **three options** for running AI models locally on your computer - no API key, no cost, no internet required after setup.

### Option 1: Ollama (Easiest - Recommended for Beginners)

Ollama is the easiest way to get started with local AI models.

#### Step 1: Install Ollama

1. Go to: https://ollama.com/download
2. Download the **Windows** installer
3. Run the installer and follow the prompts
4. Ollama will start automatically as a background service

#### Step 2: Download a Model

Open **Command Prompt** or **PowerShell** and run:

```bash
ollama pull gpt-oss
```

This downloads OpenAI's open-weight model (~14GB). It has 128K context and is designed for reasoning tasks - perfect for resume tailoring.

**Alternative models** (smaller/faster):
```bash
ollama pull qwen2.5:7b      # ~4GB, fast
ollama pull llama3.3        # ~4GB, good quality
ollama pull deepseek-r1:8b  # ~5GB, strong reasoning
```

#### Step 3: Verify Ollama is Running

```bash
ollama list
```

You should see your downloaded model(s) listed.

#### Step 4: Use in Resume Helper

1. Launch Resume Helper
2. Go to **AI Resume Helper** tab
3. Select **Ollama (Local)** as the provider
4. Leave the API key field **empty**
5. Select **gpt-oss:latest** (or your downloaded model) from the Model dropdown
6. Click **Set**

---

### Option 2: llama.cpp (High Performance)

llama.cpp provides the fastest inference with the lowest memory usage. Perfect if you want maximum performance.

#### Step 1: Install llama.cpp

**Option A: Pre-built Binary (Easiest)**
1. Go to: https://github.com/ggerganov/llama.cpp/releases
2. Download the latest `llama-cpp-windows-xxx.zip` for your system
3. Extract to a folder (e.g., `C:\llama.cpp`)

**Option B: Build from Source**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release
```

#### Step 2: Download a GGUF Model

Download models from HuggingFace (GGUF format):
- **Recommended**: [TheBloke/Llama-2-7B-Chat-GGUF](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF)
- Or search "GGUF" on HuggingFace for any model

Save the `.gguf` file to your llama.cpp folder.

#### Step 3: Start the Server

Open **Command Prompt** in your llama.cpp folder:

```bash
# For CPU (works on any PC)
.\build\bin\Release\server.exe -m your-model.gguf --host 0.0.0.0 --port 8080

# For NVIDIA GPU (faster)
.\build\bin\Release\server.exe -m your-model.gguf --host 0.0.0.0 --port 8080 -ngl 32
```

**Parameters**:
- `-m` = path to your GGUF model file
- `--port` = server port (default: 8080)
- `-ngl` = number of GPU layers (for GPU acceleration)
- `-c` = context size (e.g., `-c 8192`)

#### Step 4: Use in Resume Helper

1. Launch Resume Helper
2. Go to **AI Resume Helper** tab
3. Select **llama.cpp** as the provider
4. Leave the API key field **empty**
5. **Custom Base URL**: `http://localhost:8080/v1` (or your custom port)
6. Click **Set**

---

### Option 3: LM Studio (User-Friendly GUI)

LM Studio provides the easiest way to download, manage, and run models with a beautiful interface.

#### Step 1: Install LM Studio

1. Go to: https://lmstudio.ai/
2. Download **LM Studio** for Windows
3. Install and launch the application

#### Step 2: Download a Model

1. In LM Studio, click **🔍 Search** (or "Discover" tab)
2. Search for models (recommended):
   - `TheBloke/Llama-2-7B-Chat-GGUF`
   - `TheBloke/Mistral-7B-Instruct-v0.2-GGUF`
   - `TheBloke/Qwen2.5-7B-Instruct-GGUF`
3. Click **Download** on your chosen model
4. Wait for download to complete

#### Step 3: Start the Local Server

1. In LM Studio, click **↔️ Local Server** (left sidebar)
2. Select your downloaded model from the dropdown
3. Click **Start Server**
4. Server will start at `http://localhost:1234` by default
5. Keep LM Studio running while using Resume Helper

#### Step 4: Use in Resume Helper

1. Launch Resume Helper
2. Go to **AI Resume Helper** tab
3. Select **LM Studio** as the provider
4. Leave the API key field **empty**
5. **Custom Base URL**: `http://localhost:1234/v1` (default)
6. Click **Set**

---

## 4.6 Getting API Keys (Cloud Providers) 🔑

> **Prefer cloud AI instead of local?**  
> You can obtain API keys from any of the supported providers:
> - **OpenAI**: https://platform.openai.com/api-keys
> - **Anthropic**: https://console.anthropic.com/
> - **Google**: https://aistudio.google.com/apikey
> - **Groq**: https://console.groq.com/keys
> - **Perplexity**: https://www.perplexity.ai/settings/api
> - **xAI**: https://console.x.ai/

## 5. Using AI Features (Optional)

The **AI Resume Helper** tab lets you refine your résumé (and draft a cover-letter) with any of the supported AI models (OpenAI, Anthropic, Google, Groq, Ollama, llama.cpp, LM Studio, Perplexity, or xAI).

1. **Configure AI**

   - Choose the provider (OpenAI, Anthropic, Google, Groq, **Ollama**, **llama.cpp**, **LM Studio**, Perplexity, or xAI).
   - **For local providers** (Ollama/llama.cpp/LM Studio): Leave API key empty
   - **For llama.cpp/LM Studio**: Enter the custom base URL (e.g., `http://localhost:8080/v1`)
   - **For cloud providers**: Paste your API key
   - Click **Set**.
   - Pick the desired model in **Model**.

2. **Paste the Job Description**

   Insert the full posting into **Job Description** so the model knows what you're targeting.

3. **Load Your Latest Résumé**

   Click **🔄 Update Resume**.  
   This pulls the most-recent data from the other tabs into *Current Resume JSON*.

4. **(Optional) Add a User Prompt**

   Expand **➕ Optional User Prompt** and supply stylistic guidance or focus areas, e.g.

   > *I.e., Use a results-driven tone and emphasise on certain achievement.*

5. **Process with AI**

   | Button | Action |
   | ------ | ------ |
   | **🔍 Analyze Job** | Extract key skills / requirements from the job description |
   | **🎯 Tailor Resume** | Produce a résumé JSON aligned to those requirements (no invented skills) |
   | **✉️ Cover Letter** | Draft a cover letter based on the tailored résumé & job description |
   | **💡 Suggestions** | Provide targeted advice for further improvements |

6. **Generate a PDF**

   - In **Select PDF Type** choose **Tailored Resume** *or* **Cover Letter**.  
   - Click **Generate PDF** → then **Download PDF** to save the file.

7. **Review the Outputs**

   Check each output tab, copy or tweak content as needed, and you're ready to apply!


## 6. Application Tracker 📋

The **Application Tracker** tab helps you manage and track all your job applications in one place.

### Adding a New Application

1. Click **➕ Add Application**
2. Fill in the required fields:
   - **Job URL** - Link to the job posting
   - **Company** - Company name
   - **Position** - Job title
3. Optional fields:
   - **Location** - Job location (remote, city, etc.)
   - **Date Applied** - Defaults to today
   - **Status** - Applied, Offer, Accepted, Rejected, Withdrawn
   - **Priority** - High, Medium, Low
   - **Application Source** - LinkedIn, Indeed, Company Website, Referral, etc.
   - **Salary Range** - Min/Max expected salary
   - **Match Score** - How well you match (0-100%)
   - **Job Description** - Full job posting text
   - **Notes** - Personal notes
   - **Contact Information** - HR, Hiring Manager, Recruiter, Referral contacts
4. Click **💾 Save Application**

### Managing Applications

| Action | How To |
|--------|--------|
| **View Details** | Click any row in the applications table |
| **Edit** | Click row → **✏️ Edit** |
| **Delete** | Click row → **🗑️ Delete** |
| **Search** | Type in the search box (searches company & position) |
| **Sort** | Use the "Sort By" dropdown (date, company, match score, status, priority) |
| **Filter** | Use "Filter by Status" to show only specific statuses |

### Interview Pipeline Management 🎯

Track your progress through multiple interview rounds:

1. Click on an application row to view details
2. Click **📅 Manage Interviews**
3. You'll see all interview rounds with their status:
   - ⭕ Not Started
   - 📅 Scheduled
   - ✅ Completed

**To edit a round:** Click on any round row to open the details form:
- Date & Time
- Location (Office, Zoom, Phone, etc.)
- Interviewer name
- Status (scheduled, completed, cancelled, rescheduled)
- Outcome (pending, passed, failed, needs_follow_up)
- Notes (preparation, feedback, next steps)

**Navigation:**
- **⏭️ Advance** - Mark current round as passed and move to next
- **⬅️ Go Back** - Revert to previous round

### Document Management 📁

Attach documents to each application (resume versions, cover letters, portfolios, etc.):

1. Open application details (click a row)
2. Expand the **📁 Documents** section
3. **Upload:** Drag & drop or click to upload files
4. **Download:** Click a document → **⬇️ Download**
5. **Delete:** Click a document → **🗑️ Delete**

Supported file types: PDF, DOC, DOCX, TXT, images, code files, archives, and more.

---

## 7. Stopping the Application

To stop the Resume Helper application:

*   Go back to the terminal or command prompt window where you ran the installation script (`.bat` or `.py`).
*   Press `Ctrl + C`.
*   Close the terminal window.

This concludes the usage guide for the Resume Helper application.
