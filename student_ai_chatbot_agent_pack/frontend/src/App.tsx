import { useEffect, useState } from "react";
import { Chat } from "./components/Chat";
import { getHealth } from "./lib/api";
import type { HealthResponse } from "./types/chat";
import { motion } from "framer-motion";
import { ServerCrash, Activity, MessageSquare, BarChart2, Info, FileText, Plus, Hexagon, Search, Folder, Compass, Settings, ChevronDown } from "lucide-react";
import Dock from './components/Dock';
import './components/CardNav.css';

type StatusTone = "unknown" | "offline" | "ok" | "degraded";
type Tab = "chat" | "analytics" | "info";

function statusInfo(health: HealthResponse | null, checked: boolean) {
  if (!checked) return { tone: "unknown", label: "Connecting...", icon: <Activity className="w-4 h-4 animate-pulse" /> };
  if (!health) return { tone: "offline", label: "System Offline", icon: <ServerCrash className="w-4 h-4 text-white" /> };
  const ready = health.index_ready;
  const tone: StatusTone = health.status === "ok" && ready ? "ok" : "degraded";
  return {
    tone,
    label: `${health.provider} · ${ready ? "Online" : "Syncing"}`,
    icon: <div className={`w-2 h-2 rounded-full ${tone === 'ok' ? 'bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]' : 'bg-gray-400'}`} />
  };
}

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [checked, setChecked] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    let active = true;
    void getHealth().then((result) => {
      if (active) {
        setHealth(result);
        setChecked(true);
      }
    });
    return () => {
      active = false;
    };
  }, []);

  const status = statusInfo(health, checked);


  const items = [
    { icon: <MessageSquare size={18} strokeWidth={1.5} />, label: 'Chatbot', onClick: () => setActiveTab("chat") },
    { icon: <BarChart2 size={18} strokeWidth={1.5} />, label: 'Analytics', onClick: () => setActiveTab("analytics") },
    { icon: <Info size={18} strokeWidth={1.5} />, label: 'Project Info', onClick: () => setActiveTab("info") },
  ];


  return (
    <div className="h-screen w-full bg-[#212121] text-gray-300 font-sans flex overflow-hidden">
      
      {/* Left Sidebar (ChatGPT style) */}
      <motion.aside 
        initial={false}
        animate={{ width: isSidebarOpen ? 260 : 0, opacity: isSidebarOpen ? 1 : 0 }}
        className="flex-shrink-0 bg-[#171717] flex flex-col border-r border-white/5 overflow-hidden"
      >
        <div className="p-3 flex flex-col h-full w-[260px]">
          <div className="flex items-center justify-between mb-6 px-1">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-white/20 to-white/5 border border-white/10 flex items-center justify-center shadow-lg backdrop-blur-md">
                <Hexagon className="w-4 h-4 text-white" strokeWidth={2} />
              </div>
              <span className="font-semibold text-white tracking-wide text-[15px]">
                Campus<span className="text-gray-400 font-medium ml-[2px]">AI</span>
              </span>
            </div>
            <button onClick={() => setIsSidebarOpen(false)} className="p-1 hover:bg-white/5 rounded-lg transition-colors flex items-center justify-center w-8 h-8 group overflow-hidden">
              <div className="hamburger-menu open scale-[0.45] transition-transform duration-300 group-hover:scale-50">
                <div className="hamburger-line bg-white/60 group-hover:bg-white/90 transition-colors" />
                <div className="hamburger-line bg-white/60 group-hover:bg-white/90 transition-colors" />
              </div>
            </button>
          </div>
          
          {/* Top Actions */}
          <div className="flex flex-col gap-2 mb-4">
            <button className="flex items-center justify-center gap-2 bg-white text-black hover:bg-gray-200 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors shadow-sm">
              <Plus className="w-4 h-4" strokeWidth={2} />
              New chat
            </button>
            <div className="relative group">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 group-focus-within:text-white transition-colors" strokeWidth={1.5} />
              <input 
                type="text" 
                placeholder="Search chats..." 
                className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-white/20 focus:bg-white/10 transition-all"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-5 pr-1">
            {/* Core Navigation */}
            <div className="space-y-0.5">
              <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                <Compass className="w-4 h-4 text-gray-400" strokeWidth={1.5} />
                Discover
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                <Folder className="w-4 h-4 text-gray-400" strokeWidth={1.5} />
                Workspaces
              </button>
            </div>

            {/* Recent History */}
            <div>
              <div className="text-[11px] font-semibold text-gray-500 px-3 py-1.5 uppercase tracking-wider">Recent</div>
              <div className="space-y-0.5">
                <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors group">
                  <MessageSquare className="w-4 h-4 text-gray-500 group-hover:text-gray-300 transition-colors" strokeWidth={1.5} />
                  <span className="truncate">Data structures overview</span>
                </button>
                <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors group">
                  <MessageSquare className="w-4 h-4 text-gray-500 group-hover:text-gray-300 transition-colors" strokeWidth={1.5} />
                  <span className="truncate">React state management</span>
                </button>
              </div>
            </div>
          </div>
          
          <div className="mt-auto pt-3 border-t border-white/5 flex flex-col gap-1">
            <button className="flex items-center px-3 py-2 hover:bg-white/5 rounded-lg text-sm text-gray-300 hover:text-white transition-colors">
              <div className="flex items-center gap-3">
                <Settings className="w-4 h-4 text-gray-400" strokeWidth={1.5} />
                Settings
              </div>
            </button>
            <div className="flex items-center justify-between px-3 py-2 hover:bg-white/5 rounded-lg cursor-pointer transition-colors group">
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-blue-600 to-violet-600 flex items-center justify-center text-white font-medium text-xs shadow-sm ring-1 ring-white/10">
                  U
                </div>
                <span className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">User Account</span>
              </div>
              <ChevronDown className="w-4 h-4 text-gray-500 group-hover:text-gray-300 transition-colors" strokeWidth={1.5} />
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#212121]">
        
        {/* Header Area */}
        <header className="w-full flex items-center justify-between px-4 py-3 z-50">
          <div className="flex items-center gap-3 w-48">
            {!isSidebarOpen && (
              <div 
                onClick={() => setIsSidebarOpen(true)} 
                className="relative flex items-center justify-center w-8 h-8 rounded-lg hover:bg-white/5 cursor-pointer group transition-colors overflow-hidden ml-1"
              >
                {/* Logo - visible by default, fades out on hover */}
                <div className="absolute inset-0 flex items-center justify-center transition-all duration-300 group-hover:opacity-0 group-hover:scale-75">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-white/20 to-white/5 border border-white/10 flex items-center justify-center shadow-lg backdrop-blur-md">
                    <Hexagon className="w-3.5 h-3.5 text-white" strokeWidth={2} />
                  </div>
                </div>
                
                {/* Toggle - invisible by default, fades in on hover */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 scale-75 transition-all duration-300 group-hover:opacity-100 group-hover:scale-100">
                  <div className="hamburger-menu scale-[0.45]">
                    <div className="hamburger-line bg-white/80" />
                    <div className="hamburger-line bg-white/80" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Center Dock */}
          <div className="flex-1 flex justify-center relative h-[42px]">
            <div className="absolute inset-0 flex justify-center items-center z-50">
              <Dock 
                items={items}
                panelHeight={42}
                baseItemSize={30}
                magnification={42}
                dockHeight={42}
                spring={{ mass: 0.2, stiffness: 120, damping: 14 }}
              />
            </div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-2 text-xs font-medium text-gray-400 w-48 justify-end relative z-50">
            {status.icon}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 w-full max-w-4xl mx-auto px-4 pb-4 relative z-10 flex flex-col min-h-0 overflow-hidden">
        {activeTab === "chat" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 flex flex-col min-h-0 overflow-hidden">
            <Chat />
          </motion.div>
        )}

        {activeTab === "analytics" && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex-1 overflow-y-auto pb-20">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Usage Analytics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl text-center">
                <div className="text-gray-400 text-sm mb-2 uppercase tracking-widest">Total Queries</div>
                <div className="text-5xl font-bold text-white">12,458</div>
              </div>
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl text-center">
                <div className="text-gray-400 text-sm mb-2 uppercase tracking-widest">Avg. Latency</div>
                <div className="text-5xl font-bold text-white">1.2s</div>
              </div>
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl text-center">
                <div className="text-gray-400 text-sm mb-2 uppercase tracking-widest">Feedback Score</div>
                <div className="text-5xl font-bold text-white">4.8/5</div>
              </div>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-8 rounded-3xl max-w-3xl mx-auto">
              <h3 className="text-white font-bold mb-6 text-xl text-center">Top Intents</h3>
              <ul className="space-y-6">
                {['course_subject_info', 'student_services', 'academic_calendar', 'exam_schedule', 'office_contact_info'].map((intent, idx) => (
                  <li key={intent} className="flex items-center justify-between">
                    <span className="font-mono text-sm text-gray-300 w-1/3">{intent}</span>
                    <div className="flex-1 mx-4 h-3 bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full bg-white rounded-full" style={{ width: `${80 - (idx * 15)}%` }} />
                    </div>
                    <span className="text-sm text-white font-bold w-12 text-right">{80 - (idx * 15)}%</span>
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}

        {activeTab === "info" && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex-1 overflow-y-auto pb-20 flex flex-col items-center">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Project Information</h2>
            <div className="w-full max-w-3xl space-y-8">
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5" /> Architecture
                </h3>
                <p className="text-gray-400 leading-relaxed mb-6">
                  This system is a Retrieval-Augmented Generation (RAG) chatbot designed specifically for campus intelligence. It combines a highly optimized Logistic Regression intent classifier with a BM25 & Sentence-Transformer hybrid vector store.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-sm bg-black/20 p-6 rounded-2xl border border-white/5">
                  <div className="flex flex-col gap-1">
                    <span className="text-gray-500 uppercase tracking-wider text-xs font-bold">LLM Provider</span>
                    <span className="text-white text-base">{health?.provider || "N/A"}</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-gray-500 uppercase tracking-wider text-xs font-bold">Vector Store</span>
                    <span className="text-white text-base">Local FAISS / NumPy</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-gray-500 uppercase tracking-wider text-xs font-bold">Knowledge Base</span>
                    <span className="text-white text-base">{health?.knowledge_base_version || "N/A"}</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-gray-500 uppercase tracking-wider text-xs font-bold">Status</span>
                    <span className="text-white text-base flex items-center gap-2">
                      {status.icon} {health?.status || "N/A"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <FileText className="w-5 h-5" /> Dataset details
                </h3>
                <ul className="space-y-4 text-gray-300">
                  <li className="flex items-start gap-4 p-4 bg-black/20 rounded-2xl border border-white/5">
                    <div className="mt-1 w-2 h-2 bg-white rounded-full flex-shrink-0" />
                    <span>Intents are trained on a 50k-record custom dataset spanning 24 specific campus topics using TF-IDF vectorization.</span>
                  </li>
                  <li className="flex items-start gap-4 p-4 bg-black/20 rounded-2xl border border-white/5">
                    <div className="mt-1 w-2 h-2 bg-white rounded-full flex-shrink-0" />
                    <span>The retrieval corpus includes official university curriculums, regulations, and dynamic FAQ content.</span>
                  </li>
                  <li className="flex items-start gap-4 p-4 bg-black/20 rounded-2xl border border-white/5">
                    <div className="mt-1 w-2 h-2 bg-white rounded-full flex-shrink-0" />
                    <span>NVIDIA NIM API powers the generation phase, grounding all generated answers exclusively in the retrieved source chunks.</span>
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
    </div>
  );
}
