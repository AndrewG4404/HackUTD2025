/**
 * Assessment Setup Page - Dark Theme Internal Dashboard
 * Form for internal users (Goldman Sachs) to set up vendor comparison
 */
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

interface Vendor {
  id: string
  name: string
  website: string
  files: File[]
  doc_urls: string
}

export default function AssessPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('name', formData.name)
      formDataToSend.append('use_case', formData.use_case)
      formDataToSend.append('weights', JSON.stringify(formData.weights))
      formDataToSend.append('vendors', JSON.stringify(
        vendors.map(v => ({ id: v.id, name: v.name, website: v.website }))
      ))

      // Add files per vendor
      vendors.forEach(vendor => {
        vendor.files.forEach(file => {
          formDataToSend.append(`${vendor.id}_docs`, file)
        })
        if (vendor.doc_urls) {
          formDataToSend.append(`${vendor.id}_doc_urls`, JSON.stringify(
            vendor.doc_urls.split(',').map(url => url.trim()).filter(Boolean)
          ))
        }
      })

      // Create evaluation
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/evaluations/assess`,
        formDataToSend,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )

      const evaluationId = response.data.id

      // Start workflow
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/workflows/assessment/${evaluationId}/run`
      )

      // Redirect to results page
      router.push(`/evaluations/${evaluationId}`)
    } catch (error) {
      console.error('Error creating assessment:', error)
      alert('Error creating assessment. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-12">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 text-white">Vendor Assessment & Comparison</h1>
          <p className="text-gray-400">Compare multiple vendors and get AI-powered recommendations</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Assessment Details */}
          <Card>
            <h2 className="text-xl font-semibold mb-6 text-white">Assessment Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Evaluation Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 bg-[#0f0f0f] border border-gray-800 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="e.g., Q1 2025 Vendor Evaluation"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Use Case Description *
                </label>
                <textarea
                  required
                  value={formData.use_case}
                  onChange={(e) => setFormData({ ...formData, use_case: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-3 bg-[#0f0f0f] border border-gray-800 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                  placeholder="Describe the use case, requirements, and evaluation criteria..."
                />
              </div>
            </div>
          </Card>

          {/* Priority Weights */}
          <Card>
            <h2 className="text-xl font-semibold mb-6 text-white">Priority Weights (0-5)</h2>
            <div className="grid grid-cols-2 gap-6">
              {Object.entries(formData.weights).map(([key, value]) => (
                <div key={key}>
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium text-gray-300 capitalize">
                      {key}
                    </label>
                    <span className="text-lg font-semibold text-blue-400">{value}</span>
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
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Low</span>
                    <span>High</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Vendors */}
          <div>
            <h2 className="text-xl font-semibold mb-6 text-white">Vendors</h2>
            <div className="space-y-6">
              {vendors.map((vendor, index) => (
                <Card key={vendor.id}>
                  <div className="flex items-center mb-6">
                    <div className="w-10 h-10 bg-cyan-600/20 rounded-lg flex items-center justify-center mr-3">
                      <span className="text-cyan-400 font-bold">{String.fromCharCode(65 + index)}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-white">Vendor {String.fromCharCode(65 + index)}</h3>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Vendor Name *
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
                        className="w-full px-4 py-3 bg-[#0f0f0f] border border-gray-800 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        placeholder="Company name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Website URL *
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
                        className="w-full px-4 py-3 bg-[#0f0f0f] border border-gray-800 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        placeholder="https://example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Documents
                      </label>
                      <div className="border-2 border-dashed border-gray-700 rounded-md p-4 hover:border-blue-500 transition-colors">
                        <input
                          type="file"
                          multiple
                          accept=".pdf,.doc,.docx"
                          onChange={(e) => {
                            const newVendors = [...vendors]
                            newVendors[index].files = Array.from(e.target.files || [])
                            setVendors(newVendors)
                          }}
                          className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
                        />
                        {vendor.files.length > 0 && (
                          <div className="mt-3">
                            <p className="text-sm text-gray-400 mb-2">Selected files:</p>
                            <ul className="list-disc list-inside text-sm text-gray-500">
                              {vendor.files.map((file, idx) => (
                                <li key={idx}>{file.name}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Document URLs (comma-separated)
                      </label>
                      <input
                        type="text"
                        value={vendor.doc_urls}
                        onChange={(e) => {
                          const newVendors = [...vendors]
                          newVendors[index].doc_urls = e.target.value
                          setVendors(newVendors)
                        }}
                        className="w-full px-4 py-3 bg-[#0f0f0f] border border-gray-800 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        placeholder="https://example.com/security, https://example.com/privacy"
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          <div className="pt-4">
            <Button 
              type="submit" 
              disabled={loading}
              className="w-full"
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
                'Start Assessment'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
