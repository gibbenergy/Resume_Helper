/**
 * Test Suite: Resume Store Tests
 *
 * Tests for the Zustand resume store state management.
 * These tests verify:
 * - Initial state
 * - Personal info updates
 * - Education CRUD operations
 * - Experience CRUD operations
 * - Skills CRUD operations
 * - Projects CRUD operations
 * - Certifications CRUD operations
 * - Reset functionality
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { useResumeStore } from '@/stores/resumeStore';

// Reset store before each test
beforeEach(() => {
  useResumeStore.getState().resetResume();
});

// ============ Initial State Tests ============
describe('Resume Store: Initial State', () => {
  it('should have empty initial state', () => {
    const state = useResumeStore.getState();
    expect(state.resumeData.personal_info).toEqual({});
    expect(state.resumeData.education).toEqual([]);
    expect(state.resumeData.experience).toEqual([]);
    expect(state.resumeData.skills).toEqual([]);
    expect(state.resumeData.projects).toEqual([]);
    expect(state.resumeData.certifications).toEqual([]);
    expect(state.resumeData.others).toEqual({});
  });

  it('should have all required actions', () => {
    const state = useResumeStore.getState();
    expect(typeof state.updatePersonalInfo).toBe('function');
    expect(typeof state.addEducation).toBe('function');
    expect(typeof state.addExperience).toBe('function');
    expect(typeof state.addSkill).toBe('function');
    expect(typeof state.addProject).toBe('function');
    expect(typeof state.addCertification).toBe('function');
    expect(typeof state.resetResume).toBe('function');
  });
});

// ============ Personal Info Tests ============
describe('Resume Store: Personal Info', () => {
  it('should update personal info', () => {
    const { updatePersonalInfo } = useResumeStore.getState();

    updatePersonalInfo({ full_name: 'John Doe', email: 'john@example.com' });

    const state = useResumeStore.getState();
    expect(state.resumeData.personal_info.full_name).toBe('John Doe');
    expect(state.resumeData.personal_info.email).toBe('john@example.com');
  });

  it('should merge personal info updates', () => {
    const { updatePersonalInfo } = useResumeStore.getState();

    updatePersonalInfo({ full_name: 'John Doe' });
    updatePersonalInfo({ email: 'john@example.com' });

    const state = useResumeStore.getState();
    expect(state.resumeData.personal_info.full_name).toBe('John Doe');
    expect(state.resumeData.personal_info.email).toBe('john@example.com');
  });

  it('should handle all personal info fields', () => {
    const { updatePersonalInfo } = useResumeStore.getState();

    updatePersonalInfo({
      full_name: 'Jane Smith',
      email: 'jane@example.com',
      phone: '+1-555-123-4567',
      location: 'San Francisco, CA',
      linkedin_url: 'https://linkedin.com/in/janesmith',
      github_url: 'https://github.com/janesmith',
      portfolio_url: 'https://janesmith.dev',
      summary: 'Experienced software engineer'
    });

    const state = useResumeStore.getState();
    expect(state.resumeData.personal_info.phone).toBe('+1-555-123-4567');
    expect(state.resumeData.personal_info.linkedin_url).toBe('https://linkedin.com/in/janesmith');
  });
});

// ============ Education Tests ============
describe('Resume Store: Education', () => {
  it('should add education entry', () => {
    const { addEducation } = useResumeStore.getState();

    addEducation({
      institution: 'MIT',
      degree: 'B.S.',
      field_of_study: 'Computer Science',
      gpa: '3.9',
      start_date: '2015',
      end_date: '2019'
    });

    const state = useResumeStore.getState();
    expect(state.resumeData.education).toHaveLength(1);
    expect(state.resumeData.education[0].institution).toBe('MIT');
  });

  it('should update education entry', () => {
    const { addEducation, updateEducation } = useResumeStore.getState();

    addEducation({ institution: 'MIT', degree: 'B.S.' });
    updateEducation(0, { degree: 'M.S.' });

    const state = useResumeStore.getState();
    expect(state.resumeData.education[0].degree).toBe('M.S.');
    expect(state.resumeData.education[0].institution).toBe('MIT');
  });

  it('should remove education entry', () => {
    const { addEducation, removeEducation } = useResumeStore.getState();

    addEducation({ institution: 'MIT', degree: 'B.S.' });
    addEducation({ institution: 'Stanford', degree: 'M.S.' });
    removeEducation(0);

    const state = useResumeStore.getState();
    expect(state.resumeData.education).toHaveLength(1);
    expect(state.resumeData.education[0].institution).toBe('Stanford');
  });

  it('should clear all education entries', () => {
    const { addEducation, clearEducation } = useResumeStore.getState();

    addEducation({ institution: 'MIT', degree: 'B.S.' });
    addEducation({ institution: 'Stanford', degree: 'M.S.' });
    clearEducation();

    const state = useResumeStore.getState();
    expect(state.resumeData.education).toHaveLength(0);
  });
});

// ============ Experience Tests ============
describe('Resume Store: Experience', () => {
  it('should add experience entry', () => {
    const { addExperience } = useResumeStore.getState();

    addExperience({
      company: 'Google',
      position: 'Software Engineer',
      location: 'Mountain View, CA',
      start_date: '2019',
      end_date: 'Present'
    });

    const state = useResumeStore.getState();
    expect(state.resumeData.experience).toHaveLength(1);
    expect(state.resumeData.experience[0].company).toBe('Google');
  });

  it('should update experience entry', () => {
    const { addExperience, updateExperience } = useResumeStore.getState();

    addExperience({ company: 'Google', position: 'Junior Engineer' });
    updateExperience(0, { position: 'Senior Engineer' });

    const state = useResumeStore.getState();
    expect(state.resumeData.experience[0].position).toBe('Senior Engineer');
  });

  it('should remove experience entry', () => {
    const { addExperience, removeExperience } = useResumeStore.getState();

    addExperience({ company: 'Google', position: 'Engineer' });
    addExperience({ company: 'Meta', position: 'Senior Engineer' });
    removeExperience(0);

    const state = useResumeStore.getState();
    expect(state.resumeData.experience).toHaveLength(1);
    expect(state.resumeData.experience[0].company).toBe('Meta');
  });
});

// ============ Skills Tests ============
describe('Resume Store: Skills', () => {
  it('should add skill entry', () => {
    const { addSkill } = useResumeStore.getState();

    addSkill({
      category: 'Programming',
      name: 'Python',
      proficiency: 'Expert'
    });

    const state = useResumeStore.getState();
    expect(state.resumeData.skills).toHaveLength(1);
    expect(state.resumeData.skills[0].name).toBe('Python');
  });

  it('should add multiple skills', () => {
    const { addSkill } = useResumeStore.getState();

    addSkill({ category: 'Programming', name: 'Python' });
    addSkill({ category: 'Programming', name: 'JavaScript' });
    addSkill({ category: 'Tools', name: 'Git' });

    const state = useResumeStore.getState();
    expect(state.resumeData.skills).toHaveLength(3);
  });
});

// ============ Projects Tests ============
describe('Resume Store: Projects', () => {
  it('should add project entry', () => {
    const { addProject } = useResumeStore.getState();

    addProject({
      name: 'Resume Helper',
      description: 'AI-powered resume builder',
      technologies: 'Python, FastAPI, React',
      url: 'https://github.com/user/resume-helper'
    });

    const state = useResumeStore.getState();
    expect(state.resumeData.projects).toHaveLength(1);
    expect(state.resumeData.projects[0].name).toBe('Resume Helper');
  });
});

// ============ Certifications Tests ============
describe('Resume Store: Certifications', () => {
  it('should add certification entry', () => {
    const { addCertification } = useResumeStore.getState();

    addCertification({
      name: 'AWS Solutions Architect',
      issuer: 'Amazon',
      date_obtained: '2023',
      credential_id: 'ABC123'
    });

    const state = useResumeStore.getState();
    expect(state.resumeData.certifications).toHaveLength(1);
    expect(state.resumeData.certifications[0].issuer).toBe('Amazon');
  });
});

// ============ Set Resume Data Tests ============
describe('Resume Store: Set Resume Data', () => {
  it('should set complete resume data', () => {
    const { setResumeData } = useResumeStore.getState();

    setResumeData({
      personal_info: { full_name: 'Test User' },
      education: [{ institution: 'MIT', degree: 'B.S.' }],
      experience: [{ company: 'Google', position: 'Engineer' }],
      skills: [{ name: 'Python', category: 'Programming' }],
      projects: [{ name: 'Project', description: 'A test project' }],
      certifications: [{ name: 'Cert', issuer: 'Org' }],
      others: { custom: 'data' }
    });

    const state = useResumeStore.getState();
    expect(state.resumeData.personal_info.full_name).toBe('Test User');
    expect(state.resumeData.education).toHaveLength(1);
    expect(state.resumeData.experience).toHaveLength(1);
  });

  it('should handle partial data with defaults', () => {
    const { setResumeData } = useResumeStore.getState();

    setResumeData({
      personal_info: { full_name: 'Partial User' }
    } as any);

    const state = useResumeStore.getState();
    expect(state.resumeData.personal_info.full_name).toBe('Partial User');
    expect(state.resumeData.education).toEqual([]);
  });
});

// ============ Reset Tests ============
describe('Resume Store: Reset', () => {
  it('should reset all data to initial state', () => {
    const { updatePersonalInfo, addEducation, addExperience, resetResume } = useResumeStore.getState();

    // Add some data
    updatePersonalInfo({ full_name: 'Test User' });
    addEducation({ institution: 'MIT', degree: 'B.S.' });
    addExperience({ company: 'Google', position: 'Engineer' });

    // Reset
    resetResume();

    const state = useResumeStore.getState();
    expect(state.resumeData.personal_info).toEqual({});
    expect(state.resumeData.education).toEqual([]);
    expect(state.resumeData.experience).toEqual([]);
  });
});
