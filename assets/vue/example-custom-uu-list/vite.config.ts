import {defineConfig} from "vite";
import {resolve} from "path";
import vue from "@vitejs/plugin-vue";
import VueI18nPlugin from "@intlify/unplugin-vue-i18n/vite";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue(), VueI18nPlugin({})],
    base: '/static/',
    build: {
        minify: false,
        outDir: "../../../dev/dev_vue/static/dev_vue/example-custom-uu-list/", // TODO: change this to your desired static dir
        emptyOutDir: true,
        lib: {
            // src/index.ts is where we have exported the component(s)
            entry: resolve(__dirname, "src/index.ts"),
            name: "CustomList", // TODO: CHANGE THIS FOR YOUR OWN COMPONENT
            // the name of the output files when the build is run
            fileName: "CustomList",// TODO: CHANGE THIS FOR YOUR OWN COMPONENT
            formats: ['iife']
        },
        rollupOptions: {
            // make sure to externalize deps that shouldn't be bundled
            // into your library
            external: ["vue", "vue-i18n"],
            output: {
                // Provide global variables to use in the UMD build
                // for externalized deps
                globals: {
                    vue: "Vue",
                    'vue-i18n': "VueI18n",
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
