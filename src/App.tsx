import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { ChatArea } from "./components/ChatArea";
import { CurriculumCatalog } from "./components/CurriculumCatalog";
import { RegulationsView } from "./components/RegulationsView";
import { MultiResourceHub } from "./components/MultiResourceHub";
import { MetricsDashboard } from "./components/MetricsDashboard";
import { RagInspector } from "./components/RagInspector";
import { ChatMessage, SystemHealth } from "./types";

export default function App() {
  const [activeTab, setActiveTab] = useState<"chat" | "catalog" | "regulations" | "resources" | "metrics">("chat");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inspectedMessage, setInspectedMessage] = useState<ChatMessage | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);

  // Initial health check
  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch((err) => console.warn("Failed to fetch system health:", err));
  }, []);

  const handleSendMessage = async (query: string) => {
    if (!query.trim() || isLoading) return;

    const userMessageId = `user-${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMessageId,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Build lightweight chat history for context
      const chatHistory = messages.slice(-4).map((m) => ({
        sender: m.sender,
        text: m.text,
      }));

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          chat_history: chatHistory,
          top_k: 4,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();

      const botMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: data.answer || "No response generated.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        intent: data.intent,
        intent_confidence: data.intent_confidence,
        entities: data.entities,
        sources: data.sources || [],
        is_grounded: data.is_grounded,
        overall_confidence: data.overall_confidence,
        confidence_breakdown: data.confidence_breakdown,
        latency_ms: data.latency_ms,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      console.error("Chat request failed:", err);
      const errorMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: "I encountered an issue processing your academic query. Please ensure the backend service is running and try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        intent: "error",
        intent_confidence: 0,
        is_grounded: false,
        overall_confidence: 0,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = (messageId: string, type: "thumbs_up" | "thumbs_down") => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, feedback: type } : msg))
    );

    const targetMsg = messages.find((m) => m.id === messageId);
    if (targetMsg) {
      fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: targetMsg.text,
          answer: targetMsg.text,
          intent: targetMsg.intent || "unknown",
          feedback: type,
        }),
      }).catch((e) => console.warn("Failed to submit feedback:", e));
    }
  };

  const handleAskExternal = (prompt: string) => {
    setActiveTab("chat");
    handleSendMessage(prompt);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 antialiased selection:bg-indigo-500 selection:text-white">
      {/* Header */}
      <Header activeTab={activeTab} onSelectTab={setActiveTab} health={health} />

      {/* Main Tab Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {activeTab === "chat" && (
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onFeedback={handleFeedback}
            onInspectMessage={(msg) => setInspectedMessage(msg)}
          />
        )}

        {activeTab === "catalog" && (
          <CurriculumCatalog onAskCourse={handleAskExternal} />
        )}

        {activeTab === "resources" && (
          <MultiResourceHub onAskResource={handleAskExternal} />
        )}

        {activeTab === "regulations" && (
          <RegulationsView onAskRegulation={handleAskExternal} />
        )}

        {activeTab === "metrics" && <MetricsDashboard />}

        {/* Slide-out RAG Inspector Drawer */}
        {inspectedMessage && (
          <RagInspector
            message={inspectedMessage}
            onClose={() => setInspectedMessage(null)}
          />
        )}
      </main>
    </div>
  );
}
