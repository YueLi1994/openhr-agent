import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export const DEV_PROXY = {
  '/api': { target: 'http://127.0.0.1:8000' },
  '/health': { target: 'http://127.0.0.1:8000' },
}

export default defineConfig({
  plugins: [react()],
  server: { proxy: DEV_PROXY },
  test: { environment: 'jsdom', setupFiles: './src/test/setup.ts' },
})
