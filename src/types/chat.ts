/** Frontend view models normalized from backend/main.py by lib/api.ts. */

export interface HistoryTurn {
  role: 'user' | 'assistant';
  content: string;
}

export type Message =
  | { id: string; kind: 'user'; text: string }
  | { id: string; kind: 'assistant'; result: ChatResult; feedback?: FeedbackRating }
  | { id: string; kind: 'notice'; text: string };

export interface Conversation {
  id: string;
  title: string;
  updatedAt: number;
  messages: Message[];
  draft: string;
}

/** POST /api/chat request body. */
export interface ChatRequest {
  query: string;
  chat_history: HistoryTurn[];
  top_k: number;
}

/** A single grounded source backing an answer. */
export interface Citation {
  document_id: string;
  title: string;
  location: string;
  chunk_id: string | null;
  content: string | null;
}

/** Predicted intent for the user's message. */
export interface IntentInfo {
  label: string;
  /** In the range [0, 1]. */
  confidence: number;
}

/** Non-error chat outcomes returned with HTTP 200. */
export type AnswerStatus = "answered" | "abstained";

/** Successful POST /api/chat response (HTTP 200). */
export interface ChatResponse {
  trace_id: string;
  status: AnswerStatus;
  answer: string;
  citations: Citation[];
  intent: IntentInfo;
  overall_confidence: number;
}

/** Structured error codes the backend may return. */
export type ErrorCode =
  | "VALIDATION_ERROR"
  | "PROVIDER_ERROR"
  | "INDEX_ERROR"
  | "INTERNAL_ERROR";

/** Structured error body (HTTP 400 / 500). */
export interface ErrorResponse {
  trace_id: string;
  status: "error";
  code: ErrorCode;
  message: string;
}

/** The two possible outcomes of a chat call. */
export type ChatResult = ChatResponse | ErrorResponse;

/** Feedback rating values accepted by POST /api/feedback. */
export type FeedbackRating = "helpful" | "not_helpful";

/** POST /api/feedback request body. */
export interface FeedbackRequest {
  query: string;
  answer: string;
  intent: string;
  feedback: 'thumbs_up' | 'thumbs_down';
  comments?: string;
}

/** POST /api/feedback response body. */
export interface FeedbackResponse {
  trace_id: string;
  ok: true;
}

/** GET /api/health status values. */
export type HealthStatus = "ok" | "degraded";

/** GET /api/health response body. */
export interface HealthResponse {
  status: HealthStatus;
  version: string;
  knowledge_base_version: string;
  index_ready: boolean;
  provider: string;
}
