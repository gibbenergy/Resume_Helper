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
  
  // Actions
  updatePersonalInfo: (info: Partial<PersonalInfo>) => void;
  addEducation: (education: EducationEntry) => void;
  updateEducation: (index: number, education: Partial<EducationEntry>) => void;
  removeEducation: (index: number) => void;
  clearEducation: () => void;
  
  addExperience: (experience: ExperienceEntry) => void;
  updateExperience: (index: number, experience: Partial<ExperienceEntry>) => void;
  removeExperience: (index: number) => void;
  clearExperience: () => void;
  
  addSkill: (skill: SkillEntry) => void;
  updateSkill: (index: number, skill: Partial<SkillEntry>) => void;
  removeSkill: (index: number) => void;
  clearSkills: () => void;
  
  addProject: (project: ProjectEntry) => void;
  updateProject: (index: number, project: Partial<ProjectEntry>) => void;
  removeProject: (index: number) => void;
  clearProjects: () => void;
  
  addCertification: (certification: CertificationEntry) => void;
  updateCertification: (index: number, certification: Partial<CertificationEntry>) => void;
  removeCertification: (index: number) => void;
  clearCertifications: () => void;
  
  updateOthers: (others: Record<string, any>) => void;
  
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

  updateOthers: (others) =>
    set((state) => ({
      resumeData: {
        ...state.resumeData,
        others: { ...state.resumeData.others, ...others },
      },
    })),

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
    }),
}));

 
