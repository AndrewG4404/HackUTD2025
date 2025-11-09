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
                className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-amber-400 bg-clip-text text-transparent hover:from-purple-300 hover:via-pink-300 hover:to-amber-300 transition-all duration-300"
              >
                ✨ VendorLens
              </Link>
          
          <div className="flex items-center space-x-8">
            <Link 
              href="/apply" 
              className={`
                text-sm font-bold transition-colors duration-300
                ${isActive('/apply') 
                  ? 'text-amber-200 border-b-2 border-purple-400 pb-1' 
                  : 'text-white/90 hover:text-amber-200 hover:border-b-2 hover:border-purple-400/50 pb-1'
                }
              `}
            >
              ✨ Vendor Portal
            </Link>
            <Link 
              href="/assess" 
              className={`
                text-sm font-bold transition-colors duration-300
                ${isActive('/assess') 
                  ? 'text-amber-200 border-b-2 border-pink-400 pb-1' 
                  : 'text-white/90 hover:text-amber-200 hover:border-b-2 hover:border-pink-400/50 pb-1'
                }
              `}
            >
              📖 Internal Codex
            </Link>
          </div>
        </div>
      </nav>
    </header>
  )
}

