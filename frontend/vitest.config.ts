import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    fs: {
      // Allow serving files from the tests directory
      allow: ['..'],
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test-setup.ts'],
    include: ['../tests/frontend/**/*.{test,spec}.{js,ts,tsx}'],
    reporters: ['dot', 'json'],
    outputFile: { json: '../tests/frontend/test-results.json' },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // Resolve test dependencies from frontend/node_modules
      '@testing-library/react': path.resolve(__dirname, 'node_modules/@testing-library/react'),
      '@testing-library/jest-dom': path.resolve(__dirname, 'node_modules/@testing-library/jest-dom'),
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
      'zustand': path.resolve(__dirname, 'node_modules/zustand'),
      'axios': path.resolve(__dirname, 'node_modules/axios'),
      'zod': path.resolve(__dirname, 'node_modules/zod'),
      'react-hook-form': path.resolve(__dirname, 'node_modules/react-hook-form'),
      'react-router-dom': path.resolve(__dirname, 'node_modules/react-router-dom'),
    },
  },
});
