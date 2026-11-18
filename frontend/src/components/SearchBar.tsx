import React, { useRef } from 'react';
import { Search, Loader2, ArrowRight, Upload, FileText, CheckCircle2 } from 'lucide-react';

interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  onSearch: (q: string) => void;
  loading: boolean;
  onUpload: (file: File) => void;
  uploading: boolean;
  uploadSuccess: string | null;
  activeDocuments: string[];
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  setQuery,
  onSearch,
  loading,
  onUpload,
  uploading,
  uploadSuccess,
  activeDocuments,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="mb-6 space-y-3">
      {/* Search Input Bar */}
      <form onSubmit={handleSubmit}>
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-zinc-500 absolute left-4 pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            placeholder="Search indexed files or trigger live web fallback..."
            className="w-full pl-11 pr-48 py-3.5 rounded-lg bg-[#111216] border border-zinc-800 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-600 text-sm transition-colors"
          />

          <div className="absolute right-1.5 flex items-center space-x-1.5">
            {/* Hidden File Input */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.txt,.md,.csv,.json"
              className="hidden"
            />

            {/* Upload Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading || loading}
              className="px-3 py-2 rounded-md bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 text-zinc-300 hover:text-white border border-zinc-800 text-xs font-medium flex items-center space-x-1.5 transition-colors cursor-pointer"
              title="Upload PDF, TXT, MD or CSV into Qdrant"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400" />
                  <span>Indexing</span>
                </>
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Upload</span>
                </>
              )}
            </button>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 rounded-md bg-zinc-100 hover:bg-white disabled:bg-zinc-800 disabled:text-zinc-600 text-zinc-950 font-medium text-xs flex items-center space-x-1.5 transition-colors cursor-pointer"
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
        </div>
      </form>

      {/* Upload Notification Banner */}
      {uploadSuccess && (
        <div className="flex items-center space-x-2 py-2 px-3 rounded-md bg-emerald-950/40 border border-emerald-800/80 text-emerald-300 text-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}

      {/* Active Knowledge Registry */}
      {activeDocuments.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 py-1 text-xs">
          <span className="text-zinc-500 font-mono text-[11px] mr-1">Active Corpus:</span>
          {activeDocuments.map((doc, idx) => (
            <span
              key={idx}
              className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300 text-[11px] font-mono"
            >
              <FileText className="w-3 h-3 text-zinc-500" />
              <span className="truncate max-w-[200px]">{doc}</span>
            </span>
          ))}
        </div>
      )}

      {/* Suggested Prompts */}
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
