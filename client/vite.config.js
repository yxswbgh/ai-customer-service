import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  server:{
    proxy:{
      '/api':{
        target:'http://localhost:8000',
        changeOrigin:true,
      }
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})

//changeOrigin: true 的作用：

//浏览器发请求时，Origin 头是 http://localhost:5173。
// 如果不改这个头，后端 CORS 中间件会检查它是否在白名单里（你已经配了允许 5173）。
// 但生产环境中 Nginx 做代理时通常不暴露真实 origin，
// changeOrigin: true 让开发环境更接近生产行为。
// 虽然目前 CORS 已经允许了 5173，加了这个参数无害，且是 Vite 文档推荐的最佳实践。