/**
 * API client for Resume Helper backend
 * Base URL is configured via environment variable VITE_API_URL
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * AI Workflow APIs
 */
export const api = {
  // Test API key
  async testApiKey(provider: string, apiKey: string, model?: string) {
    return fetchAPI('/api/ai/test-api-key', {
      method: 'POST',
      body: JSON.stringify({ provider, api_key: apiKey, model }),
    });
  },

  // Get available providers
  async getProviders() {
    return fetchAPI('/api/ai/providers');
  },

  // Get models for a provider
  async getModels(provider: string) {
    return fetchAPI(`/api/ai/models?provider=${encodeURIComponent(provider)}`);
  },

  // Get cost tracking data
  async getCost() {
    return fetchAPI('/api/ai/cost');
  },

  // Update LiteLLM package
  async updateLiteLLM() {
    return fetchAPI('/api/ai/update-litellm', { method: 'POST' });
  },

  // Analyze job description
  async analyzeJob(job_description: string, resume_data: any, model?: string) {
    return fetchAPI('/api/ai/analyze-job', {
      method: 'POST',
      body: JSON.stringify({ job_description, resume_data, model }),
    });
  },

  // Tailor resume
  async tailorResume(
    resume_data: any,
    job_description: string,
    model?: string,
    user_prompt?: string,
    job_analysis_data?: any
  ) {
    return fetchAPI('/api/ai/tailor-resume', {
      method: 'POST',
      body: JSON.stringify({
        resume_data,
        job_description,
        model,
        user_prompt,
        job_analysis_data,
      }),
    });
  },

  // Generate cover letter
  async generateCoverLetter(
    resume_data: any,
    job_description: string,
    model?: string,
    user_prompt?: string,
    job_analysis_data?: any
  ) {
    return fetchAPI('/api/ai/generate-cover-letter', {
      method: 'POST',
      body: JSON.stringify({
        resume_data,
        job_description,
        model,
        user_prompt,
        job_analysis_data,
      }),
    });
  },

  // Get improvement suggestions
  async getImprovementSuggestions(
    resume_data: any,
    job_description: string,
    model?: string,
    job_analysis_data?: any
  ) {
    return fetchAPI('/api/ai/improvement-suggestions', {
      method: 'POST',
      body: JSON.stringify({
        job_description,
        resume_data,
        model,
        job_analysis_data,
      }),
    });
  },

  /**
   * Application Tracker APIs
   */

  // Get all applications
  async getApplications() {
    return fetchAPI('/api/applications');
  },

  // Get single application
  async getApplication(appId: string) {
    return fetchAPI(`/api/applications/${appId}`);
  },

  // Create application
  async createApplication(data: any) {
    return fetchAPI('/api/applications', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Update application
  async updateApplication(appId: string, data: any) {
    return fetchAPI(`/api/applications/${appId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Delete application
  async deleteApplication(appId: string) {
    return fetchAPI(`/api/applications/${appId}`, {
      method: 'DELETE',
    });
  },

  // Get application settings
  async getApplicationSettings() {
    return fetchAPI('/api/applications/settings');
  },

  // Update interview round
  async updateInterviewRound(appId: string, roundName: string, roundData: any) {
    return fetchAPI(`/api/applications/${appId}/interview-rounds/${roundName}`, {
      method: 'POST',
      body: JSON.stringify(roundData),
    });
  },

  // Upload document
  async uploadDocument(appId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/applications/${appId}/documents`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail);
    }

    return response.json();
  },

  // Download document
  async downloadDocument(appId: string, docId: number) {
    const response = await fetch(`${API_BASE_URL}/api/applications/${appId}/documents/${docId}/download`);
    
    if (!response.ok) {
      throw new Error('Download failed');
    }

    return response.blob();
  },

  // Delete document
  async deleteDocument(appId: string, docId: number) {
    return fetchAPI(`/api/applications/${appId}/documents/${docId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Resume APIs
   */

  // Build resume profile
  async buildProfile(data: any) {
    return fetchAPI('/api/resume/build-profile', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Get resume data
  async getResumeData() {
    return fetchAPI('/api/resume/data');
  },

  // Load software developer example
  async loadSoftwareDeveloperExample() {
    return fetchAPI('/api/resume/example/software-developer');
  },

  // Load process engineer example
  async loadProcessEngineerExample() {
    return fetchAPI('/api/resume/example/process-engineer');
  },

  // Load from JSON file
  async loadFromJson(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/resume/load-from-json`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load JSON' }));
      throw new Error(error.detail);
    }

    return response.json();
  },

  // Load from PDF file
  async loadFromPDF(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/resume/load-from-pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load PDF' }));
      throw new Error(error.detail);
    }

    return response.json();
  },

  // Load from DOCX file
  async loadFromDOCX(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/resume/load-from-docx`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load DOCX' }));
      throw new Error(error.detail);
    }

    return response.json();
  },

  /**
   * PDF Generation APIs
   */

  // Generate resume PDF
  async generateResumePDF(data: any) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-resume`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_data: data,
        pdf_type: 'resume'
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'PDF generation failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Generate resume DOCX
  async generateResumeDOCX(data: any) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-resume-docx`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_data: data
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'DOCX generation failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Generate JSON export
  async generateJson(data: any) {
    const response = await fetch(`${API_BASE_URL}/api/resume/generate-json`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'JSON export failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Generate job analysis PDF
  async generateJobAnalysisPDF(analysisData: any) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-job-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        analysis_data: analysisData
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Analysis PDF generation failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Generate tailored resume PDF
  async generateTailoredResumePDF(data: any) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-tailored-resume`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tailored_resume_data: data
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Tailored resume PDF generation failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Generate cover letter PDF
  async generateCoverLetterPDF(resumeData: any, coverLetterData: any, jobAnalysis: any) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-cover-letter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_data: resumeData,
        pdf_type: 'cover_letter',
        cover_letter_data: coverLetterData,
        job_analysis_data: jobAnalysis,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Cover letter PDF generation failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Generate suggestions PDF
  async generateSuggestionsPDF(content: string, fullName: string, company: string, position: string) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate-suggestions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        suggestions_content: content,
        full_name: fullName,
        company_name: company,
        job_position: position,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Suggestions PDF generation failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Generate PDF (generic)
  async generatePDF(data: any) {
    const response = await fetch(`${API_BASE_URL}/api/pdf/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'PDF generation failed' }));
      throw new Error(error.detail);
    }

    return response.blob();
  },

  // Get job description PDF URL for an application
  getJobDescriptionPDFUrl(appId: string): string {
    return `${API_BASE_URL}/api/pdf/job-description/${appId}`;
  },

  /**
   * Profile APIs - Server-side profile storage
   */

  // Get all saved profiles
  async getProfiles() {
    return fetchAPI('/api/profiles');
  },

  // Get a specific profile
  async getProfile(profileId: string) {
    return fetchAPI(`/api/profiles/${profileId}`);
  },

  // Save or update a profile
  async saveProfile(name: string, data: any, id?: string) {
    return fetchAPI('/api/profiles', {
      method: 'POST',
      body: JSON.stringify({ name, data, id }),
    });
  },

  // Delete a profile
  async deleteProfile(profileId: string) {
    return fetchAPI(`/api/profiles/${profileId}`, {
      method: 'DELETE',
    });
  },
};
 
