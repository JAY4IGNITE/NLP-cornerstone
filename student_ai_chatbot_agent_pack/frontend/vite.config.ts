import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The app calls the API under `/api`; in dev we proxy that to the backend at
// http://localhost:8000 and strip the `/api` prefix so `/api/chat` -> `/chat`.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      },
    },
  },
});
