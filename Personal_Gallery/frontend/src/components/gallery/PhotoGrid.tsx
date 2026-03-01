import React from "react"
import styled from "styled-components"
import type { Photo } from "../../types/gallery.types"


const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    grid-template-columns: repeat(3, 1fr);
    gap: ${({ theme }) => theme.spacing.md}
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.desktop}) {
    grid-template-columns: repeat(4, 1fr);
  }
`

const PhotoCard = styled.div`
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  background: ${({ theme }) => theme.colors.backgroundDark};
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.03);
  }

  button {
    opacity: 1;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    button {
      opacity: 0;
    }

    &:hover button {
      opacity: 1;
    }
  }
`

const DeleteButton = styled.button`
  position: absolute;
  top: ${({ theme }) => theme.spacing.xs};
  right: ${({ theme }) => theme.spacing.xs};
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: ${({ theme }) => theme.spacing.xs};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: 16px;
  line-height: 1;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  z-index: 10;

  &:hover {
    background: ${({ theme }) => theme.colors.danger};
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: 28px;
    height: 28px;
    font-size: 18px;
  }
`

const Image = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`

interface Props {
  photos: Photo[]
  onPhotoClick?: (photo: Photo) => void
  onPhotoDelete?: (photoId: string) => void
}

export const PhotoGrid: React.FC<Props> = ({ photos, onPhotoClick, onPhotoDelete }) => {
  const handleDelete = (e: React.MouseEvent, photoId: string) => {
    e.stopPropagation()
    onPhotoDelete?.(photoId)
  }

  if (photos.length === 0) {
    return <p>No photos yet</p>
  }

  return (
    <Grid>
      {photos.map((photo) => (
        <PhotoCard key={photo.id} onClick={() => onPhotoClick?.(photo)}>
          <Image src={photo.file_url} alt="" loading="lazy"/>
          {onPhotoDelete && (
            <DeleteButton onClick={(e) => handleDelete(e, photo.id)}>
              ✕
            </DeleteButton>
          )}
        </PhotoCard>
      ))}
    </Grid>
  )
}