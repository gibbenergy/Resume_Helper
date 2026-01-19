import { create } from 'zustand';
import type {
  JobAnalysisResult,
  TailoredResumeResult,
  CoverLetterResult,
  ImprovementSuggestionsResult,
  ResumeData,
  ModelsInfo,
} from '@/lib/types';
import { api } from '@/lib/api';
import { formatAnalysisAsMarkdown, formatSuggestionsContent } from '@/lib/utils';

interface AIStore {
  // Provider configuration
  provider: string;
  model: string | null;
  apiKey: string;
  availableProviders: string[];
  availableModels: string[];
  
  // Cost tracking
  totalCost: number;
  costDisplay: string;
  
  // AI results
  jobAnalysis: JobAnalysisResult | null;
  tailoredResume: TailoredResumeResult | null;
  coverLetter: CoverLetterResult | null;
  improvementSuggestions: ImprovementSuggestionsResult | null;
  
  // Match score and summary
  matchScore: number;
  matchSummary: string;
  
  // Job URL
  jobUrl: string;
  
  // Form inputs (persist across tab switches)
  jobDescription: string;
  userPrompt: string;
  
  // PDF paths for each content type
  pdfPaths: {
    jobAnalysis: string | null;
    tailoredResume: string | null;
    coverLetter: string | null;
    suggestions: string | null;
  };
  
  // Editable content (user-modified versions)
  editedContent: {
    jobAnalysis: string | null;
    tailoredResume: string | null;
    coverLetter: string | null;
    suggestions: string | null;
  };
  
  // Status displays
  aiStatus: string;
  processingStatus: string;
  
  // Loading states
  analyzing: boolean;
  tailoring: boolean;
  generatingCoverLetter: boolean;
  gettingSuggestions: boolean;
  testingApiKey: boolean;
  
  // Error states
  error: string | null;
  
  // Actions
  setProvider: (provider: string) => Promise<void>;
  setModel: (model: string) => void;
  setApiKey: (apiKey: string) => void;
  testApiKey: () => Promise<boolean>;
  loadProviders: () => Promise<void>;
  loadModels: (provider: string) => Promise<void>;
  loadCost: () => Promise<void>;
  updateLiteLLM: () => Promise<void>;
  
  analyzeJob: (jobDescription: string, resumeData: ResumeData) => Promise<void>;
  tailorResume: (
    resumeData: ResumeData,
    jobDescription: string,
    userPrompt?: string
  ) => Promise<void>;
  generateCoverLetter: (
    resumeData: ResumeData,
    jobDescription: string,
    userPrompt?: string
  ) => Promise<void>;
  getImprovementSuggestions: (
    resumeData: ResumeData,
    jobDescription: string
  ) => Promise<void>;
  
  // New actions
  setMatchScore: (score: number) => void;
  setMatchSummary: (summary: string) => void;
  setJobUrl: (url: string) => void;
  setJobDescription: (description: string) => void;
  setUserPrompt: (prompt: string) => void;
  setPdfPath: (type: 'jobAnalysis' | 'tailoredResume' | 'coverLetter' | 'suggestions', path: string | null) => void;
  setEditedContent: (type: 'jobAnalysis' | 'tailoredResume' | 'coverLetter' | 'suggestions', content: string) => void;
  setProcessingStatus: (status: string) => void;
  updateAIStatus: () => void;
  
  clearResults: () => void;
  clearFormInputs: () => void;
  clearError: () => void;
}

