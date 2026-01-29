/**
 * Test Suite: Diagnostic Tests
 *
 * Diagnostic tests to verify the frontend application is in a working state.
 * These tests verify:
 * - Core modules can be imported
 * - Test environment is configured
 * - ES6/TypeScript features work
 * - React ecosystem is functional
 */
import { describe, it, expect } from 'vitest';

// ============ Core Module Import Tests ============
describe('Diagnostic: Core Module Imports', () => {
  it('should import React successfully', async () => {
    const React = await import('react');
    expect(React).toBeDefined();
    expect(React.useState).toBeDefined();
    expect(React.useEffect).toBeDefined();
    expect(React.useCallback).toBeDefined();
    expect(React.useMemo).toBeDefined();
  });

  it('should import React DOM successfully', async () => {
    const ReactDOM = await import('react-dom/client');
    expect(ReactDOM).toBeDefined();
    expect(ReactDOM.createRoot).toBeDefined();
  });

  it('should import Zustand successfully', async () => {
    const Zustand = await import('zustand');
    expect(Zustand).toBeDefined();
    expect(Zustand.create).toBeDefined();
  });

  it('should import React Router successfully', async () => {
    const ReactRouter = await import('react-router-dom');
    expect(ReactRouter).toBeDefined();
    expect(ReactRouter.BrowserRouter).toBeDefined();
  });

  it('should import Axios successfully', async () => {
    const Axios = await import('axios');
    expect(Axios).toBeDefined();
    expect(Axios.default).toBeDefined();
  });

  it('should import React Hook Form successfully', async () => {
    const RHF = await import('react-hook-form');
    expect(RHF).toBeDefined();
    expect(RHF.useForm).toBeDefined();
  });

  it('should import Zod successfully', async () => {
    const Zod = await import('zod');
    expect(Zod).toBeDefined();
    expect(Zod.z).toBeDefined();
  });
});

// ============ Project Module Import Tests ============
describe('Diagnostic: Project Module Imports', () => {
  it('should import API module successfully', async () => {
    const { api } = await import('../lib/api');
    expect(api).toBeDefined();
    expect(typeof api.getProviders).toBe('function');
  });

  it('should import resume store successfully', async () => {
    const { useResumeStore } = await import('../stores/resumeStore');
    expect(useResumeStore).toBeDefined();
    expect(typeof useResumeStore).toBe('function');
  });

  it('should import AI store successfully', async () => {
    const { useAIStore } = await import('../stores/aiStore');
    expect(useAIStore).toBeDefined();
    expect(typeof useAIStore).toBe('function');
  });

  it('should import application store successfully', async () => {
    const { useApplicationStore } = await import('../stores/applicationStore');
    expect(useApplicationStore).toBeDefined();
    expect(typeof useApplicationStore).toBe('function');
  });

  it('should import utils module successfully', async () => {
    const Utils = await import('../lib/utils');
    expect(Utils).toBeDefined();
    expect(Utils.cn).toBeDefined();
  });

  it('should import types successfully', async () => {
    const Types = await import('../lib/types');
    expect(Types).toBeDefined();
  });
});

// ============ Test Environment Tests ============
describe('Diagnostic: Test Environment', () => {
  it('should have jsdom environment configured', () => {
    expect(typeof window).toBe('object');
    expect(typeof document).toBe('object');
    expect(typeof navigator).toBe('object');
  });

  it('should have window.location', () => {
    expect(window.location).toBeDefined();
    expect(typeof window.location.href).toBe('string');
  });

  it('should have document methods', () => {
    expect(typeof document.createElement).toBe('function');
    expect(typeof document.querySelector).toBe('function');
    expect(typeof document.getElementById).toBe('function');
  });

  it('should have matchMedia mocked', () => {
    expect(window.matchMedia).toBeDefined();
    const result = window.matchMedia('(min-width: 768px)');
    expect(result.matches).toBe(false);
    expect(typeof result.addListener).toBe('function');
  });

  it('should have ResizeObserver mocked', () => {
    expect(global.ResizeObserver).toBeDefined();
    const observer = new ResizeObserver(() => {});
    expect(observer.observe).toBeDefined();
    expect(observer.disconnect).toBeDefined();
  });

  it('should have localStorage available', () => {
    expect(window.localStorage).toBeDefined();
    expect(typeof window.localStorage.getItem).toBe('function');
    expect(typeof window.localStorage.setItem).toBe('function');
  });

  it('should have fetch available', () => {
    expect(typeof fetch).toBe('function');
  });
});

// ============ JavaScript/TypeScript Feature Tests ============
describe('Diagnostic: JS/TS Features', () => {
  it('should support async/await', async () => {
    const asyncFn = async () => 'test';
    const result = await asyncFn();
    expect(result).toBe('test');
  });

  it('should support Promises', async () => {
    const promise = new Promise<string>((resolve) => {
      setTimeout(() => resolve('resolved'), 10);
    });
    const result = await promise;
    expect(result).toBe('resolved');
  });

  it('should support ES6 destructuring', () => {
    const obj = { a: 1, b: 2, c: 3 };
    const { a, b } = obj;
    expect(a).toBe(1);
    expect(b).toBe(2);
  });

  it('should support spread operator', () => {
    const arr = [1, 2, 3];
    const doubled = arr.map(x => x * 2);
    expect(doubled).toEqual([2, 4, 6]);

    const obj = { a: 1, b: 2 };
    const spread = { ...obj, c: 3 };
    expect(spread).toEqual({ a: 1, b: 2, c: 3 });
  });

  it('should support optional chaining', () => {
    const obj: { a?: { b?: { c?: number } } } = {};
    expect(obj?.a?.b?.c).toBeUndefined();

    obj.a = { b: { c: 42 } };
    expect(obj?.a?.b?.c).toBe(42);
  });

  it('should support nullish coalescing', () => {
    const value: string | null = null;
    expect(value ?? 'default').toBe('default');

    const value2 = 'actual';
    expect(value2 ?? 'default').toBe('actual');
  });

  it('should support template literals', () => {
    const name = 'World';
    expect(`Hello, ${name}!`).toBe('Hello, World!');
  });

  it('should support Map and Set', () => {
    const map = new Map<string, number>();
    map.set('key', 42);
    expect(map.get('key')).toBe(42);

    const set = new Set<number>();
    set.add(1);
    set.add(2);
    expect(set.has(1)).toBe(true);
    expect(set.size).toBe(2);
  });
});
