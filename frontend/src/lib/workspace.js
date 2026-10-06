export const STORAGE_KEY = 'campusnlp.conversations.v1'
export const MAX_CONVERSATIONS = 200
const MAX_MESSAGES = 1000
const MAX_TEXT_LENGTH = 100_000
const MAX_STORAGE_LENGTH = 4_000_000

const recoveryWarning = 'Some saved history could not be loaded. The original browser data is unchanged; new changes are not saved. Export any conversations you want to keep.'
const limitWarning = 'Saved history exceeds the workspace limit. The original browser data is unchanged; new changes are not saved. Export any conversations you want to keep.'
const saveWarning = 'This browser could not save your latest changes. They are available for this session but are not saved. Export conversations you want to keep.'

function validString(value, maxLength) {
  return typeof value === 'string' && value.trim().length > 0 && value.length <= maxLength
}

function validDate(value) {
  return (typeof value === 'string' || typeof value === 'number') && Number.isFinite(new Date(value).getTime())
}

// The API currently supplies placeholder page numbers, so only document names
// are trustworthy enough to display or export.
export function normalizeSources(sources) {
  if (!Array.isArray(sources)) return []
  const documents = new Set()
  return sources.flatMap((source) => {
    if (!source || !validString(source.document, 1000)) return []
    const document = source.document.trim()
    if (documents.has(document)) return []
    documents.add(document)
    return [{ document }]
  })
}

export function normalizeConversations(value) {
  if (!Array.isArray(value)) {
    return { conversations: [], storageError: recoveryWarning, canSave: false }
  }

  let invalid = false
  let overLimit = value.length > MAX_CONVERSATIONS
  const ids = new Set()
  const conversations = []

  for (const chat of value.slice(0, MAX_CONVERSATIONS)) {
    if (!chat || !validString(chat.id, 200) || ids.has(chat.id)
      || !validString(chat.title, 200) || !Array.isArray(chat.messages)
      || !validDate(chat.createdAt) || !validDate(chat.updatedAt)) {
      invalid = true
      continue
    }

    ids.add(chat.id)
    overLimit ||= chat.messages.length > MAX_MESSAGES
    const messageIds = new Set()
    const messages = []
    for (const message of chat.messages.slice(0, MAX_MESSAGES)) {
      if (!message || !validString(message.id, 200) || messageIds.has(message.id)
        || !['user', 'assistant'].includes(message.role)
        || !validString(message.text, MAX_TEXT_LENGTH) || !validDate(message.createdAt)) {
        invalid = true
        continue
      }

      messageIds.add(message.id)
      const normalized = {
        id: message.id,
        role: message.role,
        text: message.text,
        createdAt: new Date(message.createdAt).toISOString(),
      }
      if (validString(message.intent, 200)) normalized.intent = message.intent
      if (Number.isFinite(message.confidence) && message.confidence >= 0 && message.confidence <= 1) {
        normalized.confidence = message.confidence
      }
      if (Array.isArray(message.sources)) normalized.sources = normalizeSources(message.sources)
      if (message.error === true) normalized.error = true
      if (validString(message.query, MAX_TEXT_LENGTH)) normalized.query = message.query
      messages.push(normalized)
    }

    if (messages.length > 0) {
      conversations.push({
        id: chat.id,
        title: chat.title.trim(),
        createdAt: new Date(chat.createdAt).toISOString(),
        updatedAt: new Date(chat.updatedAt).toISOString(),
        messages,
      })
    }
  }

  conversations.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
  return {
    conversations,
    storageError: overLimit ? limitWarning : invalid ? recoveryWarning : null,
    canSave: !overLimit && !invalid,
  }
}

export function loadWorkspace(storage) {
  let serialized
  try {
    serialized = (storage ?? globalThis.localStorage).getItem(STORAGE_KEY)
  } catch {
    return { conversations: [], storageError: saveWarning, canSave: false }
  }
  if (serialized == null) return { conversations: [], storageError: null, canSave: true }
  if (serialized.length > MAX_STORAGE_LENGTH) {
    return { conversations: [], storageError: limitWarning, canSave: false }
  }
  try {
    return normalizeConversations(JSON.parse(serialized))
  } catch {
    return { conversations: [], storageError: recoveryWarning, canSave: false }
  }
}

export function saveWorkspace(conversations, storage) {
  try {
    const saved = conversations.filter((chat) => chat.messages.length > 0)
    const normalized = normalizeConversations(saved)
    if (!normalized.canSave) return saveWarning
    const serialized = JSON.stringify(normalized.conversations)
    if (serialized.length > MAX_STORAGE_LENGTH) return saveWarning
    ;(storage ?? globalThis.localStorage).setItem(STORAGE_KEY, serialized)
    return null
  } catch {
    return saveWarning
  }
}

export function filterConversations(conversations, search) {
  const query = search.trim().toLocaleLowerCase()
  if (!query) return conversations
  return conversations.filter((chat) => chat.title.toLocaleLowerCase().includes(query)
    || chat.messages.some((message) => message.text.toLocaleLowerCase().includes(query)))
}

function markdownLabel(value) {
  return value.replace(/[\r\n]+/g, ' ').replace(/([\\`*_{}[\]<>#])/g, '\\$1')
}

export function conversationToMarkdown(conversation) {
  if (!conversation) return ''
  const lines = [`# ${markdownLabel(conversation.title)}`, '', 'Exported from CampusNLP.', '']
  for (const message of conversation.messages) {
    lines.push(`## ${message.role === 'user' ? 'You' : 'CampusNLP'}${message.error ? ' — Request error' : ''}`, '', message.text, '')
    const metadata = []
    if (message.intent) metadata.push(`Intent: ${markdownLabel(message.intent)}`)
    if (Number.isFinite(message.confidence)) metadata.push(`Intent confidence: ${(message.confidence * 100).toFixed(1)}%`)
    if (metadata.length) lines.push(metadata.join(' · '), '')
    const sources = normalizeSources(message.sources)
    if (sources.length) lines.push('Sources:', '', ...sources.map(({ document }) => `- ${markdownLabel(document)}`), '')
  }
  return `${lines.join('\n').trim()}\n`
}
