import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    rollupOptions: {
      input: {
        contentScript: resolve(__dirname, "src/contentScript.tsx")
      },
      output: {
        entryFileNames: "contentScript.js",
        assetFileNames: "assets/[name].[ext]"
      }
    }
  }
});


