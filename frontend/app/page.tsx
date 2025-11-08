/**
 * Landing Page - Bloomberg-style Hero with Fade Effect
 */
'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

export default function Home() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Hero Background with Gradient Fade */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-[#0f0f1a] to-[#0a0a0a]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(34,211,238,0.08),transparent_50%)]" />
      </div>

      {/* Content */}
      <div className={`relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-20 transition-opacity duration-1000 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
        <div className="container mx-auto max-w-6xl">
          {/* Hero Text */}
          <div className={`text-center mb-16 fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.2s, transform 1s ease-out 0.2s' }}>
            <h1 className="text-6xl md:text-7xl font-bold mb-6 text-white">
              Vendor<span className="text-gradient">Lens</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 mb-4 max-w-3xl mx-auto">
              Secure & Intelligent Vendor Onboarding Hub
            </p>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              AI-powered vendor assessment and comparison platform for enterprise onboarding
            </p>
          </div>

          {/* Dashboard Cards */}
          <div className={`grid md:grid-cols-2 gap-8 max-w-5xl mx-auto fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.4s, transform 1s ease-out 0.4s' }}>
            {/* Vendor Portal Card */}
            <Link href="/apply">
              <Card hover className="h-full group cursor-pointer">
                <div className="flex flex-col h-full">
                  <div className="mb-4">
                    <div className="w-12 h-12 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-600/30 transition-colors">
                      <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <h2 className="text-2xl font-semibold mb-3 text-white group-hover:text-blue-400 transition-colors">
                      Vendor Portal
                    </h2>
                    <p className="text-gray-400 mb-6 leading-relaxed">
                      Submit your company information and documents to apply for onboarding with Goldman Sachs.
                    </p>
                  </div>
                  <div className="mt-auto flex items-center text-blue-400 font-medium group-hover:translate-x-2 transition-transform">
                    Get Started
                    <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                </div>
              </Card>
            </Link>

            {/* Internal Dashboard Card */}
            <Link href="/assess">
              <Card hover className="h-full group cursor-pointer">
                <div className="flex flex-col h-full">
                  <div className="mb-4">
                    <div className="w-12 h-12 bg-cyan-600/20 rounded-lg flex items-center justify-center mb-4 group-hover:bg-cyan-600/30 transition-colors">
                      <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <h2 className="text-2xl font-semibold mb-3 text-white group-hover:text-cyan-400 transition-colors">
                      Internal Dashboard
                    </h2>
                    <p className="text-gray-400 mb-6 leading-relaxed">
                      Compare multiple vendors for specific use cases and get AI-powered recommendations and comparisons.
                    </p>
                  </div>
                  <div className="mt-auto flex items-center text-cyan-400 font-medium group-hover:translate-x-2 transition-transform">
                    Access Dashboard
                    <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                </div>
              </Card>
            </Link>
          </div>

          {/* Features Section */}
          <div className={`mt-20 grid md:grid-cols-3 gap-6 max-w-5xl mx-auto fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.6s, transform 1s ease-out 0.6s' }}>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-400 mb-2">AI-Powered</div>
              <div className="text-gray-500 text-sm">Nemotron-powered intelligent analysis</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-cyan-400 mb-2">Secure</div>
              <div className="text-gray-500 text-sm">Enterprise-grade security and compliance</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-400 mb-2">Efficient</div>
              <div className="text-gray-500 text-sm">Streamlined onboarding workflows</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

