/**
 * Vitest test setup file.
 * Configure global test utilities and mocks.
 */
import '@testing-library/jest-dom';

// Suppress console.error for known React act() warnings from Radix UI components
// These warnings come from internal async state updates in third-party components
const originalError = console.error;
console.error = (...args: unknown[]) => {
  const message = args[0];
  if (
    typeof message === 'string' &&
    (message.includes('Warning: An update to') ||
      message.includes('inside a test was not wrapped in act') ||
      message.includes('When testing, code that causes React state updates'))
  ) {
    return; // Suppress known Radix UI warnings
  }
  originalError.apply(console, args);
};

// Mock window.matchMedia for components that use media queries
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock ResizeObserver
(globalThis as typeof globalThis & { ResizeObserver: typeof ResizeObserver }).ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
