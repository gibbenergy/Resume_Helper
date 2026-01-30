import { create } from 'zustand';
import type {
  ResumeData,
  PersonalInfo,
  EducationEntry,
  ExperienceEntry,
  SkillEntry,
  ProjectEntry,
  CertificationEntry,
} from '@/lib/types';

interface ResumeStore {
  // Resume data
  resumeData: ResumeData;

  // Active profile name (for saving to custom profile names)
  activeProfileName: string | null;

  // Actions
  setActiveProfileName: (name: string | null) => void;
  updatePersonalInfo: (info: Partial<PersonalInfo>) => void;
  addEducation: (education: EducationEntry) => void;
  updateEducation: (index: number, education: Partial<EducationEntry>) => void;
  removeEducation: (index: number) => void;
  clearEducation: () => void;
  moveEducationUp: (index: number) => void;
  moveEducationDown: (index: number) => void;

  addExperience: (experience: ExperienceEntry) => void;
  updateExperience: (index: number, experience: Partial<ExperienceEntry>) => void;
  removeExperience: (index: number) => void;
  clearExperience: () => void;
  moveExperienceUp: (index: number) => void;
  moveExperienceDown: (index: number) => void;

  addSkill: (skill: SkillEntry) => void;
  updateSkill: (index: number, skill: Partial<SkillEntry>) => void;
  removeSkill: (index: number) => void;
  clearSkills: () => void;
  moveSkillUp: (index: number) => void;
  moveSkillDown: (index: number) => void;

  addProject: (project: ProjectEntry) => void;
  updateProject: (index: number, project: Partial<ProjectEntry>) => void;
  removeProject: (index: number) => void;
  clearProjects: () => void;
  moveProjectUp: (index: number) => void;
  moveProjectDown: (index: number) => void;

  addCertification: (certification: CertificationEntry) => void;
  updateCertification: (index: number, certification: Partial<CertificationEntry>) => void;
  removeCertification: (index: number) => void;
  clearCertifications: () => void;
  moveCertificationUp: (index: number) => void;
  moveCertificationDown: (index: number) => void;
  
  updateOthers: (others: Record<string, any>) => void;
  moveOthersItemUp: (sectionName: string, index: number) => void;
  moveOthersItemDown: (sectionName: string, index: number) => void;

  setResumeData: (data: ResumeData) => void;
  resetResume: () => void;
}

const initialResumeData: ResumeData = {
  personal_info: {},
  education: [],
  experience: [],
  skills: [],
  projects: [],
  certifications: [],
  others: {},
};

