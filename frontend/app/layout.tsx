import type { Metadata } from 'next'
import './globals.css'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import { ToastProvider } from '@/lib/ToastProvider'

export const metadata: Metadata = {
  title: 'VendorLens - Secure & Intelligent Vendor Onboarding',
  description: 'AI-powered vendor onboarding and assessment platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body>
        <ToastProvider>
          <Header />
          <main className="pt-16 min-h-screen">
            {children}
          </main>
          <Footer />
        </ToastProvider>
      </body>
    </html>
  )
}

