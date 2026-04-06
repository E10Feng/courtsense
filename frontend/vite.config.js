import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/sessions": "http://localhost:8000",
      "/digest": "http://localhost:8000",
      "/drills": "http://localhost:8000",
    },
  },
});
