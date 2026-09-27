import React from "react";
import { GraduationCap, Database, BookOpen, FileText, BarChart3, MessageSquare, Cloud } from "lucide-react";
import { SystemHealth } from "../types";
import { Magnet } from "../reactbits/Magnet";
import { ShinyText } from "../reactbits/ShinyText";

interface SidebarProps {
  activeTab: "chat" | "catalog" | "regulations" | "resources" | "metrics";
  onSelectTab: (tab: "chat" | "catalog" | "regulations" | "resources" | "metrics") => void;
  health: SystemHealth | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab, health }) => {
  const tabs = [
    { id: "chat" as const, label: "Assistant", icon: MessageSquare, color: "text-zinc-300" },
    { id: "resources" as const, label: "Data Hub", icon: Database, color: "text-zinc-300" },
    { id: "catalog" as const, label: "Courses", icon: BookOpen, color: "text-zinc-300" },
    { id: "regulations" as const, label: "Regulations", icon: FileText, color: "text-zinc-300" },
    { id: "metrics" as const, label: "Benchmarks", icon: BarChart3, color: "text-zinc-300" },
  ];

  return (
    <aside className="w-64 border-r border-white/10 bg-black/20 backdrop-blur-xl flex flex-col z-30 h-screen sticky top-0 shrink-0">
      {/* Brand & University Identity */}
      <div className="p-6 border-b border-white/10 flex items-center space-x-3">
        <Magnet padding={200} disabled={false} magnetStrength={4}>
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center text-zinc-300 shadow-[0_0_15px_rgba(255,255,255,0.15)] border border-white/20">
            <GraduationCap className="w-6 h-6" />
          </div>
        </Magnet>
        <div className="flex flex-col overflow-hidden">
          <div className="flex items-center space-x-2">
            <ShinyText text="CurriculumAI" disabled={false} speed={3} className="font-bold text-lg tracking-tight" />
          </div>
          <p className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold truncate">
            B.Tech CSE Assistant
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        <div className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4 px-2">Menu</div>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-300 relative group overflow-hidden ${
                isActive
                  ? "bg-white/10 text-white shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] border border-white/5"
                  : "text-zinc-400 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              {isActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent opacity-50" />
              )}
              <tab.icon className={`w-5 h-5 relative z-10 transition-transform duration-300 group-hover:scale-110 ${isActive ? tab.color : ""}`} />
              <span className="font-medium text-sm relative z-10">{tab.label}</span>
              
              {tab.id === "resources" && (
                 <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded-md bg-white/10 text-zinc-200 font-bold border border-white/20 relative z-10">
                   5
                 </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-white/10">
        <div className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-3 px-2">System</div>
        <div className="flex flex-col space-y-2 text-xs">
          <div className="flex items-center space-x-2 bg-white/10 text-zinc-200 px-3 py-2 rounded-lg border border-white/20">
            <Cloud className="w-4 h-4 shrink-0" />
            <span className="font-medium truncate">Cloudflare Vectorize</span>
          </div>
          <div className="flex items-center space-x-2 bg-white/10 text-zinc-300 px-3 py-2 rounded-lg border border-white/20">
            <span className="w-2 h-2 rounded-full bg-zinc-400 animate-pulse shrink-0 shadow-[0_0_8px_rgba(255,255,255,0.15)]"></span>
            <span className="font-medium truncate">
              {health ? `${health.indexed_chunks_count} Vectors` : "Connecting..."}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
