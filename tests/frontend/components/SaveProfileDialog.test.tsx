/**
 * Test Suite: SaveProfileDialog Component Tests
 *
 * Tests for the SaveProfileDialog component that allows users to save
 * resume profiles with custom names.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { SaveProfileDialog } from '@/components/resume/SaveProfileDialog';

describe('SaveProfileDialog', () => {
  const mockOnSave = vi.fn();
  const mockOnOpenChange = vi.fn();

  const defaultProps = {
    open: true,
    onOpenChange: mockOnOpenChange,
    defaultName: 'John Doe',
    existingProfiles: [],
    onSave: mockOnSave,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render dialog when open', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    expect(screen.getByText('Save Profile')).toBeInTheDocument();
    expect(screen.getByLabelText(/profile name/i)).toBeInTheDocument();
  });

  it('should pre-fill input with defaultName', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const input = screen.getByLabelText(/profile name/i);
    expect(input).toHaveValue('John Doe');
  });

  it('should update input value when typing', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const input = screen.getByLabelText(/profile name/i);
    fireEvent.change(input, { target: { value: 'John Doe - Software Engineer' } });

    expect(input).toHaveValue('John Doe - Software Engineer');
  });

  it('should call onSave with profile name when Save is clicked', async () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const input = screen.getByLabelText(/profile name/i);
    fireEvent.change(input, { target: { value: 'Custom Profile Name' } });

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    expect(mockOnSave).toHaveBeenCalledWith('Custom Profile Name');
  });

  it('should call onOpenChange(false) when Cancel is clicked', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnOpenChange).toHaveBeenCalledWith(false);
  });

  it('should show warning when profile name matches existing profile', () => {
    const propsWithExisting = {
      ...defaultProps,
      existingProfiles: [
        { id: '1', name: 'John Doe' },
        { id: '2', name: 'Jane Smith' },
      ],
    };

    render(<SaveProfileDialog {...propsWithExisting} />);

    // Warning should be visible because defaultName matches existing profile
    expect(screen.getByText(/profile with this name already exists/i)).toBeInTheDocument();
  });

  it('should show warning when typing name that matches existing profile (case-insensitive)', () => {
    const propsWithExisting = {
      ...defaultProps,
      defaultName: 'New Profile',
      existingProfiles: [
        { id: '1', name: 'John Doe' },
      ],
    };

    render(<SaveProfileDialog {...propsWithExisting} />);

    // Initially no warning
    expect(screen.queryByText(/profile with this name already exists/i)).not.toBeInTheDocument();

    // Type a name that matches (case-insensitive)
    const input = screen.getByLabelText(/profile name/i);
    fireEvent.change(input, { target: { value: 'john doe' } });

    // Warning should appear
    expect(screen.getByText(/profile with this name already exists/i)).toBeInTheDocument();
  });

  it('should disable Save button when input is empty', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const input = screen.getByLabelText(/profile name/i);
    fireEvent.change(input, { target: { value: '' } });

    const saveButton = screen.getByRole('button', { name: /save/i });
    expect(saveButton).toBeDisabled();
  });

  it('should disable Save button when input has only whitespace', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const input = screen.getByLabelText(/profile name/i);
    fireEvent.change(input, { target: { value: '   ' } });

    const saveButton = screen.getByRole('button', { name: /save/i });
    expect(saveButton).toBeDisabled();
  });

  it('should trim whitespace when saving', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const input = screen.getByLabelText(/profile name/i);
    fireEvent.change(input, { target: { value: '  Trimmed Name  ' } });

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    expect(mockOnSave).toHaveBeenCalledWith('Trimmed Name');
  });

  it('should save on Enter key press', () => {
    render(<SaveProfileDialog {...defaultProps} />);

    const input = screen.getByLabelText(/profile name/i);
    fireEvent.change(input, { target: { value: 'Enter Save Test' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(mockOnSave).toHaveBeenCalledWith('Enter Save Test');
  });
});
