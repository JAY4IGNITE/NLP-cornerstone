import type { ChatResult, ErrorResponse, FeedbackRating, FeedbackResponse, HealthResponse, HistoryTurn } from '../types/chat';

const API_BASE = '/api';
type JsonObject = Record<string, unknown>;
const object = (value: unknown): JsonObject => value !== null && typeof value === 'object' && !Array.isArray(value) ? value as JsonObject : {};
const string = (value: unknown, fallback = '') => typeof value === 'string' ? value : fallback;
const confidence = (value: unknown) => typeof value === 'number' && Number.isFinite(value) ? Math.max(0, Math.min(1, value)) : 0;

export function isErrorResponse(value: ChatResult): value is ErrorResponse {
  return value.status === 'error';
}

function clientError(message: string): ErrorResponse {
  return { trace_id: crypto.randomUUID(), status: 'error', code: 'INTERNAL_ERROR', message };
}

async function readJson(response: Response): Promise<JsonObject> {
  try { return object(await response.json()); } catch { return {}; }
}

function errorDetail(data: JsonObject, status: number): string {
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    const details = data.detail.map(item => string(object(item).msg)).filter(Boolean);
    if (details.length) return details.join('. ');
  }
  return status >= 500 ? 'The assistant is temporarily unavailable. Please try again.' : `The request could not be completed (${status}). Please try again.`;
}

export async function sendChat(message: string, history: HistoryTurn[] = [], signal?: AbortSignal): Promise<ChatResult> {
  signal?.throwIfAborted();
  const query = message.trim();
  if (!query || query.length > 1000) return clientError('Please enter a question between 1 and 1,000 characters.');
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, { once: true });
  const timer = setTimeout(abort, 90_000);
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, chat_history: history.slice(-10), top_k: 4 }),
      signal: controller.signal,
    });
    const raw = await readJson(response);
    signal?.throwIfAborted();
    if (!response.ok) return clientError(errorDetail(raw, response.status));
    if (typeof raw.answer !== 'string' || !raw.answer.trim()) return clientError('The assistant returned an incomplete response. Please try again.');
    const citations = (Array.isArray(raw.sources) ? raw.sources : []).map(source => {
      const item = object(source);
      const title = string(item.source_document) || string(item.document_name) || string(item.title, 'Academic document');
      const page = item.page ?? item.page_number;
      const section = string(item.section) || string(item.section_heading);
      return {
        document_id: string(item.document_id, title), title,
        location: [typeof page === 'number' || typeof page === 'string' ? `Page ${page}` : '', section].filter(Boolean).join(' · ') || 'Source reference',
        chunk_id: string(item.chunk_id) || null,
        content: string(item.text) || string(item.content) || null,
      };
    });
    return {
      trace_id: string(raw.trace_id) || crypto.randomUUID(),
      status: raw.is_fallback === true || raw.is_grounded === false ? 'abstained' : 'answered',
      answer: raw.answer, citations,
      intent: { label: string(raw.intent, 'unknown'), confidence: confidence(raw.intent_confidence) },
      overall_confidence: confidence(raw.overall_confidence ?? raw.intent_confidence),
    };
  } catch {
    signal?.throwIfAborted();
    return clientError(controller.signal.aborted ? 'This response took too long. Please try a more specific question.' : 'Could not reach the assistant. Check your connection and try again.');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
}

export async function sendFeedback(traceId: string, rating: FeedbackRating, context: { query: string; answer: string; intent: string }): Promise<FeedbackResponse | ErrorResponse> {
  try {
    const response = await fetch(`${API_BASE}/feedback`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...context, feedback: rating === 'helpful' ? 'thumbs_up' : 'thumbs_down', comments: '' }),
      signal: AbortSignal.timeout(15_000),
    });
    const data = await readJson(response);
    if (!response.ok || data.status !== 'success') return clientError('Your feedback could not be saved. Please try again.');
    return { trace_id: traceId, ok: true };
  } catch { return clientError('Your feedback could not be saved. Please try again.'); }
}

export async function getHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5_000) });
    if (!response.ok) return null;
    const raw = await readJson(response);
    if (typeof raw.status !== 'string') return null;
    return {
      status: raw.status === 'healthy' ? 'ok' : 'degraded',
      version: string(raw.version, '1.0.0'), knowledge_base_version: '1.0',
      index_ready: typeof raw.indexed_chunks_count === 'number' && raw.indexed_chunks_count > 0,
      provider: string(raw.vector_provider, 'Academic knowledge base'),
    };
  } catch { return null; }
}

export async function getMetrics(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE}/metrics`, { signal: AbortSignal.timeout(5_000) });
    if (!response.ok) return null;
    return await readJson(response);
  } catch { return null; }
}
