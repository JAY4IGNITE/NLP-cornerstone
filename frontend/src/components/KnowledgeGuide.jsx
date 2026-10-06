import {
  ArrowUpRight,
  BookOpen,
  CalendarCheck,
  ClipboardList,
  GraduationCap,
  Info,
  Route,
  Target,
} from 'lucide-react';
import { TOPICS } from '../lib/topics';

const TOPIC_ICONS = {
  BookOpen,
  CalendarCheck,
  ClipboardList,
  GraduationCap,
  Route,
  Target,
};

export default function KnowledgeGuide({ onAsk }) {
  return (
    <section className="knowledge-view" aria-labelledby="knowledge-heading">
      <p className="page-eyebrow">KNOWLEDGE GUIDE</p>
      <h1 className="page-heading" id="knowledge-heading">A little clarity for campus life.</h1>
      <p className="page-description">
        Explore the curriculum and academic rules in the project’s knowledge base.
        Choose a topic to start with a useful question.
      </p>

      <div className="topic-list">
        {TOPICS.map((topic) => {
          const Icon = TOPIC_ICONS[topic.icon];
          return (
            <article className="topic-item" key={topic.id}>
              <div className="topic-icon" aria-hidden="true"><Icon size={20} strokeWidth={1.6} /></div>
              <div className="topic-copy">
                <h2>{topic.title}</h2>
                <p>{topic.description}</p>
                <button className="text-button" type="button" onClick={() => onAsk(topic.prompt)}>
                  {topic.prompt}
                  <ArrowUpRight size={15} aria-hidden="true" />
                </button>
              </div>
            </article>
          );
        })}
      </div>

      <aside className="info-callout" aria-label="About the knowledge base">
        <Info size={19} aria-hidden="true" />
        <div>
          <h2>A focused academic demo</h2>
          <p>
            Answers draw from the bundled CSE Curriculum 2025 and Academic Regulations 2025
            documents. These are part of a synthetic demonstration dataset, not live university
            records. Check your institution’s current guidance for official decisions.
          </p>
        </div>
      </aside>

      <h2>Getting a useful answer</h2>
      <ol className="method-list">
        <li>
          <strong>Give each question its context.</strong>
          <p>Include the course name or semester. The engine treats each question independently.</p>
        </li>
        <li>
          <strong>Check the source reference.</strong>
          <p>Source labels identify the document used for the answer. Exact page references are not available.</p>
        </li>
        <li>
          <strong>Read confidence as a topic match.</strong>
          <p>The score measures intent classification confidence, not answer accuracy. The engine may decline when it cannot find a strong match.</p>
        </li>
      </ol>
    </section>
  );
}
