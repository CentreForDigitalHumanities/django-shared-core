import {defineConfig} from "vite";
import {resolve} from "path";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    base: '/static/',
    build: {
        // minify: 'esbuild',
        minify: false,
        outDir: "../../../src/cdh/vue3/static/cdh.vue3/components/uu-list/",
        emptyOutDir: true,
        lib: {
            // src/index.ts is where we have exported the component(s)
            entry: resolve(__dirname, "src/index.ts"),
            name: "UUList",
            // the name of the output files when the build is run
            fileName: "UUList",
            formats: ['iife']
        },
        rollupOptions: {
            // make sure to externalize deps that shouldn't be bundled
            // into your library
            external: ["vue", "vueI18n"],
            output: {
                // Provide global variables to use in the UMD build
                // for externalized deps
                globals: {
                    vue: "Vue",
                    vueI18n: "vueI18n",
                },
                chunkFileNames: undefined,
            },
        },
    },
    resolve: {
      alias: {
        "@": resolve(__dirname, "./src"),
      },
    },
    optimizeDeps: {
      include: ['src/**/*.vue', 'src/index.ts'],
    },
    define: {
      'process.env': {}
    }
});
