import assert from 'node:assert/strict';
import { test } from 'node:test';
import { conversationHistory, decodeConversations, newConversation } from '../../src/lib/conversations.ts';
import type { Message } from '../../src/types/chat';

const answer: Message = { id: 'a', kind: 'assistant', result: { status: 'answered', answer: '75%', trace_id: 't', intent: { label: 'attendance', confidence: .9 }, citations: [], overall_confidence: .9 } };

test('saved chats round-trip, including a draft and feedback', () => {
  const chat = { ...newConversation(), title: 'Attendance', draft: 'And exemptions?', messages: [{ id: 'u', kind: 'user' as const, text: 'Attendance?' }, { ...answer, feedback: 'helpful' as const }] };
  assert.deepEqual(decodeConversations(JSON.stringify({ version: 1, conversations: [chat] })), [chat]);
});

test('corrupt or incompatible storage throws rather than silently overwriting history', () => {
  for (const value of ['{bad', '{"version":2,"conversations":[]}', '{"version":1,"conversations":[{}]}']) {
    assert.throws(() => decodeConversations(value));
  }
  assert.deepEqual(decodeConversations(null), []);
});

test('history includes only complete successful pairs, excluding failed and stopped turns', () => {
  const messages: Message[] = [
    { id: '1', kind: 'user', text: 'Attendance?' }, answer,
    { id: '2', kind: 'user', text: 'Failed question' },
    { id: 'e', kind: 'assistant', result: { status: 'error', code: 'INTERNAL_ERROR', trace_id: 't', message: 'Offline' } },
    { id: '3', kind: 'user', text: 'Stopped question' }, { id: 'n', kind: 'notice', text: 'Stopped' },
    { id: '4', kind: 'user', text: 'Unfinished question' },
  ];
  assert.deepEqual(conversationHistory(messages), [{ role: 'user', content: 'Attendance?' }, { role: 'assistant', content: '75%' }]);
});

test('history is bounded to five complete exchanges', () => {
  const messages: Message[] = Array.from({ length: 9 }, (_, i) => [{ id: `u${i}`, kind: 'user' as const, text: `Question ${i}` }, { ...answer, id: `a${i}` }]).flat();
  const history = conversationHistory(messages);
  assert.equal(history.length, 10);
  assert.equal(history[0].content, 'Question 4');
});
