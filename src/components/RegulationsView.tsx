import React from "react";
import { Award, Clock, FileCheck, MessageSquare } from "lucide-react";
import { AnimatedContent } from "../reactbits/AnimatedContent";
import { SpotlightCard } from "../reactbits/SpotlightCard";

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
    <div className="flex-1 overflow-y-auto bg-transparent p-4 sm:p-6 lg:p-8 custom-scrollbar">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header Banner */}
        <AnimatedContent distance={20} direction="vertical" reverse={false}>
          <div className="bg-white/5 p-6 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-md flex flex-col sm:flex-row sm:items-center justify-between gap-5">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center text-zinc-300 border border-white/20">
                  <FileCheck className="w-5 h-5" />
                </div>
                <span>Official Academic Regulations Quick Reference</span>
              </h2>
              <p className="text-sm text-zinc-400 mt-2 font-medium">
                B.Tech Academic Regulations, Attendance Mandates, Examination & Grading Scheme
              </p>
            </div>
            <button
              id="regulations-inquire-btn"
              onClick={() => onAskRegulation("What are the attendance requirements and consequences of shortage?")}
              className="px-5 py-2.5 bg-zinc-700 hover:bg-zinc-600 text-white rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer shrink-0 self-start sm:self-auto shadow-[0_0_15px_rgba(255,255,255,0.15)] border border-white/20"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Ask Bot About Attendance</span>
            </button>
          </div>
        </AnimatedContent>

        {/* 4 Essential Regulatory Pillars */}
        <AnimatedContent distance={30} direction="vertical" reverse={false}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 1. Attendance Mandate */}
            <SpotlightCard className="p-6 rounded-3xl space-y-4" spotlightColor="rgba(255, 255, 255, 0.15)">
              <div className="flex items-center space-x-4 text-zinc-300">
                <div className="p-3 rounded-2xl bg-white/10 text-zinc-300 border border-white/20 shadow-inner">
                  <Clock className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-white">1. Attendance Mandate</h3>
                  <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">Clause 4.1 – 4.3</span>
                </div>
              </div>

              <div className="space-y-3 text-sm text-zinc-300 leading-relaxed pt-2">
                <div className="bg-white/5 p-4 rounded-xl border border-white/10 shadow-inner">
                  <strong className="text-white block mb-1">75% Minimum Requirement</strong>
                  Students must secure a minimum aggregate attendance of <strong>75%</strong> in all registered courses in a semester to be eligible for End-Semester Examinations (ESE).
                </div>
                <div className="bg-white/10 p-4 rounded-xl border border-white/20 text-zinc-100">
                  <strong className="block mb-1 text-zinc-300">Condonation (65% – 74%)</strong>
                  Condonation of shortage up to 10% may be granted by the Academic Council solely on genuine medical grounds upon medical certificate submission and prescribed fee payment.
                </div>
                <div className="bg-white/10 p-4 rounded-xl border border-white/20 text-zinc-100">
                  <strong className="block mb-1 text-zinc-300">Detention (&lt; 65%)</strong>
                  Students securing less than 65% attendance are detained, disqualified from ESE, and must repeat the semester in subsequent academic sessions.
                </div>
              </div>
            </SpotlightCard>

            {/* 2. Examination & Assessment Scheme */}
            <SpotlightCard className="p-6 rounded-3xl space-y-4" spotlightColor="rgba(255, 255, 255, 0.15)">
              <div className="flex items-center space-x-4 text-zinc-300">
                <div className="p-3 rounded-2xl bg-white/10 text-zinc-300 border border-white/20 shadow-inner">
                  <FileCheck className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-white">2. Examination Scheme</h3>
                  <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">40% CIA + 60% ESE</span>
                </div>
              </div>

              <div className="space-y-3 text-sm text-zinc-300 leading-relaxed pt-2">
                <div className="bg-white/5 p-4 rounded-xl border border-white/10 shadow-inner">
                  <strong className="text-white block mb-1">Continuous Internal Assessment (40 Marks)</strong>
                  Comprises Mid-term tests (20 marks), quizzes/assignments (10 marks), and classroom seminar/case studies (10 marks).
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/10 shadow-inner">
                  <strong className="text-white block mb-1">End Semester Examination (60 Marks)</strong>
                  3-hour comprehensive written exam covering all 5 course units. Minimum 40% (24/60) required to pass ESE component.
                </div>
                <div className="bg-white/10 p-4 rounded-xl border border-white/20 text-zinc-100">
                  <strong className="block mb-1 text-zinc-300">Combined Passing Standard</strong>
                  Minimum aggregate score of <strong>40%</strong> (CIA + ESE combined) is mandatory to earn course credits.
                </div>
              </div>
            </SpotlightCard>
          </div>
        </AnimatedContent>

        {/* 10-Point Letter Grading Scale Table */}
        <AnimatedContent distance={40} direction="vertical" reverse={false}>
          <div className="bg-white/5 rounded-3xl border border-white/10 p-6 shadow-2xl backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-3 rounded-2xl bg-white/10 text-zinc-300 border border-white/20 shadow-inner">
                  <Award className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-white">3. 10-Point Letter Grading System</h3>
                  <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">UGC / AICTE Standardized Relative Scale</span>
                </div>
              </div>
              <button
                onClick={() => onAskRegulation("How is CGPA calculated from SGPA and course credits?")}
                className="text-xs text-zinc-300 hover:text-zinc-200 font-semibold bg-white/10 px-3 py-1.5 rounded-lg border border-white/20 transition-colors"
              >
                Ask about SGPA/CGPA formula &rarr;
              </button>
            </div>

            <div className="overflow-x-auto pt-3">
              <table className="w-full text-sm text-left border border-white/10 rounded-xl overflow-hidden shadow-inner bg-black/20">
                <thead className="bg-white/5 text-zinc-300 font-bold uppercase tracking-wider border-b border-white/10">
                  <tr>
                    <th className="px-5 py-4">Letter Grade</th>
                    <th className="px-5 py-4">Description</th>
                    <th className="px-5 py-4">Mark Range (%)</th>
                    <th className="px-5 py-4">Grade Points (G)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-zinc-300">
                  {GRADING_SCALE.map((g) => (
                    <tr key={g.grade} className="hover:bg-white/5 transition-colors">
                      <td className="px-5 py-3 font-mono font-bold text-zinc-300 text-base">{g.grade}</td>
                      <td className="px-5 py-3 font-medium">{g.title}</td>
                      <td className="px-5 py-3">{g.marks}</td>
                      <td className="px-5 py-3 font-bold text-white text-base">{g.points}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </AnimatedContent>
      </div>
    </div>
  );
};
