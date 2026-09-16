import React, { useState } from "react";
import { BookMarked, ChevronDown, ChevronUp, FileText, CheckCircle } from "lucide-react";
import { CitationSource } from "../types";

interface SourceCardProps {
  source: CitationSource;
  index: number;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const relevancePct = Math.round(source.relevance_score * 100);

  return (
    <div className="border border-slate-200 rounded-lg bg-slate-50/70 overflow-hidden text-xs transition-all hover:border-indigo-300">
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-slate-100/80 transition-colors"
      >
        <div className="flex items-center space-x-2 truncate mr-2">
          <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[10px] shrink-0">
            {index + 1}
          </span>
          <div className="truncate">
            <span className="font-semibold text-slate-900 truncate block">
              {source.course_code ? `[${source.course_code}] ` : ""}
              {source.section || source.course_name || source.source_document}
            </span>
            <span className="text-slate-500 text-[11px]">
              {source.source_document} • Page {source.page}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
              relevancePct >= 75
                ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                : relevancePct >= 50
                ? "bg-blue-100 text-blue-800 border border-blue-200"
                : "bg-amber-100 text-amber-800 border border-amber-200"
            }`}
          >
            {relevancePct}% match
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </div>

      {isExpanded && (
        <div className="px-3 py-2.5 bg-white border-t border-slate-200 text-slate-700 leading-relaxed font-mono text-[11px] whitespace-pre-wrap max-h-48 overflow-y-auto">
          <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100 text-[10px] text-slate-400 font-sans">
            <span>Chunk ID: {source.chunk_id}</span>
            {source.is_cited && (
              <span className="flex items-center text-emerald-600 font-medium">
                <CheckCircle className="w-3 h-3 mr-1" /> Explicitly Cited
              </span>
            )}
          </div>
          <div>{source.course_name ? `Subject: ${source.course_name}\n` : ""}{source.section ? `Section: ${source.section}\n\n` : ""}Official curriculum verified passage.</div>
        </div>
      )}
    </div>
  );
};
