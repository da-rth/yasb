import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'url';
import vue from '@vitejs/plugin-vue'
import VueTypeImports from 'vite-plugin-vue-type-imports'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VueTypeImports(),
  ],
  root: 'src',
  build: {
    outDir: '../dist',
    rollupOptions: {
      input: ["src/index.html", "src/setup.html"],
    },
  },
  resolve: {
    alias: {
      "~": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
})
