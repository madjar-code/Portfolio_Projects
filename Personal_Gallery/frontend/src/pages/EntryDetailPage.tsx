import React, { useEffect, useState } from 'react'
import styled from 'styled-components'
import { PhotoGrid } from '../components/gallery/PhotoGrid'
import { photosService } from '../services/photos.service'
import type { EntryDetail } from '../types/gallery.types'
import { useParams, useNavigate } from 'react-router-dom'
import { ConfirmModal } from '../components/common/ConfirmModal'
import { useAuth } from '../contexts/AuthContext'
import { LogoutIcon } from '../components/icons'


const Container = styled.div`
  max-width: 100%;
  margin: 0 auto;
  padding: ${({ theme }) => theme.spacing.md};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    max-width: 1200px;
    padding: ${({ theme }) => theme.spacing.xl};
  }
`

const TopBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spacing.lg};
`

const BackButton = styled.button`
  background: none;
  color: ${({ theme }) => theme.colors.primary};
  font-size: 14px;
  padding: ${({ theme }) => theme.spacing.sm} 0;
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.xs};
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.7;
  }
`

const LogoutButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  background: transparent;
  color: ${({ theme }) => theme.colors.textLight};
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    background: ${({ theme }) => theme.colors.border};
    color: ${({ theme }) => theme.colors.text};
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: 44px;
    height: 44px;
  }
`

const Header = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`

const Title = styled.h1`
  font-size: 24px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 32px;
  }
`

const Description = styled.p`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textLight};
  line-height: 1.6;
  margin-bottom: ${({ theme }) => theme.spacing.lg};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 16px;
  }
`

const Meta = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.md};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textLight};
`

const LoadingText = styled.p`
  text-align: center;
  color: ${({ theme }) => theme.colors.textLight};
  padding: ${({ theme }) => theme.spacing.xl};
`

const ErrorText = styled.p`
  text-align: center;
  color: ${({ theme }) => theme.colors.danger};
  padding: ${({ theme }) => theme.spacing.xl};
`

export const EntryDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [entry, setEntry] = useState<EntryDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean
    photoId: string | null
  }>({ isOpen: false, photoId: null })

  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchEntry = async () => {
      if (!slug) return

      try {
        setLoading(true)
        const response = await photosService.getEntry(slug)
        setEntry(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to load entry')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchEntry()
  }, [slug])

  const handlePhotoClick = (photo: any) => {
    console.log('Clicked photo:', photo.id)
    // TODO: open photo in modal/lightbox
  }

  const handlePhotoDeleteClick = (photoId: string) => {
    setDeleteModal({ isOpen: true, photoId })
  }

  const handlePhotoDeleteConfirm = async () => {
    if (!deleteModal.photoId || !entry) return

    try {
      setDeleting(true)
      await photosService.deletePhoto(deleteModal.photoId)

      setEntry({
        ...entry,
        photos: entry.photos.filter(p => p.id !== deleteModal.photoId),
        photo_count: entry.photo_count - 1,
      })

      setDeleteModal({ isOpen: false, photoId: null })
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to delete photo'
      alert(errorMessage)
      console.error(err)
    } finally {
      setDeleting(false)
    }
  }

  const handlePhotoDeleteCancel = () => {
    setDeleteModal({ isOpen: false, photoId: null })
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <Container>
        <LoadingText>Loading entry...</LoadingText>
      </Container>
    )
  }

  if (error || !entry) {
    return (
      <Container>
        <ErrorText>{error || "Entry not found"}</ErrorText>
      </Container>
    )
  }

  return (
    <Container>
      <TopBar>
        <BackButton onClick={() => navigate('/gallery')}>
          ← Back to Gallery
        </BackButton>
        <LogoutButton onClick={handleLogout} title="Logout">
          <LogoutIcon size={20} />
        </LogoutButton>
      </TopBar>

      <Header>
        <Title>{entry.title}</Title>
        {entry.description && <Description>{entry.description}</Description>}
        <Meta>
          <span>{entry.photo_count} photos</span>
          <span>•</span>
          <span>{new Date(entry.created_at).toLocaleDateString()}</span>
        </Meta>
      </Header>

      <PhotoGrid
        photos={entry.photos}
        onPhotoClick={handlePhotoClick}
        onPhotoDelete={handlePhotoDeleteClick}
      />

      {deleteModal.isOpen && (
        <ConfirmModal
          title="Delete Photo"
          message="Are you sure you want to delete this photo?"
          onConfirm={handlePhotoDeleteConfirm}
          onCancel={handlePhotoDeleteCancel}
          loading={deleting}
        />
      )}
    </Container>
  )
}