import React, { useEffect, useState } from 'react'
import styled from 'styled-components'
import { useParams, useNavigate } from 'react-router-dom'
import { photosService } from '../services/photos.service'
import { PhotoGrid } from '../components/gallery/PhotoGrid'
import { ConfirmModal } from '../components/common/ConfirmModal'
import type { EntryDetail } from '../types/gallery.types'
import { useToast } from '../contexts/ToastContext'


const Container = styled.div`
  max-width: 100%;
  margin: 0 auto;
  padding: ${({ theme }) => theme.spacing.md};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    max-width: 800px;
    padding: ${({ theme }) => theme.spacing.xl};
  }
`

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`

const Title = styled.h1`
  font-size: 20px;
  color: ${({ theme }) => theme.colors.text};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 28px;
  }
`

const ButtonGroup = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.sm};
`

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s;

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
`

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.lg};
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.xs};
`

const Label = styled.label`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
  font-weight: 500;
`

const Input = styled.input`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.md};
    font-size: 16px;
  }
`

const Textarea = styled.textarea`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
  transition: border-color 0.2s;
  min-height: 100px;
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.md};
    font-size: 16px;
  }
`

const SectionTitle = styled.h2`
  font-size: 18px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.md};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 20px;
  }
`

const UploadButton = styled.label`
  display: inline-block;
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
  text-align: center;

  &:hover {
    opacity: 0.9;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 16px;
  }
`

const HiddenInput = styled.input`
  display: none;
`

const ErrorMessage = styled.div`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  background: rgba(234, 67, 53, 0.1);
  border: 1px solid ${({ theme }) => theme.colors.danger};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  color: ${({ theme }) => theme.colors.danger};
  font-size: 14px;
  margin-bottom: ${({ theme }) => theme.spacing.md};
`

const LoadingText = styled.p`
  text-align: center;
  color: ${({ theme }) => theme.colors.textLight};
  padding: ${({ theme }) => theme.spacing.xl};
`

export const EntryEditPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [entry, setEntry] = useState<EntryDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean
    photoId: string | null
  }>({ isOpen: false, photoId: null })
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const fetchEntry = async () => {
      if (!slug) return

      try {
        const response = await photosService.getEntry(slug)
        setEntry(response.data)
        setTitle(response.data.title)
        setDescription(response.data.description || '')
      } catch (err) {
        setError('Failed to load entry')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchEntry()
  }, [slug])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!slug) return

    try {
      setSaving(true)
      setError(null)
      const response = await photosService.updateEntry(slug, { title, description })
      setEntry(response.data)

      showToast('Entry updated successfully', 'success')
      navigate(`/gallery/${slug}`)
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to update entry'
      setError(errorMessage)
      showToast(errorMessage, 'error')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    navigate(`/gallery/${slug}`)
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || !entry) return

    try {
      setUploading(true)
      setError(null)

      const uploadPromises = Array.from(files).map((file) =>
        photosService.uploadPhoto(entry.id, file)
      )
    
      const responses = await Promise.all(uploadPromises)
      const newPhotos = responses.map((r) => r.data)

      setEntry({
        ...entry,
        photos: [...entry.photos, ...newPhotos],
        photo_count: entry.photo_count + newPhotos.length,
      })

      e.target.value = ''
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to upload photos'
      setError(errorMessage)
      console.error(err)
    } finally {
      setUploading(false)
    }
  }

  const handlePhotoDeleteClick = (photoId: string) => {
    setDeleteModal({ isOpen: true, photoId })
  }

  const handlePhotoDeleteConfirm = async () => {
    if (!deleteModal.photoId || !entry) return

    try {
      setDeleting(true)
      await photosService.deletePhoto(deleteModal.photoId)

      // Update entry
      setEntry({
        ...entry,
        photos: entry.photos.filter((p) => p.id !== deleteModal.photoId),
        photo_count: entry.photo_count - 1,
      })

      setDeleteModal({ isOpen: false, photoId: null })
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message || 'Failed to delete photo'
      alert(errorMessage)
      console.error(err)
    } finally {
      setDeleting(false)
    }
  }

  const handlePhotoDeleteCancel = () => {
    setDeleteModal({ isOpen: false, photoId: null })
  }

  if (loading) {
    return (
      <Container>
        <LoadingText>Loading...</LoadingText>
      </Container>
    )
  }

  if (!entry) {
    return (
      <Container>
        <ErrorMessage>Entry not found</ErrorMessage>
      </Container>
    )
  }

  return (
    <Container>
      <Header>
        <Title>Edit Entry</Title>
        <ButtonGroup>
          <Button variant="secondary" onClick={handleCancel} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </ButtonGroup>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="title">Title</Label>
          <Input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={saving}
            required
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="description">Description (optional)</Label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={saving}
            placeholder="Add a description..."
          />
        </FormGroup>
      </Form>

      <SectionTitle>Photos ({entry.photo_count})</SectionTitle>

      <UploadButton>
        {uploading ? 'Uploading...' : '+ Add Photos'}
        <HiddenInput
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileChange}
          disabled={uploading}
        />
      </UploadButton>

      <div style={{ marginTop: '16px' }}>
        <PhotoGrid
          photos={entry.photos}
          onPhotoDelete={handlePhotoDeleteClick}
        />
      </div>

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