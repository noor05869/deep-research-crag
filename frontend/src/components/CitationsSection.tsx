import React from 'react';
import { ExternalLink } from 'lucide-react';
import type { Citation } from '../types';

interface CitationsSectionProps {
  citations: Citation[];
  activeCitation: string | null;
  onSelectCitation: (citationId: string) => void;
}

export const CitationsSection: React.FC<CitationsSectionProps> = ({
  citations,
  activeCitation,
  onSelectCitation,
}) => {
  if (!citations || citations.length === 0) return null;

  const isUrl = (str: string) => str.startsWith('http://') || str.startsWith('https://');

  return (
    <section className="rounded-lg bg-[#111216] border border-zinc-800 p-6">
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-4">
        <h2 className="text-sm font-semibold text-zinc-100">
          Source Evidence ({citations.length})
        </h2>
        <span className="text-xs text-zinc-500 font-mono">Verified Citations</span>
      </div>

      <div className="space-y-3">
        {citations.map((citation) => {
          const isActive = activeCitation === citation.citation_id;
          const urlSource = isUrl(citation.source);

          return (
            <div
              key={citation.citation_id}
              id={`citation-${citation.citation_id}`}
              onClick={() => onSelectCitation(citation.citation_id)}
              className={`p-3.5 rounded-md border transition-colors cursor-pointer ${
                isActive
                  ? 'bg-zinc-800/80 border-blue-500/80 ring-1 ring-blue-500/40'
                  : 'bg-zinc-900/60 border-zinc-800 hover:border-zinc-700'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-2">
                  <span className="px-1.5 py-0.5 rounded bg-zinc-800 text-blue-400 font-mono text-xs font-semibold border border-zinc-700">
                    {citation.citation_id}
                  </span>
                  <span className="text-xs font-medium text-zinc-200 truncate max-w-sm">
                    {citation.source}
                  </span>
                </div>

                {urlSource && (
                  <a
                    href={citation.source}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="flex items-center space-x-1 text-xs text-zinc-400 hover:text-zinc-200 transition-colors"
                  >
                    <span>Source</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              {citation.quote && (
                <p className="text-xs text-zinc-400 leading-normal pl-2 border-l border-zinc-700 my-1 font-normal">
                  "{citation.quote}"
                </p>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};
