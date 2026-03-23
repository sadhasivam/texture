import { defineConfig } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';
import { config } from 'dotenv';

// Load root .env file (single source of truth)
config({ path: '../.env' });

// Docs: https://rsbuild.rs/config/
export default defineConfig({
  plugins: [pluginReact()],
  server: {
    port: parseInt(process.env.KOLAM_PORT || '3000', 10),
    strictPort: true, // Fail if port is already in use instead of trying next port
  },
  source: {
    entry: {
      index: './src/main.tsx',
    },
    define: {
      'import.meta.env.VITE_CLERK_PUBLISHABLE_KEY': JSON.stringify(
        process.env.CLERK_PUBLISHABLE_KEY || ''
      ),
      'import.meta.env.VITE_API_URL': JSON.stringify(
        process.env.LOOM_API_URL || 'http://localhost:8080/api/v1'
      ),
    },
  },
  html: {
    title: 'Texture - ML Learning Studio',
  },
});