export const useResumeStore = create<ResumeStore>((set) => ({
  resumeData: initialResumeData,
  activeProfileName: null,

  setActiveProfileName: (name) => set({ activeProfileName: name }),

  updatePersonalInfo: (info) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        personal_info: { ...state.resumeData.personal_info, ...info },
      },
    })),

  addEducation: (education) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        education: [...state.resumeData.education, education],
      },
    })),

  updateEducation: (index, education) =>
    set((state) => {
      const updated = [...state.resumeData.education];
      updated[index] = { ...updated[index], ...education };
      return {
        resumeData: {
          ...state.resumeData,
          education: updated,
        },
      };
    }),

  removeEducation: (index) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        education: state.resumeData.education.filter((_, i) => i !== index),
      },
    })),

  clearEducation: () =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        education: [],
      },
    })),

  moveEducationUp: (index) =>
    set((state) => {
      if (index <= 0) return state;
      const updated = [...state.resumeData.education];
      [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
      return { resumeData: { ...state.resumeData, education: updated } };
    }),

  moveEducationDown: (index) =>
    set((state) => {
      if (index >= state.resumeData.education.length - 1) return state;
      const updated = [...state.resumeData.education];
      [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
      return { resumeData: { ...state.resumeData, education: updated } };
    }),

  addExperience: (experience) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        experience: [...state.resumeData.experience, experience],
      },
    })),

  updateExperience: (index, experience) =>
    set((state) => {
      const updated = [...state.resumeData.experience];
      updated[index] = { ...updated[index], ...experience };
      return {
        resumeData: {
          ...state.resumeData,
          experience: updated,
        },
      };
    }),

  removeExperience: (index) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        experience: state.resumeData.experience.filter((_, i) => i !== index),
      },
    })),

  clearExperience: () =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        experience: [],
      },
    })),

  moveExperienceUp: (index) =>
    set((state) => {
      if (index <= 0) return state;
      const updated = [...state.resumeData.experience];
      [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
      return { resumeData: { ...state.resumeData, experience: updated } };
    }),

  moveExperienceDown: (index) =>
    set((state) => {
      if (index >= state.resumeData.experience.length - 1) return state;
      const updated = [...state.resumeData.experience];
      [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
      return { resumeData: { ...state.resumeData, experience: updated } };
    }),

  addSkill: (skill) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        skills: [...state.resumeData.skills, skill],
      },
    })),

  updateSkill: (index, skill) =>
    set((state) => {
      const updated = [...state.resumeData.skills];
      updated[index] = { ...updated[index], ...skill };
      return {
        resumeData: {
          ...state.resumeData,
          skills: updated,
        },
      };
    }),

  removeSkill: (index) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        skills: state.resumeData.skills.filter((_, i) => i !== index),
      },
    })),

  clearSkills: () =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        skills: [],
      },
    })),

  moveSkillUp: (index) =>
    set((state) => {
      if (index <= 0) return state;
      const updated = [...state.resumeData.skills];
      [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
      return { resumeData: { ...state.resumeData, skills: updated } };
    }),

  moveSkillDown: (index) =>
    set((state) => {
      if (index >= state.resumeData.skills.length - 1) return state;
      const updated = [...state.resumeData.skills];
      [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
      return { resumeData: { ...state.resumeData, skills: updated } };
    }),

  addProject: (project) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        projects: [...state.resumeData.projects, project],
      },
    })),

  updateProject: (index, project) =>
    set((state) => {
      const updated = [...state.resumeData.projects];
      updated[index] = { ...updated[index], ...project };
      return {
        resumeData: {
          ...state.resumeData,
          projects: updated,
        },
      };
    }),

  removeProject: (index) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        projects: state.resumeData.projects.filter((_, i) => i !== index),
      },
    })),

  clearProjects: () =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        projects: [],
      },
    })),

  moveProjectUp: (index) =>
    set((state) => {
      if (index <= 0) return state;
      const updated = [...state.resumeData.projects];
      [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
      return { resumeData: { ...state.resumeData, projects: updated } };
    }),

  moveProjectDown: (index) =>
    set((state) => {
      if (index >= state.resumeData.projects.length - 1) return state;
      const updated = [...state.resumeData.projects];
      [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
      return { resumeData: { ...state.resumeData, projects: updated } };
    }),

  addCertification: (certification) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        certifications: [...state.resumeData.certifications, certification],
      },
    })),

  updateCertification: (index, certification) =>
    set((state) => {
      const updated = [...state.resumeData.certifications];
      updated[index] = { ...updated[index], ...certification };
      return {
        resumeData: {
          ...state.resumeData,
          certifications: updated,
        },
      };
    }),

  removeCertification: (index) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        certifications: state.resumeData.certifications.filter((_, i) => i !== index),
      },
    })),

  clearCertifications: () =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        certifications: [],
      },
    })),

  moveCertificationUp: (index) =>
    set((state) => {
      if (index <= 0) return state;
      const updated = [...state.resumeData.certifications];
      [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
      return { resumeData: { ...state.resumeData, certifications: updated } };
    }),

  moveCertificationDown: (index) =>
    set((state) => {
      if (index >= state.resumeData.certifications.length - 1) return state;
      const updated = [...state.resumeData.certifications];
      [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
      return { resumeData: { ...state.resumeData, certifications: updated } };
    }),

  updateOthers: (others) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        others: { ...state.resumeData.others, ...others },
      },
    })),

  moveOthersItemUp: (sectionName, index) =>
    set((state) => {
      const currentSections = state.resumeData.others || {};
      const sectionItems = currentSections[sectionName];
      if (!Array.isArray(sectionItems) || index <= 0) return state;
      const updated = [...sectionItems];
      [updated[index - 1], updated[index]] = [updated[index], updated[index - 1]];
      return {
        resumeData: {
          ...state.resumeData,
          others: { ...currentSections, [sectionName]: updated },
        },
      };
    }),

  moveOthersItemDown: (sectionName, index) =>
    set((state) => {
      const currentSections = state.resumeData.others || {};
      const sectionItems = currentSections[sectionName];
      if (!Array.isArray(sectionItems) || index >= sectionItems.length - 1) return state;
      const updated = [...sectionItems];
      [updated[index], updated[index + 1]] = [updated[index + 1], updated[index]];
      return {
        resumeData: {
          ...state.resumeData,
          others: { ...currentSections, [sectionName]: updated },
        },
      };
    }),

  setResumeData: (data) => {
    set({
      resumeData: {
        personal_info: data.personal_info || {},
        education: Array.isArray(data.education) ? data.education : [],
        experience: Array.isArray(data.experience) ? data.experience : [],
        skills: Array.isArray(data.skills) ? data.skills : [],
        projects: Array.isArray(data.projects) ? data.projects : [],
        certifications: Array.isArray(data.certifications) ? data.certifications : [],
        others: data.others || {},
      },
    });
  },

  resetResume: () =>
    set({
      resumeData: initialResumeData,
      activeProfileName: null,
    }),
}));

 
