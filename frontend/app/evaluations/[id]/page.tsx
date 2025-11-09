/**
 * Evaluation Results Page - Dark Theme
 * Shows pipeline status and results for both application and assessment workflows
 */
'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'next/navigation'
import api from '@/lib/api'
import type { Evaluation } from '@/lib/types'
import Card from '@/components/ui/Card'
import { WorkflowVisualization } from '@/components/WorkflowVisualization'

export default function EvaluationPage() {
  const params = useParams()
  const evaluationId = params.id as string
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const [loading, setLoading] = useState(true)

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

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-amber-300">🔮 Consulting the ancient scrolls...</p>
        </div>
      </div>
    )
  }

  if (!evaluation) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-xl">📜 This prophecy scroll has been lost to time</p>
        </div>
      </div>
    )
  }

  const isRunning = evaluation.status === 'pending' || evaluation.status === 'running'
  const isCompleted = evaluation.status === 'completed'
  const isFailed = evaluation.status === 'failed'
  
  // Show workflow visualization for pending, running, AND if recently completed (within 2 mins)
  const showWorkflow = isRunning || (isCompleted && evaluation.updated_at && 
    (Date.now() - new Date(evaluation.updated_at).getTime()) < 120000)

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 text-gradient">{evaluation.name}</h1>
          <div className="flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium border-2 ${
              isRunning ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' :
              isCompleted ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
              isFailed ? 'bg-red-500/20 text-red-400 border-red-500/40' :
              'bg-gray-500/20 text-gray-400 border-gray-500/40'
            }`}>
              {isRunning ? '🔮 CHANNELING' : isCompleted ? '✨ PROPHECY COMPLETE' : isFailed ? '❌ RITUAL FAILED' : evaluation.status.toUpperCase()}
            </span>
            <span className="text-amber-300 text-sm">
              {evaluation.type === 'application' ? '📜 Single Vendor' : '🏰 Multi-Vendor Quest'}
            </span>
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
              <h2 className="text-xl font-semibold text-red-400">❌ Case Investigation Failed</h2>
          </div>
            <p className="text-gray-300">{evaluation.error || 'The investigation encountered an unknown obstacle'}</p>
          </Card>
        )}

        {isCompleted && (
          <div className="space-y-8">
            {evaluation.type === 'application' && (
              <>
                {evaluation.vendors?.[0]?.agent_outputs && (
                  <div className="grid md:grid-cols-2 gap-6">
                    <Card className="border-2 border-purple-500/30 magical-glow">
                      <h3 className="text-xl font-semibold mb-4 text-gradient">🔮 Mystical Realm Scores</h3>
                      <ul className="text-gray-300 space-y-3">
                        <li className="flex justify-between items-center">
                          <span>🔒 Guardian's Shield:</span>
                          <span className="font-semibold text-purple-400">
                            {evaluation.vendors[0].agent_outputs?.compliance?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center">
                          <span>🔮 Weaver's Web:</span>
                          <span className="font-semibold text-purple-400">
                            {evaluation.vendors[0].agent_outputs?.interoperability?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center">
                          <span>💰 Golden Treasury:</span>
                          <span className="font-semibold text-purple-400">
                            {evaluation.vendors[0].agent_outputs?.finance?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center">
                          <span>🌟 Herald's Blessing:</span>
                          <span className="font-semibold text-purple-400">
                            {evaluation.vendors[0].agent_outputs?.adoption?.score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                        <li className="flex justify-between items-center pt-3 mt-3 border-t border-purple-500/30">
                          <span className="font-semibold text-amber-200">⭐ Destiny Score:</span>
                          <span className="font-bold text-xl text-amber-400">
                            {evaluation.vendors[0].total_score?.toFixed(1) ?? '—'}/5.0
                          </span>
                        </li>
                      </ul>
                    </Card>
                    <Card className="border-2 border-purple-500/30 magical-glow">
                      <h3 className="text-xl font-semibold mb-4 text-gradient">📜 Sage Revelations</h3>
                      <div className="text-gray-300 space-y-3 text-sm">
                        <div>
                          <p className="text-amber-300 font-medium mb-1">🔒 Guardian's Vision:</p>
                          <p className="text-gray-300">
                            {(evaluation.vendors[0].agent_outputs?.compliance?.findings || []).slice(0, 2).join('; ') || 'The mists reveal nothing'}
                          </p>
                        </div>
                        <div>
                          <p className="text-amber-300 font-medium mb-1">🔮 Weaver's Insight:</p>
                          <p className="text-gray-300">
                            {(evaluation.vendors[0].agent_outputs?.interoperability?.findings || []).slice(0, 2).join('; ') || 'The threads remain unseen'}
                          </p>
                        </div>
                        <div>
                          <p className="text-amber-300 font-medium mb-1">💰 Keeper's Wisdom:</p>
                          <p className="text-gray-300">
                            {evaluation.vendors[0].agent_outputs?.finance?.notes || 'The ledger holds no secrets'}
                          </p>
                        </div>
                        <div>
                          <p className="text-amber-300 font-medium mb-1">🌟 Herald's Proclamation:</p>
                          <p className="text-gray-300">
                            {evaluation.vendors[0].agent_outputs?.adoption?.notes || 'The bells remain silent'}
                          </p>
                        </div>
                      </div>
                    </Card>
              </div>
                )}
                
                {evaluation.recommendation && (
                  <Card className="border-2 border-purple-500/30 magical-glow">
                    <h3 className="text-xl font-semibold mb-4 text-gradient">🔮 The Oracle's Prophecy</h3>
                    <div className="bg-[#0f0f0f] rounded-lg p-4 border border-purple-500/20">
                      <p className="text-amber-200">{evaluation.recommendation.reason || 'The prophecy has been fulfilled'}</p>
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
                            🕵️ INVESTIGATOR'S VERDICT
                          </div>
                          <div className="text-lg font-semibold text-emerald-100">
                            Case Closed - Suspect Cleared: {recommendedVendor?.name || finalRec.recommended_vendor_id}
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
                            ⚠️ Case Inconclusive - Insufficient Evidence
                          </div>
                        </div>
                      </div>
                      <p className="text-sm text-amber-50">
                        {finalRec.detailed_reason || evaluation.recommendation.reason || 'Could not retrieve enough trustworthy documentation to make a compliance-safe recommendation. Formal security and compliance packs must be obtained from vendors before selection.'}
                      </p>
                    </div>
                  );
                })()}

                <Card className="border-2 border-purple-500/30 magical-glow">
                  <h2 className="text-2xl font-semibold mb-6 text-gradient">🏰 Realm Comparison Chronicle</h2>
                  {evaluation.vendors && evaluation.vendors.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="border-b border-purple-500/30">
                            <th className="pb-3 text-amber-300 font-medium">Vendor</th>
                            <th className="pb-3 text-amber-300 font-medium text-center">🔒 Guardian</th>
                            <th className="pb-3 text-amber-300 font-medium text-center">🔮 Weaver</th>
                            <th className="pb-3 text-amber-300 font-medium text-center">💰 Keeper</th>
                            <th className="pb-3 text-amber-300 font-medium text-center">🌟 Herald</th>
                            <th className="pb-3 text-amber-300 font-medium text-center">⭐ Destiny</th>
                          </tr>
                        </thead>
                        <tbody>
                          {evaluation.vendors.map((vendor: any, idx: number) => (
                            <tr key={idx} className="border-b border-gray-800">
                              <td className="py-4">
                                <div>
                                  <p className="font-medium text-white">{vendor.name}</p>
                                  <p className="text-sm text-gray-500">{vendor.website}</p>
                                </div>
                              </td>
                              <td className="py-4 text-center text-purple-300">
                                {vendor.agent_outputs?.compliance?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center text-purple-300">
                                {vendor.agent_outputs?.interoperability?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center text-purple-300">
                                {vendor.agent_outputs?.finance?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center text-purple-300">
                                {vendor.agent_outputs?.adoption?.score?.toFixed(1) ?? '—'}
                              </td>
                              <td className="py-4 text-center">
                                <span className={`font-bold text-lg ${
                                  vendor.id === evaluation.recommendation?.vendor_id 
                                    ? 'text-amber-400' 
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
                    <div className="text-amber-300">
                      <p>The crystal orb reveals no comparison data</p>
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
              <Card className="border-2 border-purple-500/30 magical-glow">
                <h2 className="text-2xl font-semibold mb-6 text-gradient">📜 Quest Preparation Scroll</h2>
                <div className="space-y-3">
                  {evaluation.onboarding_checklist.map((item: string, index: number) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-[#0f0f0f] rounded-lg border border-purple-500/20">
                      <div className="flex-shrink-0 mt-1">
                        <div className="w-5 h-5 border-2 border-purple-500 rounded flex items-center justify-center">
                          <svg className="w-3 h-3 text-purple-400 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    </div>
  )
}
