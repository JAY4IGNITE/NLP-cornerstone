import { useEffect, useState } from "react";
import { Chat } from "./components/Chat";
import { getHealth } from "./lib/api";
import type { HealthResponse } from "./types/chat";
import { motion } from "framer-motion";
import { ServerCrash, Activity, MessageSquare, Hexagon, Search, Folder, Compass, Settings, ChevronDown, Plus } from "lucide-react";

type StatusTone = "unknown" | "offline" | "ok" | "degraded";

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
                  <span className="truncate">Campus Life FAQ</span>
                </button>
                <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors group">
                  <MessageSquare className="w-4 h-4 text-gray-500 group-hover:text-gray-300 transition-colors" strokeWidth={1.5} />
                  <span className="truncate">Registration Help</span>
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

          <div className="flex-1 flex justify-center relative h-[42px]">
            {/* Minimalistic Header Title */}
            <div className="font-semibold text-lg text-white">Campus AI Chat</div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-2 text-xs font-medium text-gray-400 w-48 justify-end relative z-50">
            {status.icon}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 w-full max-w-4xl mx-auto px-4 pb-4 relative z-10 flex flex-col min-h-0 overflow-hidden">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 flex flex-col min-h-0 overflow-hidden">
            <Chat />
          </motion.div>
        </main>
      </div>
    </div>
  );
}
