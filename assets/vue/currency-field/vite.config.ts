import { defineConfig } from 'vite'
import {resolve} from "path"
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: "../../../src/cdh/core/static/cdh.core/js/widget/",
    emptyOutDir: false,
    lib: {
      entry: resolve(__dirname, "src/main.ts"),
      name: "CurrencyField",
      fileName: "currency-field",
    },

    },
})
