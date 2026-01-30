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

// ============ Reorder Tests ============
describe('Resume Store: Education Reorder', () => {
  it('should move education entry up', () => {
    const { addEducation, moveEducationUp } = useResumeStore.getState();

    addEducation({ institution: 'MIT', degree: 'B.S.' });
    addEducation({ institution: 'Stanford', degree: 'M.S.' });
    addEducation({ institution: 'Harvard', degree: 'Ph.D.' });

    moveEducationUp(1); // Move Stanford up

    const state = useResumeStore.getState();
    expect(state.resumeData.education[0].institution).toBe('Stanford');
    expect(state.resumeData.education[1].institution).toBe('MIT');
    expect(state.resumeData.education[2].institution).toBe('Harvard');
  });

  it('should move education entry down', () => {
    const { addEducation, moveEducationDown } = useResumeStore.getState();

    addEducation({ institution: 'MIT', degree: 'B.S.' });
    addEducation({ institution: 'Stanford', degree: 'M.S.' });
    addEducation({ institution: 'Harvard', degree: 'Ph.D.' });

    moveEducationDown(0); // Move MIT down

    const state = useResumeStore.getState();
    expect(state.resumeData.education[0].institution).toBe('Stanford');
    expect(state.resumeData.education[1].institution).toBe('MIT');
    expect(state.resumeData.education[2].institution).toBe('Harvard');
  });

  it('should not move first education entry up', () => {
    const { addEducation, moveEducationUp } = useResumeStore.getState();

    addEducation({ institution: 'MIT', degree: 'B.S.' });
    addEducation({ institution: 'Stanford', degree: 'M.S.' });

    moveEducationUp(0); // Try to move first item up

    const state = useResumeStore.getState();
    expect(state.resumeData.education[0].institution).toBe('MIT');
    expect(state.resumeData.education[1].institution).toBe('Stanford');
  });

  it('should not move last education entry down', () => {
    const { addEducation, moveEducationDown } = useResumeStore.getState();

    addEducation({ institution: 'MIT', degree: 'B.S.' });
    addEducation({ institution: 'Stanford', degree: 'M.S.' });

    moveEducationDown(1); // Try to move last item down

    const state = useResumeStore.getState();
    expect(state.resumeData.education[0].institution).toBe('MIT');
    expect(state.resumeData.education[1].institution).toBe('Stanford');
  });
});

describe('Resume Store: Experience Reorder', () => {
  it('should move experience entry up', () => {
    const { addExperience, moveExperienceUp } = useResumeStore.getState();

    addExperience({ company: 'Google', position: 'Engineer' });
    addExperience({ company: 'Meta', position: 'Senior Engineer' });
    addExperience({ company: 'Amazon', position: 'Lead Engineer' });

    moveExperienceUp(2); // Move Amazon up

    const state = useResumeStore.getState();
    expect(state.resumeData.experience[1].company).toBe('Amazon');
    expect(state.resumeData.experience[2].company).toBe('Meta');
  });

  it('should move experience entry down', () => {
    const { addExperience, moveExperienceDown } = useResumeStore.getState();

    addExperience({ company: 'Google', position: 'Engineer' });
    addExperience({ company: 'Meta', position: 'Senior Engineer' });

    moveExperienceDown(0); // Move Google down

    const state = useResumeStore.getState();
    expect(state.resumeData.experience[0].company).toBe('Meta');
    expect(state.resumeData.experience[1].company).toBe('Google');
  });
});

describe('Resume Store: Skills Reorder', () => {
  it('should move skill entry up', () => {
    const { addSkill, moveSkillUp } = useResumeStore.getState();

    addSkill({ category: 'Programming', name: 'Python' });
    addSkill({ category: 'Programming', name: 'JavaScript' });
    addSkill({ category: 'Tools', name: 'Git' });

    moveSkillUp(1); // Move JavaScript up

    const state = useResumeStore.getState();
    expect(state.resumeData.skills[0].name).toBe('JavaScript');
    expect(state.resumeData.skills[1].name).toBe('Python');
  });

  it('should move skill entry down', () => {
    const { addSkill, moveSkillDown } = useResumeStore.getState();

    addSkill({ category: 'Programming', name: 'Python' });
    addSkill({ category: 'Programming', name: 'JavaScript' });

    moveSkillDown(0); // Move Python down

    const state = useResumeStore.getState();
    expect(state.resumeData.skills[0].name).toBe('JavaScript');
    expect(state.resumeData.skills[1].name).toBe('Python');
  });
});

