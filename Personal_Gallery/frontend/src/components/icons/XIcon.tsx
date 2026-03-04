import React from 'react'

interface XIconProps {
  size?: number
  color?: string
  className?: string
}

export const XIcon: React.FC<XIconProps> = ({ 
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
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  )
}

