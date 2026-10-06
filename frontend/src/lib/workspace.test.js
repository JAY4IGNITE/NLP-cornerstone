import assert from 'node:assert/strict'
import test from 'node:test'
import {
  MAX_CONVERSATIONS,
  STORAGE_KEY,
  conversationToMarkdown,
  filterConversations,
  loadWorkspace,
  normalizeConversations,
  saveWorkspace,
} from './workspace.js'

const createdAt = '2026-10-06T10:00:00.000Z'
const conversation = (id = 'chat-1') => ({
  id,
  title: 'Attendance requirements',
  createdAt,
  updatedAt: createdAt,
  messages: [
    { id: `${id}-user`, role: 'user', text: 'How much attendance do I need?', createdAt },
    {
      id: `${id}-answer`, role: 'assistant', text: 'Check the academic regulations.', createdAt,
      intent: 'attendance', confidence: 0,
      sources: [{ document: 'Academic Regulations.pdf', page: 1 }],
    },
  ],
})

test('restores valid conversations while discarding untrusted extra fields and placeholder pages', () => {
  const input = conversation()
  input.messages[1].html = '<script>bad()</script>'
  const result = normalizeConversations([input])
  assert.equal(result.storageError, null)
  assert.equal(result.canSave, true)
  assert.equal(result.conversations[0].messages[1].confidence, 0)
  assert.deepEqual(result.conversations[0].messages[1].sources, [{ document: 'Academic Regulations.pdf' }])
  assert.equal('html' in result.conversations[0].messages[1], false)
})

test('recovers valid records from corrupt history and protects the original stored data', () => {
  const result = normalizeConversations([null, conversation(), { id: 'broken', messages: 'invalid' }])
  assert.equal(result.conversations.length, 1)
  assert.equal(result.canSave, false)
  assert.match(result.storageError, /not.*sav|unsaved/i)
})

test('caps excessive history with an explicit warning and without authorizing destructive saves', () => {
  const result = normalizeConversations(Array.from({ length: MAX_CONVERSATIONS + 1 }, (_, i) => conversation(`chat-${i}`)))
  assert.equal(result.conversations.length, MAX_CONVERSATIONS)
  assert.equal(result.canSave, false)
  assert.match(result.storageError, /limit|large/i)
})

test('invalid and duplicate messages are reported instead of being silently overwritten', () => {
  const input = conversation()
  input.messages.push({ ...input.messages[0] }, { id: 'bad', role: 'system', text: 'Unsupported', createdAt })
  const result = normalizeConversations([input])
  assert.equal(result.conversations[0].messages.length, 2)
  assert.equal(result.canSave, false)
  assert.ok(result.storageError)
})

test('missing storage starts an empty workspace without an error', () => {
  const result = loadWorkspace({ getItem: () => null })
  assert.deepEqual(result, { conversations: [], storageError: null, canSave: true })
})

test('malformed JSON and unavailable storage remain recoverable without throwing', () => {
  const malformed = loadWorkspace({ getItem: () => '{not json' })
  assert.deepEqual(malformed.conversations, [])
  assert.equal(malformed.canSave, false)
  assert.ok(malformed.storageError)
  const unavailable = loadWorkspace({ getItem: () => { throw new Error('Access denied') } })
  assert.deepEqual(unavailable.conversations, [])
  assert.ok(unavailable.storageError)
})

test('successful persistence stores only conversations with messages under the versioned key', () => {
  const writes = new Map()
  const empty = { ...conversation('empty'), messages: [] }
  assert.equal(saveWorkspace([empty, conversation()], { setItem: (key, value) => writes.set(key, value) }), null)
  assert.equal(JSON.parse(writes.get(STORAGE_KEY)).length, 1)
})

test('quota failures report that new changes are not saved', () => {
  const error = saveWorkspace([conversation()], { setItem: () => { throw new Error('Quota exceeded') } })
  assert.match(error, /not.*sav|unsaved/i)
})

test('search matches titles and answer text without changing the original conversation order', () => {
  const first = conversation('first')
  const second = { ...conversation('second'), title: 'Library', messages: [] }
  assert.deepEqual(filterConversations([first, second], ' ACADEMIC '), [first])
  assert.deepEqual(filterConversations([first, second], 'library'), [second])
  assert.deepEqual(filterConversations([first, second], '   '), [first, second])
  assert.deepEqual(filterConversations([first, second], 'missing'), [])
})

test('markdown exports the transcript, real source names and zero confidence without invented page metadata', () => {
  const markdown = conversationToMarkdown(conversation())
  assert.match(markdown, /^# Attendance requirements/m)
  assert.match(markdown, /## You/)
  assert.match(markdown, /How much attendance do I need\?/)
  assert.match(markdown, /## CampusNLP/)
  assert.match(markdown, /Intent: attendance/)
  assert.match(markdown, /confidence: 0\.0%/i)
  assert.match(markdown, /Academic Regulations\.pdf/)
  assert.doesNotMatch(markdown, /page|p\. 1/i)
})
