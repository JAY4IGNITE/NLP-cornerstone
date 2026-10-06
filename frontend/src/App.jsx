import { useEffect, useRef, useState } from 'react';
import { BookOpen, Download, Menu, Moon, Sun, ArrowLeft } from 'lucide-react';
import Navigation from './components/UI/Navigation';
import ChatInterface from './components/Chat/ChatInterface';
import KnowledgeGuide from './components/KnowledgeGuide';
import ConversationDialog from './components/UI/ConversationDialog';
import useWorkspace from './hooks/useWorkspace';
import { conversationToMarkdown } from './lib/workspace';
import './App.css';

function readTheme() {
  try { return localStorage.getItem('campusnlp.theme') === 'dark' ? 'dark' : 'light'; }
  catch { return 'light'; }
}

export default function App() {
  const workspace = useWorkspace();
  const [view, setView] = useState('chat');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState(readTheme);
  const [dialog, setDialog] = useState(null);
  const menuRef = useRef(null);
  const sidebarRef = useRef(null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('campusnlp.theme', theme); } catch { /* Theme remains available for this visit. */ }
  }, [theme]);

  useEffect(() => {
    if (!sidebarOpen) return;
    const sidebar = sidebarRef.current;
    sidebar?.querySelector('button')?.focus();
    const onKeyDown = (event) => {
      if (event.key === 'Escape') { setSidebarOpen(false); menuRef.current?.focus(); }
      if (event.key !== 'Tab') return;
      const items = [...sidebar.querySelectorAll('button, input')].filter(el => !el.disabled && el.getClientRects().length);
      const first = items[0], last = items.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [sidebarOpen]);

  function navigate(nextView) { setView(nextView); setSidebarOpen(false); }
  function newChat() { workspace.newChat(); navigate('chat'); }
  function askTopic(prompt) { navigate('chat'); workspace.sendMessage(prompt); }
  function exportChat() {
    const text = conversationToMarkdown(workspace.activeConversation);
    const url = URL.createObjectURL(new Blob([text], { type: 'text/markdown;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `${workspace.activeConversation.title.replace(/[^a-z0-9 -]/gi, '').slice(0, 60) || 'campus-chat'}.md`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return (
    <div className={`app-shell ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <a className="skip-link" href="#main-content">Skip to content</a>
      {sidebarOpen && <div className="sidebar-scrim" onClick={() => { setSidebarOpen(false); menuRef.current?.focus(); }} aria-hidden="true" />}
      <Navigation ref={sidebarRef} open={sidebarOpen} collapsed={sidebarCollapsed} view={view}
        conversations={workspace.conversations} activeId={workspace.activeId}
        onNew={newChat} onView={navigate} onSelect={id => { workspace.selectChat(id); navigate('chat'); }}
        onRename={chat => setDialog({ type: 'rename', chat })} onDelete={chat => setDialog({ type: 'delete', chat })}
        onCollapse={() => setSidebarCollapsed(value => !value)} onClose={() => { setSidebarOpen(false); menuRef.current?.focus(); }} />
      <div className="workspace" inert={sidebarOpen ? true : undefined}>
        <header className="workspace-header">
          <div className="header-title">
            <button ref={menuRef} className="icon-button mobile-menu" aria-label="Open sidebar" aria-expanded={sidebarOpen} onClick={() => setSidebarOpen(true)}><Menu size={20} /></button>
            {sidebarCollapsed && <button className="icon-button desktop-expand" aria-label="Expand sidebar" onClick={() => setSidebarCollapsed(false)}><Menu size={20} /></button>}
            <span>Campus assistant</span><span className="header-divider">/</span><span className="header-subtitle">{view === 'guide' ? 'Topic guide' : 'Workspace'}</span>
          </div>
          <div className="header-actions">
            <button className={`connection-status ${workspace.health}`} onClick={workspace.checkHealth} title="Check connection to the CampusNLP service" aria-label={`Service ${workspace.health}. Check connection`}><span className="status-dot" />{workspace.health === 'online' ? 'Connected' : workspace.health === 'checking' ? 'Connecting' : 'Service offline'}</button>
            <span className="header-action-divider" />
            <button className="icon-button" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`} title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}>{theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}</button>
          </div>
        </header>
        <main id="main-content" className={`main-content ${view === 'guide' ? 'guide-main' : ''}`} tabIndex={-1}>
          {workspace.storageError && <div className="storage-notice" role="status">{workspace.storageError}</div>}
          {view === 'guide' ? <KnowledgeGuide onAsk={askTopic} /> : <>
            {workspace.messages.length > 0 && <div className="conversation-heading"><h1>{workspace.activeConversation?.title || 'New conversation'}</h1><button className="text-button" onClick={exportChat} title="Download this conversation as Markdown"><Download size={15} /><span>Export chat</span></button></div>}
            <ChatInterface key={workspace.activeId || 'new'} messages={workspace.messages} isThinking={workspace.isThinking} health={workspace.health} onSend={workspace.sendMessage} onRetry={workspace.retryMessage} onStop={workspace.stopRequest} onGuide={() => navigate('guide')} />
          </>}
        </main>
        {view === 'guide' && <footer className="guide-footer"><BookOpen size={14} /> A little clarity goes a long way.<button className="text-button" onClick={() => navigate('chat')}><ArrowLeft size={14} />Back to chat</button></footer>}
      </div>
      <ConversationDialog dialog={dialog} onClose={() => setDialog(null)} onRename={workspace.renameChat} onDelete={workspace.deleteChat} />
    </div>
  );
}
