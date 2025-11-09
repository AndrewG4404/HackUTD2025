/**
 * Vendor Portal - Modern User-Friendly Application
 * Step-by-step wizard style, less form-like
 */
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'
import type { ApplicationFormData } from '@/lib/types'
import Button from '@/components/ui/Button'

type Step = 1 | 2 | 3

export default function ApplyPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState<Step>(1)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    website: '',
    contact_email: '',
    hq_location: '',
    product_name: '',
    product_description: '',
    doc_urls: ''
  })
  const [files, setFiles] = useState<File[]>([])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const applicationData: ApplicationFormData = {
        name: formData.name,
        website: formData.website,
        contact_email: formData.contact_email,
        hq_location: formData.hq_location || undefined,
        product_name: formData.product_name || undefined,
        product_description: formData.product_description || undefined,
        doc_urls: formData.doc_urls || undefined,
        docs: files.length > 0 ? files : undefined,
      }

      const response = await api.createApplication(applicationData)
      const evaluationId = response.id

      await api.runApplicationWorkflow(evaluationId)

      router.push(`/evaluations/${evaluationId}`)
    } catch (error) {
      console.error('Error submitting application:', error)
      const errorMessage = error instanceof Error ? error.message : 'Error submitting application. Please try again.'
      alert(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const canProceedStep1 = formData.name && formData.website && formData.contact_email
  const canProceedStep2 = true // Step 2 is optional fields
  const canSubmit = canProceedStep1

  const steps = [
    { number: 1, title: 'Company Information', current: currentStep === 1 },
    { number: 2, title: 'Product Details', current: currentStep === 2 },
    { number: 3, title: 'Documents', current: currentStep === 3 },
  ]

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold mb-4 text-white">
            Welcome to <span className="text-gradient">VendorLens</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Let's get your company onboarded with Goldman Sachs. This will only take a few minutes.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-8">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div className={`
                    w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all
                    ${step.current 
                      ? 'bg-blue-600 text-white ring-4 ring-blue-600/30' 
                      : currentStep > step.number
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-400'
                    }
                  `}>
                    {currentStep > step.number ? (
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      step.number
                    )}
                  </div>
                  <p className={`mt-3 text-sm font-medium ${step.current ? 'text-white' : 'text-gray-500'}`}>
                    {step.title}
                  </p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-4 ${currentStep > step.number ? 'bg-green-600' : 'bg-gray-700'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form Card */}
        <div className="backdrop-blur-xl bg-black/30 border border-white/10 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit}>
            {/* Step 1: Company Information */}
            {currentStep === 1 && (
              <div className="space-y-6 animate-fade-in">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-white mb-2">Tell us about your company</h2>
                  <p className="text-gray-400">We need some basic information to get started</p>
                </div>

                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Company Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="Enter your company name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Website URL <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="url"
                      required
                      value={formData.website}
                      onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="https://yourcompany.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Contact Email <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.contact_email}
                      onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="contact@yourcompany.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Headquarters Location
                    </label>
                    <input
                      type="text"
                      value={formData.hq_location}
                      onChange={(e) => setFormData({ ...formData, hq_location: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="City, Country (optional)"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-6">
                  <Button
                    type="button"
                    onClick={() => setCurrentStep(2)}
                    disabled={!canProceedStep1}
                    className="px-8"
                  >
                    Continue →
                  </Button>
                </div>
              </div>
            )}

            {/* Step 2: Product Details */}
            {currentStep === 2 && (
              <div className="space-y-6 animate-fade-in">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-white mb-2">Product Information</h2>
                  <p className="text-gray-400">Tell us about what you're offering (optional but recommended)</p>
                </div>

                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Product Name
                    </label>
                    <input
                      type="text"
                      value={formData.product_name}
                      onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="Your product or service name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Product Description
                    </label>
                    <textarea
                      value={formData.product_description}
                      onChange={(e) => setFormData({ ...formData, product_description: e.target.value })}
                      rows={5}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-none"
                      placeholder="Describe your product or service, target market, key features..."
                    />
                  </div>
                </div>

                <div className="flex justify-between pt-6">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setCurrentStep(1)}
                    className="px-8"
                  >
                    ← Back
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setCurrentStep(3)}
                    className="px-8"
                  >
                    Continue →
                  </Button>
                </div>
              </div>
            )}

            {/* Step 3: Documents */}
            {currentStep === 3 && (
              <div className="space-y-6 animate-fade-in">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-white mb-2">Supporting Documents</h2>
                  <p className="text-gray-400">Upload documents or provide links to help us evaluate your company</p>
                </div>

                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Upload Documents
                    </label>
                    <div className="border-2 border-dashed border-white/20 rounded-xl p-8 hover:border-blue-500/50 transition-all bg-white/5">
                      <div className="text-center">
                        <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <input
                          type="file"
                          multiple
                          accept=".pdf,.doc,.docx"
                          onChange={(e) => setFiles(Array.from(e.target.files || []))}
                          className="hidden"
                          id="file-upload"
                        />
                        <label
                          htmlFor="file-upload"
                          className="cursor-pointer inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        >
                          Choose Files
                        </label>
                        <p className="text-sm text-gray-400 mt-2">PDF, DOC, or DOCX files</p>
                      </div>
                      {files.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-white/10">
                          <p className="text-sm text-gray-400 mb-3">Selected files:</p>
                          <div className="space-y-2">
                            {files.map((file, idx) => (
                              <div key={idx} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                                <span className="text-white text-sm">{file.name}</span>
                                <button
                                  type="button"
                                  onClick={() => setFiles(files.filter((_, i) => i !== idx))}
                                  className="text-red-400 hover:text-red-300"
                                >
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                  </svg>
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Document URLs (optional)
                    </label>
                    <input
                      type="text"
                      value={formData.doc_urls}
                      onChange={(e) => setFormData({ ...formData, doc_urls: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="https://example.com/security, https://example.com/privacy"
                    />
                    <p className="text-xs text-gray-500 mt-2">Separate multiple URLs with commas</p>
                  </div>
                </div>

                <div className="flex justify-between pt-6">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setCurrentStep(2)}
                    className="px-8"
                  >
                    ← Back
                  </Button>
                  <Button
                    type="submit"
                    disabled={loading || !canSubmit}
                    className="px-8"
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Submitting...
                      </span>
                    ) : (
                      'Submit Application ✓'
                    )}
                  </Button>
                </div>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
