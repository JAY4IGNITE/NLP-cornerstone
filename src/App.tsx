import { useEffect, useRef, useState } from 'react';
import { AlertCircle, ArrowUpRight, Check, ChevronRight, Moon, PanelLeftOpen, RefreshCw, ShieldCheck, Sun, Trash2 } from 'lucide-react';
import { Chat } from './components/Chat';
import { Sidebar } from './components/Sidebar';
import { Dialog } from './components/Dialog';
import { useConversations } from './hooks/useConversations';
import { getHealth } from './lib/api';
import type { Conversation, HealthResponse } from './types/chat';

type Modal = 'help' | 'settings' | Conversation | null;
function initialTheme(): 'light' | 'dark' {
  try { return localStorage.getItem('campusai.theme') === 'dark' ? 'dark' : 'light'; } catch { return 'light'; }
}

export function App() {
  const chats = useConversations();
  const [sidebarOpen, setSidebarOpen] = useState(() => window.innerWidth >= 900);
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < 900);
  const [modal, setModal] = useState<Modal>(null);
  const [theme, setTheme] = useState(initialTheme);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [checking, setChecking] = useState(true);
  const [checked, setChecked] = useState(false);
  const sidebar = useRef<HTMLElement>(null);
  const opener = useRef<HTMLButtonElement>(null);
  const toggleTheme = () => setTheme(value => value === 'light' ? 'dark' : 'light');

  useEffect(() => {
    const query = window.matchMedia('(max-width: 899px)');
    const change = () => { setIsMobile(query.matches); setSidebarOpen(!query.matches); };
    query.addEventListener('change', change);
    return () => query.removeEventListener('change', change);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('campusai.theme', theme); } catch { /* Theme still works for the current session. */ }
  }, [theme]);

  useEffect(() => {
    let mounted = true;
    const check = async () => {
      const result = await getHealth();
      if (mounted) { setHealth(result); setChecking(false); setChecked(true); }
    };
    void check();
    const timer = setInterval(() => { if (!document.hidden) void check(); }, 60_000);
    window.addEventListener('online', check);
    return () => { mounted = false; clearInterval(timer); window.removeEventListener('online', check); };
  }, []);

  useEffect(() => {
    if (!sidebarOpen || !isMobile) return;
    const panel = sidebar.current;
    panel?.querySelector<HTMLButtonElement>('button')?.focus();
    const keydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setSidebarOpen(false); opener.current?.focus(); }
      if (event.key !== 'Tab') return;
      const items = panel?.querySelectorAll<HTMLElement>('button:not(:disabled), input');
      if (!items?.length) return;
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    panel?.addEventListener('keydown', keydown);
    return () => panel?.removeEventListener('keydown', keydown);
  }, [sidebarOpen, isMobile]);

  const closeSidebar = () => { setSidebarOpen(false); requestAnimationFrame(() => opener.current?.focus()); };
  const closeOnMobile = () => { if (window.innerWidth < 900) closeSidebar(); };
  const retryHealth = async () => { setChecking(true); setHealth(await getHealth()); setChecked(true); setChecking(false); };
  const available = health?.status === 'ok' && health.index_ready;

  return <div className={`app-shell ${sidebarOpen ? 'sidebar-open' : ''}`} data-theme={theme}>
    <a className="skip-link" href="#chat-input">Skip to message</a>
    {sidebarOpen && <button className="sidebar-backdrop" aria-label="Close navigation" onClick={closeSidebar} tabIndex={-1} />}
    <aside id="chat-sidebar" ref={sidebar} className="sidebar" aria-label="Chat sidebar" role={isMobile && sidebarOpen ? 'dialog' : undefined} aria-modal={isMobile && sidebarOpen ? true : undefined} inert={!sidebarOpen}>
      <Sidebar conversations={chats.conversations} activeId={chats.active.id} pendingId={chats.pendingId}
        onNew={() => { chats.create(); closeOnMobile(); requestAnimationFrame(() => document.getElementById('chat-input')?.focus()); }} onSelect={id => { chats.select(id); closeOnMobile(); }}
        onManage={chat => setModal(chat)} onClose={closeSidebar} onHelp={() => setModal('help')} onSettings={() => setModal('settings')} />
    </aside>
    <main className="main-panel" inert={isMobile && sidebarOpen}>
      <header className="topbar">
        <div className="topbar-leading"><button ref={opener} className="icon-button sidebar-opener" aria-label="Open sidebar" aria-expanded={sidebarOpen} aria-controls="chat-sidebar" onClick={() => setSidebarOpen(true)}><PanelLeftOpen size={19} /></button>
          <span className="topbar-workspace">Your workspace</span><ChevronRight size={13} className="breadcrumb-arrow" /><span className="topbar-title">{chats.active.messages.length ? chats.active.title : 'New conversation'}</span>
        </div>
        <div className="topbar-actions"><span className="academic-badge"><ShieldCheck size={14} />Academic assistant</span><button className="icon-button" onClick={toggleTheme} aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`} title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>{theme === 'light' ? <Moon size={17} /> : <Sun size={17} />}</button></div>
      </header>
      {chats.storageError && <div className="connection-banner" role="alert"><AlertCircle size={15} /><span>{chats.storageError}</span></div>}
      {checked && !available && <div className="connection-banner" role="status"><AlertCircle size={15} /><span>{health ? 'Some campus resources are unavailable. Answers may be limited.' : 'The assistant is offline. Your saved conversations are still here.'}</span><button className="text-button" disabled={checking} onClick={() => void retryHealth()}><RefreshCw size={13} />{checking ? 'Checking…' : 'Reconnect'}</button></div>}
      <Chat key={chats.active.id} conversation={chats.active} loading={chats.pendingId === chats.active.id} otherPending={!!chats.pendingId && chats.pendingId !== chats.active.id}
        onDraft={chats.setDraft} onSubmit={chats.submit} onStop={chats.stop} onFeedback={chats.feedback} />
    </main>
    {modal && <Dialog title={modal === 'help' ? 'A guide to your campus companion' : modal === 'settings' ? 'Make yourself at home' : 'Manage conversation'} onClose={() => setModal(null)}>
      {modal === 'help' ? <div className="help-content"><p>CampusAI helps you find information in your university’s academic resources. Start with a course, a semester, or a specific question.</p><ul><li><strong>Courses & syllabi</strong><span>Topics, units, credits, and prerequisites.</span></li><li><strong>Academic guidelines</strong><span>Attendance, exams, grading, and regulations.</span></li><li><strong>Semester planning</strong><span>Subjects, course structure, and electives.</span></li></ul><div className="dialog-note"><ShieldCheck size={18} /><p>Expand the sources below an answer to see its references. If the resources don’t support an answer, CampusAI will tell you.</p></div><p className="muted">Include the course name or code in follow-up questions for the most relevant results.</p><button className="primary-button" onClick={() => { setModal(null); document.getElementById('chat-input')?.focus(); }}>Let’s start a conversation<ArrowUpRight size={16} /></button></div>
      : modal === 'settings' ? <div className="settings-content"><div className="settings-row"><div><strong>Appearance</strong><p>A comfortable space to think.</p></div><button className="secondary-button" onClick={toggleTheme}>{theme === 'light' ? <Sun size={16} /> : <Moon size={16} />}{theme === 'light' ? 'Light' : 'Dark'}</button></div><div className="settings-row"><div><strong>Assistant connection</strong><p>{checking ? 'Checking connection…' : available ? 'Connected to campus resources' : health ? 'Connected with limited resources' : 'Currently offline'}</p></div><button className="icon-button" disabled={checking} onClick={() => void retryHealth()} aria-label="Check connection"><RefreshCw size={17} /></button></div><div className="dialog-note"><ShieldCheck size={18} /><p>Conversation history is saved in this browser. Questions are sent to the configured academic backend to generate answers. Clearing browser data removes local history.</p></div><p className="muted">Thinking Orbs by <a href="https://github.com/Jakubantalik/thinking-orbs" target="_blank" rel="noopener noreferrer">Jakub Antalik</a>.</p></div>
      : <ManageConversation conversation={modal} onRename={title => { chats.rename(modal.id, title); setModal(null); }} onDelete={() => { chats.remove(modal.id); setModal(null); }} />}
    </Dialog>}
  </div>;
}

function ManageConversation({ conversation, onRename, onDelete }: { conversation: Conversation; onRename: (title: string) => void; onDelete: () => void }) {
  const [title, setTitle] = useState(conversation.title);
  const [confirmDelete, setConfirmDelete] = useState(false);
  return <form onSubmit={event => { event.preventDefault(); onRename(title); }}><label className="field-label" htmlFor="conversation-title">Conversation name</label><input className="dialog-input" id="conversation-title" value={title} maxLength={80} onChange={event => setTitle(event.target.value)} /><button className="primary-button save-title" disabled={!title.trim()}><Check size={16} />Save name</button><div className="delete-area"><p>{confirmDelete ? 'This removes the conversation from this browser. This cannot be undone.' : 'Remove this conversation and its messages from this browser.'}</p><button className="danger-button" type="button" onClick={() => confirmDelete ? onDelete() : setConfirmDelete(true)}><Trash2 size={15} />{confirmDelete ? 'Delete permanently' : 'Delete conversation'}</button>{confirmDelete && <button className="text-button" type="button" onClick={() => setConfirmDelete(false)}>Keep conversation</button>}</div></form>;
}
