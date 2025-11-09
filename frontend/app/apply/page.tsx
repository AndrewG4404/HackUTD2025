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
import { useToast } from '@/lib/ToastProvider'
import { FileUpload } from '@/components/FileUpload'
import { Modal } from '@/components/Modal'

type Step = 1 | 2 | 3 | 4

interface FieldValidation {
  [key: string]: {
    isValid: boolean
    message?: string
  }
}

export default function ApplyPage() {
  const router = useRouter()
  const toast = useToast()
  const [currentStep, setCurrentStep] = useState<Step>(1)
  const [loading, setLoading] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
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
  const [validation, setValidation] = useState<FieldValidation>({})

  // Validation functions
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url)
      return url.startsWith('http://') || url.startsWith('https://')
    } catch {
      return false
    }
  }

  const validateField = (field: string, value: string) => {
    let isValid = true
    let message = ''

    switch (field) {
      case 'contact_email':
        isValid = validateEmail(value)
        message = isValid ? '' : 'Please enter a valid email address'
        break
      case 'website':
        isValid = value ? validateUrl(value) : true
        message = isValid ? '' : 'Please enter a valid URL (starting with http:// or https://)'
        break
      case 'name':
        isValid = value.length > 0
        message = isValid ? '' : 'Company name is required'
        break
    }

    setValidation(prev => ({
      ...prev,
      [field]: { isValid, message }
    }))

    return isValid
  }

  const handleFieldChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value })
    if (value) {
      validateField(field, value)
    }
  }

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

      console.log('[Apply] Creating application...')
      const response = await api.createApplication(applicationData)
      const evaluationId = response.id
      console.log('[Apply] Application created:', evaluationId)

      setLoading(false)
      setShowSuccessModal(true)
      
      // Redirect after 2 seconds
      setTimeout(() => {
        router.push(`/evaluations/${evaluationId}`)
      }, 2000)
    } catch (error) {
      console.error('[Apply] Error submitting application:', error)
      const errMsg = error instanceof Error ? error.message : 'Error submitting application. Please try again.'
      setErrorMessage(errMsg)
      setShowErrorModal(true)
      setLoading(false)
      toast.error(errMsg)
    }
  }

  const canProceedStep1 = formData.name && formData.website && formData.contact_email && 
    validation.name?.isValid !== false && 
    validation.website?.isValid !== false && 
    validation.contact_email?.isValid !== false
  const canProceedStep2 = true // Step 2 is optional fields
  const canSubmit = canProceedStep1

  const steps = [
    { number: 1, title: 'Chapter I: Origins', current: currentStep === 1 },
    { number: 2, title: 'Chapter II: The Offering', current: currentStep === 2 },
    { number: 3, title: 'Chapter III: Sacred Scrolls', current: currentStep === 3 },
    { number: 4, title: 'Chapter IV: The Prophecy', current: currentStep === 4 },
  ]

  const progressPercentage = (currentStep / steps.length) * 100
  const estimatedTimeRemaining = Math.max(0, (steps.length - currentStep) * 1) // 1 min per step

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold mb-4 text-white">
            ✨ Begin Your <span className="text-gradient">Mystical Journey</span>
          </h1>
          <p className="text-xl text-amber-200/80 max-w-2xl mx-auto">
            Step through the portal. Share your tale so the Seven Sages may divine your company's destiny.
          </p>
          
          {/* Progress Indicator */}
          <div className="mt-6 max-w-md mx-auto">
            <div className="flex justify-between text-sm text-amber-300 mb-2">
              <span>📜 Journey Progress: {progressPercentage.toFixed(0)}% Complete</span>
              <span>⏳ ~{estimatedTimeRemaining} min remaining</span>
            </div>
            <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden border border-purple-500/30">
              <div 
                className="h-full bg-gradient-to-r from-purple-600 via-pink-500 to-amber-500 transition-all duration-500 ease-out"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-start justify-center gap-4">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                {/* Step Container */}
                <div className="flex flex-col items-center" style={{ width: '140px' }}>
                  {/* Circle */}
                  <div className={`
                    w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all border-2
                    ${step.current 
                      ? 'bg-purple-600 text-white ring-4 ring-purple-500/40 border-amber-400' 
                      : currentStep > step.number
                      ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white border-amber-300'
                      : 'bg-gray-700 text-gray-400 border-gray-600'
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
                  {/* Label */}
                  <p className={`mt-3 text-sm font-medium text-center ${step.current ? 'text-amber-200' : 'text-gray-500'}`}>
                    {step.title}
                  </p>
                </div>
                
                {/* Connecting Line */}
                {index < steps.length - 1 && (
                  <div 
                    className={`h-1 transition-all ${currentStep > step.number ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gray-700'}`}
                    style={{ width: '80px', marginBottom: '50px' }}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form Card */}
        <div className="backdrop-blur-xl bg-black/30 border-2 border-purple-500/30 rounded-2xl p-8 shadow-2xl magical-glow">
          <form onSubmit={handleSubmit}>
            {/* Step 1: Company Information */}
            {currentStep === 1 && (
              <div className="space-y-6 animate-fade-in">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gradient mb-2">📜 Chapter I: Origins</h2>
                  <p className="text-amber-200/70">Inscribe the origins of your company into the ancient records</p>
                </div>

                <div className="space-y-5">
                  {/* Company Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Company Name <span className="text-red-400">*</span>
                      <span className="text-xs text-gray-500 ml-2">e.g., ServiceNow, Salesforce</span>
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => handleFieldChange('name', e.target.value)}
                        onBlur={(e) => validateField('name', e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all pr-10"
                        placeholder="Enter your company name"
                      />
                      {validation.name?.isValid && formData.name && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          <svg className="w-5 h-5 text-green-400 animate-checkmark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                    {validation.name?.message && (
                      <p className="text-red-400 text-xs mt-1">{validation.name.message}</p>
                    )}
                  </div>

                  {/* Website URL */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Website URL <span className="text-red-400">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="url"
                        required
                        value={formData.website}
                        onChange={(e) => handleFieldChange('website', e.target.value)}
                        onBlur={(e) => validateField('website', e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all pr-10"
                        placeholder="https://yourcompany.com"
                      />
                      {validation.website?.isValid && formData.website && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          <svg className="w-5 h-5 text-green-400 animate-checkmark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                    {validation.website?.message && (
                      <p className="text-red-400 text-xs mt-1">{validation.website.message}</p>
                    )}
                  </div>

                  {/* Contact Email */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Contact Email <span className="text-red-400">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="email"
                        required
                        value={formData.contact_email}
                        onChange={(e) => handleFieldChange('contact_email', e.target.value)}
                        onBlur={(e) => validateField('contact_email', e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all pr-10"
                        placeholder="contact@yourcompany.com"
                      />
                      {validation.contact_email?.isValid && formData.contact_email && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          <svg className="w-5 h-5 text-green-400 animate-checkmark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                    {validation.contact_email?.message && (
                      <p className="text-red-400 text-xs mt-1">{validation.contact_email.message}</p>
                    )}
                  </div>

                  {/* HQ Location */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Headquarters Location
                      <span className="text-xs text-gray-500 ml-2">Optional</span>
                    </label>
                    <input
                      type="text"
                      value={formData.hq_location}
                      onChange={(e) => setFormData({ ...formData, hq_location: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all"
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
                  <h2 className="text-2xl font-bold text-gradient mb-2">✨ Chapter II: The Offering</h2>
                  <p className="text-amber-200/70">Reveal the magic your company brings to the realm (optional but enhances the prophecy)</p>
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
                  <h2 className="text-2xl font-bold text-gradient mb-2">📜 Chapter III: Sacred Scrolls</h2>
                  <p className="text-amber-200/70">Present the ancient scrolls and sacred texts for the Sages' divination</p>
                </div>

                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Upload Documents
                      <span className="text-xs text-gray-500 ml-2">Optional but recommended</span>
                    </label>
                    <FileUpload 
                      onFilesChange={setFiles}
                      currentFiles={files}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Document URLs
                      <span className="text-xs text-gray-500 ml-2">Optional</span>
                    </label>
                    <input
                      type="text"
                      value={formData.doc_urls}
                      onChange={(e) => setFormData({ ...formData, doc_urls: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none input-focus-glow transition-all"
                      placeholder="https://example.com/security, https://example.com/privacy"
                    />
                    <p className="text-xs text-gray-500 mt-2">💡 Separate multiple URLs with commas</p>
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
                    type="button"
                    onClick={() => setCurrentStep(4)}
                    className="px-8"
                  >
                    Continue to Review →
                  </Button>
                </div>
              </div>
            )}

            {/* Step 4: Review & Submit */}
            {currentStep === 4 && (
              <div className="space-y-6 animate-fade-in">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gradient mb-2">🔮 Chapter IV: The Prophecy</h2>
                  <p className="text-amber-200/70">Review your tale before the Sages divine your destiny</p>
                </div>

                <div className="space-y-4">
                  {/* Company Info Review */}
                  <div className="bg-black/30 rounded-xl p-6 border border-purple-500/20">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-amber-200">📜 Origins</h3>
                      <button
                        type="button"
                        onClick={() => setCurrentStep(1)}
                        className="text-purple-400 hover:text-purple-300 text-sm"
                      >
                        ✏️ Edit
                      </button>
                    </div>
                    <div className="space-y-2 text-gray-300 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Company Name:</span>
                        <span className="font-medium">{formData.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Website:</span>
                        <span className="font-medium">{formData.website}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Contact Email:</span>
                        <span className="font-medium">{formData.contact_email}</span>
                      </div>
                      {formData.hq_location && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Headquarters:</span>
                          <span className="font-medium">{formData.hq_location}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Product Info Review */}
                  {(formData.product_name || formData.product_description) && (
                    <div className="bg-black/30 rounded-xl p-6 border border-purple-500/20">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-lg font-semibold text-amber-200">✨ The Offering</h3>
                        <button
                          type="button"
                          onClick={() => setCurrentStep(2)}
                          className="text-purple-400 hover:text-purple-300 text-sm"
                        >
                          ✏️ Edit
                        </button>
                      </div>
                      <div className="space-y-2 text-gray-300 text-sm">
                        {formData.product_name && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">Product Name:</span>
                            <span className="font-medium">{formData.product_name}</span>
                          </div>
                        )}
                        {formData.product_description && (
                          <div>
                            <span className="text-gray-400 block mb-1">Description:</span>
                            <p className="text-gray-300">{formData.product_description}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Documents Review */}
                  <div className="bg-black/30 rounded-xl p-6 border border-purple-500/20">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-amber-200">📜 Sacred Scrolls</h3>
                      <button
                        type="button"
                        onClick={() => setCurrentStep(3)}
                        className="text-purple-400 hover:text-purple-300 text-sm"
                      >
                        ✏️ Edit
                      </button>
                    </div>
                    <div className="space-y-2 text-gray-300 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Files Uploaded:</span>
                        <span className="font-medium">{files.length} file(s)</span>
                      </div>
                      {formData.doc_urls && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Document URLs:</span>
                          <span className="font-medium">{formData.doc_urls.split(',').length} URL(s)</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-4 mt-6">
                  <p className="text-purple-300 text-sm">
                    🔮 Once submitted, the Seven Sages will begin their mystical divination. The prophecy typically manifests within 5-8 minutes.
                  </p>
                </div>

                <div className="flex justify-between pt-6">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setCurrentStep(3)}
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
                            ✨ Summoning the Sages...
                          </span>
                        ) : (
                          '🔮 Summon the Seven Sages'
                        )}
                  </Button>
                </div>
              </div>
            )}
          </form>
        </div>
      </div>

      {/* Success Modal */}
      <Modal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        type="success"
        title="✨ The Portal Awakens!"
        showCloseButton={false}
      >
        <p className="mb-4">Your tale has been inscribed in the ancient tome. The Seven Sages have begun their divination.</p>
        <p className="text-sm text-amber-300">Opening your prophecy scroll...</p>
      </Modal>

      {/* Error Modal */}
      <Modal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        type="error"
        title="Submission Failed"
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
