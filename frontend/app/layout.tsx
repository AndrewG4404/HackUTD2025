import type { Metadata } from 'next'
import './globals.css'

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
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

