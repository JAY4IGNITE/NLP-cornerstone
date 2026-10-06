# CampusAI chatbot redesign

## Objective and scope
Replace the placeholder dashboard with a focused, responsive academic chatbot. Retain the existing FastAPI retrieval pipeline, grounded answers, source citations, abstention, and feedback. Remove mock navigation, fake history, account controls, and the old loader.

## Experience
Soft neutral glass surfaces, blue accents, Outfit and Space Grotesk typography, a persistent conversation sidebar, a clear welcome screen, and a comfortable reading column. Use the published `thinking-orbs` React component for the welcome and pending-answer states. Respect reduced motion, including message entrance animations.

## Functional acceptance criteria
- Create, search, reopen, rename, and delete locally saved conversations; explain local storage and surface storage failures.
- Send actual recent conversation turns to `/api/chat`; support Enter to send, Shift+Enter for a newline, composition input, a 1,000-character limit, cancellation, retry, and actionable failures.
- Render safe Markdown, expandable citation excerpts, copy answers, regenerate the latest answer, and submit feedback with the actual question and answer. Confirm feedback only after success.
- Reflect backend availability accurately; distinguish unsupported answers from grounded answers without exposing classifier diagnostics in the main chat.
- Offer keyboard-accessible dialogs, mobile navigation, visible focus, and light/dark appearance.

## Implementation order
1. Correct the typed API adapter and add contract tests using Node's test runner with TypeScript stripping.
2. Implement validated local conversation persistence and request lifecycle handling.
3. Build the sidebar, welcome view, messages, composer, dialogs, and responsive styles.
4. Verify typecheck, build, contract/persistence tests, existing backend tests where runtime is available, and real browser flows.

## Source layout and conventions
React components live in `src/components`, hooks in `src/hooks`, API and storage helpers in `src/lib`, and shared types in `src/types`. Use typed props, native buttons and dialogs, and semantic CSS tokens. Avoid adding unsupported controls.

## Verification commands
`npm run lint`, `npm run build`, `npm test`, `python -m pytest tests`, `npm run dev`.

## Boundaries
Keep credentials in existing environment configuration. Do not publish or deploy. Do not change research datasets or trained models. Local conversation storage is browser-specific; live response quality still depends on the configured backend and its knowledge sources.

## Upstream component
[Thinking Orbs](https://github.com/Jakubantalik/thinking-orbs), MIT, Jakub Antalik. Installed from npm; do not fork or replace the component with an imitation.
