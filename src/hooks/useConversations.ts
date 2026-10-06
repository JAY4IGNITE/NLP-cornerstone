import { useEffect, useRef, useState } from 'react';
import { sendChat, sendFeedback } from '../lib/api';
import { conversationHistory, decodeConversations, newConversation, STORAGE_KEY } from '../lib/conversations';
import type { Conversation, FeedbackRating, Message } from '../types/chat';

function loadHistory() {
  try {
    const conversations = decodeConversations(localStorage.getItem(STORAGE_KEY));
    for (const chat of conversations) {
      if (chat.messages.at(-1)?.kind === 'user') chat.messages.push({ id: crypto.randomUUID(), kind: 'notice', text: 'This response was interrupted. You can try again.' });
    }
    return { conversations: conversations.length ? conversations : [newConversation()], error: '' };
  } catch {
    return { conversations: [newConversation()], error: 'Saved chats could not be loaded. New chats will stay in this tab to protect your existing history.' };
  }
}

export function useConversations() {
  const [initial] = useState(loadHistory);
  const [conversations, setConversations] = useState(initial.conversations);
  const [activeId, setActiveId] = useState(initial.conversations[0].id);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [storageError, setStorageError] = useState(initial.error);
  const request = useRef<{ id: string; controller: AbortController } | null>(null);
  const active = conversations.find(chat => chat.id === activeId) ?? conversations[0];

  useEffect(() => {
    if (initial.error) return;
    const timer = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: 1, conversations: conversations.filter(chat => chat.messages.length || chat.draft).sort((a, b) => b.updatedAt - a.updatedAt) }));
        setStorageError('');
      } catch { setStorageError('Browser storage is full or unavailable. Recent changes will stay in this tab until you free some space.'); }
    }, 250);
    return () => clearTimeout(timer);
  }, [conversations, initial.error]);

  useEffect(() => () => { request.current?.controller.abort(); }, []);

  function update(id: string, transform: (chat: Conversation) => Conversation) {
    setConversations(chats => chats.map(chat => chat.id === id ? transform(chat) : chat));
  }

  function create() {
    const empty = conversations.find(chat => !chat.messages.length && !chat.draft);
    const chat = empty ?? newConversation();
    if (!empty) setConversations(chats => [chat, ...chats]);
    setActiveId(chat.id);
  }

  function remove(id: string) {
    if (request.current?.id === id) request.current.controller.abort();
    const remaining = conversations.filter(chat => chat.id !== id);
    if (!remaining.length) remaining.push(newConversation());
    setConversations(remaining);
    if (activeId === id) setActiveId(remaining[0].id);
  }

  async function submit(text: string, retry = false) {
    const query = text.trim();
    if (!query || query.length > 1000 || request.current) return;
    const id = active.id;
    const controller = new AbortController();
    request.current = { id, controller };
    setPendingId(id);
    const userIndex = active.messages.findLastIndex(message => message.kind === 'user');
    const base = retry ? active.messages.slice(0, userIndex) : active.messages;
    const messages: Message[] = [...base, { kind: 'user', id: crypto.randomUUID(), text: query }];
    update(id, chat => ({ ...chat, messages, draft: retry ? chat.draft : '', updatedAt: Date.now(), title: chat.messages.length ? chat.title : query.slice(0, 60) }));
    try {
      const result = await sendChat(query, conversationHistory(base), controller.signal);
      if (!controller.signal.aborted) update(id, chat => ({ ...chat, updatedAt: Date.now(), messages: [...chat.messages, { kind: 'assistant', id: crypto.randomUUID(), result }] }));
    } catch {
      update(id, chat => ({ ...chat, messages: [...chat.messages, { kind: 'notice', id: crypto.randomUUID(), text: 'Response stopped. You can try again or ask a new question.' }] }));
    } finally {
      if (request.current?.controller === controller) {
        request.current = null;
        setPendingId(null);
      }
    }
  }

  async function feedback(messageId: string, rating: FeedbackRating): Promise<string | null> {
    const id = active.id;
    const index = active.messages.findIndex(message => message.id === messageId);
    const message = active.messages[index];
    const question = active.messages[index - 1];
    if (message?.kind !== 'assistant' || message.result.status === 'error' || question?.kind !== 'user') return 'Could not find this answer.';
    const result = await sendFeedback(message.result.trace_id, rating, { query: question.text, answer: message.result.answer, intent: message.result.intent.label });
    if ('status' in result) return result.message;
    update(id, chat => ({ ...chat, messages: chat.messages.map(item => item.id === messageId && item.kind === 'assistant' ? { ...item, feedback: rating } : item) }));
    return null;
  }

  return {
    conversations, active, pendingId, storageError, create, remove, submit, feedback,
    select: setActiveId,
    rename: (id: string, title: string) => update(id, chat => ({ ...chat, title: title.trim().slice(0, 80) || chat.title })),
    setDraft: (draft: string) => update(active.id, chat => ({ ...chat, draft })),
    stop: () => request.current?.controller.abort(),
  };
}
