import { useState } from 'react';
import { AlertCircle, Check, ChevronDown, Copy, FileText, RotateCcw } from 'lucide-react';
import BrandMark from '../UI/BrandMark';

export default function ChatMessage({ message, onRetry, isThinking }) {
  const [copyStatus, setCopyStatus] = useState('');
  const isUser = message.role === 'user';
  const sources = message.sources || [];
  // The engine includes this provenance prefix in its response. The same
  // document and classification are rendered in dedicated metadata below.
  const prefix = sources.length && message.intent ? `Based on ${sources[0].document} (${message.intent}): ` : '';
  const answer = prefix && message.text.startsWith(prefix) ? message.text.slice(prefix.length) : message.text;
  const topic = message.intent?.replace(/_/g, ' ');

  async function copyAnswer() {
    try {
      await navigator.clipboard.writeText(message.text);
      setCopyStatus('Copied');
    } catch { setCopyStatus('Could not copy. Select the answer text to copy it.'); }
  }

  if (isUser) return <article className="user-message" aria-label="Your question"><p>{message.text}</p></article>;
  return <article className={`assistant-message ${message.error ? 'is-error' : ''}`} aria-label={message.error ? 'Request error' : 'CampusNLP answer'}>
    <div className="assistant-avatar">{message.error ? <AlertCircle size={19} /> : <BrandMark />}</div>
    <div className="assistant-content">
      <div className="message-byline"><strong>CampusNLP</strong><span>{message.error ? 'Request interrupted' : 'Campus assistant'}</span></div>
      <div className="answer-text">{answer.split(/\n\n+/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}</div>

      {!message.error && message.intent && <details className="answer-details"><summary><ChevronDown size={14} />How this was matched</summary><div className="match-details"><dl><div><dt>Detected topic</dt><dd>{topic}</dd></div>{Number.isFinite(message.confidence) && <div><dt>Intent confidence</dt><dd>{Math.round(message.confidence * 100)}%</dd></div>}</dl><p>Confidence describes the topic match, not the accuracy of the answer. Each question is processed independently.</p>{sources.length === 0 && <p>No supporting source was returned for this response.</p>}</div></details>}
      <div className="message-actions">{message.error ? <button className="text-button" disabled={isThinking} onClick={onRetry}><RotateCcw size={14} />Try again</button> : <button className="icon-button" onClick={copyAnswer} title="Copy answer" aria-label="Copy answer">{copyStatus === 'Copied' ? <Check size={15} /> : <Copy size={15} />}</button>}<span className="copy-status" role="status">{copyStatus}</span></div>
    </div>
  </article>;
}
