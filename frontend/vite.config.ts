import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
  base: "/static/philolog/react_build/",
  plugins: [react()],
  build: {
    manifest: true,
    outDir: "../static/philolog/react_build",
    rollupOptions: {
      input: "src/main.tsx",
    },
  },
});
