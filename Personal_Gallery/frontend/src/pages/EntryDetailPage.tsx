import React, { useEffect, useState } from 'react'
import styled from 'styled-components'
import { PhotoGrid } from '../components/gallery/PhotoGrid'
import { photosService } from '../services/photos.service'
import type { EntryDetail } from '../types/gallery.types'
import { useParams, useNavigate } from 'react-router-dom'
import { ConfirmModal } from '../components/common/ConfirmModal'
import { PhotoModal } from '../components/gallery/PhotoModal'
import { EditIcon, TrashIcon } from '../components/icons'


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

const ActionsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
`

const ActionButton = styled.button<{ variant?: 'danger' }>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${({ theme }) => theme.spacing.xs};
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  
  ${({ variant, theme }) =>
    variant === 'danger'
      ? `
    background: transparent;
    color: ${theme.colors.danger};
    border: 1px solid ${theme.colors.danger};
    
    &:hover {
      background: ${theme.colors.danger};
      color: white;
    }
  `
      : `
    background: ${theme.colors.backgroundDark};
    color: ${theme.colors.text};
    
    &:hover {
      background: ${theme.colors.border};
    }
  `}

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  }
`

const ButtonText = styled.span`
  display: none;

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    display: inline;
  }
`

const ButtonIcon = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
`

const Header = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`

const Title = styled.h1`
  font-size: 20px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 28px;
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
  const [entry, setEntry] = useState<EntryDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [entryDeleteModal, setEntryDeleteModal] = useState(false)
  const [deletingEntry, setDeletingEntry] = useState(false)
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean
    photoId: string | null
  }>({ isOpen: false, photoId: null })
  const [modalState, setModalState] = useState<{
    isOpen: boolean
    currentIndex: number
  }>({ isOpen: false, currentIndex: 0 })

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
    const index = entry!.photos.findIndex((p) => p.id === photo.id)
    setModalState({ isOpen: true, currentIndex: index })
  }

  const handleModalClose = () => {
    setModalState({ isOpen: false, currentIndex: 0 })
  }

  const handleModalNavigate = (index: number) => {
    setModalState({ isOpen: true, currentIndex: index })
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

  const handleEdit = () => {
    navigate(`/gallery/${slug}/edit`)
  }

  const handleDeleteClick = () => {
    setEntryDeleteModal(true)
  }

  const handleEntryDeleteConfirm = async () => {
    if (!slug) return

    try {
      setDeletingEntry(true)
      await photosService.deleteEntry(slug)
      navigate('/gallery')
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to delete entry'
      alert(errorMessage)
      console.error(err)
    } finally {
      setDeletingEntry(false)
    }
  }

  const handleEntryDeleteCancel = () => {
    setEntryDeleteModal(false)
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
        <ActionsContainer>
          <ActionButton onClick={handleEdit} title="Edit entry">
            <ButtonIcon>
              <EditIcon size={16}/>
            </ButtonIcon>
            <ButtonText>Edit</ButtonText>
          </ActionButton>
          <ActionButton variant="danger" onClick={handleDeleteClick} title="Delete entry">
            <ButtonIcon>
              <TrashIcon size={16}/>
            </ButtonIcon>
            <ButtonText>Delete</ButtonText>
          </ActionButton>
        </ActionsContainer>
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
      {modalState.isOpen && (
        <PhotoModal
          photos={entry.photos}
          currentIndex={modalState.currentIndex}
          onClose={handleModalClose}
          onNavigate={handleModalNavigate}
        />
      )}
      {entryDeleteModal && (
        <ConfirmModal
          title="Delete Entry"
          message="Are you sure you want to delete this entry? All photos will be deleted as well."
          onConfirm={handleEntryDeleteConfirm}
          onCancel={handleEntryDeleteCancel}
          loading={deletingEntry}
        />
      )}
    </Container>
  )
}