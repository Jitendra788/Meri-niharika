import { HttpClient, HttpEvent } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import { catchError, Observable, of, timeout } from 'rxjs';

import { API_BASE_URL } from '../core/api.tokens';
import { Article } from '../features/articles/articles.types';

export type ArchiveItem = {
  id: string;
  slug: string;
  title: string;
  excerpt?: string;
  content?: string;
  author?: string;
  category_slug?: string;
  language?: string;
  pdf_url: string;
  cover_url?: string;
  page_images?: string[];
  page_texts?: string[];
  paragraphs?: string[];
  page_total?: number;
  page_has_more?: boolean;
  published_at?: string;
  created_at: string;
};

export type ArchivePagesBatch = {
  page_images: string[];
  page_texts?: string[];
  paragraphs?: string[];
  total_pages: number;
  has_more: boolean;
  next_skip: number;
};

export type AdminStats = {
  articles_total: number;
  articles_published: number;
  articles_draft: number;
  archive_total: number;
  users_total: number;
  categories_total: number;
};

export type AdminUser = {
  id: string;
  username: string;
  is_builtin: boolean;
  created_at?: string | null;
};

export type ArticleInput = {
  title: string;
  slug?: string;
  excerpt?: string;
  content?: string;
  cover_url?: string;
  category_slug?: string;
  tags?: string[];
  language?: string;
  status: 'draft' | 'published';
};

@Injectable({ providedIn: 'root' })
export class AdminApi {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);

  private auth(token: string) {
    return { Authorization: `Bearer ${token}` };
  }

  getStats(token: string) {
    const fallback: AdminStats = {
      articles_total: 0,
      articles_published: 0,
      articles_draft: 0,
      archive_total: 0,
      users_total: 1,
      categories_total: 0
    };
    return this.http.get<AdminStats>(`${this.base}/api/admin/stats`, { headers: this.auth(token) }).pipe(
      timeout(8000),
      catchError(() => of(fallback))
    );
  }

  listArticles(token: string, status = 'all', categorySlug = 'all') {
    let params = new HttpParams().set('status', status);
    if (categorySlug && categorySlug !== 'all') {
      params = params.set('category_slug', categorySlug);
    }
    return this.http.get<Article[]>(`${this.base}/api/admin/articles`, {
      headers: this.auth(token),
      params
    });
  }

  createArticle(body: ArticleInput, token: string) {
    return this.http.post<Article>(`${this.base}/api/articles`, body, { headers: this.auth(token) });
  }

  updateArticle(id: string, body: Partial<ArticleInput>, token: string) {
    return this.http.patch<Article>(`${this.base}/api/admin/articles/${id}`, body, { headers: this.auth(token) });
  }

  deleteArticle(id: string, token: string) {
    return this.http.delete<{ status: string }>(`${this.base}/api/admin/articles/${id}`, {
      headers: this.auth(token)
    });
  }

  listUsers(token: string) {
    return this.http.get<AdminUser[]>(`${this.base}/api/admin/users`, { headers: this.auth(token) });
  }

  createUser(body: { username: string; password: string }, token: string) {
    return this.http.post<AdminUser>(`${this.base}/api/admin/users`, body, { headers: this.auth(token) });
  }

  deleteUser(id: string, token: string) {
    return this.http.delete<{ status: string }>(`${this.base}/api/admin/users/${id}`, {
      headers: this.auth(token)
    });
  }

  uploadPdf(file: File, token: string): Observable<HttpEvent<{ pdf_url: string }>> {
    const fd = new FormData();
    fd.append('file', file);
    return this.http.post<{ pdf_url: string }>(`${this.base}/api/admin/upload/pdf`, fd, {
      headers: { Authorization: `Bearer ${token}` },
      reportProgress: true,
      observe: 'events'
    });
  }

  publishArchive(
    body: { title: string; language: string; pdf_url: string; cover_url?: string; category_slug?: string },
    token: string
  ) {
    return this.http.post<ArchiveItem>(`${this.base}/api/admin/archive`, body, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }

  updateArchive(id: string, body: Partial<{ title: string; category_slug: string; language: string; cover_url: string }>, token: string) {
    return this.http.patch<ArchiveItem>(`${this.base}/api/admin/archive/${id}`, body, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }

  deleteArchive(id: string, token: string) {
    return this.http.delete<{ status: string }>(`${this.base}/api/admin/archive/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }

  listArchive(limit = 100, token?: string) {
    const params = new HttpParams().set('limit', String(Math.min(limit, 500)));
    if (token) {
      return this.http.get<ArchiveItem[]>(`${this.base}/api/admin/archive`, {
        headers: this.auth(token),
        params
      }).pipe(timeout(15000), catchError(() => of([])));
    }
    return this.http.get<ArchiveItem[]>(`${this.base}/api/archive`, { params }).pipe(
      timeout(15000),
      catchError(() => of([]))
    );
  }

  getArchiveBySlug(slug: string) {
    return this.http.get<ArchiveItem>(`${this.base}/api/archive/${encodeURIComponent(slug)}`).pipe(
      timeout(30000),
      catchError(() => {
        throw new Error('Archive not found');
      })
    );
  }

  getArchivePages(slug: string, skip: number, limit = 2) {
    const params = new HttpParams().set('skip', String(skip)).set('limit', String(limit));
    return this.http
      .get<ArchivePagesBatch>(`${this.base}/api/archive/${encodeURIComponent(slug)}/pages`, { params })
      .pipe(timeout(30000));
  }
}
