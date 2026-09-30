/**
 * TypeScript interfaces mirroring the backend API contract exactly.
 * See backend/app/schemas/chat.py.
 */

/** POST /api/chat request body. */
export interface ChatRequest {
  message: string;
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
  trace_id: string;
  rating: FeedbackRating;
  reason?: string;
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
