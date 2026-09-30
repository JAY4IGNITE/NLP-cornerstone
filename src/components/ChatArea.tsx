import React, { useState, useRef, useEffect } from "react";
import Markdown from "react-markdown";
import {
  Send,
  BookOpen,
  Layers,
  ThumbsUp,
  ThumbsDown,
  Clock,
  ArrowRight
} from "lucide-react";
import { ChatMessage } from "../types";
import { SourceCard } from "./SourceCard";
import { StarBorder } from "../reactbits/StarBorder";
import { AnimatedContent } from "../reactbits/AnimatedContent";

interface ChatAreaProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (query: string) => void;
  onFeedback: (messageId: string, type: "thumbs_up" | "thumbs_down") => void;
  onInspectMessage: (message: ChatMessage) => void;
}

const SUGGESTED_QUERIES = [
  { text: "What are the hostel curfew and mess timings?", tag: "Campus Life", color: "text-zinc-300 bg-white/10 border-white/20" },
  { text: "How can I apply for revaluation and what is the fee?", tag: "Regulations", color: "text-zinc-300 bg-white/10 border-white/20" },
  { text: "What are the prerequisites and syllabus for Machine Learning (CS401)?", tag: "Curriculum", color: "text-zinc-300 bg-white/10 border-white/20" },
  { text: "What are the rules and borrowing limits in the Central Library?", tag: "Campus Life", color: "text-zinc-300 bg-white/10 border-white/20" },
  { text: "Show the Computer Networks subnetting formula and /26 CIDR host count", tag: "Study Guide", color: "text-zinc-300 bg-white/10 border-white/20" },
  { text: "What is the passing criteria, attendance rule, and 10-point grading scale?", tag: "Regulations", color: "text-zinc-300 bg-white/10 border-white/20" },
  { text: "What are the eligibility criteria and Dream Company packages for placements?", tag: "Placements", color: "text-zinc-300 bg-white/10 border-white/20" },
  { text: "What topics are covered in Unit 3 of DBMS (CS301)?", tag: "Curriculum", color: "text-zinc-300 bg-white/10 border-white/20" }
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
    <div className="flex-1 flex flex-col h-full bg-transparent">
      {/* Scrollable Conversation Stream */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-8 space-y-8">
        {messages.length === 0 ? (
          <AnimatedContent
            distance={40}
            direction="vertical"
            reverse={false}
          >
            <div className="max-w-3xl mx-auto py-10 px-4 text-center space-y-8">
              <div className="w-20 h-20 mx-auto rounded-3xl bg-white/10 text-zinc-300 flex items-center justify-center shadow-[0_0_30px_rgba(255,255,255,0.15)] border border-white/20">
                <BookOpen className="w-10 h-10" />
              </div>
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                  Academic Curriculum & Regulations Assistant
                </h2>
                <p className="text-sm text-zinc-400 mt-3 max-w-lg mx-auto leading-relaxed">
                  Ask about official B.Tech Computer Science courses, unit-level syllabi,
                  credits, course prerequisites, exam schemes, and university regulations.
                </p>
              </div>

              {/* Quick Prompt Cards */}
              <div className="pt-8">
                <span className="text-xs font-semibold text-zinc-500 uppercase tracking-widest block mb-4">
                  Suggested Academic Inquiries
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                  {SUGGESTED_QUERIES.map((item, idx) => (
                    <button
                      key={idx}
                      id={`suggested-prompt-${idx}`}
                      onClick={() => handleSuggestedClick(item.text)}
                      className="p-4 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/30 rounded-2xl text-xs text-zinc-300 hover:text-white transition-all shadow-[0_4px_20px_rgba(0,0,0,0.2)] group flex flex-col justify-between space-y-3 text-left backdrop-blur-md"
                    >
                      <div className="flex items-center justify-between w-full">
                        <span className={`text-[10px] px-2.5 py-1 rounded-md font-semibold border ${item.color}`}>
                          {item.tag}
                        </span>
                        <ArrowRight className="w-4 h-4 text-zinc-500 group-hover:text-zinc-200 transition-colors shrink-0" />
                      </div>
                      <span className="font-medium leading-relaxed">{item.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </AnimatedContent>
        ) : (
          <div className="max-w-3xl mx-auto space-y-8">
            {messages.map((msg) => (
              <AnimatedContent
                key={msg.id}
                distance={20}
                direction="vertical"
                reverse={false}
                className={`flex flex-col ${
                  msg.sender === "user" ? "items-end" : "items-start"
                }`}
              >
                {/* Message Bubble */}
                <div
                  className={`relative max-w-2xl rounded-3xl p-5 sm:p-6 text-sm leading-relaxed shadow-xl transition-all ${
                    msg.sender === "user"
                      ? "bg-zinc-700 text-white rounded-br-sm border border-white/20 shadow-[0_0_20px_rgba(255,255,255,0.15)] backdrop-blur-md"
                      : "bg-white/5 text-zinc-200 border border-white/10 rounded-bl-sm backdrop-blur-md"
                  }`}
                >
                  {/* Sender Header / Meta */}
                  {msg.sender === "bot" && (
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b border-white/10 text-xs">
                      <div className="flex items-center space-x-2">
                        {msg.intent && (
                          <span className="px-2.5 py-1 rounded-md font-semibold text-[10px] uppercase tracking-wide bg-white/10 text-zinc-300 border border-white/20">
                            {msg.intent.replace(/_/g, " ")}
                          </span>
                        )}
                        {msg.overall_confidence !== undefined && (
                          <span
                            className={`px-2.5 py-1 rounded-md text-[10px] font-medium border ${
                              msg.overall_confidence >= 0.70
                                ? "bg-white/10 text-zinc-300 border-white/20"
                                : "bg-white/10 text-zinc-300 border-white/20"
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
                        className="inline-flex items-center space-x-1.5 text-[11px] text-zinc-300 hover:text-zinc-200 font-medium transition-colors cursor-pointer bg-white/10 px-2 py-1 rounded-md border border-white/20"
                      >
                        <Layers className="w-3.5 h-3.5" />
                        <span>Inspect RAG</span>
                      </button>
                    </div>
                  )}

                  {/* Body Content */}
                  <div className={msg.sender === "user" ? "text-white" : "prose prose-invert prose-sm max-w-none text-zinc-300 prose-headings:text-zinc-100 prose-a:text-zinc-300 prose-p:my-2 prose-ul:my-2 prose-li:my-1"}>
                    {msg.sender === "user" ? (
                      <p className="whitespace-pre-wrap font-medium">{msg.text}</p>
                    ) : (
                      <Markdown>{msg.text}</Markdown>
                    )}
                  </div>

                  {/* Grounded Evidence Sources Section */}
                  {msg.sender === "bot" && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-5 pt-4 border-t border-white/10 space-y-3">
                      <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
                        <span className="flex items-center">
                          <BookOpen className="w-3.5 h-3.5 mr-1.5 text-zinc-300" />
                          Curriculum Evidence Sources ({msg.sources.length})
                        </span>
                        <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
                          Click to expand
                        </span>
                      </div>

                      <div className="space-y-2 pt-1">
                        {msg.sources.slice(0, 3).map((source, idx) => (
                          <div key={idx} className="bg-black/30 border border-white/5 rounded-xl p-1">
                             <SourceCard source={source} index={idx} />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Bot Message Footer: Latency & Feedback */}
                  {msg.sender === "bot" && (
                    <div className="flex items-center justify-between pt-4 mt-4 border-t border-white/10 text-xs text-zinc-500">
                      <span className="flex items-center text-[11px] font-medium">
                        <Clock className="w-3.5 h-3.5 mr-1.5" />
                        Processed in {msg.latency_ms || 12} ms
                      </span>

                      <div className="flex items-center space-x-2">
                        <span className="text-[10px] mr-1 uppercase tracking-wider font-semibold text-zinc-500">Feedback</span>
                        <button
                          id={`thumbs-up-${msg.id}`}
                          onClick={() => onFeedback(msg.id, "thumbs_up")}
                          className={`p-1.5 rounded-md transition-all ${
                            msg.feedback === "thumbs_up"
                              ? "text-zinc-300 bg-white/10 border border-white/20"
                              : "text-zinc-500 hover:text-zinc-200 hover:bg-white/10 border border-transparent hover:border-white/30"
                          }`}
                          title="Thumbs up"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          id={`thumbs-down-${msg.id}`}
                          onClick={() => onFeedback(msg.id, "thumbs_down")}
                          className={`p-1.5 rounded-md transition-all ${
                            msg.feedback === "thumbs_down"
                              ? "text-zinc-300 bg-white/10 border border-white/20"
                              : "text-zinc-500 hover:text-zinc-200 hover:bg-white/10 border border-transparent hover:border-white/30"
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
                <span className="text-[10px] text-zinc-500 mt-2 px-2 font-medium tracking-wide">
                  {msg.timestamp}
                </span>
              </AnimatedContent>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <AnimatedContent
                distance={20}
                direction="vertical"
                reverse={false}
                className="flex items-start space-x-3"
              >
                <div className="max-w-md bg-white/5 border border-white/10 rounded-3xl rounded-bl-sm p-5 shadow-xl backdrop-blur-md">
                  <div className="flex items-center space-x-3 text-sm text-zinc-400">
                    <span className="w-2.5 h-2.5 rounded-full bg-zinc-400 animate-ping"></span>
                    <span className="font-medium tracking-wide">
                      Classifying intent & retrieving curriculum chunks...
                    </span>
                  </div>
                </div>
              </AnimatedContent>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Form Bar */}
      <div className="p-4 sm:p-6 bg-black/40 border-t border-white/10 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex items-center space-x-3">
            <input
              id="chat-input-field"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about courses, units, prerequisites, credits, or regulations..."
              disabled={isLoading}
              className="flex-1 px-5 py-4 text-sm bg-white/5 border border-white/10 rounded-2xl focus:outline-none focus:ring-2 focus:ring-white/30 focus:bg-white/10 text-white transition-all disabled:opacity-50 shadow-inner"
            />
            
            <StarBorder as="button" type="submit" disabled={!input.trim() || isLoading} className="!p-0 border-0 bg-transparent rounded-2xl shadow-[0_0_20px_rgba(255,255,255,0.15)]">
              <div className="px-6 py-4 bg-zinc-700 hover:bg-zinc-600 text-white rounded-2xl font-semibold text-sm transition-all disabled:opacity-50 disabled:bg-white/10 flex items-center space-x-2 cursor-pointer h-full border border-white/20">
                <span>Send</span>
                <Send className="w-4 h-4 ml-1" />
              </div>
            </StarBorder>
          </form>
          <div className="flex items-center justify-between text-[10px] text-zinc-500 mt-3 px-2 font-semibold uppercase tracking-widest">
            <span>Official B.Tech CSE Curriculum Knowledge Base</span>
            <span className="flex items-center"><span className="w-1.5 h-1.5 rounded-full bg-zinc-400 mr-1.5 shadow-[0_0_5px_rgba(255,255,255,0.15)]"></span>Guardrails Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
