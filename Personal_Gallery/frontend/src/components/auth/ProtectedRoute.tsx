import React from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "../../contexts/AuthContext"
import styled from "styled-components"

const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  color: ${({ theme }) => theme.colors.textLight};
`

interface Props {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<Props> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <LoadingContainer>Loading...</LoadingContainer>
  }

  if (!isAuthenticated) {
    return <Navigate to='/login' replace/>
  }

  return <>{children}</>
}