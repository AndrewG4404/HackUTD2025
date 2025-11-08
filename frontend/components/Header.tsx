'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Header() {
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a] border-b border-gray-800">
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-white hover:text-blue-400 transition-colors">
            VendorLens
          </Link>
          
          <div className="flex items-center space-x-8">
            <Link 
              href="/apply" 
              className={`text-sm font-medium transition-colors ${
                isActive('/apply') 
                  ? 'text-blue-400 border-b-2 border-blue-400 pb-1' 
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Vendor Portal
            </Link>
            <Link 
              href="/assess" 
              className={`text-sm font-medium transition-colors ${
                isActive('/assess') 
                  ? 'text-blue-400 border-b-2 border-blue-400 pb-1' 
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Internal Dashboard
            </Link>
          </div>
        </div>
      </nav>
    </header>
  )
}

