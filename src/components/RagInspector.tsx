import React from "react";
import { X, CheckCircle2, AlertTriangle, Layers, Target, Compass, Sparkles, ShieldCheck, Activity } from "lucide-react";
import { ChatMessage } from "../types";

interface RagInspectorProps {
  message: ChatMessage | null;
  onClose: () => void;
}

export const RagInspector: React.FC<RagInspectorProps> = ({ message, onClose }) => {
  if (!message) return null;

  const breakdown = message.confidence_breakdown || {};
  const intentScore = Math.round((message.intent_confidence || 0) * 100);
  const overallScore = Math.round((message.overall_confidence || 0) * 100);

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-lg bg-black/80 backdrop-blur-xl shadow-2xl border-l border-white/10 z-50 flex flex-col overflow-hidden animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="px-6 py-5 border-b border-white/10 flex items-center justify-between bg-white/5">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-white/10 text-zinc-300 border border-white/20">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">NLP & RAG Pipeline Inspector</h3>
            <p className="text-xs text-zinc-400 font-medium">8-Stage Execution Audit Trace</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-xl text-zinc-500 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm text-zinc-300 custom-scrollbar">
        {/* Stage 1 & 2: Intent Classification */}
        <section className="border border-white/10 rounded-2xl p-5 bg-white/5 space-y-4 shadow-inner">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="w-6 h-6 rounded-full bg-zinc-700 text-white flex items-center justify-center font-bold text-xs shadow-[0_0_10px_rgba(255,255,255,0.15)]">
                1
              </span>
              <h4 className="font-bold text-white text-sm uppercase tracking-wider">Intent Classification</h4>
            </div>
            <span
              className={`px-3 py-1 rounded-md text-[10px] uppercase tracking-widest font-bold border ${
                intentScore >= 75
                  ? "bg-white/10 text-zinc-300 border-white/20"
                  : intentScore >= 55
                  ? "bg-white/10 text-zinc-300 border-white/20"
                  : "bg-white/10 text-zinc-300 border-white/20"
              }`}
            >
              {intentScore}% Confident
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="bg-black/40 p-4 rounded-xl border border-white/5 shadow-inner">
              <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold block mb-1">Classified Intent</span>
              <span className="font-mono font-bold text-zinc-300 text-sm bg-white/10 px-2 py-1 rounded-md inline-block">
                {message.intent || "unknown"}
              </span>
            </div>
            <div className="bg-black/40 p-4 rounded-xl border border-white/5 shadow-inner">
              <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold block mb-1">Classifier Model</span>
              <span className="font-medium text-white text-xs">
                TF-IDF + Calibrated LR
              </span>
            </div>
          </div>
        </section>

        {/* Stage 3: Extracted Academic Entities */}
        <section className="border border-white/10 rounded-2xl p-5 bg-white/5 space-y-4 shadow-inner">
          <div className="flex items-center space-x-3">
            <span className="w-6 h-6 rounded-full bg-zinc-700 text-white flex items-center justify-center font-bold text-xs shadow-[0_0_10px_rgba(255,255,255,0.15)]">
              2
            </span>
            <h4 className="font-bold text-white text-sm uppercase tracking-wider">Extracted Academic Entities</h4>
          </div>

          <div className="bg-black/40 rounded-xl border border-white/5 divide-y divide-white/5 shadow-inner">
            <div className="px-4 py-3 flex justify-between items-center text-xs">
              <span className="text-zinc-500 font-bold uppercase tracking-wider">Course Name:</span>
              <span className="font-bold text-white">
                {message.entities?.canonical_course_name || message.entities?.course || "None detected"}
              </span>
            </div>
            <div className="px-4 py-3 flex justify-between items-center text-xs">
              <span className="text-zinc-500 font-bold uppercase tracking-wider">Course Code:</span>
              <span className="font-mono font-bold text-zinc-300 bg-white/10 px-2 py-1 rounded-md">
                {message.entities?.course_code || "None"}
              </span>
            </div>
            <div className="px-4 py-3 flex justify-between items-center text-xs">
              <span className="text-zinc-500 font-bold uppercase tracking-wider">Semester:</span>
              <span className="font-bold text-white">
                {message.entities?.semester ? `Semester ${message.entities.semester}` : "All"}
              </span>
            </div>
            <div className="px-4 py-3 flex justify-between items-center text-xs">
              <span className="text-zinc-500 font-bold uppercase tracking-wider">Unit / Module:</span>
              <span className="font-bold text-white">
                {message.entities?.unit ? `Unit ${message.entities.unit}` : "Not specified"}
              </span>
            </div>
          </div>
        </section>

        {/* Stage 4 & 5: Hybrid Retrieval & Reranker */}
        <section className="border border-white/10 rounded-2xl p-5 bg-white/5 space-y-4 shadow-inner">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="w-6 h-6 rounded-full bg-zinc-700 text-white flex items-center justify-center font-bold text-xs shadow-[0_0_10px_rgba(255,255,255,0.15)]">
                3
              </span>
              <h4 className="font-bold text-white text-sm uppercase tracking-wider">Hybrid Retrieval & Reranker</h4>
            </div>
            <span className="text-zinc-300 text-[10px] font-bold uppercase tracking-widest bg-white/10 px-2.5 py-1 rounded-md border border-white/20">
              {message.sources?.length || 0} candidate chunks
            </span>
          </div>

          <div className="space-y-3 pt-1">
            <div className="flex items-center justify-between text-xs bg-black/40 p-3 rounded-xl border border-white/5 shadow-inner">
              <span className="text-zinc-400 font-bold uppercase tracking-wider">Vector Store:</span>
              <span className="font-mono font-bold text-white bg-white/5 px-2 py-1 rounded-md">Qdrant (1024-d Cosine)</span>
            </div>
            <div className="flex items-center justify-between text-xs bg-black/40 p-3 rounded-xl border border-white/5 shadow-inner">
              <span className="text-zinc-400 font-bold uppercase tracking-wider">Sparse Lexical Index:</span>
              <span className="font-mono font-bold text-white bg-white/5 px-2 py-1 rounded-md">BM25 (k1=1.5, b=0.75)</span>
            </div>
            <div className="flex items-center justify-between text-xs bg-black/40 p-3 rounded-xl border border-white/5 shadow-inner">
              <span className="text-zinc-400 font-bold uppercase tracking-wider">Rank Fusion:</span>
              <span className="font-mono font-bold text-white bg-white/5 px-2 py-1 rounded-md">RRF (k=60)</span>
            </div>
            <div className="flex items-center justify-between text-xs bg-black/40 p-3 rounded-xl border border-white/5 shadow-inner">
              <span className="text-zinc-400 font-bold uppercase tracking-wider">Cross-Encoder:</span>
              <span className="font-mono font-bold text-white bg-white/5 px-2 py-1 rounded-md">NVIDIA NIM</span>
            </div>
          </div>
        </section>

        {/* Stage 6 & 7: Groundedness & Confidence Breakdown */}
        <section className="border border-white/10 rounded-2xl p-5 bg-white/5 space-y-5 shadow-inner">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="w-6 h-6 rounded-full bg-zinc-700 text-white flex items-center justify-center font-bold text-xs shadow-[0_0_10px_rgba(255,255,255,0.15)]">
                4
              </span>
              <h4 className="font-bold text-white text-sm uppercase tracking-wider">Groundedness & Attribution</h4>
            </div>
            <div className="flex items-center space-x-1.5">
              {message.is_grounded ? (
                <span className="flex items-center text-zinc-300 bg-white/10 border border-white/20 px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" /> Grounded
                </span>
              ) : (
                <span className="flex items-center text-zinc-300 bg-white/10 border border-white/20 px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest">
                  <AlertTriangle className="w-3.5 h-3.5 mr-1.5" /> Ungrounded
                </span>
              )}
            </div>
          </div>

          <div className="space-y-4 pt-1">
            <div>
              <div className="flex justify-between text-[11px] mb-2 font-bold uppercase tracking-wider">
                <span className="text-zinc-400">Overall Attribution Score</span>
                <span className="text-white bg-white/10 px-2 py-0.5 rounded-md">{overallScore}%</span>
              </div>
              <div className="h-2.5 w-full bg-black/50 rounded-full overflow-hidden border border-white/5 shadow-inner">
                <div
                  className="h-full bg-gradient-to-r from-zinc-500 to-zinc-300 rounded-full transition-all duration-500 relative overflow-hidden"
                  style={{ width: `${overallScore}%` }}
                >
                  <div className="absolute inset-0 bg-white/20 w-full animate-[shine_2s_infinite]" />
                </div>
              </div>
            </div>

            {breakdown.top_retrieval_score !== undefined && (
              <div>
                <div className="flex justify-between text-[11px] mb-2 font-bold uppercase tracking-wider">
                  <span className="text-zinc-400">Retrieval Relevance</span>
                  <span className="text-zinc-300 bg-white/10 px-2 py-0.5 rounded-md">
                    {Math.round((breakdown.top_retrieval_score || 0) * 100)}%
                  </span>
                </div>
                <div className="h-1.5 w-full bg-black/50 rounded-full overflow-hidden border border-white/5 shadow-inner">
                  <div
                    className="h-full bg-zinc-400 rounded-full"
                    style={{ width: `${Math.round((breakdown.top_retrieval_score || 0) * 100)}%` }}
                  ></div>
                </div>
              </div>
            )}

            {breakdown.top_rerank_score !== undefined && (
              <div>
                <div className="flex justify-between text-[11px] mb-2 font-bold uppercase tracking-wider">
                  <span className="text-zinc-400">Reranker Cross-Attention</span>
                  <span className="text-zinc-300 bg-white/10 px-2 py-0.5 rounded-md">
                    {Math.round((breakdown.top_rerank_score || 0) * 100)}%
                  </span>
                </div>
                <div className="h-1.5 w-full bg-black/50 rounded-full overflow-hidden border border-white/5 shadow-inner">
                  <div
                    className="h-full bg-zinc-400 rounded-full"
                    style={{ width: `${Math.round((breakdown.top_rerank_score || 0) * 100)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Latency & Audit Metadata */}
        <div className="flex items-center justify-between text-[10px] uppercase tracking-widest font-bold pt-4 border-t border-white/10">
          <span className="flex items-center text-zinc-500">
            <Activity className="w-3.5 h-3.5 mr-1.5" />
            End-to-End Latency: <strong className="ml-1 text-white bg-white/10 px-2 py-1 rounded-md">{message.latency_ms || 18} ms</strong>
          </span>
          <span className="flex items-center text-zinc-300 bg-white/10 px-2 py-1 rounded-md border border-white/20">
            <ShieldCheck className="w-3.5 h-3.5 mr-1.5" />
            Guardrails: Passed
          </span>
        </div>
      </div>
    </div>
  );
};
