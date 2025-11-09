/**
 * Evaluation Results Page - Dark Theme
 * Shows pipeline status and results for both application and assessment workflows
 */
'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'next/navigation'
import api from '@/lib/api'
import type { Evaluation, VendorDecision, Vendor } from '@/lib/types'
import Card from '@/components/ui/Card'
import { WorkflowVisualization } from '@/components/WorkflowVisualization'

// Decision Badge Component
function DecisionBadge({ decision }: { decision?: VendorDecision }) {
  const status = decision?.status ?? 'pending'
  const base = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium'

  switch (status) {
    case 'approved':
      return <span className={`${base} bg-emerald-500/20 text-emerald-400 border border-emerald-500/30`}>✓ Approved</span>
    case 'approved_pending_actions':
      return (
        <span className={`${base} bg-amber-500/20 text-amber-400 border border-amber-500/30`}>
          ⏳ Approved – pending actions
        </span>
      )
    case 'declined':
      return <span className={`${base} bg-rose-500/20 text-rose-400 border border-rose-500/30`}>✗ Declined</span>
    default:
      return <span className={`${base} bg-slate-500/20 text-slate-400 border border-slate-500/30`}>⊙ Not reviewed</span>
  }
}

// Decision Modal Component
function DecisionModal({
  evaluationId,
  vendors,
  state,
  onClose,
  onUpdated,
}: {
  evaluationId: string
  vendors: Vendor[]
  state: { open: boolean; vendorId: string | null; mode: 'approve_pending' | 'approve' | 'decline' | null }
  onClose: () => void
  onUpdated: (updatedEval: Evaluation) => void
}) {
  const [notes, setNotes] = useState('')
  const [pendingActions, setPendingActions] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!state.open || !state.vendorId || !state.mode) return null

  const vendor = vendors.find((v) => v.id === state.vendorId)
  if (!vendor) return null
  
  // TypeScript guard - vendor is guaranteed to exist here

  const title =
    state.mode === 'approve_pending'
      ? `Approve ${vendor.name} with pending actions`
      : state.mode === 'approve'
      ? `Approve ${vendor.name}`
      : `Decline ${vendor.name}`

  async function handleSubmit() {
    setLoading(true)
    setError(null)
    try {
      const status: 'approved_pending_actions' | 'approved' | 'declined' =
        state.mode === 'approve_pending'
          ? 'approved_pending_actions'
          : state.mode === 'approve'
          ? 'approved'
          : 'declined'

      const payload = {
        status,
        notes: notes || undefined,
        pending_actions:
          status === 'approved_pending_actions'
            ? pendingActions
                .split('\n')
                .map((s) => s.trim())
                .filter(Boolean)
            : [],
      }

      const updatedEval = await api.setVendorDecision(evaluationId, vendor!.id, payload)
      onUpdated(updatedEval)
      onClose()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to save decision')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-xl bg-[#1a1a1a] border border-gray-800 p-6 shadow-2xl">
        <h2 className="text-lg font-semibold mb-2 text-white">{title}</h2>
        <p className="text-xs text-gray-400 mb-4">
          This action captures your vendor onboarding decision for this evaluation.
        </p>

        {state.mode === 'approve_pending' && (
          <div className="mb-4">
            <label className="block text-xs font-medium text-gray-300 mb-1">
              Pending action items (one per line)
            </label>
            <textarea
              className="w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm text-gray-200 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              rows={4}
              placeholder={'Request SOC 2 Type II report\nComplete security questionnaire\nRun POC in non-prod environment'}
              value={pendingActions}
              onChange={(e) => setPendingActions(e.target.value)}
            />
          </div>
        )}

        <div className="mb-4">
          <label className="block text-xs font-medium text-gray-300 mb-1">
            Internal notes (optional)
          </label>
          <textarea
            className="w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm text-gray-200 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            rows={3}
            placeholder="e.g. Strong fit technically, awaiting formal compliance pack and fraud checks."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        {error && (
          <div className="mb-3 p-2 rounded bg-rose-500/10 border border-rose-500/30">
            <p className="text-xs text-rose-400">{error}</p>
          </div>
        )}

        <div className="flex justify-end gap-2">
          <button
            className="rounded-md border border-gray-700 bg-[#0f0f0f] px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 transition-colors"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function EvaluationPage() {
  const params = useParams()
  const evaluationId = params.id as string
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const [loading, setLoading] = useState(true)
  const [decisionModal, setDecisionModal] = useState<{
    open: boolean
    vendorId: string | null
    mode: 'approve_pending' | 'approve' | 'decline' | null
  }>({ open: false, vendorId: null, mode: null })

  const fetchEvaluation = useCallback(async () => {
    try {
      const data = await api.getEvaluation(evaluationId)
      setEvaluation(data)
    } catch (error) {
      console.error('Error fetching evaluation:', error)
    } finally {
      setLoading(false)
    }
  }, [evaluationId])

  useEffect(() => {
    fetchEvaluation()

    // Poll if status is pending or running
    const interval = setInterval(() => {
      if (evaluation?.status === 'pending' || evaluation?.status === 'running') {
        fetchEvaluation()
      }
    }, 5000) // Poll every 5 seconds

    return () => clearInterval(interval)
  }, [evaluationId, evaluation?.status, fetchEvaluation])

  // Callback for when workflow completes
  const handleWorkflowComplete = useCallback(() => {
    console.log('Workflow completed, refreshing evaluation data...')
    setTimeout(() => fetchEvaluation(), 1500) // Wait a bit for DB to update
  }, [fetchEvaluation])

  // Open decision modal
  const openDecisionModal = (vendorId: string, mode: 'approve_pending' | 'approve' | 'decline') => {
    setDecisionModal({ open: true, vendorId, mode })
  }

  // Close decision modal
  const closeDecisionModal = () => {
    setDecisionModal({ open: false, vendorId: null, mode: null })
  }

  // Handle decision update
  const handleDecisionUpdate = (updatedEval: Evaluation) => {
    setEvaluation(updatedEval)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading evaluation...</p>
        </div>
      </div>
    )
  }

  if (!evaluation) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-xl">Evaluation not found</p>
        </div>
      </div>
    )
  }

  const isRunning = evaluation.status === 'pending' || evaluation.status === 'running'
  const isCompleted = evaluation.status === 'completed' || evaluation.status === 'finalized'
  const isFailed = evaluation.status === 'failed'
  const isFinalized = evaluation.status === 'finalized'
  
  // Show workflow visualization for pending, running, AND if recently completed (within 2 mins)
  const showWorkflow = isRunning || (isCompleted && evaluation.updated_at && 
    (Date.now() - new Date(evaluation.updated_at).getTime()) < 120000)

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 text-white">{evaluation.name}</h1>
          <div className="flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              isRunning ? 'bg-yellow-500/20 text-yellow-400' :
              isFinalized ? 'bg-blue-500/20 text-blue-400' :
              isCompleted ? 'bg-green-500/20 text-green-400' :
              isFailed ? 'bg-red-500/20 text-red-400' :
              'bg-gray-500/20 text-gray-400'
            }`}>
              {evaluation.status.toUpperCase()}
            </span>
            <span className="text-gray-500 text-sm">{evaluation.type}</span>
          </div>
        </div>
        
        {/* Live Workflow Visualization - Show when running OR just completed */}
        {showWorkflow && (
          <div className="mb-8">
            <WorkflowVisualization 
              evaluationId={evaluationId} 
              evaluationType={evaluation.type}
              onComplete={handleWorkflowComplete}
            />
          </div>
        )}

        {isFailed && (
          <Card>
            <div className="flex items-center mb-4">
              <svg className="w-6 h-6 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h2 className="text-xl font-semibold text-red-400">Evaluation Failed</h2>
            </div>
            <p className="text-gray-300">{evaluation.error || 'Unknown error occurred'}</p>
          </Card>
        )}

        {isCompleted && (
          <div className="space-y-8">
            {evaluation.type === 'application' && (
              <>
                {/* Onboarding Decision Section for Application */}
                {(evaluation.status === 'completed' || evaluation.status === 'finalized') && evaluation.vendors?.[0] && (
                  <Card>
                    <h3 className="text-xl font-semibold mb-4 text-white">Onboarding Decision</h3>
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <DecisionBadge decision={evaluation.vendors[0].decision} />
                      </div>
                      <div className="flex gap-2">
                        <button
                          className="rounded-md border border-emerald-600 bg-emerald-600/10 px-4 py-2 text-sm text-emerald-300 hover:bg-emerald-600/20 transition-colors"
                          onClick={() => openDecisionModal(evaluation.vendors[0].id, 'approve')}
                        >
                          Approve
                        </button>
                        <button
                          className="rounded-md border border-amber-600 bg-amber-600/10 px-4 py-2 text-sm text-amber-300 hover:bg-amber-600/20 transition-colors"
                          onClick={() => openDecisionModal(evaluation.vendors[0].id, 'approve_pending')}
                        >
                          Approve w/ Pending Actions
                        </button>
                        <button
                          className="rounded-md border border-rose-600 bg-rose-600/10 px-4 py-2 text-sm text-rose-300 hover:bg-rose-600/20 transition-colors"
                          onClick={() => openDecisionModal(evaluation.vendors[0].id, 'decline')}
                        >
                          Decline Vendor
                        </button>
                      </div>
                    </div>
                    {evaluation.vendors[0].decision?.pending_actions && evaluation.vendors[0].decision.pending_actions.length > 0 && (
                      <div className="mb-3">
                        <div className="text-sm font-semibold text-amber-400 mb-2">Pending Actions:</div>
                        <ul className="text-sm text-gray-300 space-y-1.5">
                          {evaluation.vendors[0].decision.pending_actions.map((action: string, i: number) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-amber-400">•</span>
                              <span>{action}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {evaluation.vendors[0].decision?.notes && (
                      <div>
                        <div className="text-sm font-semibold text-gray-400 mb-2">Decision Notes:</div>
                        <p className="text-sm text-gray-300">{evaluation.vendors[0].decision.notes}</p>
                      </div>
                    )}
                  </Card>
                )}

                {evaluation.vendors?.[0]?.agent_outputs && (
                  <div className="grid md:grid-cols-2 gap-6">
                    <Card>
                      <h3 className="text-xl font-semibold mb-4 text-white">Dimension Scores</h3>
                      <ul className="text-gray-300 space-y-3">
                        <li className="flex justify-between items-center">
                          <span>Compliance & Security:</span>
                          <span className="font-semibold text-blue-400">
                            {evaluation.vendors[0].agent_outputs?.compliance?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center">
                          <span>Technical Interoperability:</span>
                          <span className="font-semibold text-blue-400">
                            {evaluation.vendors[0].agent_outputs?.interoperability?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center">
                          <span>Finance & TCO:</span>
                          <span className="font-semibold text-blue-400">
                            {evaluation.vendors[0].agent_outputs?.finance?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center">
                          <span>Adoption & Support:</span>
                          <span className="font-semibold text-blue-400">
                            {evaluation.vendors[0].agent_outputs?.adoption?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center pt-3 mt-3 border-t border-gray-700">
                          <span className="font-semibold">Overall Score:</span>
                          <span className="font-bold text-xl text-green-400">
                            {evaluation.vendors[0].total_score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                      </ul>
                    </Card>
                    <Card>
                      <h3 className="text-xl font-semibold mb-4 text-white">Key Findings</h3>
                      <div className="text-gray-300 space-y-3 text-sm">
                        <div>
                          <p className="text-gray-400 font-medium mb-1">🔒 Compliance:</p>
                          <p className="text-gray-300">
                            {(evaluation.vendors[0].agent_outputs?.compliance?.findings || []).slice(0, 2).join('; ') || 'No findings available'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-400 font-medium mb-1">🔧 Integration:</p>
                          <p className="text-gray-300">
                            {(evaluation.vendors[0].agent_outputs?.interoperability?.findings || []).slice(0, 2).join('; ') || 'No findings available'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-400 font-medium mb-1">💰 Finance:</p>
                          <p className="text-gray-300">
                            {evaluation.vendors[0].agent_outputs?.finance?.notes || 'No notes available'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-400 font-medium mb-1">🚀 Support:</p>
                          <p className="text-gray-300">
                            {evaluation.vendors[0].agent_outputs?.adoption?.notes || 'No notes available'}
                          </p>
                        </div>
                      </div>
                    </Card>
                  </div>
                )}
                
                {evaluation.recommendation && (
                  <Card>
                    <h3 className="text-xl font-semibold mb-4 text-white">Recommendation</h3>
                    <div className="bg-[#0f0f0f] rounded-lg p-4 border border-blue-500/20">
                      <p className="text-gray-300">{evaluation.recommendation.reason || 'Evaluation completed'}</p>
                    </div>
                  </Card>
                )}
              </>
            )}

            {evaluation.type === 'assessment' && (
              <div className="space-y-6">
                {/* Rich Recommendation Card */}
                {evaluation.recommendation && evaluation.analysis?.final_recommendation && (() => {
                  const finalRec = evaluation.analysis.final_recommendation;
                  const hasRecommendation = finalRec.recommended_vendor_id && finalRec.recommended_vendor_id !== '';
                  const recommendedVendor = evaluation.vendors?.find((v: any) => v.id === finalRec.recommended_vendor_id);
                  
                  return hasRecommendation ? (
                    // Green card for clear recommendation
                    <div className="rounded-xl border border-emerald-500/60 bg-emerald-900/10 p-6">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                          <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-emerald-400 uppercase mb-1">
                            AI-powered recommendation
                          </div>
                          <div className="text-lg font-semibold text-emerald-100">
                            Recommended: {recommendedVendor?.name || finalRec.recommended_vendor_id}
                          </div>
                        </div>
                      </div>
                      <p className="text-sm text-emerald-50 mb-3">
                        {finalRec.detailed_reason || finalRec.short_reason}
                      </p>
                      {finalRec.key_tradeoffs && finalRec.key_tradeoffs.length > 0 && (
                        <ul className="text-xs text-emerald-100 list-disc list-inside space-y-1">
                          {finalRec.key_tradeoffs.map((tradeoff: string, i: number) => (
                            <li key={i}>{tradeoff}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ) : (
                    // Amber card for insufficient data
                    <div className="rounded-xl border border-amber-500/60 bg-amber-900/10 p-6">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-12 h-12 bg-amber-500/20 rounded-lg flex items-center justify-center">
                          <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-amber-400 uppercase mb-1">
                            AI-powered analysis
                          </div>
                          <div className="text-lg font-semibold text-amber-100">
                            No safe recommendation (insufficient compliance data)
                          </div>
                        </div>
                      </div>
                      <p className="text-sm text-amber-50">
                        {finalRec.detailed_reason || evaluation.recommendation.reason || 'Could not retrieve enough trustworthy documentation to make a compliance-safe recommendation. Formal security and compliance packs must be obtained from vendors before selection.'}
                      </p>
                    </div>
                  );
                })()}

                <Card>
                  <h2 className="text-2xl font-semibold mb-6 text-white">Vendor Comparison</h2>
                  {evaluation.vendors && evaluation.vendors.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="border-b border-gray-700">
                            <th className="pb-3 text-gray-400 font-medium">Vendor</th>
                            <th className="pb-3 text-gray-400 font-medium text-center">Compliance</th>
                            <th className="pb-3 text-gray-400 font-medium text-center">Technical</th>
                            <th className="pb-3 text-gray-400 font-medium text-center">Finance</th>
                            <th className="pb-3 text-gray-400 font-medium text-center">Support</th>
                            <th className="pb-3 text-gray-400 font-medium text-center">Overall</th>
                          </tr>
                        </thead>
                        <tbody>
                          {evaluation.vendors.map((vendor: any, idx: number) => (
                            <tr key={idx} className="border-b border-gray-800">
                              <td className="py-4">
                                <div className="space-y-1.5">
                                  <p className="font-medium text-white">{vendor.name}</p>
                                  <p className="text-sm text-gray-500">{vendor.website}</p>
                                  <DecisionBadge decision={vendor.decision} />
                                </div>
                              </td>
                              <td className="py-4 text-center text-gray-300">
                                {vendor.agent_outputs?.compliance?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center text-gray-300">
                                {vendor.agent_outputs?.interoperability?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center text-gray-300">
                                {vendor.agent_outputs?.finance?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center text-gray-300">
                                {vendor.agent_outputs?.adoption?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center">
                                <span className={`font-bold text-lg ${
                                  vendor.id === evaluation.recommendation?.vendor_id 
                                    ? 'text-green-400' 
                                    : 'text-gray-300'
                                }`}>
                                  {vendor.total_score?.toFixed(1) ?? '—'}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-gray-400">
                      <p>No vendor comparison data available</p>
                    </div>
                  )}
                </Card>

                {/* Per-Vendor Detail Cards */}
                {evaluation.analysis?.per_vendor && evaluation.vendors && evaluation.vendors.length > 0 && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-semibold text-white">Detailed Vendor Analysis</h2>
                    {evaluation.vendors.map((vendor: any) => {
                      const vendorAnalysis = evaluation.analysis.per_vendor[vendor.id];
                      if (!vendorAnalysis) return null;
                      
                      return (
                        <div key={vendor.id} className="rounded-xl border border-slate-700 bg-slate-900/60 p-6">
                          {/* Vendor Header */}
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <div className="text-xs uppercase text-slate-400">Vendor</div>
                              <div className="text-xl font-semibold text-slate-50 mt-1">
                                {vendor.name}
                              </div>
                              <a
                                href={vendor.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-cyan-300 underline hover:text-cyan-200"
                              >
                                {vendor.website}
                              </a>
                            </div>
                            <div className="text-right">
                              <div className="text-xs uppercase text-slate-400">Overall</div>
                              <div className="text-3xl font-bold text-white mt-1">
                                {vendor.total_score?.toFixed(1) ?? '—'}
                              </div>
                            </div>
                          </div>

                          {/* Vendor Headline */}
                          {vendorAnalysis.headline && (
                            <p className="text-sm text-slate-100 mb-4 pb-4 border-b border-slate-700">
                              {vendorAnalysis.headline}
                            </p>
                          )}

                          {/* Decision Action Buttons */}
                          {evaluation.status === 'completed' || evaluation.status === 'finalized' ? (
                            <div className="mb-4 pb-4 border-b border-slate-700">
                              <div className="flex items-center justify-between">
                                <div>
                                  <div className="text-xs uppercase text-slate-400 mb-1">Onboarding Decision</div>
                                  <DecisionBadge decision={vendor.decision} />
                                </div>
                                <div className="flex gap-2">
                                  <button
                                    className="rounded-md border border-emerald-600 bg-emerald-600/10 px-3 py-1.5 text-xs text-emerald-300 hover:bg-emerald-600/20 transition-colors"
                                    onClick={() => openDecisionModal(vendor.id, 'approve')}
                                  >
                                    Approve
                                  </button>
                                  <button
                                    className="rounded-md border border-amber-600 bg-amber-600/10 px-3 py-1.5 text-xs text-amber-300 hover:bg-amber-600/20 transition-colors"
                                    onClick={() => openDecisionModal(vendor.id, 'approve_pending')}
                                  >
                                    Approve w/ Actions
                                  </button>
                                  <button
                                    className="rounded-md border border-rose-600 bg-rose-600/10 px-3 py-1.5 text-xs text-rose-300 hover:bg-rose-600/20 transition-colors"
                                    onClick={() => openDecisionModal(vendor.id, 'decline')}
                                  >
                                    Decline
                                  </button>
                                </div>
                              </div>
                              {vendor.decision?.pending_actions && vendor.decision.pending_actions.length > 0 && (
                                <div className="mt-3">
                                  <div className="text-xs font-semibold text-amber-400 mb-1">Pending Actions:</div>
                                  <ul className="text-xs text-slate-300 space-y-1">
                                    {vendor.decision.pending_actions.map((action: string, i: number) => (
                                      <li key={i} className="flex items-start gap-2">
                                        <span className="text-amber-400">•</span>
                                        <span>{action}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {vendor.decision?.notes && (
                                <div className="mt-2">
                                  <div className="text-xs font-semibold text-slate-400 mb-1">Decision Notes:</div>
                                  <p className="text-xs text-slate-300">{vendor.decision.notes}</p>
                                </div>
                              )}
                            </div>
                          ) : null}

                          {/* 4-dimension grid */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {['security', 'interoperability', 'finance', 'adoption'].map(dim => {
                              const dimData = vendorAnalysis[dim];
                              const score = vendorAnalysis.dimension_scores?.[dim];
                              if (!dimData) return null;
                              
                              return (
                                <div key={dim} className="rounded-lg border border-slate-700/80 bg-slate-800/50 p-4">
                                  <div className="flex justify-between items-center mb-2">
                                    <span className="font-semibold capitalize text-slate-100">{dim}</span>
                                    <span className="text-xs px-2 py-1 rounded-full bg-slate-700 border border-slate-600 text-slate-200">
                                      {typeof score === 'number' ? score.toFixed(1) : '—'}/5
                                    </span>
                                  </div>
                                  <p className="text-sm text-slate-200 mb-3">
                                    {dimData.summary}
                                  </p>
                                  
                                  {/* Strengths */}
                                  {dimData.strengths && dimData.strengths.length > 0 && (
                                    <div className="mb-2">
                                      <div className="text-xs font-semibold text-green-400 mb-1">Strengths:</div>
                                      <ul className="text-xs text-slate-300 space-y-0.5">
                                        {dimData.strengths.slice(0, 2).map((s: string, i: number) => (
                                          <li key={i} className="flex items-start gap-1">
                                            <span className="text-green-400">✓</span>
                                            <span>{s}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  
                                  {/* Risks/Gaps */}
                                  {dimData.risks && dimData.risks.length > 0 && (
                                    <div>
                                      <div className="text-xs font-semibold text-amber-400 mb-1">Risks:</div>
                                      <ul className="text-xs text-slate-300 space-y-0.5">
                                        {dimData.risks.slice(0, 2).map((r: string, i: number) => (
                                          <li key={i} className="flex items-start gap-1">
                                            <span className="text-amber-400">⚠</span>
                                            <span>{r}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {evaluation.onboarding_checklist && evaluation.onboarding_checklist.length > 0 && (
              <Card>
                <h2 className="text-2xl font-semibold mb-6 text-white">Onboarding Checklist</h2>
                <div className="space-y-3">
                  {evaluation.onboarding_checklist.map((item: string, index: number) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-[#0f0f0f] rounded-lg border border-gray-800">
                      <div className="flex-shrink-0 mt-1">
                        <div className="w-5 h-5 border-2 border-blue-500 rounded flex items-center justify-center">
                          <svg className="w-3 h-3 text-blue-400 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      </div>
                      <p className="text-gray-300 flex-1">{item}</p>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}
      </div>

      {/* Decision Modal */}
      {evaluation && (
        <DecisionModal
          evaluationId={evaluationId}
          vendors={evaluation.vendors}
          state={decisionModal}
          onClose={closeDecisionModal}
          onUpdated={handleDecisionUpdate}
        />
      )}
    </div>
  )
}
