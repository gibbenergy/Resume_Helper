/**
 * Test Suite: API Client Tests
 *
 * Tests for the API client module.
 * These tests verify:
 * - API object structure
 * - Method definitions
 * - URL construction
 */
import { describe, it, expect, vi } from 'vitest';
import { api } from '@/lib/api';

// ============ API Structure Tests ============
describe('API Client: Structure', () => {
  it('should export api object', () => {
    expect(api).toBeDefined();
    expect(typeof api).toBe('object');
  });

  it('should have AI workflow methods', () => {
    expect(typeof api.testApiKey).toBe('function');
    expect(typeof api.getProviders).toBe('function');
    expect(typeof api.getModels).toBe('function');
    expect(typeof api.getCost).toBe('function');
    expect(typeof api.analyzeJob).toBe('function');
    expect(typeof api.tailorResume).toBe('function');
    expect(typeof api.generateCoverLetter).toBe('function');
    expect(typeof api.getImprovementSuggestions).toBe('function');
  });

  it('should have application tracker methods', () => {
    expect(typeof api.getApplications).toBe('function');
    expect(typeof api.getApplication).toBe('function');
    expect(typeof api.createApplication).toBe('function');
    expect(typeof api.updateApplication).toBe('function');
    expect(typeof api.deleteApplication).toBe('function');
    expect(typeof api.getApplicationSettings).toBe('function');
    expect(typeof api.updateInterviewRound).toBe('function');
    expect(typeof api.uploadDocument).toBe('function');
    expect(typeof api.downloadDocument).toBe('function');
    expect(typeof api.deleteDocument).toBe('function');
  });

  it('should have resume methods', () => {
    expect(typeof api.buildProfile).toBe('function');
    expect(typeof api.loadSoftwareDeveloperExample).toBe('function');
    expect(typeof api.loadProcessEngineerExample).toBe('function');
    expect(typeof api.loadFromJson).toBe('function');
    expect(typeof api.loadFromPDF).toBe('function');
    expect(typeof api.loadFromDOCX).toBe('function');
  });

  it('should have PDF generation methods', () => {
    expect(typeof api.generateResumePDF).toBe('function');
    expect(typeof api.generateResumeDOCX).toBe('function');
    expect(typeof api.generateJson).toBe('function');
    expect(typeof api.generateJobAnalysisPDF).toBe('function');
    expect(typeof api.generateTailoredResumePDF).toBe('function');
    expect(typeof api.generateCoverLetterPDF).toBe('function');
    expect(typeof api.generateSuggestionsPDF).toBe('function');
  });

  it('should have profile management methods', () => {
    expect(typeof api.getProfiles).toBe('function');
    expect(typeof api.getProfile).toBe('function');
    expect(typeof api.saveProfile).toBe('function');
    expect(typeof api.deleteProfile).toBe('function');
  });
});

// ============ URL Helper Tests ============
describe('API Client: URL Helpers', () => {
  it('should have getJobDescriptionPDFUrl helper', () => {
    expect(typeof api.getJobDescriptionPDFUrl).toBe('function');
  });

  it('should construct correct job description PDF URL', () => {
    const url = api.getJobDescriptionPDFUrl('test-app-123');
    expect(url).toContain('/api/pdf/job-description/test-app-123');
  });
});

// ============ Method Signature Tests ============
describe('API Client: Method Signatures', () => {
  it('testApiKey should accept provider, apiKey, and optional model', () => {
    // Just verify the function exists and accepts parameters
    // Actual API call would require mocking
    expect(api.testApiKey.length).toBeGreaterThanOrEqual(2);
  });

  it('analyzeJob should accept job_description, resume_data, and optional model', () => {
    expect(api.analyzeJob.length).toBeGreaterThanOrEqual(2);
  });

  it('tailorResume should accept multiple parameters', () => {
    expect(api.tailorResume.length).toBeGreaterThanOrEqual(2);
  });

  it('generateCoverLetter should accept multiple parameters', () => {
    expect(api.generateCoverLetter.length).toBeGreaterThanOrEqual(2);
  });
});

// ============ Async Method Tests ============
describe('API Client: Async Methods', () => {
  it('all API methods should return promises', () => {
    // Mock fetch to prevent actual API calls
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    });
    globalThis.fetch = mockFetch;

    // Test that methods return promises
    const promise = api.getProviders();
    expect(promise).toBeInstanceOf(Promise);
  });
});
