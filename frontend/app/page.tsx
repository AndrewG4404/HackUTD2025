/**
 * Landing Page - Bloomberg-style Hero with Full-Screen Video
 */
'use client'

import Link from 'next/link'
import { useEffect, useState, useRef } from 'react'

export default function Home() {
  const [isVisible, setIsVisible] = useState(false)
  const [videoLoaded, setVideoLoaded] = useState(false)
  const [videoError, setVideoError] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    setIsVisible(true)
    
    // Force video to load
    if (videoRef.current) {
      videoRef.current.load()
    }
  }, [])

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Full-Screen Video Background */}
      <div className="absolute inset-0 w-full h-full">
        <video
          ref={videoRef}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          className="absolute inset-0 w-full h-full object-cover"
          onLoadedData={() => {
            setVideoLoaded(true)
            setVideoError(false)
          }}
          onError={() => {
            setVideoError(true)
            setVideoLoaded(false)
          }}
          style={{
            opacity: videoLoaded ? 1 : 0,
            transition: 'opacity 1s ease-in-out'
          }}
        >
          <source src="/videos/hero-background.mp4" type="video/mp4" />
          <source src="/videos/hero-background.webm" type="video/webm" />
          Your browser does not support the video tag.
        </video>
        
        {/* Enhanced Video Overlay - Better text readability */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/20 to-black/50" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,0,0,0.4),transparent_60%)]" />
        {/* Additional overlay for content area */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/10 to-transparent" />
        
        {/* Fallback gradient background if video doesn't load */}
        {(!videoLoaded || videoError) && (
          <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-[#0f0f1a] to-[#0a0a0a]">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.1),transparent_50%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(34,211,238,0.08),transparent_50%)]" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className={`relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-20 transition-opacity duration-1000 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
        <div className="container mx-auto max-w-6xl">
          {/* Hero Text - Enhanced Readability */}
          <div className={`text-center mb-16 fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.2s, transform 1s ease-out 0.2s' }}>
            <h1 className="text-6xl md:text-7xl font-bold mb-6 text-white drop-shadow-2xl">
              <span className="bg-gradient-to-r from-white via-white to-blue-200 bg-clip-text text-transparent">
                Vendor
              </span>
              <span className="text-gradient drop-shadow-lg">Lens</span>
            </h1>
            <p className="text-xl md:text-2xl text-white/95 mb-4 max-w-3xl mx-auto font-medium drop-shadow-lg">
              Secure & Intelligent Vendor Onboarding Hub
            </p>
            <p className="text-lg text-white/80 max-w-2xl mx-auto drop-shadow-md">
              AI-powered vendor assessment and comparison platform for enterprise onboarding
            </p>
          </div>

          {/* Dashboard Cards - Enhanced Glassmorphism with Better Readability */}
          <div className={`grid md:grid-cols-2 gap-8 max-w-5xl mx-auto fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.4s, transform 1s ease-out 0.4s' }}>
            {/* Vendor Portal Card */}
            <Link href="/apply">
              <div className="h-full group cursor-pointer">
                <div className="
                  backdrop-blur-2xl bg-black/30 border border-white/20 rounded-xl p-8
                  hover:bg-black/40 hover:border-blue-400/60 hover:shadow-2xl hover:shadow-blue-500/30
                  transition-all duration-300 h-full flex flex-col shadow-xl
                ">
                  <div className="flex flex-col h-full">
                    <div className="mb-6">
                      <div className="w-14 h-14 bg-blue-500/30 backdrop-blur-md rounded-xl flex items-center justify-center mb-5 group-hover:bg-blue-500/40 transition-colors border border-blue-400/30 shadow-lg">
                        <svg className="w-7 h-7 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <h2 className="text-3xl font-bold mb-4 text-white drop-shadow-lg group-hover:text-blue-300 transition-colors">
                        Vendor Portal
                      </h2>
                      <p className="text-white/90 mb-6 leading-relaxed text-base drop-shadow-md">
                        Submit your company information and documents to apply for onboarding with Goldman Sachs.
                      </p>
                    </div>
                    <div className="mt-auto flex items-center text-blue-300 font-semibold group-hover:translate-x-2 transition-transform drop-shadow-md">
                      Get Started
                      <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </Link>

            {/* Internal Dashboard Card */}
            <Link href="/assess">
              <div className="h-full group cursor-pointer">
                <div className="
                  backdrop-blur-2xl bg-black/30 border border-white/20 rounded-xl p-8
                  hover:bg-black/40 hover:border-cyan-400/60 hover:shadow-2xl hover:shadow-cyan-500/30
                  transition-all duration-300 h-full flex flex-col shadow-xl
                ">
                  <div className="flex flex-col h-full">
                    <div className="mb-6">
                      <div className="w-14 h-14 bg-cyan-500/30 backdrop-blur-md rounded-xl flex items-center justify-center mb-5 group-hover:bg-cyan-500/40 transition-colors border border-cyan-400/30 shadow-lg">
                        <svg className="w-7 h-7 text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <h2 className="text-3xl font-bold mb-4 text-white drop-shadow-lg group-hover:text-cyan-300 transition-colors">
                        Internal Dashboard
                      </h2>
                      <p className="text-white/90 mb-6 leading-relaxed text-base drop-shadow-md">
                        Compare multiple vendors for specific use cases and get AI-powered recommendations and comparisons.
                      </p>
                    </div>
                    <div className="mt-auto flex items-center text-cyan-300 font-semibold group-hover:translate-x-2 transition-transform drop-shadow-md">
                      Access Dashboard
                      <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          </div>

          {/* Features Section - Enhanced Readability */}
          <div className={`mt-24 grid md:grid-cols-3 gap-8 max-w-5xl mx-auto fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.6s, transform 1s ease-out 0.6s' }}>
            <div className="text-center backdrop-blur-md bg-black/20 rounded-lg p-6 border border-white/10">
              <div className="text-4xl font-bold text-blue-300 mb-3 drop-shadow-lg">AI-Powered</div>
              <div className="text-white/80 text-sm drop-shadow-md">Nemotron-powered intelligent analysis</div>
            </div>
            <div className="text-center backdrop-blur-md bg-black/20 rounded-lg p-6 border border-white/10">
              <div className="text-4xl font-bold text-cyan-300 mb-3 drop-shadow-lg">Secure</div>
              <div className="text-white/80 text-sm drop-shadow-md">Enterprise-grade security and compliance</div>
            </div>
            <div className="text-center backdrop-blur-md bg-black/20 rounded-lg p-6 border border-white/10">
              <div className="text-4xl font-bold text-blue-300 mb-3 drop-shadow-lg">Efficient</div>
              <div className="text-white/80 text-sm drop-shadow-md">Streamlined onboarding workflows</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

