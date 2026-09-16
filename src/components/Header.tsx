import React from "react";
import { GraduationCap, Database, Cpu, CheckCircle2, BookOpen, FileText, BarChart3, MessageSquare, Cloud } from "lucide-react";
import { SystemHealth } from "../types";

interface HeaderProps {
  activeTab: "chat" | "catalog" | "regulations" | "resources" | "metrics";
  onSelectTab: (tab: "chat" | "catalog" | "regulations" | "resources" | "metrics") => void;
  health: SystemHealth | null;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onSelectTab, health }) => {
  return (
    <header className="border-b border-slate-200 bg-white shadow-xs sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & University Identity */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-900 flex items-center justify-center text-white shadow-sm">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-slate-900 text-lg tracking-tight">CurriculumAI</span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                  B.Tech CSE
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Academic NLP & Grounded RAG Student Assistant
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              id="nav-chat-btn"
              onClick={() => onSelectTab("chat")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === "chat"
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Assistant</span>
            </button>

            <button
              id="nav-resources-btn"
              onClick={() => onSelectTab("resources")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === "resources"
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <Database className="w-4 h-4 text-amber-500" />
              <span>Data Hub</span>
              <span className="ml-1 text-[10px] px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-800 font-bold">
                5 Sources
              </span>
            </button>

            <button
              id="nav-catalog-btn"
              onClick={() => onSelectTab("catalog")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === "catalog"
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>Courses</span>
            </button>

            <button
              id="nav-regulations-btn"
              onClick={() => onSelectTab("regulations")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === "regulations"
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Regulations</span>
            </button>

            <button
              id="nav-metrics-btn"
              onClick={() => onSelectTab("metrics")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === "metrics"
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Benchmarks</span>
            </button>
          </nav>

          {/* System Status Indicators with Cloudflare Vectorize */}
          <div className="hidden lg:flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-1.5 bg-amber-50 text-amber-900 px-2.5 py-1 rounded-full border border-amber-200">
              <Cloud className="w-3.5 h-3.5 text-amber-600" />
              <span className="font-semibold">Cloudflare Vectorize</span>
            </div>
            <div className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-800 px-2.5 py-1 rounded-full border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="font-medium">
                {health ? `${health.indexed_chunks_count} Vectors` : "Connecting..."}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
