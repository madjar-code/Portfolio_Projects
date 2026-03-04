import React from "react"
import styled from "styled-components"
import type { Entry } from "../../types/gallery.types"
import { DropdownMenu } from "../common/DropdownMenu"
import { LinkIcon, EditIcon, TrashIcon } from "../icons"


const Item = styled.div`
  padding: ${({ theme }) => theme.spacing.md} 0;

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.lg} 0;
  }
`

const Title = styled.h2`
  font-size: 18px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.xs};
  position: relative;
  display: inline-block;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 50%;
    width: 0;
    height: 1px;
    background-color: ${({ theme }) => theme.colors.text};
    transition: all 0.3s ease-in-out;
    transform: translateX(-50%);
  }

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

  &:hover ${Title}::after {
    width: 100%;
  }
`


interface Props {
  entry: Entry
  onClick: (slug: string) => void
  onEdit: (slug: string) => void
  onDelete: (slug: string) => void
}

export const EntryListItem: React.FC<Props> = ({ entry, onClick, onEdit, onDelete }) => {
  const handleCopyLink = () => {
    const url = `${window.location.origin}/gallery/${entry.slug}`
    navigator.clipboard.writeText(url)
    console.log('Link copied:', url)
  }

  const menuOptions = [
    {
      label: 'Copy link',
      icon: <LinkIcon size={16} />,
      onClick: handleCopyLink,
    },
    {
      label: 'Edit',
      icon: <EditIcon size={16} />,
      onClick: () => onEdit(entry.slug),
    },
    {
      label: 'Delete',
      icon: <TrashIcon size={16} />,
      onClick: () => onDelete(entry.slug),
      variant: 'danger' as const,
    },
  ]

  return (
    <Item>
      <ItemContainer>
        <ItemContent>
          <Title onClick={() => onClick(entry.slug)}>{entry.title}</Title>
          <Meta>
            <span>{entry.photo_count} photos</span>
            <span>•</span>
            <span>{new Date(entry.created_at).toLocaleDateString()}</span>
          </Meta>
        </ItemContent>
        <DropdownMenu options={menuOptions}/>
      </ItemContainer>
    </Item>
  )
}