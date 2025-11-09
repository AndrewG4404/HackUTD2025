/**
 * Evaluation Results Page - Dark Theme
 * Shows pipeline status and results for both application and assessment workflows
 */
'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import api from '@/lib/api'
import type { Evaluation } from '@/lib/types'
import Card from '@/components/ui/Card'

export default function EvaluationPage() {
  const params = useParams()
  const evaluationId = params.id as string
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchEvaluation = async () => {
      try {
        const data = await api.getEvaluation(evaluationId)
        setEvaluation(data)
      } catch (error) {
        console.error('Error fetching evaluation:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchEvaluation()

    // Poll if status is pending or running
    const interval = setInterval(() => {
      if (evaluation?.status === 'pending' || evaluation?.status === 'running') {
        fetchEvaluation()
      }
    }, 5000) // Poll every 5 seconds

    return () => clearInterval(interval)
  }, [evaluationId, evaluation?.status])

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
  const isCompleted = evaluation.status === 'completed'
  const isFailed = evaluation.status === 'failed'

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 text-white">{evaluation.name}</h1>
          <div className="flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              isRunning ? 'bg-yellow-500/20 text-yellow-400' :
              isCompleted ? 'bg-green-500/20 text-green-400' :
              isFailed ? 'bg-red-500/20 text-red-400' :
              'bg-gray-500/20 text-gray-400'
            }`}>
              {evaluation.status.toUpperCase()}
            </span>
            <span className="text-gray-500 text-sm">{evaluation.type}</span>
          </div>
        </div>
        
        {isRunning && (
          <Card>
            <div className="flex items-center mb-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-4"></div>
              <h2 className="text-xl font-semibold text-white">Pipeline Status: {evaluation.status}</h2>
            </div>
            <div className="space-y-4">
              <p className="text-gray-400">Processing evaluation with AI agents...</p>
              <div className="space-y-2">
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                </div>
                <p className="text-sm text-gray-500">This may take a few minutes</p>
              </div>
            </div>
          </Card>
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
                {evaluation.recommendation && (
                  <Card>
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mr-4">
                        <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div>
                        <h2 className="text-xl font-semibold text-green-400">Recommended: {evaluation.recommendation.vendor_id}</h2>
                        <p className="text-sm text-gray-400">AI-powered recommendation</p>
                      </div>
                    </div>
                    <div className="bg-[#0f0f0f] rounded-lg p-4 border border-green-500/20">
                      <p className="text-gray-300">{evaluation.recommendation.reason || evaluation.recommendation}</p>
                    </div>
                  </Card>
                )}

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
                                <div>
                                  <p className="font-medium text-white">{vendor.name}</p>
                                  <p className="text-sm text-gray-500">{vendor.website}</p>
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
              </div>
            )}

            {evaluation.onboarding_checklist && evaluation.onboarding_checklist.length > 0 && (
              <Card>
                <h2 className="text-2xl font-semibold mb-6 text-white">Onboarding Checklist</h2>
                <div className="space-y-3">
                  {evaluation.onboarding_checklist.map((item, index) => (
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
    </div>
  )
}
