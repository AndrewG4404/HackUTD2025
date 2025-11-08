import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
}

export default function Card({ children, className = '', hover = false }: CardProps) {
  return (
    <div 
      className={`
        bg-[#1a1a1a] border border-gray-800 rounded-lg p-6
        ${hover ? 'hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-300' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  )
}

