import React, { useCallback, useEffect, useState } from 'react'
import styled from 'styled-components'
import { photosService } from '../services/photos.service'
import { EntryListItem } from '../components/gallery/EntryListItem'
import { Divider } from '../components/common/Divider'
import { useInfiniteScroll } from '../hooks/useInfiniteScroll'
import { ConfirmModal } from '../components/common/ConfirmModal'
import type { Entry } from '../types/gallery.types'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { LogoutIcon, PlusIcon } from '../components/icons'
import { FloatingButton } from '../components/common/FloatingButton'
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
  align-items: flex-start;
  margin-bottom: ${({ theme }) => theme.spacing.lg};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    margin-bottom: ${({ theme }) => theme.spacing.xl};
  }
`

const HeaderContent = styled.div`
  flex: 1;
`

const Title = styled.h1`
  font-size: 24px;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: ${({ theme }) => theme.spacing.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 32px;
  }
`

const Subtitle = styled.p`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textLight};

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 16px;
  }
`

const LogoutButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: ${({ theme }) => theme.borderRadius.md};
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

const EntriesList = styled.div`
  display: flex;
  flex-direction: column;
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

const LoadMoreTrigger = styled.div`
  height: 20px;
  margin: ${({ theme }) => theme.spacing.md} 0;
`

export const GalleryPage: React.FC = () => {
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  const navigate = useNavigate()
  const { logout } = useAuth()
  const { showToast } = useToast()
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean
    slug: string | null
  }>({ isOpen: false, slug: null})

  const [deleting, setDeleting] = useState(false)

  const fetchEntries = useCallback(async (pageNum: number, append: boolean = false) => {
    try {
      if (append) {
        setLoadingMore(true)
      } else {
        setLoading(true)
      }

      const response = await photosService.getEntries(pageNum)
      const { results, next, count } = response.data

      setEntries(prev => append ? [...prev, ...results] : results)
      setHasMore(next !== null)
      setTotalCount(count)
      setError(null)
    } catch (err) {
      setError('Failed to load entries')
      console.error(err)
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }, [])

  useEffect(() => {
    fetchEntries(1)
  }, [fetchEntries])

  const loadMore = useCallback(() => {
    if (!loadingMore && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      fetchEntries(nextPage, true)
    }
  }, [page, loadingMore, hasMore, fetchEntries])

  const lastElementRef = useInfiniteScroll({
    loading: loadingMore,
    hasMore,
    onLoadMore: loadMore,
  })

  const handleEntryClick = (slug: string) => {
    navigate(`/gallery/${slug}`)
  }

  const handleDeleteClick = (slug: string) => {
    console.log(slug)
    setDeleteModal({ isOpen: true, slug })
  }

  const handleEditClick = (slug: string) => [
    navigate(`/gallery/${slug}/edit`)
  ]

  const handleCreateClick = () => {
    navigate(`/gallery/create`)
  }

  const handleDeleteConfirm = async () => {
    if (!deleteModal.slug) return

    try {
      setDeleting(true)

      await photosService.deleteEntry(deleteModal.slug)

      setEntries(prev => prev.filter(e => e.slug !== deleteModal.slug))
      setTotalCount (prev => prev - 1)

      showToast('Entry deleted successfully', 'success')
      setDeleteModal({ isOpen: false, slug: null })
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to delete entry'
      showToast(errorMessage, 'error')
      console.error(err)
    } finally {
      setDeleting(false)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteModal({ isOpen: false, slug: null })
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <Container>
        <LoadingText>Loading entries...</LoadingText>
      </Container>
    )
  }

  if (error) {
    return (
      <Container>
        <ErrorText>{error}</ErrorText>
      </Container>
    )
  }

  return (
    <Container>
      <Header>
        <HeaderContent>
          <Title>My Gallery</Title>
          <Subtitle>{totalCount} entries</Subtitle>
        </HeaderContent>
        <LogoutButton onClick={handleLogout} title="Logout">
          <LogoutIcon size={20} />
        </LogoutButton>
      </Header>

      <EntriesList>
        {entries.map((entry, index) => (
          <React.Fragment key={entry.id}>
            <EntryListItem
              entry={entry}
              onClick={handleEntryClick}
              onEdit={handleEditClick}
              onDelete={handleDeleteClick}
            />
            {index < entries.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </EntriesList>

      {hasMore && (
        <LoadMoreTrigger ref={lastElementRef}>
          {loadingMore && <LoadingText>Loading more...</LoadingText>}
        </LoadMoreTrigger>
      )}

      {deleteModal.isOpen && (
        <ConfirmModal
          title="Delete Entry"
          message="Are you sure you want to delete this entry? All photos will be deleted as well."
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
          loading={deleting}
        />
      )}
      <FloatingButton onClick={handleCreateClick} icon={<PlusIcon size={24} />} title="Create Entry" />
    </Container>
  )
}