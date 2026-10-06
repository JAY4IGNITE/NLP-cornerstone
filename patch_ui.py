import re

def patch_welcome():
    path = 'c:/Users/ramuv/NLP-cornerstone/src/components/Welcome.tsx'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    replacement = """import { useEffect, useRef } from 'react';
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
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(replacement)


def patch_message_bubble():
    path = 'c:/Users/ramuv/NLP-cornerstone/src/components/MessageBubble.tsx'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We will inject GSAP into the component
    if "import gsap from 'gsap';" not in content:
        content = content.replace("import { useState } from 'react';", "import { useState, useEffect, useRef } from 'react';\nimport gsap from 'gsap';")
    
    # Wrap returns with ref and animate
    new_user = """  const bubbleRef = useRef<HTMLElement>(null);
  useEffect(() => {
    if (bubbleRef.current) {
      gsap.fromTo(bubbleRef.current, { opacity: 0, y: 15, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: 'power2.out' });
    }
  }, []);

  if (message.kind === 'user') return <article ref={bubbleRef} className="user-message" aria-label="Your message"><div>{message.text}</div></article>;"""
    
    content = re.sub(r"  if \(message\.kind === 'user'\) return <article.*?article>;", new_user, content)

    # For assistant message
    new_assistant = """  return <article ref={bubbleRef} className="assistant-message" aria-label="CampusAI answer">"""
    content = content.replace("""  return <article className="assistant-message" aria-label="CampusAI answer">""", new_assistant)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def patch_css():
    path = 'c:/Users/ramuv/NLP-cornerstone/src/index.css'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Redesign variables entirely for a stunning aesthetic
    css_vars = """@import "tailwindcss";

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  font-family: 'Outfit', system-ui, -apple-system, sans-serif;
  color: #1c1c1c;
  background: #fdfdfc;
  font-synthesis: none;
  -webkit-font-smoothing: antialiased;
  
  --bg: #fdfdfc;
  --sidebar: #f5f5f4;
  --surface: #ffffff;
  --surface-hover: #f0f0f0;
  --ink: #1c1c1c;
  --muted: #737373;
  --subtle: #a3a3a3;
  --line: #e5e5e5;
  --accent: #ff4d00; /* Vivid modern orange */
  --accent-hover: #e64500;
  --accent-soft: rgba(255, 77, 0, 0.08);
  --green: #0ea5e9; /* Sky blue for contrast */
  --shadow: 0 10px 40px -10px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.03);
  color-scheme: light;
}

[data-theme="dark"] {
  --bg: #09090b;
  --sidebar: #0f0f11;
  --surface: #121214;
  --surface-hover: #1f1f22;
  --ink: #f9f9f9;
  --muted: #a1a1aa;
  --subtle: #52525b;
  --line: #27272a;
  --accent: #ff5714;
  --accent-hover: #ff763f;
  --accent-soft: rgba(255, 87, 20, 0.12);
  --green: #38bdf8;
  --shadow: 0 10px 40px -10px rgba(0,0,0,0.4);
  color-scheme: dark;
}

* { box-sizing: border-box; scrollbar-width: thin; scrollbar-color: var(--line) transparent; }
body { margin: 0; font-family: 'Outfit', sans-serif; letter-spacing: -0.01em; }"""
    
    content = re.sub(r'@import "tailwindcss";.*?body \{ margin: 0; \}', css_vars, content, flags=re.DOTALL)
    
    # Change fonts of headings to Space Grotesk
    content = content.replace("""font-family: Georgia, "Times New Roman", serif;""", """font-family: 'Space Grotesk', sans-serif;""")
    content = content.replace("""font-family: Georgia, serif;""", """font-family: 'Space Grotesk', sans-serif;""")

    # Enhance components (suggestion boxes)
    content = content.replace(""".suggestion:hover:not(:disabled) { border-color: var(--accent); background: var(--accent-soft); transform: translateY(-2px); }""",
""".suggestion:hover:not(:disabled) { border-color: var(--accent); background: var(--surface); transform: translateY(-4px); box-shadow: var(--shadow); }""")

    # Refine message bubbles to look incredibly polished
    content = content.replace(""".user-message > div { background: var(--sidebar); border: 1px solid var(--line); border-radius: 16px 16px 4px 16px; max-width: 86%; padding: 13px 18px; font-size: 14px; line-height: 1.7; white-space: pre-wrap; overflow-wrap: anywhere; }""",
""".user-message > div { background: var(--ink); color: var(--bg); border-radius: 20px 20px 4px 20px; max-width: 86%; padding: 14px 20px; font-size: 15px; font-weight: 400; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; box-shadow: var(--shadow); }""")

    content = content.replace(""".assistant-message { min-width: 0; }""",
""".assistant-message { min-width: 0; padding: 4px; }""")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


patch_welcome()
patch_message_bubble()
patch_css()
print("UI thoroughly redesigned.")
