import React from 'react';
import { Search, Loader2, ArrowRight } from 'lucide-react';

interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  onSearch: (q: string) => void;
  loading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  setQuery,
  onSearch,
  loading,
}) => {
  const samplePrompts = [
    {
      label: 'Museum Loan Policy',
      query: 'What is the standard fossil loan period and curator approval rules?',
    },
    {
      label: 'Remote Work Schedule',
      query: 'What are the core hours and remote work days allowed for employees?',
    },
    {
      label: 'Live Web Fallback',
      query: 'What are the latest updates on NASA Artemis moon mission in 2026?',
    },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="mb-6">
      <form onSubmit={handleSubmit} className="mb-3">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-zinc-500 absolute left-4 pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            placeholder="Search internal policy documents or run live corrective research..."
            className="w-full pl-11 pr-28 py-3.5 rounded-lg bg-[#111216] border border-zinc-800 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-600 text-sm transition-colors"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-1.5 px-4 py-2 rounded-md bg-zinc-100 hover:bg-white disabled:bg-zinc-800 disabled:text-zinc-600 text-zinc-950 font-medium text-xs flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400" />
                <span className="text-zinc-400">Auditing</span>
              </>
            ) : (
              <>
                <span>Research</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>
      </form>

      <div className="flex flex-wrap items-center gap-1.5">
        <span className="text-xs text-zinc-500 mr-1">Examples:</span>
        {samplePrompts.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setQuery(sample.query);
              onSearch(sample.query);
            }}
            disabled={loading}
            className="text-xs px-2.5 py-1 rounded-md bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors cursor-pointer"
          >
            {sample.label}
          </button>
        ))}
      </div>
    </div>
  );
};
