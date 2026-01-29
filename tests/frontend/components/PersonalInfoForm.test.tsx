/**
 * Test Suite: PersonalInfoForm Component Tests
 *
 * Tests for the PersonalInfoForm component auto-sync behavior.
 * These tests verify:
 * - Form values auto-sync to the store when changed
 * - Changes persist when switching tabs (simulated by unmount/remount)
 * - Prefix dropdown updates store correctly
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { useResumeStore } from '@/stores/resumeStore';

// Mock the API
vi.mock('@/lib/api', () => ({
  api: {
    getProfiles: vi.fn().mockResolvedValue({ success: true, profiles: [] }),
    saveProfile: vi.fn().mockResolvedValue({ success: true }),
    deleteProfile: vi.fn().mockResolvedValue({ success: true }),
    loadSoftwareDeveloperExample: vi.fn().mockResolvedValue({ success: false }),
    loadProcessEngineerExample: vi.fn().mockResolvedValue({ success: false }),
  },
}));

// Mock the toast
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

// Import after mocking
import { PersonalInfoForm } from '@/components/resume/PersonalInfoForm';

describe('PersonalInfoForm: Auto-sync Behavior', () => {
  beforeEach(() => {
    // Reset the store before each test
    useResumeStore.getState().resetResume();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should sync full_name changes to the store', async () => {
    render(<PersonalInfoForm />);

    const fullNameInput = screen.getByLabelText(/full name/i);
    fireEvent.change(fullNameInput, { target: { value: 'John Doe' } });

    // Wait for auto-sync to update the store
    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.full_name).toBe('John Doe');
    });
  });

  it('should sync email changes to the store', async () => {
    render(<PersonalInfoForm />);

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } });

    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.email).toBe('john@example.com');
    });
  });

  it('should sync phone changes to the store', async () => {
    render(<PersonalInfoForm />);

    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(phoneInput, { target: { value: '555-1234' } });

    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.phone).toBe('555-1234');
    });
  });

  it('should sync current_address changes to the store', async () => {
    render(<PersonalInfoForm />);

    const addressInput = screen.getByLabelText(/current address/i);
    fireEvent.change(addressInput, { target: { value: '123 Main St' } });

    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.current_address).toBe('123 Main St');
    });
  });

  it('should sync location changes to the store', async () => {
    render(<PersonalInfoForm />);

    const locationInput = screen.getByLabelText(/^location$/i);
    fireEvent.change(locationInput, { target: { value: 'New York, NY' } });

    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.location).toBe('New York, NY');
    });
  });

  it('should persist changes after unmount and remount (simulating tab switch)', async () => {
    const { unmount } = render(<PersonalInfoForm />);

    // Type a value
    const fullNameInput = screen.getByLabelText(/full name/i);
    fireEvent.change(fullNameInput, { target: { value: 'Jane Smith' } });

    // Wait for sync
    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.full_name).toBe('Jane Smith');
    });

    // Unmount (simulating switching to another tab)
    unmount();

    // Remount (simulating coming back to the tab)
    render(<PersonalInfoForm />);

    // Verify the value persisted
    const newFullNameInput = screen.getByLabelText(/full name/i);
    expect(newFullNameInput).toHaveValue('Jane Smith');
  });

  it('should clear field and persist empty value', async () => {
    // First set an initial value in the store
    useResumeStore.getState().updatePersonalInfo({ current_address: '456 Old St' });

    render(<PersonalInfoForm />);

    // Find and clear the address field
    const addressInput = screen.getByLabelText(/current address/i);
    expect(addressInput).toHaveValue('456 Old St');

    fireEvent.change(addressInput, { target: { value: '' } });

    // Wait for sync
    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.current_address).toBe('');
    });
  });
});

describe('PersonalInfoForm: Name Prefix', () => {
  beforeEach(() => {
    useResumeStore.getState().resetResume();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should display "None" when no prefix is set', () => {
    render(<PersonalInfoForm />);

    // The select trigger should show "None" as placeholder
    const selectTrigger = screen.getByRole('combobox');
    expect(selectTrigger).toHaveTextContent('None');
  });

  it('should display saved prefix value', () => {
    // Set a prefix in the store first
    useResumeStore.getState().updatePersonalInfo({ name_prefix: 'Dr.' });

    render(<PersonalInfoForm />);

    const selectTrigger = screen.getByRole('combobox');
    expect(selectTrigger).toHaveTextContent('Dr.');
  });

  it('should persist prefix after unmount/remount', async () => {
    // Set a prefix in the store
    useResumeStore.getState().updatePersonalInfo({ name_prefix: 'Prof.' });

    const { unmount } = render(<PersonalInfoForm />);

    // Verify initial value
    let selectTrigger = screen.getByRole('combobox');
    expect(selectTrigger).toHaveTextContent('Prof.');

    // Unmount
    unmount();

    // Remount
    render(<PersonalInfoForm />);

    // Verify persisted
    selectTrigger = screen.getByRole('combobox');
    expect(selectTrigger).toHaveTextContent('Prof.');
  });
});

describe('PersonalInfoForm: Multiple Fields', () => {
  beforeEach(() => {
    useResumeStore.getState().resetResume();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should sync multiple field changes to the store', async () => {
    render(<PersonalInfoForm />);

    // Fill in multiple fields
    const fullNameInput = screen.getByLabelText(/full name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const phoneInput = screen.getByLabelText(/phone/i);

    fireEvent.change(fullNameInput, { target: { value: 'Alice Johnson' } });
    fireEvent.change(emailInput, { target: { value: 'alice@test.com' } });
    fireEvent.change(phoneInput, { target: { value: '555-9999' } });

    // Verify all values synced
    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.full_name).toBe('Alice Johnson');
      expect(state.resumeData.personal_info.email).toBe('alice@test.com');
      expect(state.resumeData.personal_info.phone).toBe('555-9999');
    });
  });

  it('should preserve existing store values when updating one field', async () => {
    // Set initial values
    useResumeStore.getState().updatePersonalInfo({
      full_name: 'Existing Name',
      email: 'existing@email.com',
    });

    render(<PersonalInfoForm />);

    // Update only the phone
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(phoneInput, { target: { value: '123-4567' } });

    // Verify the phone updated but other values preserved
    await waitFor(() => {
      const state = useResumeStore.getState();
      expect(state.resumeData.personal_info.full_name).toBe('Existing Name');
      expect(state.resumeData.personal_info.email).toBe('existing@email.com');
      expect(state.resumeData.personal_info.phone).toBe('123-4567');
    });
  });
});
