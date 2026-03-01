import React from 'react'
import styled from 'styled-components'

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: ${({ theme }) => theme.spacing.md};
`

const Modal = styled.div`
  background: ${({ theme }) => theme.colors.background};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  padding: ${({ theme }) => theme.spacing.lg};
  max-width: 100%;
  width: 100%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    max-width: 400px;
    padding: ${({ theme }) => theme.spacing.xl};
    border-radius: ${({ theme }) => theme.borderRadius.lg};
  }
`

const Title = styled.h2`
  font-size: 18px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 20px;
    margin-bottom: ${({ theme }) => theme.spacing.md};
  }
`

const Message = styled.p`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textLight};
  line-height: 1.6;
  margin-bottom: ${({ theme }) => theme.spacing.lg};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    margin-bottom: ${({ theme }) => theme.spacing.xl};
  }
`

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    flex-direction: row;
    gap: ${({ theme }) => theme.spacing.md};
    justify-content: flex-end;
  }
`

const Button = styled.button<{ variant?: 'danger' | 'secondary' }>`
  padding: ${({ theme }) => theme.spacing.md};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s;
  width: 100%;

  ${({ variant, theme }) =>
    variant === 'danger'
      ? `
    background: ${theme.colors.danger};
    color: white;
  `
      : `
    background: ${theme.colors.buttonSecondary};
    color: ${theme.colors.text};
  `}

  &:hover {
    opacity: 0.8;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: auto;
    padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.lg};
  }
`

interface Props {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  onCancel: () => void
  loading?: boolean
}

export const ConfirmModal: React.FC<Props> = ({
  title,
  message,
  confirmText = 'Delete',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  loading = false,
}) => {
  return (
    <Overlay onClick={onCancel}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <Title>{title}</Title>
        <Message>{message}</Message>
        <ButtonGroup>
          <Button variant="secondary" onClick={onCancel} disabled={loading}>
            {cancelText}
          </Button>
          <Button variant="danger" onClick={onConfirm} disabled={loading}>
            {loading ? 'Deleting...' : confirmText}
          </Button>
        </ButtonGroup>
      </Modal>
    </Overlay>
  )
}