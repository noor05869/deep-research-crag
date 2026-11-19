import React, { useState, useEffect } from 'react';
import { Loader2, Timer } from 'lucide-react';
import type { PipelineStage } from '../types';

interface PipelineTrackerProps {
  stage: PipelineStage;
  message?: string;
}

export const PipelineTracker: React.FC<PipelineTrackerProps> = ({ stage, message }) => {
  const [elapsed, setElapsed] = useState<number>(0);

  useEffect(() => {
    if (stage === 'idle' || stage === 'completed' || stage === 'error') {
      setElapsed(0);
      return;
    }

    const startTime = Date.now();
    const interval = setInterval(() => {
      setElapsed(Number(((Date.now() - startTime) / 1000).toFixed(1)));
    }, 100);

    return () => clearInterval(interval);
  }, [stage]);

  if (stage === 'idle' || stage === 'completed') return null;

  const stageLabels: Record<PipelineStage, string> = {
    idle: '',
    retrieving: 'Retrieving internal knowledge chunks from Qdrant vector store...',
    grading: 'Auditing document relevance with Self-RAG noise filter...',
    fallback: 'Rewriting query and running DuckDuckGo live search fallback...',
    generating: 'Synthesizing response with verifiable inline citations...',
    evaluating: 'Auditing claims for faithfulness and question relevance...',
    completed: 'Research completed.',
    error: 'Execution halted due to error.',
  };

  return (
    <div className="flex items-center justify-between py-3 px-4 rounded-lg bg-[#111216] border border-zinc-800 text-xs text-zinc-300 mb-6">
      <div className="flex items-center space-x-2.5">
        <Loader2 className="w-4 h-4 animate-spin text-zinc-400 flex-shrink-0" />
        <span className="font-mono text-zinc-300">{message || stageLabels[stage] || 'Orchestrating state machine...'}</span>
      </div>
      <div className="flex items-center space-x-1.5 font-mono text-[11px] text-zinc-400 bg-zinc-900/80 px-2.5 py-1 rounded border border-zinc-800">
        <Timer className="w-3.5 h-3.5 text-amber-400" />
        <span className="tabular-nums font-semibold text-zinc-200">{elapsed.toFixed(1)}s</span>
        <span className="text-zinc-500">elapsed</span>
      </div>
    </div>
  );
};

