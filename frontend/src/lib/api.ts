/**
 * API client for Resume Helper backend
 * Base URL is configured via environment variable VITE_API_URL
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    job_description: string,
    resume_data: any,
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
  async getApplication(appId: number) {
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
  async updateApplication(appId: number, data: any) {
    return fetchAPI(`/api/applications/${appId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Delete application
  async deleteApplication(appId: number) {
    return fetchAPI(`/api/applications/${appId}`, {
      method: 'DELETE',
    });
  },

  // Get application settings
  async getApplicationSettings() {
    return fetchAPI('/api/applications/settings');
  },

  // Update interview round
  async updateInterviewRound(appId: number, roundName: string, roundData: any) {
    return fetchAPI(`/api/applications/${appId}/interview/${roundName}`, {
      method: 'PUT',
      body: JSON.stringify(roundData),
    });
  },

  // Upload document
  async uploadDocument(appId: number, file: File) {
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
  async downloadDocument(appId: number, docId: number) {
    const response = await fetch(`${API_BASE_URL}/api/applications/${appId}/documents/${docId}`);
    
    if (!response.ok) {
      throw new Error('Download failed');
    }

    return response.blob();
  },

  // Delete document
  async deleteDocument(appId: number, docId: number) {
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

  /**
   * PDF Generation APIs
   */

  // Generate PDF
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
};
