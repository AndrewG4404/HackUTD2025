'use client';

import { useWorkflowStream } from '@/lib/useWorkflowStream';
import Card from './ui/Card';
import { useEffect, useRef, useState } from 'react';

interface WorkflowVisualizationProps {
  evaluationId: string;
  evaluationType: 'application' | 'assessment';
  onComplete?: () => void;
}

export function WorkflowVisualization({ evaluationId, evaluationType, onComplete }: WorkflowVisualizationProps) {
  const { events, isConnected, error, currentAgent, progress } = useWorkflowStream(evaluationId, onComplete);
  const timelineEndRef = useRef<HTMLDivElement>(null);
  const [showDebug, setShowDebug] = useState(false);

  // Auto-scroll to latest event
  useEffect(() => {
    timelineEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  // Map agent names to mystical sage roles
  const agentRoleMap: Record<string, string> = {
    'IntakeAgent': '📜 The Sage of Origins',
    'VerificationAgent': '✨ The Truth Seer',
    'ComplianceAgent': '🔒 The Guardian of Laws',
    'InteroperabilityAgent': '🔮 The Weaver of Connections',
    'FinanceAgent': '💰 The Keeper of Gold',
    'AdoptionAgent': '🌟 The Herald of Change',
    'SummaryAgent': '📚 The Grand Chronicler',
    'RequirementProfileAgent': '🗝️ The Prophecy Scribe',
    'ComparisonAnalysisAgent': '⚖️ The Oracle Judge',
  };

  const agentSequence = evaluationType === 'application' 
    ? ['IntakeAgent', 'VerificationAgent', 'ComplianceAgent', 'InteroperabilityAgent', 'FinanceAgent', 'AdoptionAgent', 'SummaryAgent']
    : ['RequirementProfileAgent', 'ComplianceAgent', 'InteroperabilityAgent', 'FinanceAgent', 'AdoptionAgent', 'ComparisonAnalysisAgent'];

  // Filter events to show only meaningful ones
  const displayEvents = events.filter((e: any) => {
    if (e.event === 'workflow_start') return true;
    if (e.event === 'agent_start') return true;
    if (e.event === 'agent_complete') return true;
    if (e.event === 'vendor_start') return true;
    if (e.event === 'agent_progress') {
      // Only show key progress events
      const action = e.data?.action;
      return ['web_search_initiated', 'sources_discovered', 'no_sources_found'].includes(action);
    }
    if (e.event === 'workflow_complete') return true;
    if (e.event === 'workflow_error') return true;
    return false;
  });

  const truncate = (str: string, maxLen: number) => {
    if (!str) return '';
    return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
  };

  return (
    <div className="space-y-6">
      {/* Connection Status & Debug Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
          <span className="text-sm text-gray-300">
            {isConnected ? '🔴 Live Stream Active' : error || 'Stream Inactive'}
          </span>
          {events.length > 0 && (
            <span className="text-xs text-gray-500 ml-2">
              {displayEvents.length} key events ({events.length} total)
            </span>
          )}
        </div>
        
        {/* Debug Mode Toggle */}
        <button
          onClick={() => setShowDebug(!showDebug)}
          className="text-xs px-3 py-1.5 border border-gray-600 rounded-md hover:bg-gray-800 transition-colors"
        >
          {showDebug ? '👁️ Hide Debug Details' : '🔧 Show Debug Details'}
        </button>
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
      <Card className="p-6 border-2 border-purple-500/30 magical-glow">
        <h3 className="text-xl font-semibold mb-6 text-gradient">🔮 The Seven Sages</h3>
        <div className="flex flex-col space-y-4">
          {agentSequence.map((agent, idx) => {
            const isCompleted = progress.completed.includes(agent);
            const isCurrent = progress.current === agent;

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
                  <div className={`font-medium ${isCurrent ? 'text-purple-400' : 
                    isCompleted ? 'text-amber-400' : 'text-gray-400'}`}>
                    {agentRoleMap[agent] || agent.replace('Agent', ' Agent')}
                  </div>
                  {isCurrent && (
                    <div className="text-sm text-purple-400 animate-pulse">✨ Divining...</div>
                  )}
                  {isCompleted && (
                    <div className="text-sm text-amber-400">✅ Prophecy Complete</div>
                  )}
                </div>

                {/* Status Badge */}
                {isCurrent && (
                  <div className="px-3 py-1 bg-purple-600/20 border border-purple-500 rounded-full text-sm text-purple-300 animate-pulse">
                    🔮 Channeling
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Agent Reasoning & Discoveries - Compact View */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4 text-white">Agent Reasoning & Discoveries</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {displayEvents.length === 0 && isConnected && (
            <div className="text-center py-8 text-gray-400">
              <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
              Waiting for workflow to start...
            </div>
          )}

          {displayEvents.map((event: any, idx: number) => {
            const time = new Date(typeof event.timestamp === 'number' ? event.timestamp : Date.parse(event.timestamp)).toLocaleTimeString();
            
            return (
              <div key={idx} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 animate-fade-in">
                {/* Workflow Start */}
                {event.event === 'workflow_start' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="font-medium text-lg">🚀 Workflow Started</div>
                    <div className="text-sm text-gray-300 mt-1">
                      {event.data.type} evaluation initiated
                    </div>
                  </div>
                )}

                {/* Vendor Start */}
                {event.event === 'vendor_start' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="font-medium text-cyan-400">🏢 Analyzing Vendor</div>
                    <div className="text-sm text-gray-200 mt-1">{event.data.vendor_name}</div>
                  </div>
                )}

                {/* Agent Start */}
                {event.event === 'agent_start' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="font-medium">{event.data.agent_name} started</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {event.data.role || 'Running analysis...'}
                    </div>
                  </div>
                )}

                {/* Agent Progress - Web Search */}
                {event.event === 'agent_progress' && event.data.action === 'web_search_initiated' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="text-sm text-cyan-300">
                      🔍 {event.data.agent_name || 'Agent'} is searching vendor docs...
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {truncate(event.data.query, 80)}
                    </div>

                    {/* Debug details */}
                    {showDebug && (
                      <details className="mt-2 text-xs text-gray-500">
                        <summary className="cursor-pointer hover:text-gray-300">Show full search query</summary>
                        <pre className="mt-1 whitespace-pre-wrap break-words bg-black/30 p-2 rounded">
                          {event.data.query}
                        </pre>
                      </details>
                    )}
                  </div>
                )}

                {/* Agent Progress - Sources Found */}
                {event.event === 'agent_progress' && event.data.action === 'sources_discovered' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="text-sm text-green-400">
                      ✅ Found {event.data.count || 0} documentation sources
                    </div>
                    
                    {/* Show top sources */}
                    {event.data.urls && event.data.urls.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {event.data.urls.slice(0, 2).map((url: string, i: number) => (
                          <div key={i} className="text-xs text-blue-400 truncate">
                            📄 {url}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Debug details */}
                    {showDebug && event.data.details?.sources && (
                      <details className="mt-2 text-xs">
                        <summary className="cursor-pointer text-gray-500 hover:text-gray-300">Show source details</summary>
                        <div className="mt-1 space-y-2">
                          {event.data.details.sources.map((source: any, i: number) => (
                            <div key={i} className="bg-gray-900/50 border border-gray-700 rounded p-2">
                              <div className="flex justify-between items-start mb-1">
                                <span className="font-semibold text-blue-400">{source.title || 'Document'}</span>
                                <span className={`text-xs px-2 py-0.5 rounded ${
                                  source.credibility === 'official' ? 'bg-green-600' : 
                                  source.credibility === 'third-party-trusted' ? 'bg-blue-600' : 
                                  'bg-gray-600'
                                }`}>
                                  {source.credibility}
                                </span>
                              </div>
                              <div className="text-gray-400 truncate">{source.url}</div>
                              {source.excerpt && (
                                <div className="text-gray-500 mt-1 italic">{truncate(source.excerpt, 150)}</div>
                              )}
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                )}

                {/* Agent Progress - No Sources */}
                {event.event === 'agent_progress' && event.data.action === 'no_sources_found' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="text-sm text-yellow-400">
                      ⚠️ No accessible documentation found
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Analysis will use general knowledge
                    </div>
                  </div>
                )}

                {/* Agent Complete - This is the key "ChatGPT answer" */}
                {event.event === 'agent_complete' && (
                  <div className="border-l-2 border-emerald-500 pl-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-xs text-gray-400">{time}</div>
                        <div className="text-sm font-semibold">
                          ✅ {event.data.agent_name} completed
                        </div>
                      </div>
                      {typeof event.data.score === 'number' && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-900/50 border border-emerald-500/60">
                          Score: {event.data.score.toFixed(2)}/5
                        </span>
                      )}
                    </div>

                    {/* Show summary if available */}
                    {event.data.summary && (
                      <div className="mt-2 text-sm text-gray-200">
                        {event.data.summary}
                      </div>
                    )}

                    {/* Show key findings if no summary */}
                    {!event.data.summary && (event.data.findings_count || event.data.sources_count) && (
                      <div className="text-xs text-gray-400 mt-2">
                        {event.data.findings_count && `${event.data.findings_count} findings`}
                        {event.data.findings_count && event.data.sources_count && ' • '}
                        {event.data.sources_count && `${event.data.sources_count} sources`}
                      </div>
                    )}
                  </div>
                )}

                {/* Workflow Complete */}
                {event.event === 'workflow_complete' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="font-medium text-lg text-green-400">🎉 Workflow Complete</div>
                    <div className="text-sm text-gray-300 mt-1">
                      Evaluation finished successfully
                    </div>
                  </div>
                )}

                {/* Workflow Error */}
                {event.event === 'workflow_error' && (
                  <div>
                    <div className="text-xs text-gray-400">{time}</div>
                    <div className="font-medium text-lg text-red-400">❌ Workflow Error</div>
                    <div className="text-sm text-red-300 mt-1">
                      {event.data.error || 'An error occurred'}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          <div ref={timelineEndRef} />
        </div>
      </Card>

      {/* Event Timeline (Compact) - Only show if debug mode is on */}
      {showDebug && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4 text-white">Full Event Timeline (Debug)</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto text-sm">
            {events.length === 0 && (
              <div className="text-center py-4 text-gray-500">
                No events yet
              </div>
            )}
            {events.map((event: any, idx: number) => (
              <div key={idx} className="flex gap-3 text-gray-400">
                <span className="text-gray-600 font-mono text-xs">
                  {new Date(typeof event.timestamp === 'number' ? event.timestamp : Date.parse(event.timestamp)).toLocaleTimeString()}
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
      )}
    </div>
  );
}
