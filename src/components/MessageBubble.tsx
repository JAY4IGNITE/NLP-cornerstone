import { useState, useEffect, useRef } from 'react';
import gsap from 'gsap';
import ReactMarkdown from 'react-markdown';
import { AlertCircle, Check, ChevronDown, Copy, FileText, RotateCcw, ThumbsDown, ThumbsUp } from 'lucide-react';
import { ThinkingOrb } from 'thinking-orbs';
import type { FeedbackRating, Message } from '../types/chat';

interface Props {
  message: Message;
  canRetry: boolean;
  onRetry: () => void;
  onFeedback: (id: string, rating: FeedbackRating) => Promise<string | null>;
}

export function MessageBubble({ message, canRetry, onRetry, onFeedback }: Props) {
  const [copied, setCopied] = useState(false);
  const [actionError, setActionError] = useState('');
  const [saving, setSaving] = useState(false);
  const bubbleRef = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!bubbleRef.current || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const animation = gsap.fromTo(bubbleRef.current, { opacity: 0, y: 15, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: 'power2.out' });
    return () => { animation.revert(); };
  }, []);

  if (message.kind === 'user') return <article ref={bubbleRef} className="user-message" aria-label="Your message"><div>{message.text}</div></article>;
  if (message.kind === 'notice') return <div className="message-notice"><p>{message.text}</p>{canRetry && <button className="text-button" onClick={onRetry}><RotateCcw size={14} />Try again</button>}</div>;
  const { result } = message;
  if (result.status === 'error') return <article className="message-error" role="alert"><AlertCircle size={19} /><div><strong>We couldn’t get an answer</strong><p>{result.message}</p>{canRetry && <button className="text-button" onClick={onRetry}><RotateCcw size={14} />Try again</button>}</div></article>;

  const copy = async () => {
    try { await navigator.clipboard.writeText(result.answer); setCopied(true); setActionError(''); }
    catch { setActionError('Copy is unavailable in this browser. You can select and copy the answer.'); }
  };
  const rate = async (rating: FeedbackRating) => {
    if (saving || message.feedback) return;
    setSaving(true);
    setActionError(await onFeedback(message.id, rating) ?? '');
    setSaving(false);
  };

  return <article ref={bubbleRef} className="assistant-message" aria-label="CampusAI answer">
    <div className="assistant-byline"><ThinkingOrb state="breathing" size={20} paused aria-hidden="true" /><strong>CampusAI</strong><span>Academic assistant</span></div>
    {result.status === 'abstained' && <div className="answer-caution"><AlertCircle size={14} />I couldn’t verify a supported answer</div>}
    <div className="markdown"><ReactMarkdown components={{
      h1: ({ children }) => <h2>{children}</h2>,
      h3: ({ children }) => <h2>{children}</h2>,
      a: ({ children, href }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>,
      img: ({ alt }) => <span>{alt}</span>,
    }}>{result.answer}</ReactMarkdown></div>

    {result.citations.length > 0 && <details className="sources">
      <summary><span><FileText size={14} />{result.citations.length} source{result.citations.length === 1 ? '' : 's'}</span><span className="sources-preview">View references<ChevronDown size={14} /></span></summary>
      <div className="source-list">{result.citations.map((citation, index) => <div className="source-reference" key={`${citation.chunk_id ?? citation.document_id}-${index}`}>
        <span className="source-number">{index + 1}</span><div><strong>{citation.title.replace(/_/g, ' ')}</strong><span>{citation.location}</span>{citation.content && <p>{citation.content}</p>}</div>
      </div>)}</div>
    </details>}
    <div className="answer-actions">
      <button className="icon-button" aria-label={copied ? 'Answer copied' : 'Copy answer'} title={copied ? 'Copied' : 'Copy answer'} onClick={copy}>{copied ? <Check size={15} /> : <Copy size={15} />}</button>
      <span className="action-divider" />
      <button className={`icon-button ${message.feedback === 'helpful' ? 'action-selected' : ''}`} disabled={saving || !!message.feedback} aria-label="Helpful answer" aria-pressed={message.feedback === 'helpful'} title="Helpful" onClick={() => void rate('helpful')}><ThumbsUp size={15} /></button>
      <button className={`icon-button ${message.feedback === 'not_helpful' ? 'action-selected' : ''}`} disabled={saving || !!message.feedback} aria-label="Unhelpful answer" aria-pressed={message.feedback === 'not_helpful'} title="Not helpful" onClick={() => void rate('not_helpful')}><ThumbsDown size={15} /></button>
      {canRetry && <button className="icon-button" aria-label="Regenerate answer" title="Regenerate answer" onClick={onRetry}><RotateCcw size={15} /></button>}
      <span className="action-status" role="status">{saving ? 'Saving feedback…' : message.feedback ? 'Thanks for your feedback' : copied ? 'Copied to clipboard' : ''}</span>
    </div>
    {actionError && <p className="inline-error" role="alert">{actionError}</p>}
  </article>;
}
