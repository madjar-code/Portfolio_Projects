import React, { useState, useEffect } from "react"
import styled, { keyframes } from "styled-components"
import { useParams, useNavigate, Link as RouterLink } from "react-router-dom"
import { authService } from "../services/auth.service"

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${({ theme }) => theme.spacing.md};
  background: ${({ theme }) => theme.colors.background};
`

const Card = styled.div`
  width: 100%;
  max-width: 400px;
  background: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  padding: ${({ theme }) => theme.spacing.xl};
  text-align: center;

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.xl} ${({ theme }) => theme.spacing.xxl};
  }
`

const spin = keyframes`
  to { transform: rotate(360deg); }
`

const Spinner = styled.div`
  width: 48px;
  height: 48px;
  border: 4px solid ${({ theme }) => theme.colors.border};
  border-top-color: ${({ theme }) => theme.colors.primary};
  border-radius: 50%;
  animation: ${spin} 0.8s linear infinite;
  margin: 0 auto ${({ theme }) => theme.spacing.lg};
`

const Icon = styled.div<{ variant: 'success' | 'error' }>`
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin: 0 auto ${({ theme }) => theme.spacing.lg};
  
  ${({ variant, theme }) =>
    variant === 'success'
      ? `
    background: rgba(52, 168, 83, 0.1);
    color: ${theme.colors.secondary};
  `
      : `
    background: rgba(234, 67, 53, 0.1);
    color: ${theme.colors.danger};
  `}
`

const Title = styled.h1`
  font-size: 24px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 28px;
  }
`

const Message = styled.p`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textLight};
  line-height: 1.6;
  margin-bottom: ${({ theme }) => theme.spacing.xl};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 16px;
  }
`

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    flex-direction: row;
    justify-content: center;
    gap: ${({ theme }) => theme.spacing.md};
  }
`

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.lg};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s;
  width: 100%;

  ${({ variant, theme }) =>
    variant === 'secondary'
      ? `
    background: ${theme.colors.backgroundDark};
    color: ${theme.colors.text};
  `
      : `
    background: ${theme.colors.primary};
    color: white;
  `}

  &:hover:not(:disabled) {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: auto;
    padding: ${({ theme }) => theme.spacing.md} ${({ theme }) => theme.spacing.xl};
    font-size: 16px;
  }
`

const Link = styled(RouterLink)`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.lg};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s;
  width: 100%;
  text-align: center;
  text-decoration: none;
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  display: inline-block;

  &:hover {
    opacity: 0.9;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: auto;
    padding: ${({ theme }) => theme.spacing.md} ${({ theme }) => theme.spacing.xl};
    font-size: 16px;
  }
`

export const ActivationPage: React.FC = () => {
  const { uid, token } = useParams<{ uid: string; token: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const activate = async () => {
      if (!uid || !token) {
        setError('Invalid activation link')
        setLoading(false)
        return
      }

      try {
        await authService.activateAccount({ uid, token })
        setSuccess(true)
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.error?.message ||
          err.response?.data?.detail ||
          'Activation failed. The link may be invalid or expired.'
        setError(errorMessage)
        console.error('Activation error:', err)
      } finally {
        setLoading(false)
      }
    }

    activate()
  }, [uid, token])

  const handleResendActivation = async () => {
    navigate('/login')
  }

  if (loading) {
    return (
      <Container>
        <Card>
          <Spinner />
          <Title>Activating Account</Title>
          <Message>Please wait while we activate your account...</Message>
        </Card>
      </Container>
    )
  }

  if (success) {
    return (
      <Container>
        <Card>
          <Icon variant="success">✓</Icon>
          <Title>Account Activated!</Title>
          <Message>
            Your account has been successfully activated. You can now sign in to your account.
          </Message>
          <Link to="/login">Go to Login</Link>
        </Card>
      </Container>
    )
  }

  return (
    <Container>
      <Card>
        <Icon variant="error">✗</Icon>
        <Title>Activation Failed</Title>
        <Message>{error}</Message>
        <ButtonGroup>
          <Button variant="secondary" onClick={handleResendActivation}>
            Go to Login
          </Button>
        </ButtonGroup>
      </Card>
    </Container>
  )
}