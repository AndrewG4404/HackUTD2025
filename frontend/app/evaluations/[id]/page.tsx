/**
 * Evaluation Results Page
 * Shows pipeline status and results for both application and assessment workflows
 */
'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import axios from 'axios'

interface Evaluation {
  id: string
  type: string
  name: string
  status: string
  vendors?: any[]
  recommendation?: any
  onboarding_checklist?: string[]
  error?: string
}

export default function EvaluationPage() {
  const params = useParams()
  const evaluationId = params.id as string
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchEvaluation = async () => {
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/evaluations/${evaluationId}`
        )
        setEvaluation(response.data)
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
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading evaluation...</p>
        </div>
      </main>
    )
  }

  if (!evaluation) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Evaluation not found</p>
        </div>
      </main>
    )
  }

  const isRunning = evaluation.status === 'pending' || evaluation.status === 'running'
  const isCompleted = evaluation.status === 'completed'
  const isFailed = evaluation.status === 'failed'

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">{evaluation.name}</h1>
        
        {isRunning && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-xl font-semibold mb-4">Pipeline Status: {evaluation.status}</h2>
            <div className="space-y-4">
              <p className="text-gray-600">Processing evaluation...</p>
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 mt-2"></div>
              </div>
            </div>
          </div>
        )}

        {isFailed && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-8">
            <h2 className="text-xl font-semibold text-red-800 mb-4">Evaluation Failed</h2>
            <p className="text-red-600">{evaluation.error || 'Unknown error occurred'}</p>
          </div>
        )}

        {isCompleted && (
          <div className="space-y-8">
            {evaluation.type === 'application' && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-semibold mb-6">Application Results</h2>
                {/* TODO: Render vendor profile, dimension scores, verification flags, checklist */}
                <p className="text-gray-600">Results will be displayed here</p>
              </div>
            )}

            {evaluation.type === 'assessment' && (
              <div className="space-y-6">
                {evaluation.recommendation && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <h2 className="text-xl font-semibold text-green-800 mb-2">
                      Recommended Vendor
                    </h2>
                    <p className="text-green-700">{evaluation.recommendation.reason}</p>
                  </div>
                )}

                <div className="bg-white rounded-lg shadow-md p-8">
                  <h2 className="text-2xl font-semibold mb-6">Comparison Results</h2>
                  {/* TODO: Render comparison table and radar chart */}
                  <p className="text-gray-600">Comparison results will be displayed here</p>
                </div>
              </div>
            )}

            {evaluation.onboarding_checklist && evaluation.onboarding_checklist.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-semibold mb-4">Onboarding Checklist</h2>
                <ul className="list-disc list-inside space-y-2">
                  {evaluation.onboarding_checklist.map((item, index) => (
                    <li key={index} className="text-gray-700">{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}

