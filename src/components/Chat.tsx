import { useEffect, useRef, useState } from 'react';
import { ArrowDown } from 'lucide-react';
import { ThinkingOrb } from 'thinking-orbs';
import type { Conversation, FeedbackRating } from '../types/chat';
import { Composer } from './Composer';
import { MessageBubble } from './MessageBubble';
import { Welcome } from './Welcome';

interface Props {
  conversation: Conversation;
  loading: boolean;
  otherPending: boolean;
  onDraft: (value: string) => void;
  onSubmit: (value: string, retry?: boolean) => void;
  onStop: () => void;
  onFeedback: (id: string, rating: FeedbackRating) => Promise<string | null>;
}

export function Chat({ conversation, loading, otherPending, onDraft, onSubmit, onStop, onFeedback }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [awayFromBottom, setAwayFromBottom] = useState(false);
  const [waiting, setWaiting] = useState(false);
  const lastUser = conversation.messages.findLast(message => message.kind === 'user');
  const lastMessage = conversation.messages.at(-1);
  const retry = () => { if (lastUser?.kind === 'user') onSubmit(lastUser.text, true); };
  const toBottom = () => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  };
  useEffect(() => {
    if (conversation.messages.length && (!awayFromBottom || lastMessage?.kind === 'user')) toBottom();
  }, [conversation.messages.length, loading]);
  useEffect(() => {
    if (!loading) { setWaiting(false); return; }
    const timer = setTimeout(() => setWaiting(true), 15_000);
    return () => clearTimeout(timer);
  }, [loading]);

  return <div className={`chat-surface ${conversation.messages.length ? 'has-messages' : 'is-welcome'}`}>
    {conversation.messages.length > 0 && <h1 className="sr-only">Conversation with CampusAI</h1>}
    <div className="chat-scroll" ref={scrollRef} onScroll={event => {
      const node = event.currentTarget;
      setAwayFromBottom(node.scrollHeight - node.scrollTop - node.clientHeight > 150);
    }}>
      {!conversation.messages.length ? <Welcome onSuggestion={text => onSubmit(text)} disabled={otherPending} /> : <div className="message-list" role="log" aria-label="Conversation" aria-live="polite" aria-relevant="additions text">
        <div className="conversation-start"><span />Your conversation<span /></div>
        {conversation.messages.map((message, index) => <MessageBubble key={message.id} message={message} canRetry={index === conversation.messages.length - 1 && !loading && !otherPending} onRetry={retry} onFeedback={onFeedback} />)}
        {loading && <div className="thinking" role="status"><ThinkingOrb state="working" size={32} aria-hidden="true" /><div><strong>Thinking it through</strong><span>{waiting ? 'Still working on your answer. You can stop at any time.' : 'Finding context in your campus resources…'}</span></div></div>}
      </div>}
    </div>
    {awayFromBottom && conversation.messages.length > 0 && <button className="jump-bottom icon-button" onClick={toBottom} aria-label="Jump to latest message" title="Jump to latest"><ArrowDown size={18} /></button>}
    <Composer value={conversation.draft} onChange={onDraft} onSubmit={text => onSubmit(text)} loading={loading} otherPending={otherPending} onStop={onStop} />
  </div>;
}
