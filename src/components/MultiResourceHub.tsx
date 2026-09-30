import React, { useState, useEffect } from "react";
import {
  Database,
  Cloud,
  RefreshCw,
  Search,
  BookOpen,
  FileText,
  Building2,
  Bookmark,
  Calendar,
  Layers,
  ArrowRight,
  CheckCircle2,
  PlusCircle,
  FileCode,
  Zap,
} from "lucide-react";
import { ResourcesCatalogResponse, CloudflareStatusResponse } from "../types";
import { SpotlightCard } from "../reactbits/SpotlightCard";
import { AnimatedContent } from "../reactbits/AnimatedContent";

interface MultiResourceHubProps {
  onAskResource: (prompt: string) => void;
}

export const MultiResourceHub: React.FC<MultiResourceHubProps> = ({ onAskResource }) => {
  const [catalog, setCatalog] = useState<ResourcesCatalogResponse | null>(null);
  const [cfStatus, setCfStatus] = useState<CloudflareStatusResponse | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // Form for custom snippet
  const [customTitle, setCustomTitle] = useState("");
  const [customCategory, setCustomCategory] = useState("campus_services");
  const [customCourse, setCustomCourse] = useState("");
  const [customContent, setCustomContent] = useState("");
  const [isSubmittingCustom, setIsSubmittingCustom] = useState(false);

  // Fetch catalog & Cloudflare status
  const loadData = () => {
    fetch("/api/resources")
      .then((res) => res.json())
      .then((data) => setCatalog(data))
      .catch((e) => console.warn("Failed to fetch resources catalog:", e));

    fetch("/api/cloudflare/status")
      .then((res) => res.json())
      .then((data) => setCfStatus(data))
      .catch((e) => console.warn("Failed to fetch Cloudflare status:", e));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSyncAll = async () => {
    setIsSyncing(true);
    setSyncMessage(null);
    try {
      const res = await fetch("/api/resources/sync", { method: "POST" });
      const data = await res.json();
      setSyncMessage(data.message || "Sync complete!");
      loadData();
      setTimeout(() => setSyncMessage(null), 4000);
    } catch (e: any) {
      setSyncMessage("Sync error occurred.");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleLiveSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const categoryParam = activeCategory !== "all" ? `&category=${activeCategory}` : "";
      const res = await fetch(`/api/resources/search?q=${encodeURIComponent(searchQuery)}${categoryParam}`);
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (e) {
      console.warn("Search failed:", e);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddCustomSnippet = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customTitle.trim() || !customContent.trim()) return;
    setIsSubmittingCustom(true);
    try {
      const res = await fetch("/api/resources/custom", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: customTitle,
          category: customCategory,
          course_code: customCourse,
          content: customContent,
          author: "Student User"
        })
      });
      if (res.ok) {
        setShowAddModal(false);
        setCustomTitle("");
        setCustomContent("");
        setCustomCourse("");
        loadData();
      }
    } catch (e) {
      console.warn("Error adding custom snippet:", e);
    } finally {
      setIsSubmittingCustom(false);
    }
  };

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case "curriculum": return <BookOpen className="w-5 h-5 text-zinc-300" />;
      case "regulations": return <FileText className="w-5 h-5 text-zinc-300" />;
      case "campus_services": return <Building2 className="w-5 h-5 text-zinc-300" />;
      case "study_guides": return <Bookmark className="w-5 h-5 text-zinc-300" />;
      case "academic_calendar": return <Calendar className="w-5 h-5 text-zinc-300" />;
      default: return <Layers className="w-5 h-5 text-zinc-400" />;
    }
  };

  const sampleQuestions: Record<string, string[]> = {
    curriculum: [
      "What are the prerequisites for Compiler Design (CS304)?",
      "Which topics are taught in Unit 4 of Database Management Systems?",
      "Explain the syllabus and credits for Machine Learning (CS401)"
    ],
    regulations: [
      "What is the procedure and fee for semester revaluation?",
      "What is the minimum attendance requirement and medical condonation limit?",
      "What are the penalties for examination malpractice?"
    ],
    campus_services: [
      "What are the hostel curfew and mess timings?",
      "How many books can a B.Tech student borrow from the Central Library?",
      "What are the eligibility criteria and package tiers for placements?"
    ],
    study_guides: [
      "Show the Computer Networks subnetting formula and /26 CIDR host count",
      "Explain Banker's Algorithm and deadlock safety in Operating Systems",
      "What are the First and Follow rules in Compiler Design parsing?"
    ],
    academic_calendar: [
      "When are the Mid-Term 1 and End-Semester exam dates?",
      "What is the date for course registration and last instructional day?",
      "When is the winter vacation scheduled?"
    ]
  };

  const filteredResources = catalog?.resources.filter((r) =>
    activeCategory === "all" ? true : r.category === activeCategory
  ) || [];

  return (
    <div className="flex-1 overflow-y-auto bg-transparent p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header & Cloudflare Vectorize Status Banner */}
        <AnimatedContent distance={20} direction="vertical" reverse={false}>
          <div className="bg-black/40 backdrop-blur-md rounded-3xl p-8 text-white shadow-2xl border border-white/10 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-white/5 via-transparent to-white/5 pointer-events-none" />
            
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8 relative z-10">
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] uppercase tracking-widest font-semibold bg-white/10 text-zinc-300 border border-white/20">
                    <Cloud className="w-3.5 h-3.5" />
                    <span>Cloudflare Vectorize Active</span>
                  </span>
                  <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] uppercase tracking-widest font-semibold bg-white/10 text-zinc-300 border border-white/20">
                    <Zap className="w-3.5 h-3.5" />
                    <span>Edge Vector Acceleration</span>
                  </span>
                </div>
                <h1 className="text-3xl font-bold tracking-tight">
                  Multi-Resource Academic Knowledge Hub
                </h1>
                <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
                  Integrated across 5 university resources: Curriculum Handbook, Academic Regulations,
                  Campus Student Services, Technical Revision Cheat Sheets, and the Official Academic Calendar.
                </p>
              </div>

              {/* Cloudflare Vector Store Telemetry */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10 text-center min-w-[120px] shadow-inner">
                  <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold mb-1">Total Vectors</p>
                  <p className="text-2xl font-bold text-white">
                    {cfStatus ? cfStatus.total_vectors : "131+"}
                  </p>
                </div>
                <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10 text-center min-w-[120px] shadow-inner">
                  <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold mb-1">Dimensions</p>
                  <p className="text-2xl font-bold text-zinc-300">1024-d</p>
                </div>
                <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10 text-center min-w-[120px] shadow-inner">
                  <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold mb-1">Distance Metric</p>
                  <p className="text-2xl font-bold text-zinc-300">Cosine</p>
                </div>

                <div className="flex flex-col gap-3">
                  <button
                    id="sync-resources-btn"
                    onClick={handleSyncAll}
                    disabled={isSyncing}
                    className="inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-zinc-700 hover:bg-zinc-600 text-white font-semibold text-xs transition-all disabled:opacity-50 shadow-[0_0_15px_rgba(255,255,255,0.15)] border border-white/20"
                  >
                    <RefreshCw className={`w-4 h-4 ${isSyncing ? "animate-spin" : ""}`} />
                    <span>{isSyncing ? "Syncing..." : "Sync All Data"}</span>
                  </button>
                  <button
                    id="add-custom-snippet-btn"
                    onClick={() => setShowAddModal(true)}
                    className="inline-flex items-center justify-center space-x-1.5 px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white font-semibold text-xs border border-white/10 transition-all shadow-inner"
                  >
                    <PlusCircle className="w-4 h-4" />
                    <span>Contribute Note</span>
                  </button>
                </div>
              </div>
            </div>

            {syncMessage && (
              <div className="mt-6 p-3 rounded-xl bg-white/10 text-zinc-300 border border-white/20 text-xs flex items-center space-x-2 font-medium">
                <CheckCircle2 className="w-4 h-4" />
                <span>{syncMessage}</span>
              </div>
            )}
          </div>
        </AnimatedContent>

        {/* Search & Category Filter Navigation */}
        <AnimatedContent distance={20} direction="vertical" reverse={false}>
          <div className="bg-black/40 backdrop-blur-md rounded-2xl p-5 shadow-xl border border-white/10 space-y-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
              {/* Category Filter Pills */}
              <div className="flex flex-wrap gap-2.5">
                <button
                  onClick={() => setActiveCategory("all")}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                    activeCategory === "all"
                      ? "bg-zinc-700 text-white shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                      : "bg-white/5 text-zinc-400 hover:text-white hover:bg-white/10 border border-white/5"
                  }`}
                >
                  All Resources ({catalog?.total_indexed_chunks || 49})
                </button>
                <button
                  onClick={() => setActiveCategory("curriculum")}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                    activeCategory === "curriculum"
                      ? "bg-zinc-700 text-white shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                      : "bg-white/5 text-zinc-400 hover:text-white hover:bg-white/10 border border-white/5"
                  }`}
                >
                  Curriculum ({catalog?.category_breakdown?.curriculum || 26})
                </button>
                <button
                  onClick={() => setActiveCategory("regulations")}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                    activeCategory === "regulations"
                      ? "bg-zinc-700 text-white shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                      : "bg-white/5 text-zinc-400 hover:text-white hover:bg-white/10 border border-white/5"
                  }`}
                >
                  Regulations ({catalog?.category_breakdown?.regulations || 9})
                </button>
                <button
                  onClick={() => setActiveCategory("campus_services")}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                    activeCategory === "campus_services"
                      ? "bg-zinc-700 text-white shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                      : "bg-white/5 text-zinc-400 hover:text-white hover:bg-white/10 border border-white/5"
                  }`}
                >
                  Campus Life ({catalog?.category_breakdown?.campus_services || 8})
                </button>
                <button
                  onClick={() => setActiveCategory("study_guides")}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                    activeCategory === "study_guides"
                      ? "bg-zinc-700 text-white shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                      : "bg-white/5 text-zinc-400 hover:text-white hover:bg-white/10 border border-white/5"
                  }`}
                >
                  Revision Guides ({catalog?.category_breakdown?.study_guides || 5})
                </button>
                <button
                  onClick={() => setActiveCategory("academic_calendar")}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                    activeCategory === "academic_calendar"
                      ? "bg-zinc-700 text-white shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                      : "bg-white/5 text-zinc-400 hover:text-white hover:bg-white/10 border border-white/5"
                  }`}
                >
                  Calendar ({catalog?.category_breakdown?.academic_calendar || 1})
                </button>
              </div>

              {/* Direct Vector Search Input */}
              <form onSubmit={handleLiveSearch} className="flex items-center space-x-3 w-full md:w-auto">
                <div className="relative w-full sm:w-72">
                  <Search className="w-4 h-4 text-zinc-400 absolute left-4 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Vector search chunks..."
                    className="w-full pl-10 pr-4 py-2.5 text-sm bg-black/40 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/30 text-white shadow-inner transition-all"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSearching}
                  className="px-4 py-2.5 bg-zinc-700 hover:bg-zinc-600 text-white text-sm font-semibold rounded-xl transition-all shadow-[0_0_15px_rgba(255,255,255,0.15)] shrink-0 border border-white/20"
                >
                  {isSearching ? "..." : "Search"}
                </button>
              </form>
            </div>
          </div>
        </AnimatedContent>

        {/* Live Vector Search Results if Active */}
        {searchResults.length > 0 && (
          <AnimatedContent distance={30} direction="vertical" reverse={false}>
            <div className="bg-white/10 backdrop-blur-md rounded-3xl p-6 shadow-2xl border border-white/20 space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-zinc-200 flex items-center space-x-2 uppercase tracking-wider">
                  <Search className="w-4 h-4" />
                  <span>Vector Matches for "{searchQuery}" ({searchResults.length})</span>
                </h2>
                <button
                  onClick={() => setSearchResults([])}
                  className="text-xs font-semibold text-zinc-400 hover:text-white transition-colors bg-white/5 px-3 py-1.5 rounded-lg border border-white/10"
                >
                  Clear Results
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {searchResults.map((r, i) => (
                  <div key={i} className="p-5 bg-black/40 rounded-2xl border border-white/5 space-y-3 shadow-inner">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-zinc-300 uppercase tracking-wider bg-white/10 px-2 py-1 rounded-md">
                        {r.metadata?.course_code || r.metadata?.category}
                      </span>
                      <span className="text-zinc-300 bg-white/10 px-2.5 py-1 rounded-md font-mono text-[10px] font-bold border border-white/20">
                        Score: {r.score?.toFixed(4)}
                      </span>
                    </div>
                    <p className="text-sm font-bold text-white line-clamp-1">
                      {r.metadata?.section_heading || r.metadata?.course_name}
                    </p>
                    <p className="text-xs text-zinc-400 line-clamp-3 bg-white/5 p-3 rounded-xl border border-white/5 leading-relaxed">
                      {r.metadata?.text}
                    </p>
                    <div className="flex items-center justify-between text-[11px] text-zinc-500 pt-2 font-medium">
                      <span>{r.metadata?.source_document} (p.{r.metadata?.page_number})</span>
                      <button
                        onClick={() => onAskResource(`Explain the official regulations or syllabus for: ${r.metadata?.section_heading || r.metadata?.course_name}`)}
                        className="text-zinc-300 hover:text-zinc-200 font-bold flex items-center space-x-1.5 transition-colors bg-white/10 px-2.5 py-1.5 rounded-lg border border-white/20"
                      >
                        <span>Ask AI</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </AnimatedContent>
        )}

        {/* Resources Grid */}
        <AnimatedContent distance={40} direction="vertical" reverse={false}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredResources.map((res) => (
              <SpotlightCard
                key={res.id}
                className="p-7 flex flex-col justify-between h-full space-y-6"
                spotlightColor="rgba(255, 255, 255, 0.15)"
              >
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="p-3 rounded-2xl bg-white/5 border border-white/10 shadow-inner">
                        {getCategoryIcon(res.category)}
                      </div>
                      <div>
                        <h3 className="font-bold text-white text-lg">{res.name}</h3>
                        <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mt-1">{res.type}</p>
                      </div>
                    </div>
                    <span className="text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-lg font-bold bg-white/10 text-zinc-300 border border-white/20">
                      {res.total_chunks} Chunks
                    </span>
                  </div>

                  <p className="text-sm text-zinc-400 leading-relaxed font-medium">
                    {res.description}
                  </p>

                  {/* Source PDFs */}
                  <div className="space-y-2 pt-3">
                    <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                      Source Documents:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {res.source_documents.map((doc, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-[11px] font-mono font-semibold bg-black/40 text-zinc-300 border border-white/10 shadow-inner"
                        >
                          <FileCode className="w-3.5 h-3.5 text-zinc-500" />
                          <span>{doc}</span>
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Sample Inquiries */}
                  <div className="space-y-2 pt-3">
                    <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                      Suggested Inquiries for Chatbot:
                    </p>
                    <div className="space-y-2">
                      {(sampleQuestions[res.category] || []).map((q, qIdx) => (
                        <button
                          key={qIdx}
                          onClick={() => onAskResource(q)}
                          className="w-full text-left text-xs text-zinc-300 hover:text-white bg-white/5 hover:bg-white/10 p-3 rounded-xl border border-white/5 hover:border-white/30 transition-all flex items-center justify-between group shadow-inner"
                        >
                          <span className="truncate pr-3 font-medium">{q}</span>
                          <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-200 transition-colors shrink-0" />
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-5 border-t border-white/10 flex items-center justify-between text-xs font-semibold">
                  <span className="inline-flex items-center space-x-1.5 text-zinc-300 bg-white/10 px-3 py-1.5 rounded-lg border border-white/20">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Indexed in Vectorize</span>
                  </span>
                  <button
                    onClick={() => onAskResource(`Provide an executive summary of ${res.name} and what key regulations students should know.`)}
                    className="text-zinc-300 hover:text-zinc-200 flex items-center space-x-1.5 transition-colors bg-white/10 px-3 py-1.5 rounded-lg border border-white/20"
                  >
                    <span>Query Resource</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </SpotlightCard>
            ))}
          </div>
        </AnimatedContent>

        {/* Contributing Modal */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-md flex items-center justify-center p-4">
            <AnimatedContent distance={0} direction="vertical" reverse={false} className="max-w-lg w-full">
              <div className="bg-[#0b0f1e] rounded-3xl w-full p-8 shadow-2xl border border-white/10 space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-white/10">
                  <h3 className="font-bold text-white text-lg">
                    Contribute Knowledge Chunk
                  </h3>
                  <button
                    onClick={() => setShowAddModal(false)}
                    className="p-2 text-zinc-500 hover:text-white hover:bg-white/10 rounded-xl transition-colors"
                  >
                    ✕
                  </button>
                </div>

                <form onSubmit={handleAddCustomSnippet} className="space-y-5 text-sm">
                  <div>
                    <label className="block font-bold text-zinc-300 mb-2 text-xs uppercase tracking-widest">Title / Section</label>
                    <input
                      type="text"
                      required
                      value={customTitle}
                      onChange={(e) => setCustomTitle(e.target.value)}
                      placeholder="e.g. Hostels Wi-Fi Access Point Reset Procedure"
                      className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/30 text-white shadow-inner transition-all"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block font-bold text-zinc-300 mb-2 text-xs uppercase tracking-widest">Category</label>
                      <select
                        value={customCategory}
                        onChange={(e) => setCustomCategory(e.target.value)}
                        className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/30 text-white shadow-inner transition-all appearance-none"
                      >
                        <option value="campus_services">Campus Services & Facilities</option>
                        <option value="curriculum">Curriculum & Course Notes</option>
                        <option value="regulations">Academic Regulations</option>
                        <option value="study_guides">Technical Study Guides</option>
                        <option value="academic_calendar">Academic Calendar</option>
                      </select>
                    </div>
                    <div>
                      <label className="block font-bold text-zinc-300 mb-2 text-xs uppercase tracking-widest">Course Code</label>
                      <input
                        type="text"
                        value={customCourse}
                        onChange={(e) => setCustomCourse(e.target.value)}
                        placeholder="e.g. CS303 or blank"
                        className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/30 text-white shadow-inner transition-all"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block font-bold text-zinc-300 mb-2 text-xs uppercase tracking-widest">Snippet Content</label>
                    <textarea
                      required
                      rows={5}
                      value={customContent}
                      onChange={(e) => setCustomContent(e.target.value)}
                      placeholder="Enter the official text, instructions, or formula guidelines..."
                      className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/30 text-white shadow-inner transition-all"
                    />
                  </div>

                  <div className="flex items-center justify-end space-x-3 pt-4 border-t border-white/10">
                    <button
                      type="button"
                      onClick={() => setShowAddModal(false)}
                      className="px-5 py-2.5 border border-white/10 rounded-xl font-semibold text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmittingCustom}
                      className="px-5 py-2.5 bg-zinc-700 hover:bg-zinc-600 text-white rounded-xl font-semibold shadow-[0_0_15px_rgba(255,255,255,0.15)] transition-all disabled:opacity-50 border border-white/20"
                    >
                      {isSubmittingCustom ? "Indexing..." : "Index into Vectorize"}
                    </button>
                  </div>
                </form>
              </div>
            </AnimatedContent>
          </div>
        )}
      </div>
    </div>
  );
};
