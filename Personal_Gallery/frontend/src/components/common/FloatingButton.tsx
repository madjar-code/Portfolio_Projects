import React from 'react'
import styled from 'styled-components'

const Button = styled.button`
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: ${({ theme }) => theme.borderRadius.full};
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s;
  z-index: 100;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  &:active {
    transform: scale(0.95);
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: 50px;
    height: 50px;
    bottom: 32px;
    right: 32px;
  }
`

interface Props {
  onClick: () => void
  icon: React.ReactNode
  title?: string
}

export const FloatingButton: React.FC<Props> = ({ onClick, icon, title }) => {
  return (
    <Button onClick={onClick} title={title}>
      {icon}
    </Button>
  )
}