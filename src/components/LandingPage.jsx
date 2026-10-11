import { ArrowRight, BookOpen, Moon, Sun } from 'lucide-react';
import BrandMark from './UI/BrandMark';
import { TOPICS } from '../lib/topics';
import './LandingPage.css';

export default function LandingPage({ theme, onToggleTheme }) {
  return (
    <div className="landing-page">
      <a className="skip-link" href="#main-content" onClick={event => { event.preventDefault(); document.getElementById('main-content')?.focus(); }}>Skip to content</a>
      <header className="landing-header">
        <a className="brand-home" href="#home" aria-label="CampusNLP home">
          <BrandMark animate={false} />
          <span>Campus<span className="brand-light">NLP</span></span>
        </a>
        <nav className="landing-nav" aria-label="Main navigation">
          <a className="landing-guide-link" href="#guide">Topic guide</a>
          <button className="icon-button" onClick={onToggleTheme} aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}>
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
          <a className="landing-nav-cta" href="#chat">Open assistant <ArrowRight size={15} aria-hidden="true" /></a>
        </nav>
      </header>

      <main id="main-content" tabIndex={-1}>
        <section className="landing-hero" aria-labelledby="landing-title">
          <div className="landing-emblem"><BrandMark /></div>
          <p className="landing-eyebrow">A LITTLE CLARITY FOR CAMPUS LIFE</p>
          <h1 id="landing-title">Your campus,<br /><span>a little clearer.</span></h1>
          <p className="landing-description">Less time searching through handbooks. More time for what matters. Find answers to your academic questions, with sources to guide you.</p>
          <a className="primary-button landing-primary" href="#chat">Start a conversation <ArrowRight size={17} aria-hidden="true" /></a>
          <p className="landing-caption">No account needed. Just a question.</p>
        </section>

        <section className="landing-topics" aria-labelledby="landing-topics-title">
          <div className="landing-topics-intro">
            <p className="landing-eyebrow">A PLACE TO START</p>
            <h2 id="landing-topics-title">Everyday questions.<br />A clearer next step.</h2>
            <p>Explore the curriculum and academic regulations in our demo knowledge collection.</p>
            <a className="text-button" href="#guide"><BookOpen size={15} aria-hidden="true" /> Explore the topic guide <ArrowRight size={14} aria-hidden="true" /></a>
          </div>
          <ul className="landing-topic-list">
            {TOPICS.slice(0, 4).map((topic, index) => (
              <li key={topic.id}>
                <a href="#guide">
                  <span className="landing-topic-number" aria-hidden="true">0{index + 1}</span>
                  <span>{topic.title}</span>
                  <ArrowRight size={17} aria-hidden="true" />
                </a>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer className="landing-footer">
        <span>CampusNLP <span className="landing-footer-dot" aria-hidden="true">·</span> Your campus, clarified.</span>
        <span>Grounded in sources. Built for students.</span>
      </footer>
    </div>
  );
}
