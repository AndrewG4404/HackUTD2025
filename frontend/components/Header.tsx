'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Header() {
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

  return (
    <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-sm bg-black/0">
      <nav className="container mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          <Link 
            href="/" 
            className="text-2xl font-bold text-white hover:text-blue-400 transition-colors duration-300"
          >
            VendorLens
          </Link>
          
          <div className="flex items-center space-x-8">
            <Link 
              href="/apply" 
              className={`
                text-sm font-medium transition-colors duration-300
                ${isActive('/apply') 
                  ? 'text-white border-b-2 border-blue-400 pb-1' 
                  : 'text-white/90 hover:text-white hover:border-b-2 hover:border-white/50 pb-1'
                }
              `}
            >
              Vendor Portal
            </Link>
            <Link 
              href="/assess" 
              className={`
                text-sm font-medium transition-colors duration-300
                ${isActive('/assess') 
                  ? 'text-white border-b-2 border-cyan-400 pb-1' 
                  : 'text-white/90 hover:text-white hover:border-b-2 hover:border-white/50 pb-1'
                }
              `}
            >
              Internal Dashboard
            </Link>
          </div>
        </div>
      </nav>
    </header>
  )
}

