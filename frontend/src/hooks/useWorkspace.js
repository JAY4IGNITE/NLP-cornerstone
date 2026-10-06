import { useCallback, useEffect, useRef, useState } from 'react'
import { loadWorkspace, normalizeSources, saveWorkspace } from '../lib/workspace.js'

const API_BASE = (import.meta.env?.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
const QUERY_TIMEOUT = 45_000
const HEALTH_TIMEOUT = 5_000
const createId = () => globalThis.crypto.randomUUID()
const now = () => new Date().toISOString()

export default function useWorkspace() {
  const [initial] = useState(() => loadWorkspace())
  const [conversations, setConversations] = useState(initial.conversations)
  const [activeId, setActiveId] = useState(null)
  const [isThinking, setIsThinking] = useState(false)
  const [health, setHealth] = useState('checking')
  const [storageError, setStorageError] = useState(initial.storageError)
  const conversationsRef = useRef(initial.conversations)
  const activeIdRef = useRef(null)
  const requestRef = useRef(null)
  const healthRequestRef = useRef(null)
  const mountedRef = useRef(false)
  const lastSavedRef = useRef(initial.conversations)

  // Keep an immediately current reference so rapid clicks cannot launch two
  // requests or route a response into a different conversation before a render.
  const updateConversations = useCallback((update) => {
    const next = update(conversationsRef.current)
    conversationsRef.current = next
    setConversations(next)
  }, [])

  const activate = useCallback((id) => {
    activeIdRef.current = id
    setActiveId(id)
  }, [])

  useEffect(() => {
    if (!initial.canSave || lastSavedRef.current === conversations) return
    lastSavedRef.current = conversations
    setStorageError(saveWorkspace(conversations))
  }, [conversations, initial.canSave])

  const finishRequest = useCallback((request, response) => {
    if (!mountedRef.current || requestRef.current !== request) return
    clearTimeout(request.timer)
    requestRef.current = null
    updateConversations((chats) => chats.map((chat) => {
      if (chat.id !== request.chatId) return chat
      const message = { id: request.responseId, role: 'assistant', createdAt: now(), ...response }
      const existing = chat.messages.some((item) => item.id === request.responseId)
      return {
        ...chat,
        updatedAt: message.createdAt,
        messages: existing
          ? chat.messages.map((item) => item.id === request.responseId ? message : item)
          : [...chat.messages, message],
      }
    }).sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)))
    setIsThinking(false)
  }, [updateConversations])

  const stopRequest = useCallback(() => {
    const request = requestRef.current
    if (!request) return
    finishRequest(request, { text: 'Request stopped. You can retry this question whenever you are ready.', error: true, query: request.query })
    request.controller.abort()
  }, [finishRequest])

  const inspectHealth = useCallback(async () => {
    const previous = healthRequestRef.current
    if (previous) {
      clearTimeout(previous.timer)
      previous.controller.abort()
    }
    const request = { controller: new AbortController() }
    healthRequestRef.current = request
    request.timer = setTimeout(() => request.controller.abort(), HEALTH_TIMEOUT)
    try {
      const response = await fetch(`${API_BASE}/api/health`, { signal: request.controller.signal })
      const data = response.ok ? await response.json() : null
      if (mountedRef.current && healthRequestRef.current === request) {
        setHealth(data?.status === 'healthy' ? 'online' : 'offline')
      }
    } catch {
      if (mountedRef.current && healthRequestRef.current === request) setHealth('offline')
    } finally {
      clearTimeout(request.timer)
      if (healthRequestRef.current === request) healthRequestRef.current = null
    }
  }, [])

  const checkHealth = useCallback(() => {
    setHealth('checking')
    return inspectHealth()
  }, [inspectHealth])

  useEffect(() => {
    mountedRef.current = true
    // This synchronizes with the external health endpoint; state updates only
    // occur after its asynchronous fetch completes.
    // eslint-disable-next-line react/set-state-in-effect
    inspectHealth()
    return () => {
      mountedRef.current = false
      for (const ref of [requestRef, healthRequestRef]) {
        if (ref.current) {
          clearTimeout(ref.current.timer)
          ref.current.controller.abort()
          ref.current = null
        }
      }
    }
  }, [inspectHealth])

  const runQuery = useCallback(async (chatId, query, responseId = createId()) => {
    const request = { chatId, query, responseId, controller: new AbortController() }
    requestRef.current = request
    setIsThinking(true)
    request.timer = setTimeout(() => {
      finishRequest(request, {
        text: 'The campus service took too long to respond. Please try this question again.',
        error: true,
        query,
      })
      request.controller.abort()
    }, QUERY_TIMEOUT)

    try {
      const response = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
        signal: request.controller.signal,
      })
      if (!response.ok) {
        finishRequest(request, {
          text: response.status >= 500
            ? 'The campus service is temporarily unavailable. Please try again.'
            : 'The campus service could not process this question. Please try again.',
          error: true,
          query,
        })
        return
      }
      const data = await response.json()
      if (!data || typeof data.answer !== 'string' || !data.answer.trim()) {
        finishRequest(request, { text: 'The campus service returned an incomplete response. Please try again.', error: true, query })
        return
      }
      const message = { text: data.answer, sources: normalizeSources(data.sources) }
      if (typeof data.intent === 'string' && data.intent.trim()) message.intent = data.intent
      if (Number.isFinite(data.confidence) && data.confidence >= 0 && data.confidence <= 1) {
        message.confidence = data.confidence
      }
      finishRequest(request, message)
    } catch {
      finishRequest(request, {
        text: 'Unable to reach the campus service. Check your connection and try again.',
        error: true,
        query,
      })
    }
  }, [finishRequest])

  const sendMessage = useCallback((text) => {
    if (requestRef.current || typeof text !== 'string' || !text.trim()) return false
    const query = text.trim()
    const timestamp = now()
    const message = { id: createId(), role: 'user', text: query, createdAt: timestamp }
    let chatId = activeIdRef.current
    if (!chatId || !conversationsRef.current.some((chat) => chat.id === chatId)) {
      chatId = createId()
      updateConversations((chats) => [{
        id: chatId,
        title: query.replace(/\s+/g, ' ').slice(0, 72),
        createdAt: timestamp,
        updatedAt: timestamp,
        messages: [message],
      }, ...chats])
      activate(chatId)
    } else {
      updateConversations((chats) => chats.map((chat) => chat.id === chatId
        ? { ...chat, updatedAt: timestamp, messages: [...chat.messages, message] }
        : chat).sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)))
    }
    runQuery(chatId, query)
    return true
  }, [activate, runQuery, updateConversations])

  const retryMessage = useCallback((messageId) => {
    if (requestRef.current) return false
    const chat = conversationsRef.current.find((item) => item.id === activeIdRef.current)
    const message = chat?.messages.find((item) => item.id === messageId)
    if (!message?.error || !message.query) return false
    runQuery(chat.id, message.query, message.id)
    return true
  }, [runQuery])

  const newChat = useCallback(() => {
    stopRequest()
    activate(null)
  }, [activate, stopRequest])

  const selectChat = useCallback((id) => {
    if (id === activeIdRef.current || !conversationsRef.current.some((chat) => chat.id === id)) return
    stopRequest()
    activate(id)
  }, [activate, stopRequest])

  const deleteChat = useCallback((id) => {
    if (requestRef.current?.chatId === id) stopRequest()
    updateConversations((chats) => chats.filter((chat) => chat.id !== id))
    if (activeIdRef.current === id) activate(null)
  }, [activate, stopRequest, updateConversations])

  const renameChat = useCallback((id, title) => {
    if (typeof title !== 'string' || !title.trim()) return
    updateConversations((chats) => chats.map((chat) => chat.id === id
      ? { ...chat, title: title.trim().replace(/\s+/g, ' ').slice(0, 200) }
      : chat))
  }, [updateConversations])

  const activeConversation = conversations.find((chat) => chat.id === activeId) ?? null
  return {
    conversations,
    activeId,
    activeConversation,
    messages: activeConversation?.messages ?? [],
    isThinking,
    health,
    storageError,
    newChat,
    selectChat,
    deleteChat,
    renameChat,
    sendMessage,
    retryMessage,
    stopRequest,
    checkHealth,
  }
}
