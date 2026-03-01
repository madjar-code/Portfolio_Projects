import { useRef, useCallback } from 'react'

interface UseInfiniteScrollProps {
  loading: boolean
  hasMore: boolean
  onLoadMore: () => void
}

export const useInfiniteScroll = ({
  loading,
  hasMore,
  onLoadMore,
}: UseInfiniteScrollProps) => {
  const observer = useRef<IntersectionObserver | null>(null)

  const lastElementRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (loading) return
      if (observer.current) observer.current.disconnect()

      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          onLoadMore()
        }
      })

      if (node) observer.current.observe(node)
    },
    [loading, hasMore, onLoadMore]
  )

  return lastElementRef
}