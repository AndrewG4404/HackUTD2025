# Frontend SSE Visualization Guide

## Overview

This guide provides step-by-step instructions to implement **real-time agentic workflow visualization** in the VendorLens frontend using Server-Sent Events (SSE).

## 🎯 What We're Building

A live visualization page at `/evaluations/{id}` that displays:
1. **Agent Pipeline View**: Sequential flow showing which agent is currently executing
2. **Agent Communication Panel**: Live LLM reasoning, document discoveries, and findings
3. **Event Timeline**: Chronological log of all agent activities with timestamps

---

## 📋 Prerequisites

- Backend SSE endpoint implemented (`GET /api/workflows/{evaluation_id}/stream`)
- Frontend running with existing evaluation detail page
- `NEXT_PUBLIC_API_URL` configured in `frontend/.env.local`

---

## 🔧 Step 1: Create SSE Hook

### File: `frontend/lib/useWorkflowStream.ts` (NEW FILE)

Create a custom React hook to manage SSE connections:

```typescript
import { useEffect, useState, useCallback } from 'react';

export interface WorkflowEvent {
  event: string;
  data: any;
  timestamp: string;
}

export interface UseWorkflowStreamResult {
  events: WorkflowEvent[];
  isConnected: boolean;
  error: string | null;
  currentAgent: string | null;
  progress: {
    completed: string[];
    current: string | null;
    pending: string[];
  };
}

const AGENT_SEQUENCE = [
  'IntakeAgent',
  'VerificationAgent',
  'ComplianceAgent',
  'InteroperabilityAgent',
  'FinanceAgent',
  'AdoptionAgent',
  'SummaryAgent'
];

export function useWorkflowStream(evaluationId: string | null): UseWorkflowStreamResult {
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [completedAgents, setCompletedAgents] = useState<string[]>([]);

  useEffect(() => {
    if (!evaluationId) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    const eventSource = new EventSource(`${apiUrl}/workflows/${evaluationId}/stream`);

    eventSource.onopen = () => {
      console.log('SSE connection opened');
      setIsConnected(true);
      setError(null);
    };

    // Handle all event types
    const eventTypes = [
      'workflow_start',
      'agent_start',
      'agent_thinking',
      'agent_progress',
      'agent_complete',
      'vendor_start',
      'vendor_complete',
      'workflow_complete',
      'workflow_error'
    ];

    eventTypes.forEach(eventType => {
      eventSource.addEventListener(eventType, (e: MessageEvent) => {
        const data = JSON.parse(e.data);
        const newEvent: WorkflowEvent = {
          event: eventType,
          data,
          timestamp: e.lastEventId || new Date().toISOString()
        };

        setEvents(prev => [...prev, newEvent]);

        // Update agent tracking
        if (eventType === 'agent_start') {
          setCurrentAgent(data.agent || data.status);
        } else if (eventType === 'agent_complete') {
          setCompletedAgents(prev => [...prev, data.agent]);
          setCurrentAgent(null);
        } else if (eventType === 'workflow_complete' || eventType === 'workflow_error') {
          setCurrentAgent(null);
          setIsConnected(false);
        }
      });
    });

    eventSource.onerror = (err) => {
      console.error('SSE error:', err);
      setError('Connection lost. Refresh to reconnect.');
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [evaluationId]);

  // Calculate progress
  const progress = {
    completed: completedAgents,
    current: currentAgent,
    pending: AGENT_SEQUENCE.filter(
      agent => !completedAgents.includes(agent) && agent !== currentAgent
    )
  };

  return { events, isConnected, error, currentAgent, progress };
}
```

---

## 🔧 Step 2: Create Visualization Components

### File: `frontend/components/WorkflowVisualization.tsx` (NEW FILE)

