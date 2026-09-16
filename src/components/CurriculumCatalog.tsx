import React, { useState, useEffect } from "react";
import { Search, BookOpen, Layers, CheckCircle2, ChevronRight, X, MessageSquare, Award } from "lucide-react";
import { CourseSummary, CourseDetail } from "../types";

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
    <div className="flex-1 overflow-y-auto bg-slate-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Title and Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-indigo-600" />
              <span>Official B.Tech CSE Curriculum Catalog</span>
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Accredited courses, credits, unit syllabi, prerequisites, and learning outcomes
            </p>
          </div>

          {/* Search & Semester Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                id="catalog-search-input"
                type="text"
                placeholder="Search course or code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500 text-slate-800"
              />
            </div>

            <div className="flex items-center space-x-1">
              <button
                id="sem-filter-all"
                onClick={() => setSelectedSemester(null)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                  selectedSemester === null
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                All
              </button>
              {[3, 5, 6, 7, 8].map((sem) => (
                <button
                  key={sem}
                  id={`sem-filter-${sem}`}
                  onClick={() => setSelectedSemester(sem)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                    selectedSemester === sem
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  Sem {sem}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Courses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCourses.map((c) => (
            <div
              key={c.course_code}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs hover:shadow-xs hover:border-indigo-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-xs px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {c.course_code}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                    Semester {c.semester}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-sm leading-snug mt-1 mb-2">
                  {c.course_name}
                </h3>

                <div className="flex items-center space-x-4 text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100">
                  <span className="flex items-center">
                    <Layers className="w-3.5 h-3.5 mr-1 text-slate-400" />
                    5 Curricular Units
                  </span>
                  <span className="flex items-center">
                    <Award className="w-3.5 h-3.5 mr-1 text-slate-400" />
                    4.0 Credits
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2 mt-4 pt-3 border-t border-slate-100">
                <button
                  id={`view-detail-${c.course_code}`}
                  onClick={() => handleOpenDetail(c.course_code)}
                  className="flex-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-medium transition-colors flex items-center justify-center space-x-1 cursor-pointer"
                >
                  <span>Syllabus & Units</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
                <button
                  id={`ask-about-${c.course_code}`}
                  onClick={() => onAskCourse(`What are the prerequisites and unit topics for ${c.course_name}?`)}
                  className="p-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg transition-colors cursor-pointer"
                  title="Ask assistant about this course"
                >
                  <MessageSquare className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Course Detail Modal */}
      {selectedCourse && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-xs px-2 py-0.5 rounded-md bg-indigo-100 text-indigo-800">
                    {selectedCourse.course_code}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    Semester {selectedCourse.semester} • B.Tech {selectedCourse.branch}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-base mt-1">
                  {selectedCourse.course_name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedCourse(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/50"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-5 text-xs text-slate-700">
              {selectedCourse.chunks.map((chunk, idx) => (
                <div key={idx} className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-1.5">
                  <div className="flex items-center justify-between text-indigo-900 font-semibold border-b border-slate-200 pb-1.5">
                    <span>{chunk.section}</span>
                    <span className="text-[10px] text-slate-400 font-normal">
                      Page {chunk.page}
                    </span>
                  </div>
                  <p className="whitespace-pre-wrap leading-relaxed text-slate-800 font-mono text-[11px] pt-1">
                    {chunk.text}
                  </p>
                </div>
              ))}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Source: {selectedCourse.document_name}
              </span>
              <button
                id="modal-ask-btn"
                onClick={() => {
                  const query = `Provide a full breakdown of prerequisites and syllabus for ${selectedCourse.course_name} (${selectedCourse.course_code})`;
                  setSelectedCourse(null);
                  onAskCourse(query);
                }}
                className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-medium transition-colors flex items-center space-x-1.5 cursor-pointer"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Ask Assistant About This</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