export const useAIStore = create<AIStore>((set, get) => ({
  provider: 'Ollama (Local)',
  model: null,
  apiKey: '',
  availableProviders: [],
  availableModels: [],
  totalCost: 0.0,
  costDisplay: 'Total Cost: $0.000000',
  jobAnalysis: null,
  tailoredResume: null,
  coverLetter: null,
  improvementSuggestions: null,
  matchScore: 0,
  matchSummary: '',
  jobUrl: '',
  jobDescription: '',
  userPrompt: '',
  pdfPaths: {
    jobAnalysis: null,
    tailoredResume: null,
    coverLetter: null,
    suggestions: null,
  },
  editedContent: {
    jobAnalysis: null,
    tailoredResume: null,
    coverLetter: null,
    suggestions: null,
  },
  aiStatus: '',
  processingStatus: '',
  analyzing: false,
  tailoring: false,
  generatingCoverLetter: false,
  gettingSuggestions: false,
  testingApiKey: false,
  error: null,

  setProvider: async (provider: string) => {
    set({ provider });
    await get().loadModels(provider);
    // Silently sync the backend provider after models load
    // Get the newly loaded default model and sync backend
    const newModel = get().model;
    if (newModel) {
      // Call test-api-key in background to switch backend provider (no UI feedback)
      api.testApiKey(provider, '', newModel).catch(() => {});
    }
  },

  setModel: (model: string) => set({ model }),

  setApiKey: (apiKey: string) => set({ apiKey }),

  testApiKey: async () => {
    const { provider, apiKey, model } = get();
    set({ testingApiKey: true, error: null });
    try {
      // For Ollama, pass empty string - backend will handle it
      const keyToTest = provider === 'Ollama (Local)' ? '' : apiKey;
      const response = await api.testApiKey(provider, keyToTest, model || undefined);
      set({ testingApiKey: false });
      if (response.success) {
        await get().loadCost(); // Refresh cost after successful test
      }
      return response.success || false;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to test API key',
        testingApiKey: false,
      });
      return false;
    }
  },

  loadProviders: async () => {
    try {
      const response = await api.getProviders();
      if (response.success && response.providers) {
        set({ availableProviders: response.providers });
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  },

  loadModels: async (provider: string) => {
    try {
      const response = await api.getModels(provider);
      if (response.success && response.models) {
        set({
          availableModels: response.models,
          model: response.default || response.models[0] || null,
        });
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  },

  loadCost: async () => {
    try {
      const response = await api.getCost();
      // Backend returns {success: true, cost: number, display: string} directly
      if (response.success) {
        set({
          totalCost: (response as any).cost || 0.0,
          costDisplay: (response as any).display || 'Total Cost: $0.000000',
        });
      }
    } catch (error) {
      console.error('Failed to load cost:', error);
    }
  },

  updateLiteLLM: async () => {
    try {
      const response = await api.updateLiteLLM();
      if (response.success) {
        // After updating LiteLLM, refresh the cost to get updated pricing
        await get().loadCost();
        // Show success message
        alert(response.data?.message || 'LiteLLM updated successfully');
      } else {
        alert(response.data?.message || 'Failed to update LiteLLM');
      }
    } catch (error) {
      console.error('Failed to update LiteLLM:', error);
      alert('Failed to update LiteLLM. Please check the console for details.');
    }
  },

  analyzeJob: async (jobDescription: string, resumeData: ResumeData) => {
    const { model } = get();
    set({ analyzing: true, error: null });
    try {
      // Validate resumeData structure before sending
      if (!resumeData || !resumeData.personal_info) {
        const errorMsg = 'Resume data is incomplete. Please fill in at least the Personal Information section.';
        set({
          error: errorMsg,
          analyzing: false,
        });
        return;
      }
      
      const result = await api.analyzeJob(jobDescription, resumeData, model || undefined);
      
      // Update match score and summary if analysis succeeded
      if (result.success && result.analysis) {
        const analysis = result.analysis;
        // Format as markdown for editable content
        const formattedMarkdown = formatAnalysisAsMarkdown(analysis);
        set({
          jobAnalysis: result,
          analyzing: false,
          matchScore: analysis.match_score || 0,
          matchSummary: analysis.match_summary || '',
          jobUrl: analysis.job_url || get().jobUrl || '',
          processingStatus: 'Job analysis completed successfully!',
          editedContent: {
            ...get().editedContent,
            jobAnalysis: formattedMarkdown,
          },
        });
        get().updateAIStatus();
      } else {
        set({ 
          jobAnalysis: result, 
          analyzing: false, 
          processingStatus: result.error || 'Analysis failed',
          error: result.error || 'The LLM response is missing required fields. Please try a different model or check your model configuration.'
        });
      }
      
      // Refresh cost after operation
      await get().loadCost();
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to analyze job',
        analyzing: false,
      });
    }
  },

  tailorResume: async (
    resumeData: ResumeData,
    jobDescription: string,
    userPrompt?: string
  ) => {
    const { model, jobAnalysis } = get();
    set({ tailoring: true, error: null });
    try {
      // Auto-analyze if no job analysis exists
      let analysisData = jobAnalysis?.analysis;
      if (!analysisData) {
        set({ processingStatus: 'Auto-analyzing job description...' });
        const analysisResult = await api.analyzeJob(jobDescription, resumeData, model || undefined);
        if (analysisResult.success && analysisResult.analysis) {
          analysisData = analysisResult.analysis;
          set({
            jobAnalysis: analysisResult,
            matchScore: analysisData.match_score || 0,
            matchSummary: analysisData.match_summary || '',
            jobUrl: analysisData.job_url || get().jobUrl,
          });
          get().updateAIStatus();
        }
      }
      
      const result = await api.tailorResume(
        resumeData,
        jobDescription,
        model || undefined,
        userPrompt,
        analysisData
      );
      
      if (result.success && result.tailored_resume) {
        const tailoredJson = JSON.stringify(result.tailored_resume, null, 2);
        set({
          tailoredResume: result,
          tailoring: false,
          processingStatus: 'Resume tailored successfully!',
          editedContent: {
            ...get().editedContent,
            tailoredResume: tailoredJson,
          },
        });
      } else {
        set({ tailoredResume: result, tailoring: false, processingStatus: 'Resume tailored successfully!' });
      }
      // Refresh cost after operation
      await get().loadCost();
      get().updateAIStatus();
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to tailor resume',
        tailoring: false,
      });
    }
  },

  generateCoverLetter: async (
    resumeData: ResumeData,
    jobDescription: string,
    userPrompt?: string
  ) => {
    const { model, jobAnalysis } = get();
    set({ generatingCoverLetter: true, error: null });
    try {
      const result = await api.generateCoverLetter(
        resumeData,
        jobDescription,
        model || undefined,
        userPrompt,
        jobAnalysis?.analysis
      );
      if (result.success && result.body_content) {
        set({
          generatingCoverLetter: false,
          coverLetter: result,
          processingStatus: 'Cover letter generated successfully!',
          editedContent: {
            ...get().editedContent,
            coverLetter: result.body_content,
          },
        });
      } else {
        set({ generatingCoverLetter: false, coverLetter: result, processingStatus: 'Cover letter generated successfully!' });
      }
      // Refresh cost after operation
      await get().loadCost();
      get().updateAIStatus();
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to generate cover letter',
        generatingCoverLetter: false,
      });
    }
  },

  getImprovementSuggestions: async (resumeData: ResumeData, jobDescription: string) => {
    const { model, jobAnalysis } = get();
    set({ gettingSuggestions: true, error: null });
    try {
      const result = await api.getImprovementSuggestions(
        resumeData,
        jobDescription,
        model || undefined,
        jobAnalysis?.analysis
      );
      if (result.success && result.content) {
        // Format the content for proper bullet point display
        const formattedContent = formatSuggestionsContent(result.content);
        set({
          improvementSuggestions: result,
          gettingSuggestions: false,
          processingStatus: 'Improvement suggestions generated successfully!',
          editedContent: {
            ...get().editedContent,
            suggestions: formattedContent,
          },
        });
      } else {
        set({ improvementSuggestions: result, gettingSuggestions: false, processingStatus: 'Improvement suggestions generated successfully!' });
      }
      // Refresh cost after operation
      await get().loadCost();
      get().updateAIStatus();
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Failed to get improvement suggestions',
        gettingSuggestions: false,
      });
    }
  },

  setMatchScore: (score: number) => set({ matchScore: score }),
  
  setMatchSummary: (summary: string) => set({ matchSummary: summary }),
  
  setJobUrl: (url: string) => set({ jobUrl: url }),
  
  setJobDescription: (description: string) => set({ jobDescription: description }),
  
  setUserPrompt: (prompt: string) => set({ userPrompt: prompt }),
  
  setPdfPath: (type: 'jobAnalysis' | 'tailoredResume' | 'coverLetter' | 'suggestions', path: string | null) =>
    set((state) => ({
      pdfPaths: {
        ...state.pdfPaths,
        [type]: path,
      },
    })),
  
  setEditedContent: (type: 'jobAnalysis' | 'tailoredResume' | 'coverLetter' | 'suggestions', content: string) =>
    set((state) => ({
      editedContent: {
        ...state.editedContent,
        [type]: content,
      },
    })),
  
  setProcessingStatus: (status: string) => set({ processingStatus: status }),
  
  updateAIStatus: () => {
    const { provider, model, costDisplay } = get();
    const statusText = provider === 'Ollama (Local)' ? '✅ Ready' : (get().apiKey ? '✅ Ready' : '⚠️ Setup needed');
    const modelText = model || 'Default';
    set({ aiStatus: `Current AI: ${provider} • ${modelText} • ${statusText} • ${costDisplay}` });
  },

  clearResults: () =>
    set({
      jobAnalysis: null,
      tailoredResume: null,
      coverLetter: null,
      improvementSuggestions: null,
      matchScore: 0,
      matchSummary: '',
      pdfPaths: {
        jobAnalysis: null,
        tailoredResume: null,
        coverLetter: null,
        suggestions: null,
      },
      editedContent: {
        jobAnalysis: null,
        tailoredResume: null,
        coverLetter: null,
        suggestions: null,
      },
      processingStatus: '',
    }),

  clearFormInputs: () =>
    set({
      jobDescription: '',
      userPrompt: '',
      jobUrl: '',
    }),

  clearError: () => set({ error: null }),
}));

