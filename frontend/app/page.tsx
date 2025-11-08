/**
 * Landing Page
 * Simple split layout with two cards for workflow selection
 */
import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">VendorLens</h1>
          <p className="text-xl text-gray-600">
            Secure & Intelligent Vendor Onboarding Hub
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Vendor Application Card */}
          <Link href="/apply">
            <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow cursor-pointer">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                Vendor Application
              </h2>
              <p className="text-gray-600 mb-6">
                Submit your company information and documents to apply for onboarding.
              </p>
              <div className="text-blue-600 font-medium">
                Get Started →
              </div>
            </div>
          </Link>
          
          {/* Vendor Assessment Card */}
          <Link href="/assess">
            <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow cursor-pointer">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                Vendor Assessment & Comparison
              </h2>
              <p className="text-gray-600 mb-6">
                Compare multiple vendors for a specific use case and get AI-powered recommendations.
              </p>
              <div className="text-blue-600 font-medium">
                Get Started →
              </div>
            </div>
          </Link>
        </div>
      </div>
    </main>
  )
}

