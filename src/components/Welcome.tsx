import { ArrowUpRight, BookOpen, CalendarDays, GraduationCap, ListChecks } from 'lucide-react';
import { ThinkingOrb } from 'thinking-orbs';

const suggestions = [
  { icon: BookOpen, category: 'Explore a course', text: 'What will I learn in DBMS?', question: 'What topics are covered in the DBMS course?' },
  { icon: ListChecks, category: 'Know the guidelines', text: 'How much attendance do I need?', question: 'What is the minimum attendance requirement?' },
  { icon: CalendarDays, category: 'Plan my semester', text: 'Which subjects are in semester 5?', question: 'Which subjects are offered in Semester 5?' },
  { icon: GraduationCap, category: 'Understand my grades', text: 'How is my CGPA calculated?', question: 'How is CGPA calculated under the academic regulations?' },
];

export function Welcome({ onSuggestion, disabled }: { onSuggestion: (text: string) => void; disabled: boolean }) {
  return <section className="welcome" aria-labelledby="welcome-title">
    <div className="welcome-orb"><ThinkingOrb state="breathing" size={64} aria-label="CampusAI is ready to help" /></div>
    <p className="eyebrow">A little clarity for campus life</p>
    <h1 id="welcome-title">Less searching.<br /><em>More understanding.</em></h1>
    <p className="welcome-description">Your courses, your questions, your next step.<br />Let’s make sense of it together.</p>
    <div className="suggestion-heading"><span>A few places to start</span><span aria-hidden="true">↙</span></div>
    <div className="suggestions">{suggestions.map(({ icon: Icon, category, text, question }) => <button key={category} className="suggestion" disabled={disabled} onClick={() => onSuggestion(question)}>
      <span className="suggestion-category"><Icon size={16} strokeWidth={1.6} />{category}</span>
      <span className="suggestion-question">{text}<ArrowUpRight size={16} /></span>
    </button>)}</div>
  </section>;
}
