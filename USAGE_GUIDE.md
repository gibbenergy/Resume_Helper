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
    *   Check if Python 3.11+ is installed. If not, it will download and set up a local version.
    *   Ensure `pip` (Python package installer) is available.
    *   Create a Python virtual environment (`venv`) if it doesn't exist.
    *   Install the required dependencies listed in `requirements.txt`.
    *   Check if the default port (53630) is busy and attempt to free it if necessary.
    *   Start the Resume Helper application.
4.  Your default web browser should automatically open to `http://localhost:53630`, displaying the application interface.

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

*   Use the "Generate JSON" and "Download JSON" buttons (in the "Generate Resume" tab) to save all your entered data to a `.json` file.
*   Use the "Load from JSON" button (in the "Generate Resume" tab) to load data from a previously saved `.json` file.

## 4. Generating Your Resume

1.  Navigate to the **Generate Resume** tab.
2.  Click the **Generate Resume (PDF)** button.
3.  A PDF file of your resume will be generated and saved. Click the **Download PDF** button to download the file .

## 4.5 Getting Your API Keys 🔑

> **Need an OpenAI or Google Gemini key?**  
> Follow the step-by-step guide here:  
> **[How to obtain your API keys](docs/API_KEYS.md)**

## 5. Using AI Features (Optional)

The **AI Resume Helper** tab lets you refine your résumé (and draft a cover-letter) with OpenAI or Gemini models.

1. **Configure AI**

   - Choose the provider **(OpenAI or Gemini)**.  
   - Paste your API key.  
   - Click **🧪 Test and Save API Key**.  
   - Pick the desired model in **Model**.

2. **Paste the Job Description**

   Insert the full posting into **Job Description** so the model knows what you’re targeting.

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

   Check each output tab, copy or tweak content as needed, and you’re ready to apply!


## 6. Stopping the Application

To stop the Resume Helper application:

*   Go back to the terminal or command prompt window where you ran the installation script (`.bat` or `.py`).
*   Press `Ctrl + C`.
*   Close the terminal window.

This concludes the usage guide for the Resume Helper application.
