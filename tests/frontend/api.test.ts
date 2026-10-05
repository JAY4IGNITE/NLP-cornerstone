import assert from 'node:assert/strict';
import { afterEach, mock, test } from 'node:test';
import { getHealth, sendChat, sendFeedback } from '../../src/lib/api.ts';

afterEach(() => mock.restoreAll());
const reply = { answer: 'Attendance is **75%**.', intent: 'attendance_rules', intent_confidence: .9, overall_confidence: 0, is_grounded: true, is_fallback: false, sources: [{ source_document: 'Regulations.pdf', page: 12, section: 'Attendance', chunk_id: 'attendance-1' }] };
const respond = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

test('sends prior turns and maps real citation fields without losing zero confidence', async () => {
  let payload: unknown;
  mock.method(globalThis, 'fetch', async (_url: string, options: RequestInit) => {
    payload = JSON.parse(options.body as string);
    return respond(reply);
  });
  const history = [{ role: 'user' as const, content: 'Tell me about attendance.' }];
  const result = await sendChat('What about exemptions?', history);
  assert.deepEqual(payload, { query: 'What about exemptions?', chat_history: history, top_k: 4 });
  assert.equal(result.status, 'answered');
  assert.equal(result.overall_confidence, 0);
  assert.equal(result.citations[0].title, 'Regulations.pdf');
  assert.equal(result.citations[0].location, 'Page 12 · Attendance');
});

test('an unsupported response with text is still abstained', async () => {
  mock.method(globalThis, 'fetch', async () => respond({ ...reply, is_grounded: false, is_fallback: true }));
  assert.equal((await sendChat('Unknown question')).status, 'abstained');
});

test('a refusal flagged as grounded is not presented as a supported answer', async () => {
  mock.method(globalThis, 'fetch', async () => respond({ ...reply, is_fallback: true, intent: 'out_of_scope' }));
  assert.equal((await sendChat('Out of scope')).status, 'abstained');
});

test('validation arrays and malformed successful responses produce readable errors', async () => {
  mock.method(globalThis, 'fetch', async () => respond({ detail: [{ msg: 'String should have at most 1000 characters' }] }, 422));
  const error = await sendChat('Question');
  assert.equal(error.status, 'error');
  if (error.status === 'error') assert.match(error.message, /1000 characters/);
  mock.restoreAll();
  mock.method(globalThis, 'fetch', async () => respond({ unexpected: true }));
  assert.equal((await sendChat('Question')).status, 'error');
});

test('overlong messages never reach the backend', async () => {
  const fetch = mock.method(globalThis, 'fetch', async () => respond(reply));
  assert.equal((await sendChat('x'.repeat(1001))).status, 'error');
  assert.equal(fetch.mock.callCount(), 0);
});

test('explicit cancellation propagates instead of becoming an assistant error', async () => {
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(sendChat('Hello', [], controller.signal), { name: 'AbortError' });
});

test('feedback includes the real question, answer and intent, and reports failures', async () => {
  let payload: unknown;
  mock.method(globalThis, 'fetch', async (_url: string, options: RequestInit) => {
    payload = JSON.parse(options.body as string);
    return respond({ status: 'success' });
  });
  const context = { query: 'Attendance?', answer: '75%', intent: 'attendance_rules' };
  assert.deepEqual(await sendFeedback('trace', 'helpful', context), { trace_id: 'trace', ok: true });
  assert.deepEqual(payload, { ...context, feedback: 'thumbs_up', comments: '' });
  mock.restoreAll();
  mock.method(globalThis, 'fetch', async () => respond({}, 500));
  assert.equal((await sendFeedback('trace', 'helpful', context) as {status: string}).status, 'error');
});

test('backend health reflects index readiness', async () => {
  mock.method(globalThis, 'fetch', async () => respond({ status: 'healthy', indexed_chunks_count: 0 }));
  assert.equal((await getHealth())?.index_ready, false);
});
