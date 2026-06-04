import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { catchError, of } from 'rxjs';

import { API_BASE_URL } from '../../core/api.tokens';
import { Article, Category } from './articles.types';

@Injectable({ providedIn: 'root' })
export class ArticlesApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);

  listPublished(limit = 30, skip = 0, categorySlug?: string) {
    let params = new HttpParams().set('limit', limit).set('skip', skip);
    if (categorySlug) params = params.set('category', categorySlug);
    const lang = this.getLang();
    if (lang) params = params.set('lang', lang);
    return this.http.get<Article[]>(`${this.baseUrl}/api/articles`, { params }).pipe(catchError(() => of([])));
  }

  getBySlug(slug: string) {
    const lang = this.getLang();
    const url = `${this.baseUrl}/api/articles/${encodeURIComponent(slug)}`;
    const params = lang ? new HttpParams().set('lang', lang) : undefined;
    return this.http.get<Article>(url, params ? { params } : {});
  }

  listSeriesParts(seriesSlug: string) {
    const url = `${this.baseUrl}/api/articles/series/${encodeURIComponent(seriesSlug)}/parts`;
    return this.http.get<Article[]>(url).pipe(catchError(() => of([])));
  }

  listCategories() {
    const lang = this.getLang();
    const params = lang ? new HttpParams().set('lang', lang) : undefined;
    return this.http.get<Category[]>(`${this.baseUrl}/api/categories`, params ? { params } : {}).pipe(catchError(() => of([])));
  }

  // Frontend uses URL query param `?lang=hi|en` (default: hi).
  private getLang(): string | null {
    try {
      const u = new URL(window.location.href);
      const v = u.searchParams.get('lang');
      if (v === 'hi' || v === 'en') return v;
      return 'hi';
    } catch {
      return 'hi';
    }
  }
}

