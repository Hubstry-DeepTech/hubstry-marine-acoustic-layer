import { defineConfig } from "vite";

// base relativa: funciona tanto em hmal.hubstry.dev quanto no endereço padrão do GitHub Pages
export default defineConfig({ base: "./", build: { outDir: "dist", assetsInlineLimit: 0 } });
