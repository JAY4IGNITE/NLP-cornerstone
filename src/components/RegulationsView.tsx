import React from "react";
import { Award, Clock, FileCheck, HelpCircle, ShieldAlert, BookOpen, MessageSquare } from "lucide-react";

interface RegulationsViewProps {
  onAskRegulation: (query: string) => void;
}

export const RegulationsView: React.FC<RegulationsViewProps> = ({ onAskRegulation }) => {
  const GRADING_SCALE = [
    { grade: "O", title: "Outstanding", marks: "90 – 100", points: "10.0" },
    { grade: "A+", title: "Excellent", marks: "80 – 89", points: "9.0" },
    { grade: "A", title: "Very Good", marks: "70 – 79", points: "8.0" },
    { grade: "B+", title: "Good", marks: "60 – 69", points: "7.0" },
    { grade: "B", title: "Above Average", marks: "55 – 59", points: "6.0" },
    { grade: "C", title: "Average", marks: "50 – 54", points: "5.0" },
    { grade: "P", title: "Pass", marks: "40 – 49", points: "4.0" },
    { grade: "F", title: "Fail", marks: "< 40", points: "0.0" },
    { grade: "Ab", title: "Absent", marks: "—", points: "0.0" },
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header Banner */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
              <FileCheck className="w-5 h-5 text-indigo-600" />
              <span>Official Academic Regulations Quick Reference</span>
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              B.Tech Academic Regulations, Attendance Mandates, Examination & Grading Scheme
            </p>
          </div>
          <button
            id="regulations-inquire-btn"
            onClick={() => onAskRegulation("What are the attendance requirements and consequences of shortage?")}
            className="px-3.5 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-xs font-semibold transition-colors flex items-center space-x-1.5 cursor-pointer shrink-0 self-start sm:self-auto"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Ask Bot About Attendance</span>
          </button>
        </div>

        {/* 4 Essential Regulatory Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* 1. Attendance Mandate */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-3">
            <div className="flex items-center space-x-2.5 text-indigo-900">
              <div className="p-2 rounded-lg bg-indigo-50 text-indigo-700">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900">1. Attendance Mandate</h3>
                <span className="text-[11px] text-slate-500">Clause 4.1 – 4.3</span>
              </div>
            </div>

            <div className="space-y-2 text-xs text-slate-700 leading-relaxed pt-1">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <strong className="text-slate-900 block mb-0.5">75% Minimum Requirement</strong>
                Students must secure a minimum aggregate attendance of <strong>75%</strong> in all registered courses in a semester to be eligible for End-Semester Examinations (ESE).
              </div>
              <div className="bg-amber-50/60 p-3 rounded-xl border border-amber-200/60 text-amber-900">
                <strong className="block mb-0.5">Condonation (65% – 74%)</strong>
                Condonation of shortage up to 10% may be granted by the Academic Council solely on genuine medical grounds upon medical certificate submission and prescribed fee payment.
              </div>
              <div className="bg-rose-50/60 p-3 rounded-xl border border-rose-200/60 text-rose-900">
                <strong className="block mb-0.5">Detention (&lt; 65%)</strong>
                Students securing less than 65% attendance are detained, disqualified from ESE, and must repeat the semester in subsequent academic sessions.
              </div>
            </div>
          </div>

          {/* 2. Examination & Assessment Scheme */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-3">
            <div className="flex items-center space-x-2.5 text-indigo-900">
              <div className="p-2 rounded-lg bg-indigo-50 text-indigo-700">
                <FileCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900">2. Examination Scheme</h3>
                <span className="text-[11px] text-slate-500">40% CIA + 60% ESE</span>
              </div>
            </div>

            <div className="space-y-2 text-xs text-slate-700 leading-relaxed pt-1">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <strong className="text-slate-900 block mb-0.5">Continuous Internal Assessment (40 Marks)</strong>
                Comprises Mid-term tests (20 marks), quizzes/assignments (10 marks), and classroom seminar/case studies (10 marks).
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <strong className="text-slate-900 block mb-0.5">End Semester Examination (60 Marks)</strong>
                3-hour comprehensive written exam covering all 5 course units. Minimum 40% (24/60) required to pass ESE component.
              </div>
              <div className="bg-emerald-50/60 p-3 rounded-xl border border-emerald-200/60 text-emerald-900">
                <strong className="block mb-0.5">Combined Passing Standard</strong>
                Minimum aggregate score of <strong>40%</strong> (CIA + ESE combined) is mandatory to earn course credits.
              </div>
            </div>
          </div>
        </div>

        {/* 10-Point Letter Grading Scale Table */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-indigo-50 text-indigo-700">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900">3. 10-Point Letter Grading System</h3>
                <span className="text-[11px] text-slate-500">UGC / AICTE Standardized Relative Scale</span>
              </div>
            </div>
            <button
              onClick={() => onAskRegulation("How is CGPA calculated from SGPA and course credits?")}
              className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Ask about SGPA/CGPA formula &rarr;
            </button>
          </div>

          <div className="overflow-x-auto pt-2">
            <table className="w-full text-xs text-left border border-slate-200 rounded-lg overflow-hidden">
              <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-2.5">Letter Grade</th>
                  <th className="px-4 py-2.5">Description</th>
                  <th className="px-4 py-2.5">Mark Range (%)</th>
                  <th className="px-4 py-2.5">Grade Points (G)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {GRADING_SCALE.map((g) => (
                  <tr key={g.grade} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-2 font-mono font-bold text-indigo-700">{g.grade}</td>
                    <td className="px-4 py-2 font-medium">{g.title}</td>
                    <td className="px-4 py-2">{g.marks}</td>
                    <td className="px-4 py-2 font-semibold text-slate-900">{g.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
