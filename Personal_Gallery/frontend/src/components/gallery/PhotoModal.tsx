import React, { useEffect } from "react"
import styled from "styled-components"
import type { Photo } from "../../types/gallery.types"
import { ChevronLeftIcon, ChevronRightIcon, XIcon } from '../icons'

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease-in-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
`

const ModalContainer = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: ${({ theme }) => theme.spacing.md};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.xl};
  }
`

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spacing.md};
  color: white;
`

const Counter = styled.div`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 16px;
  }
`

const CloseButton = styled.button`
  width: 40px;
  height: 40px;
  border-radius: ${({ theme }) => theme.borderRadius.full};
  background: rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  padding: 0;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: 44px;
    height: 44px;
  }
`

const ImageContainer = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
`

const Image = styled.img`
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  animation: zoomIn 0.2s ease-in-out;

  @keyframes zoomIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
`

const NavButton = styled.button<{ direction: 'left' | 'right' }>`
  position: absolute;
  top: 50%;
  ${({ direction }) => (direction === 'left' ? 'left: 16px;' : 'right: 16px;')}
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: ${({ theme }) => theme.borderRadius.full};
  background: rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
  padding: 0;

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.2);
  }

  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: 56px;
    height: 56px;
  }
`

const Footer = styled.div`
  margin-top: ${({ theme }) => theme.spacing.md};
  color: white;
  text-align: center;
`

const PhotoTitle = styled.div`
  font-size: 16px;
  font-weight: 500;
  margin-bottom: ${({ theme }) => theme.spacing.xs};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 18px;
  }
`

const PhotoMeta = styled.div`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  gap: ${({ theme }) => theme.spacing.sm};
  justify-content: center;
  flex-wrap: wrap;
`

interface Props {
  photos: Photo[]
  currentIndex: number
  onClose: () => void
  onNavigate: (index: number) => void
}

export const PhotoModal: React.FC<Props> = ({
  photos,
  currentIndex,
  onNavigate,
  onClose,
}) => {
  const currentPhoto = photos[currentIndex]
  const hasPrev = currentIndex > 0
  const hasNext = currentIndex < photos.length - 1

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Estape') {
        onClose()
      } else if (e.key === 'ArrowLeft' && hasPrev) {
        onNavigate(currentIndex - 1)
      } else if (e.key === 'ArrowRight' && hasNext) {
        onNavigate(currentIndex + 1)
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'unset'
    }
  }, [currentIndex, hasPrev, hasNext, onClose, onNavigate])

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget){
      onClose()
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <Overlay onClick={handleOverlayClick}>
      <ModalContainer>
        <Header>
          <Counter>
            {currentIndex + 1} / {photos.length}
          </Counter>
          <CloseButton onClick={onClose}>
            <XIcon size={20} />
          </CloseButton>
        </Header>

        <ImageContainer>
          {hasPrev && (
            <NavButton
              direction="left"
              onClick={() => onNavigate(currentIndex - 1)}
            >
              <ChevronLeftIcon size={24} />
            </NavButton>
          )}

          <Image
            key={currentPhoto.id}
            src={currentPhoto.file_url}
            alt=""
          />

          {hasNext && (
            <NavButton
              direction="right"
              onClick={() => onNavigate(currentIndex + 1)}
            >
              <ChevronRightIcon size={24} />
            </NavButton>
          )}
        </ImageContainer>

        <Footer>
          <PhotoTitle>{currentPhoto.entry_title}</PhotoTitle>
          <PhotoMeta>
            <span>
              {currentPhoto.width} × {currentPhoto.height}
            </span>
            <span>•</span>
            <span>{formatFileSize(currentPhoto.file_size)}</span>
          </PhotoMeta>
        </Footer>
      </ModalContainer>
    </Overlay>
  )
}
