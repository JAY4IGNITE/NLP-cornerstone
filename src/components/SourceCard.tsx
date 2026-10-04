import { useState } from "react";
import type { Citation } from "../types/chat";
import { ChevronDown, ChevronUp } from "lucide-react";

interface SourceCardProps {
  citation: Citation;
}

/** Renders a single citation as a clearly marked "source" card. */
export function SourceCard({ citation }: SourceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { title, location, document_id, chunk_id, content } = citation;
  return (
    <article 
      className={`source-card ${content ? 'cursor-pointer' : ''}`}
      onClick={() => content && setIsExpanded(!isExpanded)}
    >
      <div className="flex items-start justify-between w-full">
        <div className="flex items-start gap-3">
          <span className="source-card__badge" aria-hidden="true">
            DOC
          </span>
          <div className="source-card__body">
            <p className="source-card__title">{title || "Untitled source"}</p>
            {location ? <p className="source-card__location">{location}</p> : null}
            <p className="source-card__meta">
              <span className="source-card__id">{document_id}</span>
              {chunk_id ? (
                <span className="source-card__chunk">chunk {chunk_id}</span>
              ) : null}
            </p>
          </div>
        </div>
        {content && (
          <div className="text-slate-400 mt-1">
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        )}
      </div>
      {isExpanded && content && (
        <div className="mt-3 pt-3 border-t border-white/10 text-xs text-slate-300 whitespace-pre-wrap font-mono bg-black/20 p-2 rounded">
          {content}
        </div>
      )}
    </article>
  );
}
