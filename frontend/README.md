# Frontend entry point moved

The redesigned CampusNLP workspace now runs through the root application. From the repository root, install dependencies with `npm ci`, then run `npm run dev` to start the UI and API together.

The canonical UI lives in `src/workspace/`; `src/App.tsx` and `src/main.tsx` mount it. `npm run dev:web` runs only the UI. The API proxy targets port 8002.

The scripts in this folder delegate to the root app for compatibility. See the root README for setup and verification.
