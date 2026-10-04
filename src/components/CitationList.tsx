import type { Citation } from "../types/chat";
import { SourceCard } from "./SourceCard";

interface CitationListProps {
  citations: Citation[];
}

/** Renders the citations array as a labelled list of SourceCards. */
export function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) {
    return null;
  }
  return (
    <section className="citations" aria-label="Sources">
      <h4 className="citations__title">Sources ({citations.length})</h4>
      <ul className="citations__list">
        {citations.map((citation, index) => (
          <li key={`${citation.document_id}-${citation.chunk_id ?? index}`}>
            <SourceCard citation={citation} />
          </li>
        ))}
      </ul>
    </section>
  );
}