```typescript
'use client';

import { useWorkflowStream } from '@/lib/useWorkflowStream';
import { Card } from './ui/Card';
import { useEffect, useRef } from 'react';

interface WorkflowVisualizationProps {
  evaluationId: string;
  evaluationType: 'application' | 'assessment';
}

export function WorkflowVisualization({ evaluationId, evaluationType }: WorkflowVisualizationProps) {
  const { events, isConnected, error, currentAgent, progress } = useWorkflowStream(evaluationId);
  const timelineEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest event
  useEffect(() => {
    timelineEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
        <span className="text-sm text-gray-300">
          {isConnected ? 'Live Stream Active' : error || 'Stream Inactive'}
        </span>
      </div>

      {/* Agent Pipeline View */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-6 text-white">Agent Pipeline</h3>
        <div className="flex flex-col space-y-4">
          {['IntakeAgent', 'VerificationAgent', 'ComplianceAgent', 'InteroperabilityAgent', 
            'FinanceAgent', 'AdoptionAgent', 'SummaryAgent'].map((agent, idx) => {
            const isCompleted = progress.completed.includes(agent);
            const isCurrent = progress.current === agent;
            const isPending = !isCompleted && !isCurrent;

            return (
              <div key={agent} className="flex items-center gap-4">
                {/* Step Number */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold
                  ${isCompleted ? 'bg-green-600 text-white' : 
                    isCurrent ? 'bg-blue-600 text-white animate-pulse' : 
                    'bg-gray-700 text-gray-400'}`}>
                  {isCompleted ? '✓' : idx + 1}
                </div>

                {/* Agent Name */}
                <div className="flex-1">
                  <div className={`font-medium ${isCurrent ? 'text-blue-400' : 
                    isCompleted ? 'text-green-400' : 'text-gray-400'}`}>
                    {agent.replace('Agent', '')}
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
                  <div className="px-3 py-1 bg-blue-600/20 border border-blue-500 rounded-full text-sm text-blue-400">
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
          {events
            .filter(e => ['agent_thinking', 'agent_progress', 'agent_complete'].includes(e.event))
            .map((event, idx) => (
              <div key={idx} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-blue-400">
                    {event.data.agent?.replace('Agent', '') || 'System'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {/* Event Content */}
                {event.event === 'agent_thinking' && (
                  <div className="text-gray-300">
                    <div className="text-sm opacity-75">Thinking:</div>
                    <div className="mt-1">{event.data.action}</div>
                    {event.data.context && (
                      <div className="mt-2 text-sm text-gray-400 italic">{event.data.context}</div>
                    )}
                  </div>
                )}

                {event.event === 'agent_progress' && (
                  <div className="text-gray-300">
                    <div className="text-sm opacity-75">Progress:</div>
                    <div className="mt-1">{event.data.message}</div>
                    {event.data.details && (
                      <div className="mt-2 text-xs text-gray-400 font-mono">
                        {JSON.stringify(event.data.details, null, 2)}
                      </div>
                    )}
                  </div>
                )}

                {event.event === 'agent_complete' && (
                  <div className="text-green-400">
                    <div className="flex items-center gap-2">
                      <span>✓ Completed</span>
                      {event.data.score !== undefined && (
                        <span className="text-white font-semibold">Score: {event.data.score}</span>
                      )}
                    </div>
                    {event.data.source_count && (
                      <div className="text-xs text-gray-400 mt-1">
                        Sources: {event.data.source_count} | Confidence: {event.data.confidence || 'N/A'}
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
                {event.data.agent || event.data.vendor_name || event.data.message || ''}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
```

---

## 🔧 Step 3: Update Evaluation Detail Page

### File: `frontend/app/evaluations/[id]/page.tsx`

Integrate the visualization component. **Add at the top of the file** (after imports):

```typescript
import { WorkflowVisualization } from '@/components/WorkflowVisualization';
```

Then, **add a new section** right after the status header and before the results section:

```typescript
{/* Live Workflow Visualization - Show when running */}
{evaluation.status === 'running' && (
  <div className="mb-8">
    <h2 className="text-2xl font-bold mb-4 text-white">
      🔴 Live Workflow Execution
    </h2>
    <WorkflowVisualization 
      evaluationId={id} 
      evaluationType={evaluation.type}
    />
  </div>
)}
```

### Complete Context (Where to Place)

Find this section in the file:

```typescript
{/* Status Display */}
<div className="mb-8">
  <h2 className="text-2xl font-bold mb-4 text-white">Status</h2>
  <Card className="p-6">
    {/* ... status badges ... */}
  </Card>
</div>
```

Add the visualization **immediately after** this status section:

```typescript
{/* Status Display */}
<div className="mb-8">
  <h2 className="text-2xl font-bold mb-4 text-white">Status</h2>
  <Card className="p-6">
    {/* ... existing status badges ... */}
  </Card>
</div>

{/* ADD THIS NEW SECTION */}
{evaluation.status === 'running' && (
  <div className="mb-8">
    <h2 className="text-2xl font-bold mb-4 text-white">
      🔴 Live Workflow Execution
    </h2>
    <WorkflowVisualization 
      evaluationId={id} 
      evaluationType={evaluation.type}
    />
  </div>
)}

{/* Results Section (existing) */}
{isCompleted && (
  // ... existing results code ...
)}
```

---

## 🔧 Step 4: Optional - Auto-refresh on Completion

To automatically refresh the evaluation data when the workflow completes, update the hook:

### File: `frontend/lib/useWorkflowStream.ts`

Add a callback prop:

```typescript
export function useWorkflowStream(
  evaluationId: string | null,
  onComplete?: () => void  // NEW
): UseWorkflowStreamResult {
  // ... existing code ...

  eventTypes.forEach(eventType => {
    eventSource.addEventListener(eventType, (e: MessageEvent) => {
      // ... existing event handling ...

      // NEW: Call onComplete callback
      if (eventType === 'workflow_complete' && onComplete) {
        setTimeout(() => onComplete(), 1000); // Delay to ensure DB is updated
      }
    });
  });

  // ... rest of hook ...
}
```

Then in the page component:

```typescript
const handleWorkflowComplete = useCallback(() => {
  // Refetch evaluation data
  fetchEvaluation();
}, [id]);

// Pass to visualization
<WorkflowVisualization 
  evaluationId={id} 
  evaluationType={evaluation.type}
  onComplete={handleWorkflowComplete}  // NEW
/>
```

---

## 🎨 Step 5: Styling Enhancements (Optional)

### Add Pulsing Animation to `globals.css`

```css
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
  }
}

.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

Apply to current agent indicator:

```typescript
<div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold
  ${isCurrent ? 'bg-blue-600 text-white animate-pulse animate-pulse-glow' : /* ... */}`}>
```

---

## 🧪 Step 6: Testing

### Test Scenario 1: Application Workflow

1. Navigate to `/apply`
2. Fill form with ServiceNow details
3. Submit and note the evaluation ID
4. Click "View Details" or navigate to `/evaluations/{id}`
5. **Immediately** (within 3 seconds), you should see:
   - "Live Stream Active" indicator (green pulsing dot)
   - Agent Pipeline showing IntakeAgent as "Active"
   - Events appearing in the communication panel

6. Watch the flow:
   - IntakeAgent completes (green checkmark)
   - VerificationAgent becomes active (blue, pulsing)
   - ComplianceAgent shows "Discovered 2 documentation URLs"
   - LLM reasoning appears: "Analyzing certifications..."
   - Each agent completes with score and confidence
   - SummaryAgent finalizes
   - "WORKFLOW COMPLETE" appears in timeline

7. Page auto-refreshes (if implemented) showing final results

### Test Scenario 2: Assessment Workflow

1. Navigate to `/assess`
2. Create assessment with ServiceNow vs Salesforce
3. Submit and navigate to `/evaluations/{id}`
4. Watch vendor-by-vendor processing:
   - "Vendor A (ServiceNow)" banner appears
   - All 4 agents run for ServiceNow
   - "Vendor A complete - Score: 8.2"
   - "Vendor B (Salesforce)" banner appears
   - All 4 agents run for Salesforce
   - Final recommendation shown

### Expected Behavior

- **Latency**: Events should appear within 1-2 seconds of backend emission
- **Order**: Events in chronological order (no out-of-order arrivals)
- **Completion**: Stream closes after `workflow_complete` event
- **Reconnection**: If stream drops, error message shows; refresh to reconnect

### Debugging

If events don't appear:

1. **Check browser console** for EventSource errors
2. **Check Network tab** - should see `stream` connection with `text/event-stream`
3. **Check backend logs** - should see "Workflow started" and agent print statements
4. **Verify environment variable**: `NEXT_PUBLIC_API_URL` must be set
5. **CORS**: Backend must allow `text/event-stream` from frontend origin

```bash
# Test backend directly
curl -N "http://localhost:8000/api/workflows/{id}/stream"
# Should see events streaming
```

---

## 🎯 UI/UX Best Practices

### Loading States

Show placeholder while connecting:

```typescript
{!isConnected && events.length === 0 && (
  <div className="text-center py-8 text-gray-400">
    <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
    Connecting to live stream...
  </div>
)}
```

### Error Recovery

```typescript
{error && (
  <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-4">
    <div className="flex items-center gap-2 text-red-400">
      <span>⚠️</span>
      <span>{error}</span>
    </div>
    <button 
      onClick={() => window.location.reload()} 
      className="mt-2 text-sm text-red-300 underline">
      Refresh Page
    </button>
  </div>
)}
```

### Empty State

```typescript
{isConnected && events.length === 0 && (
  <div className="text-center py-8 text-gray-400">
    Waiting for workflow to start...
  </div>
)}
```

---

## 📊 Event Statistics (Optional Enhancement)

Add a stats summary at the top:

```typescript
const stats = {
  totalEvents: events.length,
  agentsCompleted: progress.completed.length,
  documentsFound: events.filter(e => 
    e.event === 'agent_progress' && e.data.details?.urls_found
  ).reduce((sum, e) => sum + e.data.details.urls_found, 0),
  duration: events.length > 0 
    ? Math.round((new Date(events[events.length - 1].timestamp).getTime() - 
        new Date(events[0].timestamp).getTime()) / 1000)
    : 0
};

// Display
<div className="grid grid-cols-4 gap-4 mb-6">
  <Card className="p-4 text-center">
    <div className="text-2xl font-bold text-blue-400">{stats.totalEvents}</div>
    <div className="text-sm text-gray-400">Events</div>
  </Card>
  <Card className="p-4 text-center">
    <div className="text-2xl font-bold text-green-400">{stats.agentsCompleted}</div>
    <div className="text-sm text-gray-400">Agents Done</div>
  </Card>
  <Card className="p-4 text-center">
    <div className="text-2xl font-bold text-purple-400">{stats.documentsFound}</div>
    <div className="text-sm text-gray-400">Docs Found</div>
  </Card>
  <Card className="p-4 text-center">
    <div className="text-2xl font-bold text-yellow-400">{stats.duration}s</div>
    <div className="text-sm text-gray-400">Duration</div>
  </Card>
</div>
```

---

## ✅ Verification Checklist

- [ ] `useWorkflowStream.ts` hook created
- [ ] `WorkflowVisualization.tsx` component created
- [ ] Component imported in evaluation detail page
- [ ] Conditional rendering when `status === 'running'`
- [ ] EventSource connects to backend SSE endpoint
- [ ] Events display in real-time (<2s latency)
- [ ] Agent pipeline shows current/completed/pending states
- [ ] Communication panel shows LLM reasoning
- [ ] Timeline shows chronological events
- [ ] Connection status indicator works
- [ ] Error handling and recovery implemented
- [ ] Auto-scroll to latest event works
- [ ] Styling matches existing dark theme
- [ ] Tested with both application and assessment workflows

---

## 🚀 Success Criteria

When complete, judges should be able to:

1. **Start an evaluation** from `/apply` or `/assess`
2. **Immediately navigate** to the evaluation detail page
3. **See live updates** as agents execute:
   - Which agent is currently running
   - What the agent is thinking (LLM outputs)
   - What documents the agent discovered
   - Real-time scores and confidence levels
4. **Watch the recommendation** being built in real-time
5. **See final results** automatically appear when workflow completes

This creates a **transparent, impressive demonstration** of the agentic workflow that clearly shows the AI agents researching, reasoning, and collaborating to produce the evaluation.

---

## 🎬 Demo Script for Judges

**Judge Walkthrough (2 minutes):**

1. "Let me show you our agentic workflow in action..."
2. Click "Assess Vendors" → Enter ServiceNow vs Salesforce
3. Submit → Navigate to evaluation page
4. **Point out**:
   - "See the live stream indicator? The agents are working now."
   - "Here's the Compliance Agent discovering ServiceNow's trust documentation..."
   - "Watch it analyze the content with the LLM..."
   - "Now it's finding ISO 27001 and SOC 2 certifications..."
   - "Each agent contributes its specialized expertise..."
5. Wait for completion (30-60 seconds)
6. "And here's the final recommendation based on weighted scoring."

**Impact**: Judges see the AI isn't a black box—it's a transparent, multi-agent system doing real research and reasoning.

---

## 🐛 Common Issues & Fixes

### Issue: Events not appearing
**Fix**: Check `NEXT_PUBLIC_API_URL` - must start with `http://` and include `/api`

### Issue: "Connection lost" immediately
**Fix**: Backend SSE endpoint not running or CORS misconfigured

### Issue: Old data showing after completion
**Fix**: Implement auto-refresh callback (Step 4)

### Issue: Timeline jumps around
**Fix**: Ensure `timelineEndRef` scroll is `smooth`, not `auto`

### Issue: Too many events, UI laggy
**Fix**: Add pagination or limit displayed events:
```typescript
.slice(-50) // Show last 50 events only
```

---

🎉 **You're done!** The frontend now provides a stunning real-time visualization of your agentic workflow.

