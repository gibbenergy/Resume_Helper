import { create } from 'zustand';
import type {
  Application,
  ApplicationCreateRequest,
  ApplicationSettings,
  InterviewRound,
} from '@/lib/types';
import { api } from '@/lib/api';

interface ApplicationStore {
  applications: Application[];
  selectedApplication: Application | null;
  loading: boolean;
  error: string | null;
  settings: ApplicationSettings | null;
  selectedRound: string | null;

  // Actions
  fetchApplications: () => Promise<void>;
  fetchApplication: (appId: string) => Promise<void>;
  createApplication: (data: ApplicationCreateRequest) => Promise<Application | null>;
  updateApplication: (appId: string, data: Partial<ApplicationCreateRequest>) => Promise<boolean>;
  deleteApplication: (appId: string) => Promise<boolean>;
  setSelectedApplication: (application: Application | null) => void;
  clearError: () => void;
  fetchSettings: () => Promise<void>;
  updateInterviewRound: (
    appId: string,
    roundName: string,
    roundData: Partial<InterviewRound>
  ) => Promise<boolean>;
  uploadDocument: (appId: string, file: File) => Promise<boolean>;
  downloadDocument: (appId: string, docId: number) => Promise<void>;
  deleteDocument: (appId: string, docId: number) => Promise<boolean>;
  setSelectedRound: (roundName: string | null) => void;
}

export const useApplicationStore = create<ApplicationStore>((set, get) => ({
  applications: [],
  selectedApplication: null,
  loading: false,
  error: null,
  settings: null,
  selectedRound: null,

  fetchApplications: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.getApplications();
      if (response.success && response.data) {
        set({ applications: response.data, loading: false });
      } else {
        set({ error: response.error || 'Failed to fetch applications', loading: false });
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch applications',
        loading: false,
      });
    }
  },

  fetchApplication: async (appId: string) => {
    set({ loading: true, error: null });
    try {
      const response = await api.getApplication(appId);
      if (response.success && response.data) {
        set({ selectedApplication: response.data, loading: false });
      } else {
        set({ error: response.error || 'Failed to fetch application', loading: false });
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch application',
        loading: false,
      });
    }
  },

  createApplication: async (data: ApplicationCreateRequest) => {
    set({ loading: true, error: null });
    try {
      const response = await api.createApplication(data);
      if (response.success && response.data) {
        const newApp = response.data;
        set((state) => ({
          applications: [newApp, ...state.applications],
          loading: false,
        }));
        return newApp;
      } else {
        set({ error: response.error || 'Failed to create application', loading: false });
        return null;
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create application',
        loading: false,
      });
      return null;
    }
  },

  updateApplication: async (appId: string, data: Partial<ApplicationCreateRequest>) => {
    set({ loading: true, error: null });
    try {
      const response = await api.updateApplication(appId, data);
      if (response.success && response.data) {
        const updated = response.data;
        set((state) => ({
          applications: state.applications.map((app) =>
            String(app.id) === appId ? updated : app
          ),
          selectedApplication:
            String(state.selectedApplication?.id) === appId ? updated : state.selectedApplication,
          loading: false,
        }));
        return true;
      } else {
        set({ error: response.error || 'Failed to update application', loading: false });
        return false;
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update application',
        loading: false,
      });
      return false;
    }
  },

  deleteApplication: async (appId: string) => {
    set({ loading: true, error: null });
    try {
      const response = await api.deleteApplication(appId);
      if (response.success) {
        set((state) => ({
          applications: state.applications.filter((app) => String(app.id) !== appId),
          selectedApplication:
            String(state.selectedApplication?.id) === appId ? null : state.selectedApplication,
          loading: false,
        }));
        return true;
      } else {
        set({ error: response.error || 'Failed to delete application', loading: false });
        return false;
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete application',
        loading: false,
      });
      return false;
    }
  },

  setSelectedApplication: (application) => set({ selectedApplication: application }),

  clearError: () => set({ error: null }),

  fetchSettings: async () => {
    try {
      const response = await api.getApplicationSettings();
      if (response.success && response.data) {
        set({ settings: response.data });
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  },

  updateInterviewRound: async (appId, roundName, roundData) => {
    set({ loading: true, error: null });
    try {
      const response = await api.updateInterviewRound(appId, roundName, roundData);
      if (response.success) {
        // Refresh the application to get updated interview pipeline
        await get().fetchApplication(appId);
        set({ loading: false });
        return true;
      } else {
        set({ error: response.error || 'Failed to update interview round', loading: false });
        return false;
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update interview round',
        loading: false,
      });
      return false;
    }
  },

  uploadDocument: async (appId, file) => {
    set({ loading: true, error: null });
    try {
      const response = await api.uploadDocument(appId, file);
      if (response.success) {
        // Refresh the application to get updated documents
        await get().fetchApplication(appId);
        set({ loading: false });
        return true;
      } else {
        set({ error: response.error || 'Failed to upload document', loading: false });
        return false;
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to upload document',
        loading: false,
      });
      return false;
    }
  },

  downloadDocument: async (appId, docId) => {
    try {
      const selectedApp = get().selectedApplication;
      const doc = selectedApp?.documents?.find(d => d.id === docId);
      const blob = await api.downloadDocument(appId, docId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      // Use actual document name instead of generic name
      const filename = doc?.name || `document_${docId}`;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to download document',
      });
    }
  },

  deleteDocument: async (appId, docId) => {
    set({ loading: true, error: null });
    try {
      const response = await api.deleteDocument(appId, docId);
      if (response.success) {
        // Refresh the application to get updated documents
        await get().fetchApplication(appId);
        set({ loading: false });
        return true;
      } else {
        set({ error: response.error || 'Failed to delete document', loading: false });
        return false;
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete document',
        loading: false,
      });
      return false;
    }
  },

  setSelectedRound: (roundName) => set({ selectedRound: roundName }),
}));

