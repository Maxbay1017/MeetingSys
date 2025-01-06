import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'

//引入 node 提供内置模块 path,可以获取绝对路径
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  css: {
    postcss: {
      plugins: [
        tailwindcss,
        autoprefixer,
      ],
    },
  },
  resolve: {
    alias: {
     "@": path.resolve(__dirname, 'src')
    }
   },
  //配置代理跨域
  server:{
    proxy:{
       '/api': {
        target: 'http://192.168.1.21:8000',
        // target: 'http://0.0.0.0:8000',
        changeOrigin: true
      },
    }
  }
})
