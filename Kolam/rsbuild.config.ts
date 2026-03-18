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
      'import.meta.env.VITE_API_URL': JSON.stringify('/api/v1'),
    },
  },
  html: {
    title: 'Texture - ML Learning Studio',
  },
});
