import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/analyze': 'http://127.0.0.1:8000',
      '/mock': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000'
    }
  },
  build: { outDir: 'dist', emptyOutDir: true }
});