describe('Resume Store: Projects Reorder', () => {
  it('should move project entry up', () => {
    const { addProject, moveProjectUp } = useResumeStore.getState();

    addProject({ name: 'Project A', description: 'First' });
    addProject({ name: 'Project B', description: 'Second' });
    addProject({ name: 'Project C', description: 'Third' });

    moveProjectUp(2); // Move Project C up

    const state = useResumeStore.getState();
    expect(state.resumeData.projects[1].name).toBe('Project C');
    expect(state.resumeData.projects[2].name).toBe('Project B');
  });

  it('should move project entry down', () => {
    const { addProject, moveProjectDown } = useResumeStore.getState();

    addProject({ name: 'Project A', description: 'First' });
    addProject({ name: 'Project B', description: 'Second' });

    moveProjectDown(0); // Move Project A down

    const state = useResumeStore.getState();
    expect(state.resumeData.projects[0].name).toBe('Project B');
    expect(state.resumeData.projects[1].name).toBe('Project A');
  });
});

describe('Resume Store: Certifications Reorder', () => {
  it('should move certification entry up', () => {
    const { addCertification, moveCertificationUp } = useResumeStore.getState();

    addCertification({ name: 'AWS', issuer: 'Amazon' });
    addCertification({ name: 'GCP', issuer: 'Google' });
    addCertification({ name: 'Azure', issuer: 'Microsoft' });

    moveCertificationUp(1); // Move GCP up

    const state = useResumeStore.getState();
    expect(state.resumeData.certifications[0].name).toBe('GCP');
    expect(state.resumeData.certifications[1].name).toBe('AWS');
  });

  it('should move certification entry down', () => {
    const { addCertification, moveCertificationDown } = useResumeStore.getState();

    addCertification({ name: 'AWS', issuer: 'Amazon' });
    addCertification({ name: 'GCP', issuer: 'Google' });

    moveCertificationDown(0); // Move AWS down

    const state = useResumeStore.getState();
    expect(state.resumeData.certifications[0].name).toBe('GCP');
    expect(state.resumeData.certifications[1].name).toBe('AWS');
  });
});

describe('Resume Store: Others Reorder', () => {
  it('should move others item up within section', () => {
    const { updateOthers, moveOthersItemUp } = useResumeStore.getState();

    updateOthers({
      'Patents': [
        { title: 'Patent A', organization: 'USPTO' },
        { title: 'Patent B', organization: 'USPTO' },
        { title: 'Patent C', organization: 'USPTO' }
      ]
    });

    moveOthersItemUp('Patents', 1); // Move Patent B up

    const state = useResumeStore.getState();
    expect(state.resumeData.others['Patents'][0].title).toBe('Patent B');
    expect(state.resumeData.others['Patents'][1].title).toBe('Patent A');
    expect(state.resumeData.others['Patents'][2].title).toBe('Patent C');
  });

  it('should move others item down within section', () => {
    const { updateOthers, moveOthersItemDown } = useResumeStore.getState();

    updateOthers({
      'Publications': [
        { title: 'Paper A', organization: 'Journal' },
        { title: 'Paper B', organization: 'Journal' },
        { title: 'Paper C', organization: 'Journal' }
      ]
    });

    moveOthersItemDown('Publications', 0); // Move Paper A down

    const state = useResumeStore.getState();
    expect(state.resumeData.others['Publications'][0].title).toBe('Paper B');
    expect(state.resumeData.others['Publications'][1].title).toBe('Paper A');
    expect(state.resumeData.others['Publications'][2].title).toBe('Paper C');
  });

  it('should not move first others item up', () => {
    const { updateOthers, moveOthersItemUp } = useResumeStore.getState();

    updateOthers({
      'Awards': [
        { title: 'Award A', organization: 'Org' },
        { title: 'Award B', organization: 'Org' }
      ]
    });

    moveOthersItemUp('Awards', 0); // Try to move first item up

    const state = useResumeStore.getState();
    expect(state.resumeData.others['Awards'][0].title).toBe('Award A');
    expect(state.resumeData.others['Awards'][1].title).toBe('Award B');
  });

  it('should not move last others item down', () => {
    const { updateOthers, moveOthersItemDown } = useResumeStore.getState();

    updateOthers({
      'Awards': [
        { title: 'Award A', organization: 'Org' },
        { title: 'Award B', organization: 'Org' }
      ]
    });

    moveOthersItemDown('Awards', 1); // Try to move last item down

    const state = useResumeStore.getState();
    expect(state.resumeData.others['Awards'][0].title).toBe('Award A');
    expect(state.resumeData.others['Awards'][1].title).toBe('Award B');
  });

  it('should handle non-existent section gracefully', () => {
    const { moveOthersItemUp, moveOthersItemDown } = useResumeStore.getState();

    // Should not throw errors
    moveOthersItemUp('NonExistent', 0);
    moveOthersItemDown('NonExistent', 0);

    const state = useResumeStore.getState();
    expect(state.resumeData.others).toEqual({});
  });
});

