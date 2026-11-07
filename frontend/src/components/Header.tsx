import React from 'react';
import { Shield, Database, Cpu } from 'lucide-react';

interface HeaderProps {
  serverHealthy: boolean | null;
}

export const Header: React.FC<HeaderProps> = ({ serverHealthy }) => {
  return (
    <header className="border-b border-zinc-800 bg-[#0c0d12] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-200">
            <Shield className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-sm text-zinc-100 tracking-tight">DeepResearch-CRAG</span>
            <span className="text-[11px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/60 font-mono">
              Self-RAG
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center space-x-2 text-xs text-zinc-400">
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-800/60 border border-zinc-800 text-zinc-300">
              <Database className="w-3.5 h-3.5 text-zinc-400" /> Qdrant
            </span>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-800/60 border border-zinc-800 text-zinc-300">
              <Cpu className="w-3.5 h-3.5 text-zinc-400" /> Gemini Flash
            </span>
          </div>

          <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-zinc-800/60 border border-zinc-800 text-xs">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                serverHealthy === true
                  ? 'bg-emerald-400'
                  : serverHealthy === false
                  ? 'bg-rose-400'
                  : 'bg-amber-400 animate-pulse'
              }`}
            />
            <span className="text-zinc-300 font-medium">
              {serverHealthy === true ? 'Ready' : serverHealthy === false ? 'Offline' : 'Connecting'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
