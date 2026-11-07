import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import type { Citation } from '../types';

interface ReportViewerProps {
  response: string;
  citations: Citation[];
  onSelectCitation: (citationId: string) => void;
  activeCitation: string | null;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  response,
  onSelectCitation,
  activeCitation,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderFormattedText = (text: string) => {
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, index) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        const citationId = part;
        const isActive = activeCitation === citationId;
        return (
          <button
            key={index}
            onClick={() => onSelectCitation(citationId)}
            className={`inline-flex items-center justify-center px-1.5 py-0.5 mx-0.5 rounded text-[11px] font-mono font-medium transition-colors cursor-pointer ${
              isActive
                ? 'bg-blue-600 text-white ring-1 ring-blue-400'
                : 'bg-zinc-800 text-blue-400 hover:bg-blue-600 hover:text-white border border-zinc-700'
            }`}
            title={`View citation ${part}`}
          >
            {part}
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <article className="rounded-lg bg-[#111216] border border-zinc-800 p-6 mb-6">
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-4">
        <h2 className="text-sm font-semibold text-zinc-100">Synthesis Report</h2>
        <button
          onClick={handleCopy}
          className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-zinc-800/60 hover:bg-zinc-800 text-xs text-zinc-400 hover:text-zinc-200 transition-colors border border-zinc-700/60 cursor-pointer"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-zinc-400" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      <div className="text-zinc-200 text-sm leading-relaxed max-w-[68ch] whitespace-pre-line space-y-3">
        {renderFormattedText(response)}
      </div>
    </article>
  );
};
