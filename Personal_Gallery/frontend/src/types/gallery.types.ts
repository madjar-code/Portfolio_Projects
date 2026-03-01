
export interface Entry {
  id: string
  slug: string
  title: string
  description?: string
  photo_count: number
  first_photo_url?: string
  created_at: string
  updated_at: string
}

export interface EntryDetail extends Entry {
  photos: Photo[]
}

export interface Photo {
  id: string
  entry: string
  entry_title: string
  entry_slug: string
  file_url: string
  file_size: number
  width: number
  height: number
  created_at: string
  updated_at: string
}