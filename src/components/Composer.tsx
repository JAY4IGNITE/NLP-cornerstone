import { useEffect, useRef } from 'react';
import { ArrowUp, CornerDownLeft, ShieldCheck, Square } from 'lucide-react';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (value: string) => void;
  loading: boolean;
  otherPending: boolean;
  onStop: () => void;
}

export function Composer({ value, onChange, onSubmit, loading, otherPending, onStop }: Props) {
  const input = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    if (input.current) {
      input.current.style.height = 'auto';
      input.current.style.height = `${Math.min(input.current.scrollHeight, 160)}px`;
    }
  }, [value]);
  return <div className="composer-dock">
    <form className="composer" onSubmit={event => { event.preventDefault(); onSubmit(value); }}>
      <label className="sr-only" htmlFor="chat-input">Message CampusAI</label>
      <textarea id="chat-input" ref={input} placeholder="Ask anything about your academics…" value={value} maxLength={1000} rows={1}
        onChange={event => onChange(event.target.value)} aria-describedby="composer-hint" onKeyDown={event => {
          if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing && event.keyCode !== 229) {
            event.preventDefault(); if (!loading && !otherPending) onSubmit(value);
          }
        }} />
      <div className="composer-toolbar"><span className="composer-context"><span className="context-dot" />Campus knowledge<span className="context-divider">/</span><span className="context-secondary">Academic assistant</span></span>
        <div className="composer-send-area">{value.length > 800 ? <span className="character-count">{value.length}/1000</span> : <span className="send-hint"><CornerDownLeft size={12} /> to send</span>}
          {loading ? <button type="button" className="send-button stop-button" onClick={onStop} aria-label="Stop response" title="Stop response"><Square size={15} fill="currentColor" /></button>
            : <button className="send-button" type="submit" disabled={!value.trim() || otherPending} aria-label="Send message" title={otherPending ? 'Wait for the other conversation to finish' : 'Send message'}><ArrowUp size={20} /></button>}
        </div>
      </div>
    </form>
    <p className="composer-disclaimer" id="composer-hint"><ShieldCheck size={13} />{otherPending ? 'Another conversation is answering. You can draft your next question.' : 'Grounded in campus resources. Always double-check important details.'}<span className="sr-only"> Enter to send. Shift and Enter for a new line.</span></p>
  </div>;
}
