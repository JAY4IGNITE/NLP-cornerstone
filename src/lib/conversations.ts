import type { Conversation, HistoryTurn, Message } from '../types/chat';

export const STORAGE_KEY = 'campusai.conversations.v1';

export function newConversation(): Conversation {
  return { id: crypto.randomUUID(), title: 'New conversation', updatedAt: Date.now(), messages: [], draft: '' };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function isMessage(value: unknown): value is Message {
  if (!isRecord(value) || typeof value.id !== 'string') return false;
  if (value.kind === 'user' || value.kind === 'notice') return typeof value.text === 'string';
  if (value.kind !== 'assistant' || !isRecord(value.result)) return false;
  if (value.feedback !== undefined && value.feedback !== 'helpful' && value.feedback !== 'not_helpful') return false;
  const result = value.result;
  if (typeof result.trace_id !== 'string') return false;
  if (result.status === 'error') return typeof result.message === 'string' && typeof result.code === 'string';
  return (result.status === 'answered' || result.status === 'abstained') && typeof result.answer === 'string'
    && typeof result.overall_confidence === 'number' && isRecord(result.intent)
    && typeof result.intent.label === 'string' && typeof result.intent.confidence === 'number'
    && Array.isArray(result.citations) && result.citations.every(c => isRecord(c)
      && typeof c.title === 'string' && typeof c.location === 'string' && typeof c.document_id === 'string'
      && (c.content === null || typeof c.content === 'string') && (c.chunk_id === null || typeof c.chunk_id === 'string'));
}

export function decodeConversations(raw: string | null): Conversation[] {
  if (!raw) return [];
  const data: unknown = JSON.parse(raw);
  if (!isRecord(data) || data.version !== 1 || !Array.isArray(data.conversations)) throw new Error('Invalid history format');
  const ids = new Set<string>();
  for (const chat of data.conversations) {
    if (!isRecord(chat) || typeof chat.id !== 'string' || ids.has(chat.id) || typeof chat.title !== 'string'
      || typeof chat.updatedAt !== 'number' || !Number.isFinite(chat.updatedAt) || typeof chat.draft !== 'string'
      || !Array.isArray(chat.messages) || !chat.messages.every(isMessage)) throw new Error('Invalid conversation');
    ids.add(chat.id);
  }
  return data.conversations as Conversation[];
}

export function conversationHistory(messages: Message[]): HistoryTurn[] {
  const turns: HistoryTurn[] = [];
  for (let i = 0; i < messages.length - 1; i++) {
    const user = messages[i];
    const assistant = messages[i + 1];
    if (user.kind === 'user' && assistant.kind === 'assistant' && assistant.result.status !== 'error') {
      turns.push({ role: 'user', content: user.text }, { role: 'assistant', content: assistant.result.answer });
    }
  }
  return turns.slice(-10);
}

export function matchesConversation(chat: Conversation, search: string): boolean {
  const query = search.trim().toLocaleLowerCase();
  return !query || chat.title.toLocaleLowerCase().includes(query) || chat.messages.some(message =>
    (message.kind === 'assistant' ? message.result.status === 'error' ? message.result.message : message.result.answer : message.text).toLocaleLowerCase().includes(query));
}
