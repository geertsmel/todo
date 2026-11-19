import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// En développement (npm run dev), les appels /api sont redirigés vers l'API locale.
// En production (Docker), c'est nginx qui joue ce rôle.
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
