import React, { useState } from 'react'
import styled from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { photosService } from '../services/photos.service'
import { PhotoGrid } from '../components/gallery/PhotoGrid'
import type { Photo } from '../types/gallery.types'
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
  white-space: pre-line;
`

const EmptyState = styled.div`
  text-align: center;
  padding: ${({ theme }) => theme.spacing.xl};
  color: ${({ theme }) => theme.colors.textLight};
  font-size: 14px;
`

export const EntryCreatePage: React.FC = () => {
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [photos, setPhotos] = useState<File[]>([])
  const [photoPreviews, setPhotoPreviews] = useState<string[]>([])
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    if (photos.length === 0) {
      setError('Please add at least one photo')
      return
    }

    try {
      setCreating(true)
      setError(null)

      const entryResponse = await photosService.createEntry({
        title: title.trim(),
        description: description.trim() || undefined,
      })

      const entryId = entryResponse.data.id

      const uploadPromises = photos.map((file) =>
        photosService.uploadPhoto(entryId, file)
      )

      await Promise.all(uploadPromises)

      showToast('Entry created successfully', 'success')
      navigate(`/gallery/${entryResponse.data.slug}`)
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message || 'Failed to create entry'
      setError(errorMessage)
      showToast(errorMessage, 'error')
      console.error(err)
    } finally {
      setCreating(false)
    }
  }

  const handleCancel = () => {
    navigate('/gallery')
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return

    const newFiles = Array.from(files)
    const validFiles: File[] = []
    const errors: string[] = []

    setError(null)

    for (const file of newFiles) {
      try {
        await photosService.validatePhoto(file)
        validFiles.push(file)
      } catch (err: any) {
        const errorMessage = err.response?.data?.error?.message || `${file.name}: Validation failed`
        errors.push(errorMessage)
      }
    }

    if (errors.length > 0) {
      setError(errors.join('\n'))
    }

    if (validFiles.length > 0) {
      setPhotos((prev) => [...prev, ...validFiles])

      validFiles.forEach((file) => {
        const reader = new FileReader()
        reader.onloadend = () => {
          setPhotoPreviews((prev) => [...prev, reader.result as string])
        }
        reader.readAsDataURL(file)
      })
    }

    e.target.value = ''
  }

  const handlePhotoDeleteClick = (photoId: string) => {
    const index = parseInt(photoId.replace('preview-', ''))
    setPhotos((prev) => prev.filter((_, i) => i !== index))
    setPhotoPreviews((prev) => prev.filter((_, i) => i !== index))
  }

  const previewPhotos: Photo[] = photoPreviews.map((url, index) => ({
    id: `preview-${index}`,
    entry: '',
    entry_title: '',
    entry_slug: '',
    file_url: url,
    file_size: photos[index]?.size || 0,
    width: 0,
    height: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }))

  return (
    <Container>
      <Header>
        <Title>Create Entry</Title>
        <ButtonGroup>
          <Button variant="secondary" onClick={handleCancel} disabled={creating}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={creating}>
            {creating ? 'Creating...' : 'Create'}
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
            disabled={creating}
            required
            placeholder="Enter entry title"
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="description">Description (optional)</Label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={creating}
            placeholder="Add a description..."
          />
        </FormGroup>
      </Form>

      <SectionTitle>Photos ({photos.length})</SectionTitle>

      <UploadButton>
        {creating ? 'Uploading...' : '+ Add Photos'}
        <HiddenInput
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileChange}
          disabled={creating}
        />
      </UploadButton>

      <div style={{ marginTop: '16px' }}>
        {previewPhotos.length > 0 ? (
          <PhotoGrid photos={previewPhotos} onPhotoDelete={handlePhotoDeleteClick} />
        ) : (
          <EmptyState>No photos added yet. Click "+ Add Photos" to get started.</EmptyState>
        )}
      </div>


    </Container>
  )
}