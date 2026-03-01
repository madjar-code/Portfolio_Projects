import React from "react"
import styled from "styled-components"
import type { Entry } from "../../types/gallery.types"


const Item = styled.div`
  padding: ${({theme}) => theme.spacing.md} 0;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${({ theme }) => theme.colors.backgroundDark};
    margin: 0 -${({ theme }) => theme.spacing.sm};
    padding-left: ${({ theme }) => theme.spacing.sm};
    padding-right: ${({ theme }) => theme.spacing.sm};
    border-radius: ${({ theme }) => theme.borderRadius.md};
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.lg} 0;

    &:hover {
      margin: 0 -${({ theme }) => theme.spacing.md};
      padding-left: ${({ theme }) => theme.spacing.md};
      padding-right: ${({ theme }) => theme.spacing.md};
    }
  }
`

const Title = styled.h2`
  font-size: 18px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.xs};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 20px;
  }
`

const Meta = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.md};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textLight};
`

const ItemContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    gap: ${({ theme }) => theme.spacing.md};
  }
`

const ItemContent = styled.div`
  flex: 1;
  cursor: pointer;
`

const DeleteButton = styled.button`
  padding: ${({ theme }) => theme.spacing.xs} ${({ theme }) => theme.spacing.sm};
  color: ${({ theme }) => theme.colors.danger};
  font-size: 12px;
  background: ${({ theme }) => theme.colors.buttonSecondary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  transition: opacity 0.2s;
  white-space: nowrap;

  &:hover {
    opacity: 0.7;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
    font-size: 14px;
  }
`

interface Props {
  entry: Entry
  onClick: (slug: string) => void
  onDelete: (slug: string) => void
}

export const EntryListItem: React.FC<Props> = ({ entry, onClick, onDelete }) => {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete(entry.slug)
  }

  return (
    <Item onClick={() => onClick(entry.slug)}>
      <ItemContainer>
        <ItemContent onClick={() => onClick(entry.slug)}>
          <Title>{entry.title}</Title>
          <Meta>
            <span>{entry.photo_count} photos</span>
            <span>•</span>
            <span>{new Date(entry.created_at).toLocaleDateString()}</span>
          </Meta>
        </ItemContent>
        <DeleteButton onClick={handleDelete}>Delete</DeleteButton>
      </ItemContainer>
    </Item>
  )
}