import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/proxy/Greenie': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Greenie/, ''),
      },
      '/proxy/Slinker': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Slinker/, ''),
      },
      '/proxy/Trapper': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Trapper/, ''),
      },
      '/proxy/Gobber': {
        target: 'http://localhost:8085',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Gobber/, ''),
      },
      '/proxy/Sneaker': {
        target: 'http://localhost:8086',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Sneaker/, ''),
      },
      '/proxy/Hider': {
        target: 'http://localhost:8087',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Hider/, ''),
      },
      '/proxy/Poltergeist': {
        target: 'http://localhost:8088',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Poltergeist/, ''),
      },
      '/proxy/Shrewd': {
        target: 'http://localhost:8089',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/proxy\/Shrewd/, ''),
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
