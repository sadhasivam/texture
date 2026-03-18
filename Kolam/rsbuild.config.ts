import { defineConfig } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';

// Docs: https://rsbuild.rs/config/
export default defineConfig({
  plugins: [pluginReact()],
  source: {
    entry: {
      index: './src/main.tsx',
    },
    define: {
      // Replace import.meta.env.VITE_API_URL with actual value at build time
      'import.meta.env.VITE_API_URL': JSON.stringify(
        process.env.VITE_API_URL || '/api/v1'
      ),
    },
  },
  html: {
    title: 'Texture - ML Learning Studio',
  },
});
