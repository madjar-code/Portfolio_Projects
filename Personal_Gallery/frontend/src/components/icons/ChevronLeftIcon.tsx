import React from 'react'

interface ChevronLeftIconProps {
  size?: number
  color?: string
  className?: string
}

export const ChevronLeftIcon: React.FC<ChevronLeftIconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className 
}) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      width={size}
      height={size}
      className={className}
    >
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}

