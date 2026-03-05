// src/contexts/ToastContext.tsx
import React, { createContext, useContext, useState, useCallback } from 'react'
import styled from 'styled-components'

type ToastType = 'success' | 'error' | 'info' | 'warning'

interface Toast {
  id: string
  message: string
  type: ToastType
  isRemoving?: boolean
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

const ToastContainer = styled.div`
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.sm};
  max-width: 400px;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    left: 24px;
    right: 24px;
    max-width: none;
  }
`

const ToastItem = styled.div<{ type: ToastType; isRemoving?: boolean }>`
  padding: ${({ theme }) => theme.spacing.md};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  box-shadow: ${({ theme }) => theme.shadows.lg};
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  font-size: 14px;
  background: white;
  border: 2px solid;
  animation: ${({ isRemoving }) => (isRemoving ? 'slideOut' : 'slideIn')} 0.3s ease-out;

  ${({ type, theme }) => {
    switch (type) {
      case 'success':
        return `
          border-color: ${theme.colors.secondary};
          color: ${theme.colors.secondary};
        `
      case 'error':
        return `
          border-color: ${theme.colors.danger};
          color: ${theme.colors.danger};
        `
      case 'warning':
        return `
          border-color: ${theme.colors.warning};
          color: ${theme.colors.text};
        `
      case 'info':
      default:
        return `
          border-color: ${theme.colors.primary};
          color: ${theme.colors.primary};
        `
    }
  }}

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`

const ToastIcon = styled.span`
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
`

const ToastMessage = styled.span`
  flex: 1;
`

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substring(7)
    const newToast: Toast = { id, message, type, isRemoving: false }

    setToasts((prev) => [...prev, newToast])

    // Start removal animation after 2.7 seconds
    setTimeout(() => {
      setToasts((prev) =>
        prev.map((toast) =>
          toast.id === id ? { ...toast, isRemoving: true } : toast
        )
      )
    }, 2700)

    // Actually remove after animation completes (3 seconds total)
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id))
    }, 3000)
  }, [])

  const getIcon = (type: ToastType) => {
    switch (type) {
      case 'success':
        return '✓'
      case 'error':
        return '✕'
      case 'warning':
        return '⚠'
      case 'info':
      default:
        return 'ℹ'
    }
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <ToastContainer>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} type={toast.type} isRemoving={toast.isRemoving}>
            <ToastIcon>{getIcon(toast.type)}</ToastIcon>
            <ToastMessage>{toast.message}</ToastMessage>
          </ToastItem>
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  )
}