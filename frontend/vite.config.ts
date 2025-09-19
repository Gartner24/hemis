import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  // Environment variables that will be available in the app
  envPrefix: 'VITE_',
  // preview allowed hosts
  preview: {
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'hemis-frontend',
      'hemis-backend',
      'hemis-redis',
      'host.docker.internal',
      'hemis.gartnercodes.com',
      '147.93.118.183',
      '*'
    ],
    cors: true,
    port: 5173,
    host: true,
    strictPort: true,
    https: false,
    open: false,
  },
})
