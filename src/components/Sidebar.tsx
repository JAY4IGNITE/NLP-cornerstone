import { useMemo, useRef, useEffect, useState } from 'react';
import { ArrowUpRight, BookOpen, MessageSquare, MoreHorizontal, PanelLeftClose, Plus, Search, Settings2, X } from 'lucide-react';
import { matchesConversation } from '../lib/conversations';
import type { Conversation } from '../types/chat';

interface Props {
  conversations: Conversation[];
  activeId: string;
  pendingId: string | null;
  onNew: () => void;
  onSelect: (id: string) => void;
  onManage: (chat: Conversation) => void;
  onClose: () => void;
  onHelp: () => void;
  onSettings: () => void;
}

export function Sidebar({ conversations, activeId, pendingId, onNew, onSelect, onManage, onClose, onHelp, onSettings }: Props) {
  const [search, setSearch] = useState('');
  const searchRef = useRef<HTMLInputElement>(null);
  const saved = useMemo(() => conversations.filter(chat => chat.messages.length || chat.draft).sort((a, b) => b.updatedAt - a.updatedAt), [conversations]);
  const filtered = saved.filter(chat => matchesConversation(chat, search));
  useEffect(() => {
    const focusSearch = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault(); searchRef.current?.focus();
      }
    };
    window.addEventListener('keydown', focusSearch);
    return () => window.removeEventListener('keydown', focusSearch);
  }, []);

  return <>
    <div className="sidebar-brand">
      <div className="brand"><span className="brand-mark" aria-hidden="true"><i /><i /><i /><i /></span><span>Campus<span className="brand-ai">AI</span></span></div>
      <button className="icon-button" onClick={onClose} aria-label="Close sidebar" title="Close sidebar"><PanelLeftClose size={18} /></button>
    </div>
    <button className="new-chat-button" onClick={() => { setSearch(''); onNew(); }}><Plus size={18} />New conversation<ArrowUpRight size={15} /></button>
    <div className="chat-search"><Search size={16} /><input ref={searchRef} value={search} onChange={event => setSearch(event.target.value)} aria-label="Search conversations" placeholder="Search conversations" />{search ? <button className="icon-button" onClick={() => setSearch('')} aria-label="Clear search"><X size={14} /></button> : <kbd title="Ctrl or Command K">⌘ K</kbd>}</div>
    <div className="history-heading"><span>Your conversations</span><span>{saved.length.toString().padStart(2, '0')}</span></div>
    <nav className="conversation-list" aria-label="Conversations">
      {!filtered.length ? <div className="history-empty"><MessageSquare size={23} strokeWidth={1.3} /><p>{search ? 'No conversations found' : 'A fresh start awaits'}</p><span>{search ? 'Try a different word or phrase.' : 'Your conversations will find a home here.'}</span></div> : filtered.map(chat => <div key={chat.id} className={`conversation-row ${chat.id === activeId ? 'selected' : ''}`}>
        <button className="conversation-select" onClick={() => onSelect(chat.id)} aria-current={chat.id === activeId ? 'page' : undefined} title={chat.title}>
          <MessageSquare size={16} /><span>{chat.title}</span>{pendingId === chat.id && <span className="pending-dot" aria-label="Answering" />}
        </button>
        <button className="conversation-menu icon-button" onClick={() => onManage(chat)} aria-label={`Manage ${chat.title}`} title="Rename or delete"><MoreHorizontal size={17} /></button>
      </div>)}
    </nav>
    <div className="sidebar-bottom">
      <div className="sidebar-note"><span className="note-star" aria-hidden="true">✳</span><p>A little help.<br /><strong>Ahead of every class.</strong></p></div>
      <button className="sidebar-link" onClick={onHelp}><BookOpen size={17} />What can I ask?<ArrowUpRight size={14} /></button>
      <button className="sidebar-link" onClick={onSettings}><Settings2 size={17} />Preferences</button>

    </div>
  </>;
}
