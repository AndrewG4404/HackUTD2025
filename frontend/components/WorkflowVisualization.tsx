'use client';

import { useWorkflowStream } from '@/lib/useWorkflowStream';
import Card from './ui/Card';
import { useEffect, useRef } from 'react';

interface WorkflowVisualizationProps {
  evaluationId: string;
  evaluationType: 'application' | 'assessment';
  onComplete?: () => void;
}

export function WorkflowVisualization({ evaluationId, evaluationType, onComplete }: WorkflowVisualizationProps) {
  const { events, isConnected, error, currentAgent, progress } = useWorkflowStream(evaluationId, onComplete);
  const timelineEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest event
  useEffect(() => {
    timelineEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const agentSequence = evaluationType === 'application' 
    ? ['IntakeAgent', 'VerificationAgent', 'ComplianceAgent', 'InteroperabilityAgent', 'FinanceAgent', 'AdoptionAgent', 'SummaryAgent']
    : ['UseCaseAgent', 'ComplianceAgent', 'InteroperabilityAgent', 'FinanceAgent', 'AdoptionAgent', 'ComparisonAgent'];

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
        <span className="text-sm text-gray-300">
          {isConnected ? '🔴 Live Stream Active' : error || 'Stream Inactive'}
        </span>
        {events.length > 0 && (
          <span className="text-xs text-gray-500 ml-2">
            {events.length} events
          </span>
        )}
      </div>

      {/* Error Recovery */}
      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-2 text-sm text-red-300 underline hover:text-red-200">
            Refresh Page
          </button>
        </div>
      )}

      {/* Agent Pipeline View */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-6 text-white">Agent Pipeline</h3>
        <div className="flex flex-col space-y-4">
          {agentSequence.map((agent, idx) => {
            const isCompleted = progress.completed.includes(agent);
            const isCurrent = progress.current === agent;
            const isPending = !isCompleted && !isCurrent;

            return (
              <div key={agent} className="flex items-center gap-4">
                {/* Step Number */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all
                  ${isCompleted ? 'bg-green-600 text-white' : 
                    isCurrent ? 'bg-blue-600 text-white animate-pulse shadow-lg shadow-blue-500/50' : 
                    'bg-gray-700 text-gray-400'}`}>
                  {isCompleted ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    idx + 1
                  )}
                </div>

                {/* Agent Name */}
                <div className="flex-1">
                  <div className={`font-medium ${isCurrent ? 'text-blue-400' : 
                    isCompleted ? 'text-green-400' : 'text-gray-400'}`}>
                    {agent.replace('Agent', ' Agent')}
                  </div>
                  {isCurrent && (
                    <div className="text-sm text-gray-400 animate-pulse">Analyzing...</div>
                  )}
                  {isCompleted && (
                    <div className="text-sm text-gray-500">Completed</div>
                  )}
                </div>

                {/* Status Badge */}
                {isCurrent && (
                  <div className="px-3 py-1 bg-blue-600/20 border border-blue-500 rounded-full text-sm text-blue-400 animate-pulse">
                    Active
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Agent Communication Panel */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4 text-white">Agent Reasoning & Discoveries</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {events.length === 0 && isConnected && (
            <div className="text-center py-8 text-gray-400">
              <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
              Waiting for workflow to start...
            </div>
          )}

          {events
            .filter(e => ['agent_thinking', 'agent_progress', 'agent_complete', 'workflow_start', 'vendor_start'].includes(e.event))
            .map((event, idx) => (
              <div key={idx} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 animate-fade-in">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-blue-400">
                    {event.data.agent_name?.replace('Agent', '') || 
                     event.data.agent?.replace('Agent', '') ||
                     event.data.vendor_name ||
                     'System'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {/* Event Content */}
                {event.event === 'workflow_start' && (
                  <div className="text-gray-300">
                    <div className="text-sm opacity-75">🚀 Workflow Started</div>
                    <div className="mt-1">{event.data.type} evaluation initiated</div>
                  </div>
                )}

                {event.event === 'vendor_start' && (
                  <div className="text-cyan-300">
                    <div className="text-sm opacity-75">🏢 Analyzing Vendor</div>
                    <div className="mt-1">{event.data.vendor_name}</div>
                  </div>
                )}

                {event.event === 'agent_thinking' && (
                  <div className="text-gray-300">
                    <div className="text-sm opacity-75">💭 Thinking:</div>
                    <div className="mt-1">{event.data.action || event.data.message}</div>
                    {event.data.context && (
                      <div className="mt-2 text-sm text-gray-400 italic">{event.data.context}</div>
                    )}
                    {event.data.prompt_preview && (
                      <div className="mt-2 text-xs text-gray-500 font-mono bg-black/30 p-2 rounded">
                        {event.data.prompt_preview}
                      </div>
                    )}
                  </div>
                )}

                {event.event === 'agent_progress' && (
                  <div className="text-gray-300">
                    <div className="text-sm opacity-75">📊 Progress:</div>
                    <div className="mt-1">{event.data.message}</div>
                    {event.data.urls && event.data.urls.length > 0 && (
                      <div className="mt-2 text-xs text-blue-400">
                        {event.data.urls.map((url: string, i: number) => (
                          <div key={i} className="truncate">• {url}</div>
                        ))}
                      </div>
                    )}
                    {event.data.details && (
                      <div className="mt-2 text-xs text-gray-400 font-mono bg-black/30 p-2 rounded max-h-32 overflow-y-auto">
                        {typeof event.data.details === 'string' 
                          ? event.data.details 
                          : JSON.stringify(event.data.details, null, 2)}
                      </div>
                    )}
                  </div>
                )}

                {event.event === 'agent_complete' && (
                  <div className="text-green-400">
                    <div className="flex items-center gap-2">
                      <span>✓ Completed</span>
                      {event.data.score !== undefined && (
                        <span className="text-white font-semibold">
                          Score: {typeof event.data.score === 'number' ? event.data.score.toFixed(1) : event.data.score}
                        </span>
                      )}
                    </div>
                    {event.data.source_count && (
                      <div className="text-xs text-gray-400 mt-1">
                        Sources: {event.data.source_count} | Confidence: {event.data.confidence || 'N/A'}
                      </div>
                    )}
                    {event.data.findings && Array.isArray(event.data.findings) && event.data.findings.length > 0 && (
                      <div className="mt-2 text-xs text-gray-300">
                        {event.data.findings.slice(0, 3).map((finding: string, i: number) => (
                          <div key={i}>• {finding}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          <div ref={timelineEndRef} />
        </div>
      </Card>

      {/* Event Timeline (Compact) */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4 text-white">Event Timeline</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto text-sm">
          {events.length === 0 && (
            <div className="text-center py-4 text-gray-500">
              No events yet
            </div>
          )}
          {events.map((event, idx) => (
            <div key={idx} className="flex gap-3 text-gray-400">
              <span className="text-gray-600 font-mono text-xs">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
              <span className="text-gray-500">•</span>
              <span className={`
                ${event.event === 'workflow_complete' ? 'text-green-400 font-semibold' :
                  event.event === 'workflow_error' ? 'text-red-400 font-semibold' :
                  event.event === 'agent_complete' ? 'text-green-400' :
                  event.event === 'agent_start' ? 'text-blue-400' :
                  'text-gray-400'}
              `}>
                {event.event.replace(/_/g, ' ').toUpperCase()}
              </span>
              <span className="text-gray-500 truncate">
                {event.data.agent_name || event.data.agent || event.data.vendor_name || event.data.message || ''}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