// ============ Active Profile Name Tests ============
describe('Resume Store: Active Profile Name', () => {
  it('should have null activeProfileName by default', () => {
    const state = useResumeStore.getState();
    expect(state.activeProfileName).toBeNull();
  });

  it('should set activeProfileName using setActiveProfileName', () => {
    useResumeStore.getState().setActiveProfileName('John Doe - Software Engineer');

    const state = useResumeStore.getState();
    expect(state.activeProfileName).toBe('John Doe - Software Engineer');
  });

  it('should clear activeProfileName when set to null', () => {
    // First set a value
    useResumeStore.getState().setActiveProfileName('Test Profile');
    expect(useResumeStore.getState().activeProfileName).toBe('Test Profile');

    // Then clear it
    useResumeStore.getState().setActiveProfileName(null);
    expect(useResumeStore.getState().activeProfileName).toBeNull();
  });

  it('should clear activeProfileName when resetResume is called', () => {
    // Set a profile name
    useResumeStore.getState().setActiveProfileName('My Profile');
    expect(useResumeStore.getState().activeProfileName).toBe('My Profile');

    // Reset the resume
    useResumeStore.getState().resetResume();

    // activeProfileName should be null
    expect(useResumeStore.getState().activeProfileName).toBeNull();
  });

  it('should preserve activeProfileName when updating personal info', () => {
    // Set active profile name
    useResumeStore.getState().setActiveProfileName('Persistent Profile');

    // Update personal info
    useResumeStore.getState().updatePersonalInfo({
      full_name: 'Test User',
      email: 'test@example.com',
    });

    // activeProfileName should still be set
    expect(useResumeStore.getState().activeProfileName).toBe('Persistent Profile');
  });

  it('should preserve activeProfileName when adding education', () => {
    useResumeStore.getState().setActiveProfileName('Education Test');
    useResumeStore.getState().addEducation({ institution: 'MIT', degree: 'B.S.' });

    expect(useResumeStore.getState().activeProfileName).toBe('Education Test');
  });

  it('should allow switching between different profile names', () => {
    // Set first profile
    useResumeStore.getState().setActiveProfileName('John Doe - Process Engineer');
    expect(useResumeStore.getState().activeProfileName).toBe('John Doe - Process Engineer');

    // Change to second profile
    useResumeStore.getState().setActiveProfileName('John Doe - Software Engineer');
    expect(useResumeStore.getState().activeProfileName).toBe('John Doe - Software Engineer');

    // Change to third profile
    useResumeStore.getState().setActiveProfileName('John Doe - Data Scientist');
    expect(useResumeStore.getState().activeProfileName).toBe('John Doe - Data Scientist');
  });
});
