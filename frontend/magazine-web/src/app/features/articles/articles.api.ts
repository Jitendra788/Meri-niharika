import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { catchError, Observable, of, switchMap } from 'rxjs';

import { API_BASE_URL } from '../../core/api.tokens';
import { StaticDataService } from '../../core/static-data.service';
import { Article, Category } from './articles.types';

@Injectable({ providedIn: 'root' })
export class ArticlesApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);
  private readonly staticData = inject(StaticDataService);

  listPublished(limit = 30, skip = 0, categorySlug?: string) {
    let params = new HttpParams().set('limit', limit).set('skip', skip);
    if (categorySlug) params = params.set('category', categorySlug);
    const lang = this.getLang();
    if (lang) params = params.set('lang', lang);

    return this.http.get<Article[]>(`${this.baseUrl}/api/articles`, { params }).pipe(
      switchMap((list) => (list?.length ? of(list) : this.staticData.listPublished(limit, skip, categorySlug, lang))),
      catchError(() => this.staticData.listPublished(limit, skip, categorySlug, lang))
    );
  }

  getBySlug(slug: string): Observable<Article | null> {
    const lang = this.getLang();
    const url = `${this.baseUrl}/api/articles/${encodeURIComponent(slug)}`;
    const reqParams = lang ? new HttpParams().set('lang', lang) : undefined;
    return this.http.get<Article>(url, reqParams ? { params: reqParams } : {}).pipe(
      catchError(() => this.staticData.getBySlug(slug))
    );
  }

  listSeriesParts(seriesSlug: string) {
    const url = `${this.baseUrl}/api/articles/series/${encodeURIComponent(seriesSlug)}/parts`;
    return this.http.get<Article[]>(url).pipe(
      switchMap((list) => (list?.length ? of(list) : this.staticData.listSeriesParts(seriesSlug))),
      catchError(() => this.staticData.listSeriesParts(seriesSlug))
    );
  }

  listCategories() {
    const lang = this.getLang();
    const params = lang ? new HttpParams().set('lang', lang) : undefined;
    return this.http
      .get<Category[]>(`${this.baseUrl}/api/categories`, params ? { params } : {})
      .pipe(catchError(() => of([])));
  }

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
