import { useEffect, useRef } from 'react';
import { ArrowUpRight, BookOpen, CalendarDays, GraduationCap, ListChecks } from 'lucide-react';
import { ThinkingOrb } from 'thinking-orbs';
import gsap from 'gsap';

const suggestions = [
  { icon: BookOpen, category: 'Explore a course', text: 'What will I learn in DBMS?', question: 'What topics are covered in the DBMS course?' },
  { icon: ListChecks, category: 'Know the guidelines', text: 'How much attendance do I need?', question: 'What is the minimum attendance requirement?' },
  { icon: CalendarDays, category: 'Plan my semester', text: 'Which subjects are in semester 5?', question: 'Which subjects are offered in Semester 5?' },
  { icon: GraduationCap, category: 'Understand my grades', text: 'How is my CGPA calculated?', question: 'How is CGPA calculated under the academic regulations?' },
];

export function Welcome({ onSuggestion, disabled }: { onSuggestion: (text: string) => void; disabled: boolean }) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo('.welcome-orb', { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 1, ease: 'power3.out' });
      gsap.fromTo('.eyebrow', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.8, delay: 0.2, ease: 'power2.out' });
      gsap.fromTo('.welcome h1', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, delay: 0.3, ease: 'power3.out' });
      gsap.fromTo('.welcome-description', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.8, delay: 0.4, ease: 'power2.out' });
      gsap.fromTo('.suggestion-heading', { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.5, ease: 'power2.out' });
      gsap.fromTo('.suggestion', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, delay: 0.6, ease: 'back.out(1.2)' });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return <section className="welcome" aria-labelledby="welcome-title" ref={containerRef}>
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
