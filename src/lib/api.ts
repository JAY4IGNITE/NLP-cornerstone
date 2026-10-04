/**
 * Thin API client for the backend. All calls go through the `/api` base path,
 * which the Vite dev server proxies to the backend (stripping the prefix).
 *
 * Non-2xx responses are parsed and returned as the backend's structured
 * `ErrorResponse` so the UI can render them uniformly. Network/parse failures
 * are converted into a synthetic client-side `ErrorResponse` so callers never
 * have to deal with thrown exceptions.
 */
import type {
  ChatResponse,
  ErrorCode,
  ErrorResponse,
  FeedbackRating,
  FeedbackResponse,
  HealthResponse,
} from "../types/chat";

const API_BASE = "/api";

/** Narrow a chat result to the error variant. */
export function isErrorResponse(
  value: ChatResponse | ErrorResponse,
): value is ErrorResponse {
  return value.status === "error";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isStructuredError(value: unknown): value is ErrorResponse {
  return (
    isRecord(value) &&
    value.status === "error" &&
    typeof value.code === "string" &&
    typeof value.message === "string" &&
    typeof value.trace_id === "string"
  );
}

function isChatResponse(value: unknown): value is ChatResponse {
  return (
    isRecord(value) &&
    (value.status === "answered" || value.status === "abstained") &&
    typeof value.answer === "string" &&
    typeof value.trace_id === "string" &&
    Array.isArray(value.citations) &&
    isRecord(value.intent)
  );
}

function isHealthResponse(value: unknown): value is HealthResponse {
  return (
    isRecord(value) &&
    (value.status === "ok" || value.status === "degraded") &&
    typeof value.version === "string" &&
    typeof value.knowledge_base_version === "string" &&
    typeof value.index_ready === "boolean" &&
    typeof value.provider === "string"
  );
}

function clientTraceId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return `client-${crypto.randomUUID()}`;
    }
  } catch {
    /* fall through to the timestamp-based id below */
  }
  return `client-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function clientError(message: string, code: ErrorCode = "INTERNAL_ERROR"): ErrorResponse {
  return { trace_id: clientTraceId(), status: "error", code, message };
}

async function parseJsonSafe(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

/** Send a chat message; resolves to a ChatResponse or a (structured) ErrorResponse. */
export async function sendChat(message: string): Promise<ChatResponse | ErrorResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
  } catch {
    return clientError(
      "Could not reach the server. Make sure the backend is running on port 8000.",
    );
  }

  const data = await parseJsonSafe(response);
  if (!response.ok) {
    return isStructuredError(data)
      ? data
      : clientError(`The request failed with status ${response.status}.`);
  }
  return isChatResponse(data)
    ? data
    : clientError("The server returned an unexpected response.");
}

/**
 * Submit thumbs up/down feedback for a previous answer. Fire-and-forget from the
 * UI's perspective, but the resolved value is still typed for callers that care.
 */
export async function sendFeedback(
  traceId: string,
  rating: FeedbackRating,
  reason?: string,
): Promise<FeedbackResponse | ErrorResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trace_id: traceId, rating, reason }),
    });
  } catch {
    return clientError("Could not submit feedback.");
  }

  const data = await parseJsonSafe(response);
  if (!response.ok) {
    return isStructuredError(data) ? data : clientError("Feedback submission failed.");
  }
  if (isRecord(data) && data.ok === true && typeof data.trace_id === "string") {
    return { trace_id: data.trace_id, ok: true };
  }
  return clientError("Unexpected feedback response.");
}

/** Fetch backend health. Returns null on any failure so callers stay robust. */
export async function getHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) return null;
    const data = await parseJsonSafe(response);
    return isHealthResponse(data) ? data : null;
  } catch {
    return null;
  }
}
