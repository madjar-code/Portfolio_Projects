import React from 'react'

interface ChevronRightIconProps {
  size?: number
  color?: string
  className?: string
}

export const ChevronRightIcon: React.FC<ChevronRightIconProps> = ({ 
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
      <polyline points="9 18 15 12 9 6" />
    </svg>
  )
}

