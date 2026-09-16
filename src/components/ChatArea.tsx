import React, { useState, useRef, useEffect } from "react";
import Markdown from "react-markdown";
import {
  Send,
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Layers,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Clock,
  ArrowRight
} from "lucide-react";
import { ChatMessage } from "../types";
import { SourceCard } from "./SourceCard";

interface ChatAreaProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (query: string) => void;
  onFeedback: (messageId: string, type: "thumbs_up" | "thumbs_down") => void;
  onInspectMessage: (message: ChatMessage) => void;
}

const SUGGESTED_QUERIES = [
  { text: "What are the hostel curfew and mess timings?", tag: "Campus Life", color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  { text: "How can I apply for revaluation and what is the fee?", tag: "Regulations", color: "bg-amber-50 text-amber-700 border-amber-200" },
  { text: "What are the prerequisites and syllabus for Machine Learning (CS401)?", tag: "Curriculum", color: "bg-indigo-50 text-indigo-700 border-indigo-200" },
  { text: "What are the rules and borrowing limits in the Central Library?", tag: "Campus Life", color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  { text: "Show the Computer Networks subnetting formula and /26 CIDR host count", tag: "Study Guide", color: "bg-purple-50 text-purple-700 border-purple-200" },
  { text: "What is the passing criteria, attendance rule, and 10-point grading scale?", tag: "Regulations", color: "bg-amber-50 text-amber-700 border-amber-200" },
  { text: "What are the eligibility criteria and Dream Company packages for placements?", tag: "Placements", color: "bg-blue-50 text-blue-700 border-blue-200" },
  { text: "What topics are covered in Unit 3 of DBMS (CS301)?", tag: "Curriculum", color: "bg-indigo-50 text-indigo-700 border-indigo-200" }
];

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onFeedback,
  onInspectMessage,
}) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleSuggestedClick = (prompt: string) => {
    if (isLoading) return;
    onSendMessage(prompt);
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-slate-50/50">
      {/* Scrollable Conversation Stream */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="max-w-2xl mx-auto py-10 px-4 text-center space-y-6">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-200">
              <BookOpen className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                Academic Curriculum & Regulations Assistant
              </h2>
              <p className="text-sm text-slate-600 mt-2 max-w-lg mx-auto">
                Ask about official B.Tech Computer Science courses, unit-level syllabi,
                credits, course prerequisites, exam schemes, and university regulations.
              </p>
            </div>

            {/* Quick Prompt Cards */}
            <div className="pt-4">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-3">
                Suggested Academic Inquiries
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left">
                {SUGGESTED_QUERIES.map((item, idx) => (
                  <button
                    key={idx}
                    id={`suggested-prompt-${idx}`}
                    onClick={() => handleSuggestedClick(item.text)}
                    className="p-3 bg-white border border-slate-200 hover:border-indigo-400 rounded-xl text-xs text-slate-700 hover:text-indigo-900 transition-all shadow-2xs hover:shadow-xs group flex flex-col justify-between space-y-2 text-left"
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold border ${item.color}`}>
                        {item.tag}
                      </span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600 shrink-0" />
                    </div>
                    <span className="text-slate-800 font-medium">{item.text}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.sender === "user" ? "items-end" : "items-start"
                }`}
              >
                {/* Message Bubble */}
                <div
                  className={`relative max-w-2xl rounded-2xl p-4 sm:p-5 text-sm leading-relaxed shadow-xs transition-all ${
                    msg.sender === "user"
                      ? "bg-indigo-600 text-white rounded-br-xs"
                      : "bg-white text-slate-800 border border-slate-200 rounded-bl-xs"
                  }`}
                >
                  {/* Sender Header / Meta */}
                  {msg.sender === "bot" && (
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-3 border-b border-slate-100 text-xs">
                      <div className="flex items-center space-x-2">
                        {msg.intent && (
                          <span className="px-2 py-0.5 rounded-full font-semibold text-[10px] uppercase tracking-wide bg-indigo-50 text-indigo-700 border border-indigo-200">
                            {msg.intent.replace(/_/g, " ")}
                          </span>
                        )}
                        {msg.overall_confidence !== undefined && (
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                              msg.overall_confidence >= 0.70
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                : "bg-amber-50 text-amber-700 border border-amber-200"
                            }`}
                          >
                            {Math.round(msg.overall_confidence * 100)}% confidence
                          </span>
                        )}
                      </div>

                      {/* Inspect pipeline button */}
                      <button
                        id={`inspect-btn-${msg.id}`}
                        onClick={() => onInspectMessage(msg)}
                        className="inline-flex items-center space-x-1 text-[11px] text-indigo-600 hover:text-indigo-800 font-medium hover:underline cursor-pointer"
                      >
                        <Layers className="w-3.5 h-3.5" />
                        <span>Inspect RAG Pipeline</span>
                      </button>
                    </div>
                  )}

                  {/* Body Content */}
                  <div className={msg.sender === "user" ? "text-white" : "prose prose-sm max-w-none text-slate-800 prose-headings:text-slate-900 prose-p:my-1 prose-ul:my-1 prose-li:my-0.5"}>
                    {msg.sender === "user" ? (
                      <p className="whitespace-pre-wrap font-medium">{msg.text}</p>
                    ) : (
                      <Markdown>{msg.text}</Markdown>
                    )}
                  </div>

                  {/* Grounded Evidence Sources Section */}
                  {msg.sender === "bot" && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
                      <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
                        <span className="flex items-center">
                          <BookOpen className="w-3.5 h-3.5 mr-1 text-indigo-600" />
                          Curriculum Evidence Sources ({msg.sources.length})
                        </span>
                        <span className="text-[11px] text-slate-400">
                          Click to expand passage
                        </span>
                      </div>

                      <div className="space-y-1.5 pt-1">
                        {msg.sources.slice(0, 3).map((source, idx) => (
                          <SourceCard key={idx} source={source} index={idx} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Bot Message Footer: Latency & Feedback */}
                  {msg.sender === "bot" && (
                    <div className="flex items-center justify-between pt-3 mt-3 border-t border-slate-100 text-xs text-slate-400">
                      <span className="flex items-center text-[11px]">
                        <Clock className="w-3 h-3 mr-1" />
                        Processed in {msg.latency_ms || 12} ms
                      </span>

                      <div className="flex items-center space-x-2">
                        <span className="text-[11px] mr-1 text-slate-400">Helpful?</span>
                        <button
                          id={`thumbs-up-${msg.id}`}
                          onClick={() => onFeedback(msg.id, "thumbs_up")}
                          className={`p-1 rounded-md transition-colors ${
                            msg.feedback === "thumbs_up"
                              ? "text-emerald-600 bg-emerald-50"
                              : "text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                          }`}
                          title="Thumbs up"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          id={`thumbs-down-${msg.id}`}
                          onClick={() => onFeedback(msg.id, "thumbs_down")}
                          className={`p-1 rounded-md transition-colors ${
                            msg.feedback === "thumbs_down"
                              ? "text-rose-600 bg-rose-50"
                              : "text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                          }`}
                          title="Thumbs down"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Timestamp */}
                <span className="text-[10px] text-slate-400 mt-1 px-1">
                  {msg.timestamp}
                </span>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="max-w-md bg-white border border-slate-200 rounded-2xl rounded-bl-xs p-4 shadow-xs">
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <span className="w-2 h-2 rounded-full bg-indigo-600 animate-ping"></span>
                    <span className="font-medium">
                      Classifying intent & retrieving curriculum chunks...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Form Bar */}
      <div className="p-3 sm:p-4 bg-white border-t border-slate-200">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="flex items-center space-x-2">
            <input
              id="chat-input-field"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about courses, units, prerequisites, credits, or academic regulations..."
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:bg-white text-slate-900 transition-all disabled:opacity-50"
            />
            <button
              id="send-query-btn"
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium text-sm transition-all shadow-xs disabled:opacity-40 flex items-center space-x-1 cursor-pointer"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 px-1">
            <span>Official B.Tech CSE Curriculum Knowledge Base</span>
            <span>Hallucination Guardrails: Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
