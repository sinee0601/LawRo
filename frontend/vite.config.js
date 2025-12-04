import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // 네트워크 접속 허용
    port: 5173,
    allowedHosts: ['lawro.duckdns.org'], // 사용자의 도메인 추가
  },
})
