# CampusNLP interface redesign

Build a professional student question workspace around the existing `/api/query` and `/api/health` endpoints. Retain CampusNLP branding with warm neutral surfaces, restrained green accents, clear typography, a collapsible sidebar, and a focused chat column.

## Scope and acceptance

- Responsive chat shell, empty/loading/error states, keyboard access, reduced motion, light/dark themes.
- Real API answers and document references. Label confidence as topic classification confidence, not answer accuracy. Omit placeholder page numbers.
- Locally saved conversations with search, rename, delete confirmation, new chat, copy and Markdown export. Disclose browser-only storage and independently processed questions.
- Topic guide and starter prompts grounded in the synthetic demo knowledge collection.
- Real health checks, retry and cancellation without responses leaking across conversations.
- Replace hard-coded analytics and cosmetic feedback. No unsupported uploads, voice, model picker, streaming or accounts.

## Implementation and verification

Existing React/Vite and Lucide dependencies; semantic CSS tokens and functional components. UI in `src/components`, state in `src/hooks`, data utilities and Node tests in `src/lib`.

Build order: audit capabilities; implement state and shell in parallel; integrate; verify. Preserve pre-existing backend/data/training/notebook work.

From `frontend`: `npm run build`, `npm run lint`, `node --test src/lib/workspace.test.js`, and `npm run dev -- --host 127.0.0.1`. FastAPI runs on port 8000. Verify real answer/source rendering, retry, history persistence/search, theme and responsive layouts at 320, 768, 1024 and 1440px. Inspect screenshots, focus, overflow and console output. No new services/dependencies or unrelated commits.
