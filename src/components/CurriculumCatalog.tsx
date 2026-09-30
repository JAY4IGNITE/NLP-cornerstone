import React, { useState, useEffect } from "react";
import { Search, BookOpen, Layers, ChevronRight, X, MessageSquare, Award } from "lucide-react";
import { CourseSummary, CourseDetail } from "../types";
import { SpotlightCard } from "../reactbits/SpotlightCard";
import { AnimatedContent } from "../reactbits/AnimatedContent";

interface CurriculumCatalogProps {
  onAskCourse: (query: string) => void;
}

const FALLBACK_COURSES: CourseSummary[] = [
  { course_code: "CS201", course_name: "Data Structures and Algorithms", branch: "CSE", semester: 3, total_units: 5, sections_count: 8 },
  { course_code: "CS301", course_name: "Database Management Systems", branch: "CSE", semester: 5, total_units: 5, sections_count: 8 },
  { course_code: "CS302", course_name: "Operating Systems", branch: "CSE", semester: 5, total_units: 5, sections_count: 8 },
  { course_code: "CS303", course_name: "Computer Networks", branch: "CSE", semester: 5, total_units: 5, sections_count: 8 },
  { course_code: "CS304", course_name: "Compiler Design", branch: "CSE", semester: 6, total_units: 5, sections_count: 8 },
  { course_code: "CS305", course_name: "Web Technologies", branch: "CSE", semester: 6, total_units: 5, sections_count: 8 },
  { course_code: "CS306", course_name: "Software Engineering", branch: "CSE", semester: 6, total_units: 5, sections_count: 8 },
  { course_code: "CS401", course_name: "Machine Learning", branch: "CSE", semester: 7, total_units: 5, sections_count: 8 },
  { course_code: "CS402", course_name: "Artificial Intelligence", branch: "CSE", semester: 7, total_units: 5, sections_count: 8 },
  { course_code: "CS403", course_name: "Cloud Computing", branch: "CSE", semester: 8, total_units: 5, sections_count: 8 },
];

