/**
 * Internal Dashboard - Modern Assessment Setup with Charts
 * Dashboard-style layout with pie charts and information
 */
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import type { AssessmentFormData, EvaluationSummary } from '@/lib/types'
import Button from '@/components/ui/Button'
import { FileUpload } from '@/components/FileUpload'
import { Modal } from '@/components/Modal'
import { useToast as useToastNotifications } from '@/lib/ToastProvider'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface Vendor {
  id: string
  name: string
  website: string
  files: File[]
  doc_urls: string
}

const COLORS = ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899']

// Weight presets
const WEIGHT_PRESETS = {
  balanced: { security: 3, cost: 3, interoperability: 3, adoption: 3 },
  security_first: { security: 5, cost: 2, interoperability: 3, adoption: 3 },
  cost_focused: { security: 3, cost: 5, interoperability: 2, adoption: 3 },
  integration_focused: { security: 3, cost: 3, interoperability: 5, adoption: 2 },
}

export default function AssessPage() {
  const router = useRouter()
  const toast = useToastNotifications()
  const [loading, setLoading] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [evaluations, setEvaluations] = useState<EvaluationSummary[]>([])
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [formData, setFormData] = useState({
    name: '',
    use_case: '',
    weights: {
      security: 3,
      cost: 3,
      interoperability: 3,
      adoption: 3
    }
  })
  const [vendors, setVendors] = useState<Vendor[]>([
    { id: 'vendor-a', name: '', website: '', files: [], doc_urls: '' },
    { id: 'vendor-b', name: '', website: '', files: [], doc_urls: '' }
  ])
  const [showForm, setShowForm] = useState(false)

  // Fetch evaluations for dashboard stats
  useEffect(() => {
    const fetchEvaluations = async () => {
      if (showForm) return // Don't fetch if showing form
      
      setDashboardLoading(true)
      try {
        console.log('[Assess] Fetching evaluations for dashboard...')
        const data = await api.listEvaluations()
        console.log('[Assess] Fetched evaluations:', data.length)
        setEvaluations(data)
      } catch (error) {
        console.error('[Assess] Error fetching evaluations:', error)
        // Set empty array on error so UI shows "no assessments"
        setEvaluations([])
      } finally {
        setDashboardLoading(false)
      }
    }
    
    fetchEvaluations()
  }, [showForm])

  // Calculate dashboard stats from actual data
  const totalAssessments = evaluations.filter(e => e.type === 'assessment').length
  const activeEvaluations = evaluations.filter(e => e.status === 'running' || e.status === 'pending').length
  const completedEvaluations = evaluations.filter(e => e.status === 'completed')
  // Note: vendor count not available in summary, showing total assessments instead
  const totalVendorsEvaluated = totalAssessments * 2 // Estimate: most assessments compare 2 vendors
  const recentEvaluations = evaluations
    .filter(e => e.type === 'assessment')
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3)

  // Prepare chart data for weights
  const weightChartData = Object.entries(formData.weights).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: value,
    fullMark: 5
  }))

  const totalWeight = Object.values(formData.weights).reduce((a, b) => a + b, 0)

  // Calculate estimated time (vendors × agents × avg time per agent)
  const estimatedMinutes = vendors.length * 7 * 0.5 // 7 agents, ~0.5 min each
  const totalFiles = vendors.reduce((sum, v) => sum + v.files.length, 0)
  const totalUrls = vendors.reduce((sum, v) => sum + (v.doc_urls ? v.doc_urls.split(',').length : 0), 0)

  const applyPreset = (presetKey: keyof typeof WEIGHT_PRESETS) => {
    setFormData({
      ...formData,
      weights: WEIGHT_PRESETS[presetKey]
    })
    toast.success(
      `${presetKey.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')} weights applied`
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const assessmentData: AssessmentFormData = {
        name: formData.name,
        use_case: formData.use_case,
        weights: formData.weights,
        vendors: vendors.map(v => ({
          id: v.id,
          name: v.name,
          website: v.website,
          files: v.files,
          doc_urls: v.doc_urls,
        })),
      }

      console.log('[Assess] Creating assessment...')
      const response = await api.createAssessment(assessmentData)
      const evaluationId = response.id
      console.log('[Assess] Assessment created:', evaluationId)

      setLoading(false)
      setShowSuccessModal(true)
      
      // Redirect after 2 seconds
      setTimeout(() => {
        router.push(`/evaluations/${evaluationId}`)
      }, 2000)
    } catch (error) {
      console.error('[Assess] Error creating assessment:', error)
      const errMsg = error instanceof Error ? error.message : 'Error creating assessment. Please try again.'
      setErrorMessage(errMsg)
      setShowErrorModal(true)
      setLoading(false)
      toast.error(errMsg)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-12">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2 text-white">Vendor Assessment Dashboard</h1>
            <p className="text-gray-400">Compare vendors and get AI-powered recommendations</p>
          </div>
          <Button
            onClick={() => setShowForm(!showForm)}
            variant={showForm ? 'secondary' : 'primary'}
            className="px-6"
          >
            {showForm ? 'View Dashboard' : 'New Assessment'}
          </Button>
        </div>

        {!showForm ? (
          /* Dashboard View */
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6">
                <div className="text-sm text-gray-400 mb-1">Total Assessments</div>
                <div className="text-3xl font-bold text-white">
                  {dashboardLoading ? '—' : totalAssessments}
                </div>
                <div className="text-xs text-green-400 mt-2">All time</div>
              </div>
              <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6">
                <div className="text-sm text-gray-400 mb-1">Active Evaluations</div>
                <div className="text-3xl font-bold text-white">
                  {dashboardLoading ? '—' : activeEvaluations}
                </div>
                <div className="text-xs text-blue-400 mt-2">In progress</div>
              </div>
              <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6">
                <div className="text-sm text-gray-400 mb-1">Vendors Evaluated</div>
                <div className="text-3xl font-bold text-white">
                  {dashboardLoading ? '—' : totalVendorsEvaluated}
                </div>
                <div className="text-xs text-cyan-400 mt-2">All time</div>
              </div>
              <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6">
                <div className="text-sm text-gray-400 mb-1">Completed</div>
                <div className="text-3xl font-bold text-white">
                  {dashboardLoading ? '—' : completedEvaluations.length}
                </div>
                <div className="text-xs text-purple-400 mt-2">Successfully finished</div>
              </div>
            </div>

            {/* Charts and Info Row */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Priority Weights Chart */}
              <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">Priority Weights Distribution</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={weightChartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {weightChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1a1a1a', 
                          border: '1px solid #333',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                        itemStyle={{
                          color: '#fff'
                        }}
                        labelStyle={{
                          color: '#fff'
                        }}
                      />
                      <Legend 
                        wrapperStyle={{ color: '#fff', fontSize: '12px' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="text-sm text-gray-400">Total Weight: <span className="text-white font-semibold">{totalWeight}/20</span></div>
                </div>
              </div>

              {/* Quick Info Card */}
              <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">Assessment Overview</h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                    <div>
                      <div className="text-white font-medium">AI-Powered Analysis</div>
                      <div className="text-sm text-gray-400">Nemotron agents analyze vendors across multiple dimensions</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full mt-2"></div>
                    <div>
                      <div className="text-white font-medium">Multi-Vendor Comparison</div>
                      <div className="text-sm text-gray-400">Compare up to multiple vendors simultaneously</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
                    <div>
                      <div className="text-white font-medium">Customizable Weights</div>
                      <div className="text-sm text-gray-400">Set priority weights for Security, Cost, Interoperability, and Adoption</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-pink-400 rounded-full mt-2"></div>
                    <div>
                      <div className="text-white font-medium">Automated Recommendations</div>
                      <div className="text-sm text-gray-400">Get AI-powered vendor recommendations based on your criteria</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Assessments */}
            <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">Recent Assessments</h3>
              <div className="space-y-3">
                {dashboardLoading ? (
                  <div className="text-center py-8 text-gray-400">Loading...</div>
                ) : recentEvaluations.length > 0 ? (
                  recentEvaluations.map((evaluation) => (
                    <div 
                      key={evaluation.id} 
                      className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 hover:border-blue-500/30 transition-colors cursor-pointer"
                      onClick={() => router.push(`/evaluations/${evaluation.id}`)}
                    >
                      <div>
                        <div className="text-white font-medium">{evaluation.name}</div>
                        <div className="text-sm text-gray-400">
                          {evaluation.type === 'assessment' ? 'Multi-vendor' : 'Single vendor'} • {' '}
                          {new Date(evaluation.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          evaluation.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          evaluation.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                          evaluation.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {evaluation.status.charAt(0).toUpperCase() + evaluation.status.slice(1)}
                        </span>
                        <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">View →</button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <p className="mb-2">No assessments yet</p>
                    <p className="text-sm">Click "New Assessment" to get started</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Assessment Form */
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Assessment Details */}
            <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-8">
              <h2 className="text-2xl font-bold mb-6 text-white">Assessment Details</h2>
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Evaluation Name <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    placeholder="e.g., Q1 2025 Vendor Evaluation"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Use Case Description <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    required
                    value={formData.use_case}
                    onChange={(e) => setFormData({ ...formData, use_case: e.target.value })}
                    rows={5}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-none"
                    placeholder="Describe the use case, requirements, and evaluation criteria..."
                  />
                </div>
              </div>
            </div>

            {/* Priority Weights with Chart */}
            <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
                <div>
                  <h2 className="text-2xl font-bold text-white">Priority Weights</h2>
                  <div className="text-sm text-gray-400 mt-1">Adjust sliders or use presets below</div>
                </div>
                
                {/* Preset Buttons */}
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => applyPreset('balanced')}
                    className="px-3 py-2 bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/30 rounded-lg text-blue-300 text-xs font-medium transition-colors"
                  >
                    ⚖️ Balanced
                  </button>
                  <button
                    type="button"
                    onClick={() => applyPreset('security_first')}
                    className="px-3 py-2 bg-green-600/20 hover:bg-green-600/40 border border-green-500/30 rounded-lg text-green-300 text-xs font-medium transition-colors"
                  >
                    🔒 Security First
                  </button>
                  <button
                    type="button"
                    onClick={() => applyPreset('cost_focused')}
                    className="px-3 py-2 bg-yellow-600/20 hover:bg-yellow-600/40 border border-yellow-500/30 rounded-lg text-yellow-300 text-xs font-medium transition-colors"
                  >
                    💰 Cost Focused
                  </button>
                  <button
                    type="button"
                    onClick={() => applyPreset('integration_focused')}
                    className="px-3 py-2 bg-purple-600/20 hover:bg-purple-600/40 border border-purple-500/30 rounded-lg text-purple-300 text-xs font-medium transition-colors"
                  >
                    🔧 Integration Focused
                  </button>
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  {Object.entries(formData.weights).map(([key, value]) => (
                    <div key={key}>
                      <div className="flex justify-between items-center mb-3">
                        <label className="block text-sm font-medium text-gray-300 capitalize">
                          {key}
                        </label>
                        <span className="text-2xl font-bold text-blue-400">{value}</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="5"
                        value={value}
                        onChange={(e) => setFormData({
                          ...formData,
                          weights: { ...formData.weights, [key]: parseInt(e.target.value) }
                        })}
                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        style={{
                          background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(value / 5) * 100}%, #374151 ${(value / 5) * 100}%, #374151 100%)`
                        }}
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-2">
                        <span>Low Priority</span>
                        <span>High Priority</span>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="flex items-center justify-center">
                  <div className="w-full max-w-xs">
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={weightChartData}
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${value}`}
                        >
                          {weightChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#1a1a1a', 
                            border: '1px solid #333',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                          itemStyle={{
                            color: '#fff'
                          }}
                          labelStyle={{
                            color: '#fff'
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>

            {/* Vendors */}
            <div>
              <h2 className="text-2xl font-bold mb-6 text-white">Vendors to Compare</h2>
              <div className="grid md:grid-cols-2 gap-6">
                {vendors.map((vendor, index) => (
                  <div key={vendor.id} className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-xl p-6 hover:border-blue-500/30 transition-colors">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center">
                        <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-xl flex items-center justify-center mr-4 shadow-lg">
                          <span className="text-white font-bold text-xl">{String.fromCharCode(65 + index)}</span>
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-white">Vendor {String.fromCharCode(65 + index)}</h3>
                          <p className="text-xs text-gray-400">
                            {vendor.files.length} file(s) • {vendor.doc_urls ? vendor.doc_urls.split(',').length : 0} URL(s)
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Vendor Name <span className="text-red-400">*</span>
                          <span className="text-xs text-gray-500 ml-2">e.g., ServiceNow</span>
                        </label>
                        <input
                          type="text"
                          required
                          value={vendor.name}
                          onChange={(e) => {
                            const newVendors = [...vendors]
                            newVendors[index].name = e.target.value
                            setVendors(newVendors)
                          }}
                          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all"
                          placeholder="Company name"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          🌐 Website URL <span className="text-red-400">*</span>
                        </label>
                        <input
                          type="url"
                          required
                          value={vendor.website}
                          onChange={(e) => {
                            const newVendors = [...vendors]
                            newVendors[index].website = e.target.value
                            setVendors(newVendors)
                          }}
                          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all"
                          placeholder="https://example.com"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          📄 Documents
                          <span className="text-xs text-gray-500 ml-2">Optional</span>
                        </label>
                        <FileUpload
                          onFilesChange={(files) => {
                            const newVendors = [...vendors]
                            newVendors[index].files = files
                            setVendors(newVendors)
                          }}
                          currentFiles={vendor.files}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          🔗 Document URLs
                          <span className="text-xs text-gray-500 ml-2">Optional</span>
                        </label>
                        <input
                          type="text"
                          value={vendor.doc_urls}
                          onChange={(e) => {
                            const newVendors = [...vendors]
                            newVendors[index].doc_urls = e.target.value
                            setVendors(newVendors)
                          }}
                          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all"
                          placeholder="https://example.com/security, https://example.com/privacy"
                        />
                        <p className="text-xs text-gray-500 mt-1">💡 Separate with commas</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cost Estimator */}
            <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-xl p-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white mb-2">Estimated Evaluation Time</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div className="bg-black/20 rounded-lg p-3">
                      <div className="text-2xl font-bold text-blue-400">~{Math.ceil(estimatedMinutes)} min</div>
                      <div className="text-xs text-gray-400">Total Time</div>
                    </div>
                    <div className="bg-black/20 rounded-lg p-3">
                      <div className="text-2xl font-bold text-cyan-400">{vendors.length}</div>
                      <div className="text-xs text-gray-400">Vendors</div>
                    </div>
                    <div className="bg-black/20 rounded-lg p-3">
                      <div className="text-2xl font-bold text-purple-400">{totalFiles}</div>
                      <div className="text-xs text-gray-400">Files</div>
                    </div>
                    <div className="bg-black/20 rounded-lg p-3">
                      <div className="text-2xl font-bold text-pink-400">{totalUrls}</div>
                      <div className="text-xs text-gray-400">URLs</div>
                    </div>
                  </div>
                  <p className="text-sm text-blue-300">
                    💡 {vendors.length} vendors × 7 agents × ~30s per agent = ~{Math.ceil(estimatedMinutes)} minutes
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-4">
              <Button 
                type="submit" 
                disabled={loading}
                className="w-full py-4 text-lg"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating Assessment...
                  </span>
                ) : (
                  'Start Assessment →'
                )}
              </Button>
            </div>
          </form>
        )}
      </div>

      {/* Success Modal */}
      <Modal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        type="success"
        title="Assessment Created!"
        showCloseButton={false}
      >
        <p className="mb-4">Your assessment has been created successfully.</p>
        <p className="text-sm text-gray-400">Redirecting to evaluation page...</p>
      </Modal>

      {/* Error Modal */}
      <Modal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        type="error"
        title="Assessment Failed"
      >
        <p className="mb-4">{errorMessage}</p>
        <Button
          onClick={() => setShowErrorModal(false)}
          variant="primary"
          className="w-full"
        >
          Try Again
        </Button>
      </Modal>
    </div>
  )
}
