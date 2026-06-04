export type Article = {
  id: string;
  title: string;
  slug: string;
  excerpt?: string | null;
  cover_url?: string | null;
  content?: string | null;
  category_slug?: string | null;
  series_slug?: string | null;
  series_title?: string | null;
  part_number?: number | null;
  parts_total?: number | null;
  tags?: string[];
  language?: string | null;
  status: 'draft' | 'published';
  published_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type Category = {
  id: string;
  name: string;
  slug: string;
  language?: string | null;
  order?: number;
  is_active?: boolean;
};

