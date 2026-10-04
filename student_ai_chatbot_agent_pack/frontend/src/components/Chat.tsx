import { useCallback, useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import type { ChatResult, FeedbackRating } from "../types/chat";
import { isErrorResponse, sendChat, sendFeedback } from "../lib/api";

import { motion, AnimatePresence } from "framer-motion";
import { Send, AlertCircle, ThumbsUp, ThumbsDown, Bot } from "lucide-react";
import LatticeLoader from './LatticeLoader';

interface UserMessage {
  kind: "user";
  id: string;
  text: string;
}

interface AssistantMessage {
  kind: "assistant";
  id: string;
  result: ChatResult;
}

type Message = UserMessage | AssistantMessage;

let messageCounter = 0;
function nextId(): string {
  messageCounter += 1;
  return `m${messageCounter}`;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<Record<string, FeedbackRating>>({});
  const listEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const submit = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    
    setMessages((prev) => [...prev, { kind: "user", id: nextId(), text: trimmed }]);
    setInput("");
    setLoading(true);
    const result = await sendChat(trimmed);
    setMessages((prev) => [...prev, { kind: "assistant", id: nextId(), result }]);
    setLoading(false);
  }, [input, loading]);

  const onKeyDown = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void submit();
    }
  }, [submit]);

  const onFeedback = useCallback((msgId: string, traceId: string, rating: FeedbackRating) => {
    setFeedback((prev) => ({ ...prev, [msgId]: rating }));
    void sendFeedback(traceId, rating);
  }, []);

  return (
    <div className="flex flex-col flex-1 relative bg-[#212121]">
      
      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth">
        {messages.length === 0 && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute inset-0 flex flex-col items-center justify-center space-y-8"
          >
            <h2 className="text-3xl font-semibold text-white">What can I help with?</h2>
          </motion.div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              className={`flex w-full ${msg.kind === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.kind === "user" ? (
                <div className="bg-[#2f2f2f] text-gray-100 px-5 py-3 rounded-[1.5rem] max-w-[80%] whitespace-pre-wrap text-[15px]">
                  {msg.text}
                </div>
              ) : (
                <div className="flex gap-4 w-full max-w-3xl">
                  <div className="w-8 h-8 rounded-full border border-white/10 flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-gray-300" strokeWidth={1.5} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <AssistantBubble 
                      message={msg} 
                      feedback={feedback[msg.id]} 
                      onFeedback={onFeedback} 
                    />
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start w-full max-w-3xl">
            <div className="flex gap-4 w-full">
              <div className="w-8 h-8 rounded-full border border-white/10 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-gray-300" strokeWidth={1.5} />
              </div>
              <div className="flex items-center gap-3 h-8 text-gray-400">
                <LatticeLoader
                  status="working"
                  label="Thinking"
                  doneLabel="Done in"
                  errorLabel="Failed after"
                  pattern="orbit"
                  grid={3}
                  shape="round"
                  doneColor="#22c55e"
                  errorColor="#ef4444"
                  cellSize={4}
                  gap={2}
                  fontSize={14}
                  step={90}
                  idleOpacity={0.15}
                  glow={false}
                  glowColor=""
                  showTimer
                  color="#f5f5f5"
                />
              </div>
            </div>
          </motion.div>
        )}
        <div ref={listEndRef} className="h-4" />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-[#212121] flex justify-center sticky bottom-0 z-10 w-full max-w-3xl mx-auto pb-6 pt-4">
        <div className="w-full flex flex-col gap-2 relative">
          <div className="relative w-full flex items-center gap-2 bg-[#2f2f2f] border border-white/10 rounded-[1.5rem] px-4 py-2 focus-within:border-white/30 transition-colors">
            <textarea
              className="flex-1 bg-transparent text-white py-2 max-h-32 min-h-[24px] resize-none outline-none placeholder:text-gray-400 text-[15px]"
              placeholder="Message CampusAI..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={loading}
              rows={1}
            />
            
            <div className="flex items-center gap-1 pr-1">
              <button
                onClick={submit}
                disabled={!input.trim() || loading}
                className="w-8 h-8 flex items-center justify-center rounded-full transition-all disabled:opacity-30 disabled:hover:bg-transparent bg-white text-black hover:bg-gray-200"
              >
                <Send className="w-4 h-4 mr-0.5 mt-0.5" strokeWidth={2} />
              </button>
            </div>
          </div>
          <div className="text-center text-xs text-gray-500 mt-1">
            CampusAI can make mistakes. Consider verifying important academic information.
          </div>
        </div>
      </div>
    </div>
  );
}

function AssistantBubble({ message, feedback, onFeedback }: any) {
  const { result } = message;

  if (isErrorResponse(result)) {
    return (
      <div className="bg-black border border-white/50 text-white px-5 py-4 rounded-2xl rounded-tl-sm max-w-[85%]">
        <div className="flex items-center gap-2 mb-2 font-bold text-white">
          <AlertCircle className="w-4 h-4" />
          Error {result.code}
        </div>
        <p className="text-sm">{result.message}</p>
      </div>
    );
  }

  const isAbstained = result.status === "abstained";
  
  return (
    <div className="w-full flex flex-col text-gray-100">
      
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded text-gray-400 border border-white/10`}>
          {isAbstained ? 'Abstained' : 'Answered'}
        </span>
        <span className="text-[10px] text-gray-500 font-mono">
          {result.intent.label}
        </span>
      </div>

      <div className="text-[15px] leading-relaxed whitespace-pre-wrap mb-2">
        {result.answer}
      </div>

      {result.citations && result.citations.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-2">Sources</div>
          <div className="space-y-2">
            {result.citations.map((c: any, i: number) => (
              <div key={i} className="flex gap-3 items-start bg-black/20 p-2.5 rounded-lg border border-white/5">
                <span className="text-xs font-bold text-black bg-white px-1.5 py-0.5 rounded">{c.document_id}</span>
                <div className="min-w-0">
                  <div className="text-sm font-medium text-gray-200 truncate">{c.title}</div>
                  <div className="text-xs text-gray-500 truncate">{c.location}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 pt-3 flex items-center gap-2">
        {feedback ? (
          <span className="text-xs text-white font-medium">Feedback recorded ✓</span>
        ) : (
          <>
            <span className="text-xs text-gray-500">Helpful?</span>
            <button onClick={() => onFeedback(message.id, result.trace_id, 'helpful')} className="p-1 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-white">
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button onClick={() => onFeedback(message.id, result.trace_id, 'not_helpful')} className="p-1 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-white">
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </>
        )}
      </div>
    </div>
  );
}
