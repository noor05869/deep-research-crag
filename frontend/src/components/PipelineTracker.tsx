import React from 'react';
import { Loader2 } from 'lucide-react';
import type { PipelineStage } from '../types';

interface PipelineTrackerProps {
  stage: PipelineStage;
}

export const PipelineTracker: React.FC<PipelineTrackerProps> = ({ stage }) => {
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
    <div className="flex items-center space-x-2.5 py-3 px-4 rounded-lg bg-[#111216] border border-zinc-800 text-xs text-zinc-300 mb-6">
      <Loader2 className="w-4 h-4 animate-spin text-zinc-400 flex-shrink-0" />
      <span className="font-mono text-zinc-300">{stageLabels[stage] || 'Orchestrating state machine...'}</span>
    </div>
  );
};
