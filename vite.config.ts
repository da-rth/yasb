import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import {fileURLToPath, URL} from 'url';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  root: 'src',
  build: {
    outDir: '../dist',
    rollupOptions: {
      input: ["src/index.html", "src/setup.html"],
    },
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
})
