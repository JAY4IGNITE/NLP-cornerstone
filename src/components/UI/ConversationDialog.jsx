import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

export default function ConversationDialog({ dialog, onClose, onRename, onDelete }) {
  const ref = useRef(null);
  const [title, setTitle] = useState(dialog.chat.title);
  useEffect(() => {
    const modal = ref.current;
    modal.showModal();
    return () => modal.close();
  }, []);
  return <dialog ref={ref} className="conversation-dialog" onCancel={onClose} onClick={e => { if (e.target === ref.current) onClose(); }} aria-labelledby="dialog-title">
    {dialog && <form onSubmit={e => { e.preventDefault(); if (dialog.type === 'rename') onRename(dialog.chat.id, title.trim()); else onDelete(dialog.chat.id); onClose(); }}>
      <div className="dialog-heading"><h2 id="dialog-title">{dialog.type === 'rename' ? 'Rename conversation' : 'Delete conversation?'}</h2><button type="button" className="icon-button" aria-label="Close dialog" onClick={onClose}><X size={18} /></button></div>
      {dialog.type === 'rename' ? <label className="dialog-label">Conversation name<input autoFocus maxLength={100} required value={title} onChange={e => setTitle(e.target.value)} /></label> : <p>“{dialog.chat.title}” will be removed from this browser. This cannot be undone.</p>}
      <div className="dialog-actions"><button autoFocus={dialog.type === 'delete'} type="button" className="secondary-button" onClick={onClose}>Cancel</button><button className={dialog.type === 'delete' ? 'danger-button' : 'primary-button'} disabled={dialog.type === 'rename' && !title.trim()}>{dialog.type === 'rename' ? 'Save name' : 'Delete chat'}</button></div>
    </form>}
  </dialog>;
}
