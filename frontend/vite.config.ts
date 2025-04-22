import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // listen on all addresses (so Railway’s hostname can reach it)
    host: true,
    // explicitly allow our deployed domain
    allowedHosts: ['frontend-production-575a.up.railway.app'],
    port: 3000,
    // proxy: {
    //   '/api': {
    //     target: 'http://localhost:8000',
    //     changeOrigin: true,
    //   },
    // },
  },
  // if we're using `vite preview` on Railway, mirror the same settings:
  preview: {
    host: true,
    allowedHosts: ['frontend-production-575a.up.railway.app'],
    port: 8080,
  },
});
