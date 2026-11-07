import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { PipelineTracker } from './components/PipelineTracker';
import { AuditBanner } from './components/AuditBanner';
import { ReportViewer } from './components/ReportViewer';
import { CitationsSection } from './components/CitationsSection';
import type { ResearchResponse, PipelineStage } from './types';
import { AlertCircle } from 'lucide-react';

export function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState<PipelineStage>('idle');
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [serverHealthy, setServerHealthy] = useState<boolean | null>(null);
  const [activeCitation, setActiveCitation] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        setServerHealthy(res.ok);
      } catch {
        setServerHealthy(false);
      }
    };
    checkHealth();
  }, []);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setActiveCitation(null);

    setStage('retrieving');
    const timer1 = setTimeout(() => setStage('grading'), 1500);
    const timer2 = setTimeout(() => setStage('fallback'), 3000);
    const timer3 = setTimeout(() => setStage('generating'), 5500);
    const timer4 = setTimeout(() => setStage('evaluating'), 8000);

    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned ${response.status}`);
      }

      const data: ResearchResponse = await response.json();
      setResult(data);
      setStage('completed');
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An unexpected error occurred during execution.');
      setStage('error');
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      setLoading(false);
    }
  };

  const handleSelectCitation = (citationId: string) => {
    setActiveCitation(citationId);
    const el = document.getElementById(`citation-${citationId}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 flex flex-col font-sans">
      <Header serverHealthy={serverHealthy} />

      <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-zinc-100 mb-1">
            Autonomous Deep Research
          </h1>
          <p className="text-xs text-zinc-400 max-w-2xl leading-normal">
            Corrective-RAG & Self-RAG Engine. Audits internal vector documents, discards irrelevant noise, rewrites queries for live search fallback, and verifies factual grounding before output.
          </p>
        </div>

        <SearchBar
          query={query}
          setQuery={setQuery}
          onSearch={handleSearch}
          loading={loading}
        />

        <PipelineTracker stage={stage} />

        {error && (
          <div className="p-3.5 rounded-lg bg-rose-950/30 border border-rose-800 text-rose-300 flex items-start space-x-2.5 mb-6 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
            <div>
              <p className="font-medium text-rose-200">Execution Error</p>
              <p className="text-rose-400/90 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {result && (
          <div>
            <AuditBanner data={result} />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-7">
                <ReportViewer
                  response={result.final_response}
                  citations={result.citations}
                  onSelectCitation={handleSelectCitation}
                  activeCitation={activeCitation}
                />
              </div>

              <div className="lg:col-span-5 sticky top-20">
                <CitationsSection
                  citations={result.citations}
                  activeCitation={activeCitation}
                  onSelectCitation={handleSelectCitation}
                />
              </div>
            </div>
          </div>
        )}

        {!result && !loading && !error && (
          <div className="mt-8 border border-zinc-800/80 rounded-lg p-6 bg-[#111216] text-xs text-zinc-400">
            <h2 className="text-sm font-semibold text-zinc-200 mb-1.5">How This Engine Operates</h2>
            <p className="leading-relaxed mb-3">
              This system does not pass raw retrieval results into an LLM. It acts as an autonomous state machine:
            </p>
            <ul className="space-y-1.5 text-zinc-400 list-disc list-inside">
              <li><strong className="text-zinc-300">Self-RAG Grading:</strong> Each retrieved chunk is scored for relevance. Irrelevant noise is stripped before generation.</li>
              <li><strong className="text-zinc-300">Live Search Fallback:</strong> If internal policy coverage is incomplete, an LLM query rewriter executes a live web search via DuckDuckGo.</li>
              <li><strong className="text-zinc-300">Fact Audit:</strong> Before releasing any response, an independent auditor verifies that every claim is strictly grounded in the reference documents.</li>
            </ul>
          </div>
        )}
      </main>

      <footer className="border-t border-zinc-800/80 py-4 text-center text-xs text-zinc-500">
        <p>DeepResearch-CRAG • LangGraph + Qdrant + Google Gemini</p>
      </footer>
    </div>
  );
}

export default App;
