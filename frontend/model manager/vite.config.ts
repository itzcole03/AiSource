import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
          icons: ['lucide-react'],
        },
      },
    },
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      // API routes - Route to backend on port 8002
      '^/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Backend routes
      '^/backend': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        rewrite: (path) => path.replace(/^\/backend/, '')
      },
      // V1 API routes (for model providers)
      '^/v1': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        timeout: 10000
      },
      // Health check endpoint
      '^/health': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        timeout: 5000
      },
      // Marketplace providers endpoint (must come before general providers)
      '^/providers/marketplace': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        rewrite: (path) => path.replace(/^\/providers\/marketplace/, '/providers/marketplace')
      },
      // General providers endpoint
      '^/providers': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        timeout: 10000
      },
      // System endpoint
      '^/system': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        timeout: 10000
      }
    },
  },
  preview: {
    host: true,
    port: 5173,
  },
});