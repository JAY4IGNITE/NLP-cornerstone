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
  ExternalLink,
  PlusCircle,
  FileCode,
  ShieldCheck,
  Zap,
  Info
} from "lucide-react";
import { ResourcesCatalogResponse, CloudflareStatusResponse } from "../types";

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
      case "curriculum":
        return <BookOpen className="w-5 h-5 text-indigo-600" />;
      case "regulations":
        return <FileText className="w-5 h-5 text-amber-600" />;
      case "campus_services":
        return <Building2 className="w-5 h-5 text-emerald-600" />;
      case "study_guides":
        return <Bookmark className="w-5 h-5 text-purple-600" />;
      case "academic_calendar":
        return <Calendar className="w-5 h-5 text-rose-600" />;
      default:
        return <Layers className="w-5 h-5 text-slate-600" />;
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
    <div className="flex-1 overflow-y-auto bg-slate-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header & Cloudflare Vectorize Status Banner */}
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-md border border-slate-800">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center space-x-3">
                <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  <Cloud className="w-3.5 h-3.5" />
                  <span>Cloudflare Vectorize Active</span>
                </span>
                <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  <Zap className="w-3.5 h-3.5" />
                  <span>Edge Vector Acceleration</span>
                </span>
              </div>
              <h1 className="text-2xl font-bold tracking-tight">
                Multi-Resource Academic Knowledge Hub
              </h1>
              <p className="text-sm text-slate-300 max-w-2xl">
                Integrated across 5 university datasets: Curriculum Handbook, Academic Regulations,
                Campus Student Services, Technical Revision Cheat Sheets, and the Official Academic Calendar.
              </p>
            </div>

            {/* Cloudflare Vector Store Telemetry */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="bg-white/10 backdrop-blur-xs rounded-xl p-3 border border-white/10 text-center min-w-[110px]">
                <p className="text-xs text-slate-300">Total Vectors</p>
                <p className="text-xl font-bold text-white">
                  {cfStatus ? cfStatus.total_vectors : "131+"}
                </p>
              </div>
              <div className="bg-white/10 backdrop-blur-xs rounded-xl p-3 border border-white/10 text-center min-w-[110px]">
                <p className="text-xs text-slate-300">Dimensions</p>
                <p className="text-xl font-bold text-indigo-300">1024-d</p>
              </div>
              <div className="bg-white/10 backdrop-blur-xs rounded-xl p-3 border border-white/10 text-center min-w-[110px]">
                <p className="text-xs text-slate-300">Distance Metric</p>
                <p className="text-xl font-bold text-emerald-300">Cosine</p>
              </div>

              <div className="flex flex-col gap-2">
                <button
                  id="sync-resources-btn"
                  onClick={handleSyncAll}
                  disabled={isSyncing}
                  className="inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-sm transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? "animate-spin" : ""}`} />
                  <span>{isSyncing ? "Syncing..." : "Sync All Data"}</span>
                </button>
                <button
                  id="add-custom-snippet-btn"
                  onClick={() => setShowAddModal(true)}
                  className="inline-flex items-center justify-center space-x-1.5 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium text-xs border border-white/20 transition-colors"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>Contribute Note</span>
                </button>
              </div>
            </div>
          </div>

          {syncMessage && (
            <div className="mt-4 p-2.5 rounded-lg bg-emerald-500/20 text-emerald-200 border border-emerald-500/30 text-xs flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>{syncMessage}</span>
            </div>
          )}
        </div>

        {/* Search & Category Filter Navigation */}
        <div className="bg-white rounded-xl p-4 shadow-xs border border-slate-200 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Category Filter Pills */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setActiveCategory("all")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === "all"
                    ? "bg-slate-900 text-white shadow-xs"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                All Resources ({catalog?.total_indexed_chunks || 49})
              </button>
              <button
                onClick={() => setActiveCategory("curriculum")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === "curriculum"
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                Curriculum ({catalog?.category_breakdown?.curriculum || 26})
              </button>
              <button
                onClick={() => setActiveCategory("regulations")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === "regulations"
                    ? "bg-amber-600 text-white shadow-xs"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                Regulations ({catalog?.category_breakdown?.regulations || 9})
              </button>
              <button
                onClick={() => setActiveCategory("campus_services")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === "campus_services"
                    ? "bg-emerald-600 text-white shadow-xs"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                Campus Life & Hostel ({catalog?.category_breakdown?.campus_services || 8})
              </button>
              <button
                onClick={() => setActiveCategory("study_guides")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === "study_guides"
                    ? "bg-purple-600 text-white shadow-xs"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                Revision Guides ({catalog?.category_breakdown?.study_guides || 5})
              </button>
              <button
                onClick={() => setActiveCategory("academic_calendar")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === "academic_calendar"
                    ? "bg-rose-600 text-white shadow-xs"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                Calendar ({catalog?.category_breakdown?.academic_calendar || 1})
              </button>
            </div>

            {/* Direct Vector Search Input */}
            <form onSubmit={handleLiveSearch} className="flex items-center space-x-2">
              <div className="relative w-full sm:w-64">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Vector search chunks..."
                  className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                />
              </div>
              <button
                type="submit"
                disabled={isSearching}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg transition-colors shadow-xs"
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </form>
          </div>
        </div>

        {/* Live Vector Search Results if Active */}
        {searchResults.length > 0 && (
          <div className="bg-white rounded-xl p-5 shadow-xs border border-indigo-200 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-900 flex items-center space-x-2">
                <Search className="w-4 h-4 text-indigo-600" />
                <span>Cloudflare Vectorize Matches for "{searchQuery}" ({searchResults.length})</span>
              </h2>
              <button
                onClick={() => setSearchResults([])}
                className="text-xs text-slate-500 hover:text-slate-800"
              >
                Clear Results
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {searchResults.map((r, i) => (
                <div key={i} className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-indigo-700 uppercase">
                      {r.metadata?.course_code || r.metadata?.category}
                    </span>
                    <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-mono text-[11px] border border-emerald-200">
                      Score: {r.score?.toFixed(4)}
                    </span>
                  </div>
                  <p className="text-xs font-medium text-slate-800 line-clamp-1">
                    {r.metadata?.section_heading || r.metadata?.course_name}
                  </p>
                  <p className="text-xs text-slate-600 line-clamp-3 bg-white p-2 rounded border border-slate-100">
                    {r.metadata?.text}
                  </p>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                    <span>{r.metadata?.source_document} (p.{r.metadata?.page_number})</span>
                    <button
                      onClick={() => onAskResource(`Explain the official regulations or syllabus for: ${r.metadata?.section_heading || r.metadata?.course_name}`)}
                      className="text-indigo-600 hover:text-indigo-800 font-medium flex items-center space-x-1"
                    >
                      <span>Ask AI</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Resources Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredResources.map((res) => (
            <div
              key={res.id}
              className="bg-white rounded-xl p-6 shadow-xs border border-slate-200 hover:border-indigo-300 transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 rounded-xl bg-slate-100 border border-slate-200">
                      {getCategoryIcon(res.category)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 text-base">{res.name}</h3>
                      <p className="text-xs text-slate-500">{res.type}</p>
                    </div>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded-full font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {res.total_chunks} Chunks
                  </span>
                </div>

                <p className="text-sm text-slate-600 leading-relaxed">
                  {res.description}
                </p>

                {/* Source PDFs */}
                <div className="space-y-1.5 pt-2">
                  <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Source Documents:
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {res.source_documents.map((doc, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-mono bg-slate-100 text-slate-700 border border-slate-200"
                      >
                        <FileCode className="w-3 h-3 text-slate-500" />
                        <span>{doc}</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Sample Inquiries */}
                <div className="space-y-1.5 pt-2">
                  <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Suggested Inquiries for Chatbot:
                  </p>
                  <div className="space-y-1.5">
                    {(sampleQuestions[res.category] || []).map((q, qIdx) => (
                      <button
                        key={qIdx}
                        onClick={() => onAskResource(q)}
                        className="w-full text-left text-xs text-slate-700 hover:text-indigo-700 bg-slate-50 hover:bg-indigo-50/50 p-2 rounded-lg border border-slate-200/80 transition-colors flex items-center justify-between group"
                      >
                        <span className="truncate pr-2">{q}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600 shrink-0" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="inline-flex items-center space-x-1 text-emerald-700 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Indexed in Vectorize</span>
                </span>
                <button
                  onClick={() => onAskResource(`Provide an executive summary of ${res.name} and what key regulations students should know.`)}
                  className="font-semibold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
                >
                  <span>Query Dataset</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Contributing Modal */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                <h3 className="font-bold text-slate-900 text-base">
                  Contribute Knowledge Chunk to Cloudflare Vectorize
                </h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-slate-400 hover:text-slate-600 text-sm font-semibold"
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleAddCustomSnippet} className="space-y-4 text-xs">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Title / Section</label>
                  <input
                    type="text"
                    required
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    placeholder="e.g. Hostels Wi-Fi Access Point Reset Procedure"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Category</label>
                    <select
                      value={customCategory}
                      onChange={(e) => setCustomCategory(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                    >
                      <option value="campus_services">Campus Services & Facilities</option>
                      <option value="curriculum">Curriculum & Course Notes</option>
                      <option value="regulations">Academic Regulations</option>
                      <option value="study_guides">Technical Study Guides</option>
                      <option value="academic_calendar">Academic Calendar</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Course Code (Optional)</label>
                    <input
                      type="text"
                      value={customCourse}
                      onChange={(e) => setCustomCourse(e.target.value)}
                      placeholder="e.g. CS303 or blank"
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                    />
                  </div>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Snippet Content</label>
                  <textarea
                    required
                    rows={4}
                    value={customContent}
                    onChange={(e) => setCustomContent(e.target.value)}
                    placeholder="Enter the official text, instructions, or formula guidelines..."
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>

                <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-200">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 border border-slate-300 rounded-lg font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmittingCustom}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium shadow-xs"
                  >
                    {isSubmittingCustom ? "Indexing..." : "Index into Vectorize"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
