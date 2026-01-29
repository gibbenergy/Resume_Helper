import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./setup.ts'],
    include: ['./**/*.{test,spec}.{js,ts,tsx}'],
    reporters: ['dot', 'json'],
    outputFile: { json: './test-results.json' },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../frontend/src'),
    },
  },
});
