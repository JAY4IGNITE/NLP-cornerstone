import { useEffect, useRef, useState } from 'react';
import { ArrowDown, ArrowRight, ArrowUp, BookOpen, CalendarCheck, ClipboardList, GraduationCap, Search, ShieldCheck, Square } from 'lucide-react';
import ChatMessage from './ChatMessage';
import BrandMark from '../UI/BrandMark';
import { TOPICS } from '../../lib/topics';

const ICONS = { CalendarCheck, BookOpen, ClipboardList, GraduationCap };

export default function ChatInterface({ messages, isThinking, health, onSend, onRetry, onStop, onGuide }) {
  const [input, setInput] = useState('');
  const [showJump, setShowJump] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);
  const endRef = useRef(null);
  const empty = messages.length === 0;

  useEffect(() => {
    if (!showJump) endRef.current?.scrollIntoView({ behavior: 'instant', block: 'end' });
  }, [messages.length, isThinking, showJump]);
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 176)}px`;
    }
  }, [input]);

  function submit(event) {
    event?.preventDefault();
    if (!input.trim() || isThinking) return;
    onSend(input.trim());
    setInput('');
    setShowJump(false);
    inputRef.current?.focus();
  }

  const composer = <div className="composer-area">
    <form className="composer" onSubmit={submit}>
      <label className="sr-only" htmlFor="question">Your campus question</label>
      <textarea ref={inputRef} id="question" rows={1} maxLength={2000} placeholder="Ask about courses, exams, campus rules…" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => {
        if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); submit(); }
      }} />
      <div className="composer-toolbar"><span className="composer-context"><BookOpen size={15} />Campus knowledge<span className="context-separator">·</span><span>Demo collection</span></span><div className="composer-actions">{input.length > 1800 && <span className="character-count">{input.length}/2000</span>}{isThinking ? <button type="button" className="send-button stop-button" onClick={onStop} aria-label="Stop request" title="Stop request"><Square size={14} fill="currentColor" /></button> : <button type="submit" className="send-button" disabled={!input.trim()} aria-label="Send question" title="Send question"><ArrowUp size={20} /></button>}</div></div>
    </form>
    <p className="composer-caption">{health === 'offline' ? 'The service is unavailable. You can still browse your saved chats.' : <>Ask one complete question at a time. <span className="keyboard-hint">Shift + Enter for a new line.</span></>}</p>
  </div>;

  return <div className={`chat-interface ${empty ? 'is-empty' : 'has-messages'}`}>
    <div className="chat-scroll" ref={scrollRef} onScroll={() => {
      const el = scrollRef.current;
      setShowJump(el.scrollHeight - el.scrollTop - el.clientHeight > 160);
    }}>
      {empty ? <div className="welcome-content">
        <div className="welcome-brand"><BrandMark /></div>
        <div className="welcome-eyebrow">YOUR CAMPUS, CLARIFIED</div>
        <h1>A little less searching.<br /><span>A lot more clarity.</span></h1>
        <p className="welcome-description">From your first lecture to your final exam.<br className="mobile-linebreak" /> Find answers in your campus knowledge base.</p>
        {composer}
        <div className="suggestions-heading"><span>A good place to start</span><button className="text-button" onClick={onGuide}>All topics <ArrowRight size={14} /></button></div>
        <div className="suggestions-grid">{TOPICS.slice(0, 4).map(topic => {
          const Icon = ICONS[topic.icon];
          return <button key={topic.id} className="suggestion-card" onClick={() => { onSend(topic.prompt); setShowJump(false); }}><span className={`suggestion-icon topic-${topic.id}`}><Icon size={19} strokeWidth={1.7} /></span><span className="suggestion-copy"><strong>{topic.title}</strong><span>{topic.prompt}</span></span><ArrowUp size={16} className="suggestion-arrow" /></button>;
        })}</div>
        <div className="welcome-trust"><ShieldCheck size={15} /><span>Grounded in the collection. Sources included when available.</span></div>
      </div> : <div className="message-list" role="log" aria-label="Conversation" aria-live="polite" aria-relevant="additions text">
        {messages.map(message => <ChatMessage key={message.id} message={message} onRetry={() => onRetry(message.id)} isThinking={isThinking} />)}
        {isThinking && <div className="thinking-message" role="status"><div className="assistant-avatar"><BrandMark /></div><div><strong>Looking into it</strong><span><Search size={13} />Matching your question with campus sources<span className="loading-dots" aria-hidden="true"><i /><i /><i /></span></span></div></div>}
        <div ref={endRef} />
      </div>}
    </div>
    {!empty && <div className="chat-dock">{showJump && <button className="jump-button" onClick={() => { setShowJump(false); endRef.current?.scrollIntoView({ behavior: 'instant', block: 'end' }); }}><ArrowDown size={15} />Latest message</button>}{composer}</div>}
    <footer className="chat-footer"><span>CampusNLP uses a synthetic demo collection. Verify important information with your institution.</span><span className="footer-brand">BUILT FOR CAMPUS LIFE</span></footer>
  </div>;
}
