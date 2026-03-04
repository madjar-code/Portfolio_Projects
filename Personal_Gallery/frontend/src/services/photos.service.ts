import { api } from "./api"
import type { Entry, EntryDetail, Photo } from '../types/gallery.types'
import type { PaginatedResponse } from "../types/api.types";


export const photosService = {
  getEntries: (page: number = 1) => 
    api.get<PaginatedResponse<Entry>>(`/entries/?page=${page}`),

  getEntry: (slug: string) =>
    api.get<EntryDetail>(`/entries/${slug}/`),

  createEntry: (data: { title: string; description?: string }) =>
    api.post<EntryDetail>(`/entries/create/`, data),

  updateEntry: (slug: string, data: { title: string; description?: string }) =>
    api.put<EntryDetail>(`/entries/${slug}/update/`, data),

  getPhotos: () =>
    api.get<Photo[]>(`/photos/`),

  uploadPhoto: (entryId: string, file: File) => {
    const formData = new FormData()
    formData.append('entry', entryId)
    formData.append('file', file)

    return api.post<Photo>(`/photos/create/`,
      formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
  },

  validatePhoto: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<{ valid: boolean; message: string }>('/photos/validate/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  deletePhoto: (photoId: string) =>
    api.delete(`/photos/${photoId}/delete/`),

  deleteEntry: (entrySlug: string) =>
    api.delete(`/entries/${entrySlug}/delete/`),
}