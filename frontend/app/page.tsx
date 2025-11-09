/**
 * Landing Page - Bloomberg-style Hero with Full-Screen Video
 */
'use client'

import Link from 'next/link'
import { useEffect, useState, useRef } from 'react'
import { AnimatedCounter } from '@/components/AnimatedCounter'

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
          {/* Hero Text - Bold Statement Style */}
          <div className={`mb-12 fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.2s, transform 1s ease-out 0.2s' }}>
            <p className="text-sm md:text-base uppercase tracking-widest text-gray-400 mb-6 font-semibold">GOLDMAN SACHS • VENDOR ONBOARDING</p>
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-8 leading-tight">
              <span className="text-white drop-shadow-2xl">AI agents evaluate vendors </span>
              <span className="text-blue-400 drop-shadow-2xl">in 5 minutes</span>
            </h1>
            <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl font-light leading-relaxed drop-shadow-lg">
              Watch 7 specialized AI agents research security, compliance, and integrations in real-time—turning weeks of manual work into transparent, intelligent recommendations.
            </p>
            
            {/* Powered by Badge */}
            <div className="flex items-center gap-3 mb-10">
              <div className="px-4 py-2 bg-white/10 backdrop-blur-md border border-white/20 rounded-full flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-white/90 text-sm font-medium">Powered by NVIDIA Nemotron</span>
              </div>
            </div>

            <div className="flex gap-4 flex-wrap">
              <Link href="/apply">
                <button className="px-8 py-4 bg-white text-black font-bold text-lg rounded-lg hover:bg-gray-200 transition-all hover-scale shadow-xl">
                  VENDOR PORTAL
                </button>
              </Link>
              <Link href="/assess">
                <button className="px-8 py-4 border-2 border-white text-white font-bold text-lg rounded-lg hover:bg-white hover:text-black transition-all hover-scale shadow-xl">
                  INTERNAL DASHBOARD
                </button>
              </Link>
            </div>
          </div>


          {/* Features Stats - Minimal Style */}
          <div className={`mt-20 grid grid-cols-3 gap-12 max-w-4xl mx-auto fade-in ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`} style={{ transition: 'opacity 1s ease-out 0.6s, transform 1s ease-out 0.6s' }}>
            <div className="text-center">
              <div className="text-5xl md:text-6xl font-bold text-white mb-2 drop-shadow-lg">
                {isVisible && <AnimatedCounter end={7} />}
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wide">AI Agents</div>
            </div>
            <div className="text-center">
              <div className="text-5xl md:text-6xl font-bold text-white mb-2 drop-shadow-lg">
                {isVisible && <AnimatedCounter end={5} />}
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wide">Minutes</div>
            </div>
            <div className="text-center">
              <div className="text-5xl md:text-6xl font-bold text-white mb-2 drop-shadow-lg">
                {isVisible && <AnimatedCounter end={100} suffix="%" />}
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wide">Transparent</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

