import { useState } from 'react';
import { BookOpen, ChevronLeft, GraduationCap, MessageSquare, PanelLeftClose, Pencil, Search, SquarePen, Trash2, X } from 'lucide-react';
import BrandMark from './BrandMark';
import { filterConversations } from '../../lib/workspace';

export default function Navigation({ ref, open, collapsed, view, conversations, activeId, onNew, onView, onSelect, onRename, onDelete, onCollapse, onClose }) {
  const [search, setSearch] = useState('');
  const filtered = filterConversations(conversations, search);
  return <aside ref={ref} className={`sidebar ${open ? 'is-open' : ''} ${collapsed ? 'is-collapsed' : ''}`} aria-label="Sidebar">
    <div className="sidebar-brand"><button className="brand-home" onClick={onNew} aria-label="CampusNLP, start a new chat"><BrandMark /><span>Campus<span className="brand-light">NLP</span></span></button><button className="icon-button sidebar-collapse" title="Collapse sidebar" aria-label="Collapse sidebar" onClick={onCollapse}><PanelLeftClose size={18} /></button><button className="icon-button sidebar-close" aria-label="Close sidebar" onClick={onClose}><X size={20} /></button></div>
    <div className="workspace-label"><span className="workspace-dot" />STUDENT WORKSPACE</div>
    <nav className="sidebar-nav" aria-label="Main navigation">
      <button className="new-chat-button" onClick={() => { setSearch(''); onNew(); }}><SquarePen size={18} /><span>New chat</span><span className="new-chat-plus">+</span></button>
      <label className="search-field"><Search size={17} /><input type="search" placeholder="Search conversations" aria-label="Search conversations" value={search} onChange={e => setSearch(e.target.value)} />{search && <button className="search-clear" aria-label="Clear search" onClick={() => setSearch('')}><X size={14} /></button>}</label>
    </nav>
    <div className="history-section">
      <div className="section-label">{search ? 'SEARCH RESULTS' : 'YOUR CONVERSATIONS'}<span>{filtered.length > 0 ? filtered.length : ''}</span></div>
      <div className="history-list">
        {filtered.length === 0 ? <div className="history-empty"><MessageSquare size={22} strokeWidth={1.5} /><p>{search ? 'No conversations found' : 'A fresh start.'}</p><span>{search ? 'Try a different word or phrase.' : 'Your conversations will appear here.'}</span></div> : filtered.map(chat => <div className={`history-item ${view === 'chat' && chat.id === activeId ? 'is-active' : ''}`} key={chat.id}>
          <button className="history-select" onClick={() => onSelect(chat.id)} aria-current={view === 'chat' && chat.id === activeId ? 'page' : undefined} title={chat.title}><MessageSquare size={15} /><span>{chat.title}</span></button>
          <div className="history-actions"><button className="icon-button" aria-label={`Rename ${chat.title}`} title="Rename chat" onClick={() => onRename(chat)}><Pencil size={13} /></button><button className="icon-button" aria-label={`Delete ${chat.title}`} title="Delete chat" onClick={() => onDelete(chat)}><Trash2 size={13} /></button></div>
        </div>)}
      </div>
    </div>
    <div className="sidebar-bottom">
      <div className="sidebar-note"><div className="sidebar-note-heading"><BookOpen size={16} /><span>Answers with a source.</span></div><p>Explore the academic topics in our demo knowledge collection.</p><button className="text-button" onClick={() => onView('guide')}>Explore the guide <ChevronLeft className="arrow-forward" size={14} /></button></div>
      <div className="local-profile"><div className="profile-icon"><GraduationCap size={20} /></div><div><strong>Your personal workspace</strong><span>Chats saved in this browser</span></div><span className="local-indicator" title="Local browser storage" /></div>
    </div>
  </aside>;
}