export const CurriculumCatalog: React.FC<CurriculumCatalogProps> = ({ onAskCourse }) => {
  const [courses, setCourses] = useState<CourseSummary[]>(FALLBACK_COURSES);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSemester, setSelectedSemester] = useState<number | null>(null);
  const [selectedCourse, setSelectedCourse] = useState<CourseDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  useEffect(() => {
    fetch("/api/curriculum/courses")
      .then((res) => res.json())
      .then((data) => {
        if (data.courses && data.courses.length > 0) {
          setCourses(data.courses);
        }
      })
      .catch(() => {
        // use fallback courses
      });
  }, []);

  const handleOpenDetail = (courseCode: string) => {
    setIsLoadingDetail(true);
    fetch(`/api/curriculum/courses/${courseCode}`)
      .then((res) => res.json())
      .then((data) => {
        setSelectedCourse(data);
        setIsLoadingDetail(false);
      })
      .catch(() => {
        setIsLoadingDetail(false);
      });
  };

  const filteredCourses = courses.filter((c) => {
    const matchesSearch =
      c.course_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.course_code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSem = selectedSemester === null || c.semester === selectedSemester;
    return matchesSearch && matchesSem;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-transparent p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Title and Controls */}
        <AnimatedContent distance={20} direction="vertical" reverse={false}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white/5 p-6 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-md">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center text-zinc-300 border border-white/20">
                  <BookOpen className="w-5 h-5" />
                </div>
                <span>Official B.Tech CSE Curriculum</span>
              </h2>
              <p className="text-sm text-zinc-400 mt-2 max-w-lg">
                Accredited courses, credits, unit syllabi, prerequisites, and learning outcomes
              </p>
            </div>

            {/* Search & Semester Filters */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-3" />
                <input
                  id="catalog-search-input"
                  type="text"
                  placeholder="Search course or code..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2.5 text-sm bg-black/40 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/30 focus:bg-white/10 text-white transition-all w-64 shadow-inner"
                />
              </div>

              <div className="flex items-center space-x-1.5 p-1.5 bg-black/40 border border-white/10 rounded-xl shadow-inner">
                <button
                  id="sem-filter-all"
                  onClick={() => setSelectedSemester(null)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    selectedSemester === null
                      ? "bg-zinc-700 text-white shadow-[0_0_10px_rgba(255,255,255,0.15)]"
                      : "text-zinc-400 hover:text-white hover:bg-white/10"
                  }`}
                >
                  All
                </button>
                {[3, 5, 6, 7, 8].map((sem) => (
                  <button
                    key={sem}
                    id={`sem-filter-${sem}`}
                    onClick={() => setSelectedSemester(sem)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      selectedSemester === sem
                        ? "bg-zinc-700 text-white shadow-[0_0_10px_rgba(255,255,255,0.15)]"
                        : "text-zinc-400 hover:text-white hover:bg-white/10"
                    }`}
                  >
                    Sem {sem}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </AnimatedContent>

        {/* Courses Grid */}
        <AnimatedContent distance={30} direction="vertical" reverse={false}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredCourses.map((c) => (
              <SpotlightCard
                key={c.course_code}
                className="p-6 flex flex-col justify-between"
                spotlightColor="rgba(255, 255, 255, 0.15)"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-mono font-bold text-xs px-2.5 py-1 rounded-md bg-white/10 text-zinc-200 border border-white/20">
                      {c.course_code}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 bg-white/5 border border-white/10 px-2.5 py-1 rounded-md">
                      Semester {c.semester}
                    </span>
                  </div>

                  <h3 className="font-bold text-white text-base leading-snug mt-2 mb-3">
                    {c.course_name}
                  </h3>

                  <div className="flex items-center space-x-4 text-xs text-zinc-400 mt-4 pt-4 border-t border-white/10">
                    <span className="flex items-center font-medium">
                      <Layers className="w-4 h-4 mr-1.5 text-zinc-500" />
                      5 Units
                    </span>
                    <span className="flex items-center font-medium">
                      <Award className="w-4 h-4 mr-1.5 text-zinc-500" />
                      4.0 Credits
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-3 mt-6 pt-4 border-t border-white/10">
                  <button
                    id={`view-detail-${c.course_code}`}
                    onClick={() => handleOpenDetail(c.course_code)}
                    className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl text-xs font-semibold transition-all flex items-center justify-center space-x-1.5 cursor-pointer"
                  >
                    <span>Syllabus & Units</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    id={`ask-about-${c.course_code}`}
                    onClick={() => onAskCourse(`What are the prerequisites and unit topics for ${c.course_name}?`)}
                    className="p-2 bg-white/10 hover:bg-white/10 border border-white/20 text-zinc-300 rounded-xl transition-all cursor-pointer shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                    title="Ask assistant about this course"
                  >
                    <MessageSquare className="w-4 h-4" />
                  </button>
                </div>
              </SpotlightCard>
            ))}
          </div>
        </AnimatedContent>
      </div>

      {/* Course Detail Modal */}
      {selectedCourse && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <AnimatedContent distance={0} direction="vertical" reverse={false} className="max-w-2xl w-full">
            <div className="bg-[#0b0f1e] rounded-3xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-white/10 overflow-hidden">
              {/* Modal Header */}
              <div className="px-8 py-5 border-b border-white/10 flex items-center justify-between bg-white/5 backdrop-blur-md">
                <div>
                  <div className="flex items-center space-x-3 mb-1.5">
                    <span className="font-mono font-bold text-xs px-2.5 py-1 rounded-md bg-white/10 text-zinc-200 border border-white/20">
                      {selectedCourse.course_code}
                    </span>
                    <span className="text-xs text-zinc-400 font-medium">
                      Semester {selectedCourse.semester} • B.Tech {selectedCourse.branch}
                    </span>
                  </div>
                  <h3 className="font-bold text-white text-xl">
                    {selectedCourse.course_name}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedCourse(null)}
                  className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="flex-1 overflow-y-auto p-8 space-y-6 text-sm text-zinc-300 bg-black/20 custom-scrollbar">
                {selectedCourse.chunks.map((chunk, idx) => (
                  <div key={idx} className="border border-white/10 rounded-2xl p-5 bg-white/5 space-y-3 shadow-inner">
                    <div className="flex items-center justify-between text-zinc-200 font-semibold border-b border-white/10 pb-2">
                      <span>{chunk.section}</span>
                      <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold bg-black/30 px-2 py-1 rounded-md">
                        Page {chunk.page}
                      </span>
                    </div>
                    <p className="whitespace-pre-wrap leading-relaxed font-mono text-[11.5px] pt-1 text-zinc-400">
                      {chunk.text}
                    </p>
                  </div>
                ))}
              </div>

              {/* Modal Footer */}
              <div className="px-8 py-5 border-t border-white/10 bg-white/5 backdrop-blur-md flex items-center justify-between">
                <span className="text-xs text-zinc-500 font-medium">
                  Source: <span className="text-zinc-400">{selectedCourse.document_name}</span>
                </span>
                <button
                  id="modal-ask-btn"
                  onClick={() => {
                    const query = `Provide a full breakdown of prerequisites and syllabus for ${selectedCourse.course_name} (${selectedCourse.course_code})`;
                    setSelectedCourse(null);
                    onAskCourse(query);
                  }}
                  className="px-5 py-2.5 bg-zinc-700 hover:bg-zinc-600 text-white rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer shadow-[0_0_20px_rgba(255,255,255,0.15)] border border-white/20"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Ask Assistant About This</span>
                </button>
              </div>
            </div>
          </AnimatedContent>
        </div>
      )}
    </div>
  );
};
