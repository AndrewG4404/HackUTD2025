/**
 * Assessment Setup Page
 * Form for internal users to set up vendor comparison
 */
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

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
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Vendor Assessment & Comparison</h1>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-8 space-y-8">
          {/* Basic Info */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Assessment Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Evaluation Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Use Case Description *
                </label>
                <textarea
                  required
                  value={formData.use_case}
                  onChange={(e) => setFormData({ ...formData, use_case: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>
          </div>

          {/* Weights */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Priority Weights (0-5)</h2>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(formData.weights).map(([key, value]) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                    {key}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    value={value}
                    onChange={(e) => setFormData({
                      ...formData,
                      weights: { ...formData.weights, [key]: parseInt(e.target.value) }
                    })}
                    className="w-full"
                  />
                  <div className="text-center text-sm text-gray-600">{value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Vendors */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Vendors</h2>
            <div className="space-y-6">
              {vendors.map((vendor, index) => (
                <div key={vendor.id} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium mb-4">Vendor {String.fromCharCode(65 + index)}</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
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
                        className="w-full px-4 py-2 border border-gray-300 rounded-md"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
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
                        className="w-full px-4 py-2 border border-gray-300 rounded-md"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Documents
                      </label>
                      <input
                        type="file"
                        multiple
                        accept=".pdf,.doc,.docx"
                        onChange={(e) => {
                          const newVendors = [...vendors]
                          newVendors[index].files = Array.from(e.target.files || [])
                          setVendors(newVendors)
                        }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
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
                        className="w-full px-4 py-2 border border-gray-300 rounded-md"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Creating Assessment...' : 'Start Assessment'}
          </button>
        </form>
      </div>
    </main>
  )
}

