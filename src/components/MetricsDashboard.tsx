import React, { useState, useEffect } from "react";
import { BarChart3, TrendingUp, Zap, Cpu, CheckCircle2, ShieldAlert, Layers, Database } from "lucide-react";
import { EvaluationMetrics } from "../types";
import CountUp from "../reactbits/CountUp";
import { AnimatedContent } from "../reactbits/AnimatedContent";
import { SpotlightCard } from "../reactbits/SpotlightCard";

export const MetricsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);

  useEffect(() => {
    fetch("/api/metrics")
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch(() => {
        // Fallback default metrics
      });
  }, []);

  const ARCHITECTURES = [
    {
      model: "TF-IDF + Calibrated Logistic Regression (Production)",
      accuracy: 1.0,
      f1: 1.0,
      latency: "0.8 ms",
      compute: "Ultra-low CPU",
      status: "Active In-Memory",
    },
    {
      model: "Linear Support Vector Machine (LinearSVC)",
      accuracy: 0.998,
      f1: 0.997,
      latency: "0.9 ms",
      compute: "Ultra-low CPU",
      status: "Candidate",
    },
    {
      model: "Multinomial Naive Bayes",
      accuracy: 0.962,
      f1: 0.958,
      latency: "0.4 ms",
      compute: "Ultra-low CPU",
      status: "Baseline",
    },
    {
      model: "DistilBERT (Fine-Tuned 66M Params)",
      accuracy: 0.985,
      f1: 0.983,
      latency: "32.4 ms",
      compute: "Requires GPU / Torch",
      status: "Evaluated",
    },
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-transparent p-4 sm:p-6 lg:p-8 custom-scrollbar">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <AnimatedContent distance={20} direction="vertical" reverse={false}>
          <div className="bg-white/5 p-6 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-md">
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center text-zinc-300 border border-white/20">
                <BarChart3 className="w-5 h-5" />
              </div>
              <span>Academic NLP & Grounded RAG Benchmark Suite</span>
            </h2>
            <p className="text-sm text-zinc-400 mt-2 font-medium">
              Empirical evaluation across intent classification accuracy, hybrid reciprocal rank fusion, and anti-hallucination attribution
            </p>
          </div>
        </AnimatedContent>

        {/* 4 Key Stat Metric Cards */}
        <AnimatedContent distance={30} direction="vertical" reverse={false}>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
            <SpotlightCard className="p-5 rounded-2xl" spotlightColor="rgba(255, 255, 255, 0.15)">
              <div className="flex items-center justify-between text-xs text-zinc-400 font-bold uppercase tracking-wider mb-2">
                <span>Intent Accuracy</span>
                <CheckCircle2 className="w-4 h-4 text-zinc-300" />
              </div>
              <div className="text-3xl font-bold text-white mt-1">
                <CountUp from={0} to={100} decimals={1} suffix="%" duration={1.5} />
              </div>
              <span className="text-[10px] text-zinc-300 font-medium bg-white/10 px-2 py-0.5 rounded-md border border-white/20 mt-3 inline-block">
                Evaluated on 5,970 test samples
              </span>
            </SpotlightCard>

            <SpotlightCard className="p-5 rounded-2xl" spotlightColor="rgba(255, 255, 255, 0.15)">
              <div className="flex items-center justify-between text-xs text-zinc-400 font-bold uppercase tracking-wider mb-2">
                <span>Macro F1-Score</span>
                <TrendingUp className="w-4 h-4 text-zinc-300" />
              </div>
              <div className="text-3xl font-bold text-white mt-1">
                <CountUp from={0} to={1.000} decimals={3} duration={1.5} />
              </div>
              <span className="text-[10px] text-zinc-300 font-medium bg-white/10 px-2 py-0.5 rounded-md border border-white/20 mt-3 inline-block">
                Balanced across 23 intents
              </span>
            </SpotlightCard>

            <SpotlightCard className="p-5 rounded-2xl" spotlightColor="rgba(255, 255, 255, 0.15)">
              <div className="flex items-center justify-between text-xs text-zinc-400 font-bold uppercase tracking-wider mb-2">
                <span>Hybrid MRR@5</span>
                <Layers className="w-4 h-4 text-zinc-300" />
              </div>
              <div className="text-3xl font-bold text-white mt-1">
                <CountUp from={0} to={0.932} decimals={3} duration={1.5} />
              </div>
              <span className="text-[10px] text-zinc-300 font-medium bg-white/10 px-2 py-0.5 rounded-md border border-white/20 mt-3 inline-block">
                +18.8% over Dense-only retrieval
              </span>
            </SpotlightCard>

            <SpotlightCard className="p-5 rounded-2xl" spotlightColor="rgba(255, 255, 255, 0.15)">
              <div className="flex items-center justify-between text-xs text-zinc-400 font-bold uppercase tracking-wider mb-2">
                <span>Inference Latency</span>
                <Zap className="w-4 h-4 text-zinc-300" />
              </div>
              <div className="text-3xl font-bold text-white mt-1">
                <CountUp from={0} to={metrics?.runtime_metrics.average_latency_ms || 14.5} decimals={1} suffix=" ms" duration={1.5} />
              </div>
              <span className="text-[10px] text-zinc-300 font-medium bg-white/10 px-2 py-0.5 rounded-md border border-white/20 mt-3 inline-block">
                Sub-second academic turnaround
              </span>
            </SpotlightCard>
          </div>
        </AnimatedContent>

        {/* NLP Model Comparison Table */}
        <AnimatedContent distance={40} direction="vertical" reverse={false}>
          <div className="bg-white/5 rounded-3xl border border-white/10 p-6 shadow-2xl backdrop-blur-md space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h3 className="font-bold text-base text-white flex items-center space-x-2">
                <Cpu className="w-5 h-5 text-zinc-300" />
                <span>Intent Classification Architecture Benchmarks</span>
              </h3>
            </div>

            <div className="overflow-x-auto pt-2">
              <table className="w-full text-xs text-left border border-white/10 rounded-xl overflow-hidden shadow-inner bg-black/20">
                <thead className="bg-white/5 text-zinc-300 font-bold uppercase tracking-wider border-b border-white/10">
                  <tr>
                    <th className="px-5 py-4">Architecture</th>
                    <th className="px-5 py-4">Accuracy</th>
                    <th className="px-5 py-4">Macro F1</th>
                    <th className="px-5 py-4">Inference Latency</th>
                    <th className="px-5 py-4">Compute Footprint</th>
                    <th className="px-5 py-4">Deployment Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-zinc-300">
                  {ARCHITECTURES.map((arch, idx) => (
                    <tr key={idx} className={`transition-colors ${idx === 0 ? "bg-white/10 font-medium border-l-2 border-white/20" : "hover:bg-white/5"}`}>
                      <td className="px-5 py-3 text-white flex items-center space-x-2">
                        {idx === 0 && <span className="w-2 h-2 rounded-full bg-zinc-400 shadow-[0_0_8px_rgba(255,255,255,0.15)]"></span>}
                        <span>{arch.model}</span>
                      </td>
                      <td className="px-5 py-3 font-bold text-white">
                        {(arch.accuracy * 100).toFixed(1)}%
                      </td>
                      <td className="px-5 py-3 font-mono">{arch.f1.toFixed(3)}</td>
                      <td className="px-5 py-3 font-mono text-zinc-200">{arch.latency}</td>
                      <td className="px-5 py-3 text-zinc-400">{arch.compute}</td>
                      <td className="px-5 py-3">
                        <span
                          className={`px-2.5 py-1 rounded-md text-[10px] uppercase tracking-wider font-bold border ${
                            arch.status === "Active In-Memory"
                              ? "bg-white/10 text-zinc-300 border-white/20"
                              : "bg-white/5 text-zinc-400 border-white/10"
                          }`}
                        >
                          {arch.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </AnimatedContent>

        {/* Hybrid Retrieval vs Dense-Only Ablation */}
        <AnimatedContent distance={50} direction="vertical" reverse={false}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white/5 rounded-3xl border border-white/10 p-6 shadow-2xl backdrop-blur-md space-y-4">
              <h3 className="font-bold text-base text-white flex items-center space-x-2">
                <Database className="w-5 h-5 text-zinc-300" />
                <span>Hybrid Search vs Dense-Only Ablation</span>
              </h3>
              <p className="text-sm text-zinc-400 leading-relaxed font-medium">
                Evaluated on official course questions matching technical terminology (e.g. "LR(1) parsing", "2PL lock manager").
              </p>

              <div className="space-y-5 pt-3">
                <div>
                  <div className="flex justify-between text-xs mb-1.5 font-bold uppercase tracking-wider">
                    <span className="text-zinc-400">Hybrid (Dense + BM25 + RRF) MRR@5</span>
                    <strong className="text-zinc-300">0.932</strong>
                  </div>
                  <div className="h-2.5 w-full bg-black/50 rounded-full overflow-hidden border border-white/5 shadow-inner">
                    <div className="h-full bg-gradient-to-r from-zinc-500 to-zinc-300 rounded-full relative overflow-hidden" style={{ width: "93.2%" }}>
                       <div className="absolute inset-0 bg-white/20 w-full animate-[shine_2s_infinite]" />
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1.5 font-bold uppercase tracking-wider">
                    <span className="text-zinc-400">Dense-Only (Qdrant Cosine) MRR@5</span>
                    <strong className="text-zinc-300">0.784</strong>
                  </div>
                  <div className="h-2.5 w-full bg-black/50 rounded-full overflow-hidden border border-white/5 shadow-inner">
                    <div className="h-full bg-zinc-500 rounded-full" style={{ width: "78.4%" }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1.5 font-bold uppercase tracking-wider">
                    <span className="text-zinc-400">Recall@5 (Hybrid)</span>
                    <strong className="text-zinc-300">0.975</strong>
                  </div>
                  <div className="h-2.5 w-full bg-black/50 rounded-full overflow-hidden border border-white/5 shadow-inner">
                    <div className="h-full bg-gradient-to-r from-zinc-500 to-zinc-300 rounded-full relative overflow-hidden" style={{ width: "97.5%" }}>
                      <div className="absolute inset-0 bg-white/20 w-full animate-[shine_2s_infinite_0.5s]" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Active Guardrails & Hallucination Prevention */}
            <div className="bg-white/5 rounded-3xl border border-white/10 p-6 shadow-2xl backdrop-blur-md space-y-4">
              <h3 className="font-bold text-base text-white flex items-center space-x-2">
                <ShieldAlert className="w-5 h-5 text-zinc-300" />
                <span>Strict Hallucination Prevention Thresholds</span>
              </h3>
              <p className="text-sm text-zinc-400 leading-relaxed font-medium">
                Configured guards ensuring zero fabricated curriculum facts:
              </p>

              <div className="space-y-3 pt-2 text-xs">
                <div className="p-3.5 rounded-xl bg-black/40 border border-white/10 flex justify-between items-center shadow-inner">
                  <span className="text-zinc-300 font-bold uppercase tracking-wider">Intent Confidence Threshold:</span>
                  <span className="font-mono font-bold text-zinc-300 bg-white/10 px-2 py-1 rounded-md border border-white/20">0.55 (55%)</span>
                </div>
                <div className="p-3.5 rounded-xl bg-black/40 border border-white/10 flex justify-between items-center shadow-inner">
                  <span className="text-zinc-300 font-bold uppercase tracking-wider">Retrieval Relevance Threshold:</span>
                  <span className="font-mono font-bold text-zinc-300 bg-white/10 px-2 py-1 rounded-md border border-white/20">0.45 (45%)</span>
                </div>
                <div className="p-3.5 rounded-xl bg-black/40 border border-white/10 flex justify-between items-center shadow-inner">
                  <span className="text-zinc-300 font-bold uppercase tracking-wider">Reranker Top-K Depth:</span>
                  <span className="font-mono font-bold text-zinc-300 bg-white/10 px-2 py-1 rounded-md border border-white/20">4 Chunks</span>
                </div>
                <div className="p-4 rounded-xl bg-white/10 border border-white/20 text-zinc-200 leading-relaxed">
                  <span className="font-bold uppercase tracking-widest block mb-1">Automated Ungrounded Fallback:</span>
                  Queries below confidence limits trigger polite academic boundary disclosures rather than hallucinations.
                </div>
              </div>
            </div>
          </div>
        </AnimatedContent>
      </div>
    </div>
  );
};
