import type {
  ChatResponse,
  ErrorCode,
  ErrorResponse,
  FeedbackRating,
  FeedbackResponse,
  HealthResponse,
} from "../types/chat";

const API_BASE = "/api";

export function isErrorResponse(
  value: ChatResponse | ErrorResponse,
): value is ErrorResponse {
  return value.status === "error";
}

function clientTraceId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return `client-${crypto.randomUUID()}`;
    }
  } catch {}
  return `client-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function clientError(message: string, code: ErrorCode = "INTERNAL_ERROR"): ErrorResponse {
  return { trace_id: clientTraceId(), status: "error", code, message };
}

async function parseJsonSafe(response: Response): Promise<any> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export async function sendChat(message: string): Promise<ChatResponse | ErrorResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message, chat_history: [], top_k: 4 }),
    });
  } catch {
    return clientError(
      "Could not reach the server. Make sure the backend is running.",
    );
  }

  const rawData = await parseJsonSafe(response);
  if (!response.ok) {
    return clientError(rawData?.detail || `The request failed with status ${response.status}.`);
  }
  
  if (!rawData) {
      return clientError("The server returned an empty response.");
  }

  const data: ChatResponse = {
    status: rawData.answer ? "answered" : "abstained",
    trace_id: clientTraceId(),
    answer: rawData.answer || "No response generated.",
    intent: {
      label: rawData.intent || "unknown",
      confidence: rawData.intent_confidence || 0,
    },
    citations: (rawData.sources || []).map((s: any) => ({
      document_id: s.document_id || "unknown",
      title: s.document_name || "Document",
      location: s.section_heading || "General",
      chunk_id: s.chunk_id || null,
      content: s.text || s.content || null
    })),
    overall_confidence: rawData.overall_confidence || rawData.intent_confidence || 0,
  };

  return data;
}

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
      body: JSON.stringify({
          query: "Unknown Query (via Chat UI)", 
          answer: "Unknown Answer",
          intent: "unknown",
          feedback: rating === "helpful" ? "thumbs_up" : "thumbs_down",
          comments: reason || ""
      }),
    });
  } catch {
    return clientError("Could not submit feedback.");
  }

  if (!response.ok) {
    return clientError("Feedback submission failed.");
  }
  return { trace_id: traceId, ok: true };
}

export async function getHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) return null;
    const rawData = await parseJsonSafe(response);
    if (!rawData) return null;
    
    return {
      status: rawData.status === "healthy" ? "ok" : "degraded",
      version: rawData.version || "1.0.0",
      knowledge_base_version: "1.0",
      index_ready: rawData.indexed_chunks_count > 0,
      provider: rawData.vector_provider || "Local Engine",
    };
  } catch {
    return null;
  }
}
