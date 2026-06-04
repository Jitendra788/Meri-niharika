import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, map, Observable, of, shareReplay } from 'rxjs';

import { Article } from '../features/articles/articles.types';
import { SiteSettings } from '../features/site/site-settings.types';
import { SITE_DEFAULTS } from '../features/site/site-settings.defaults';

@Injectable({ providedIn: 'root' })
export class StaticDataService {
  private readonly http = inject(HttpClient);

  private readonly articles$ = this.http.get<Article[]>('/data/articles.json').pipe(
    catchError(() => of([] as Article[])),
    shareReplay(1)
  );

  private readonly site$ = this.http.get<SiteSettings>('/data/site.json').pipe(
    catchError(() => of(null)),
    shareReplay(1)
  );

  hasStaticArticles(): Observable<boolean> {
    return this.articles$.pipe(map((list) => list.length > 0));
  }

  listPublished(limit = 30, skip = 0, categorySlug?: string, lang?: string | null): Observable<Article[]> {
    return this.articles$.pipe(
      map((all) => {
        let rows = all;
        if (categorySlug) rows = rows.filter((a) => a.category_slug === categorySlug);
        if (lang === 'en' || lang === 'hi') {
          rows = rows.filter((a) => !a.language || a.language === lang || a.language === 'hi');
        }
        return rows.slice(skip, skip + limit);
      })
    );
  }

  getBySlug(slug: string): Observable<Article | null> {
    return this.articles$.pipe(map((all) => all.find((a) => a.slug === slug) ?? null));
  }

  listSeriesParts(seriesSlug: string): Observable<Article[]> {
    return this.articles$.pipe(
      map((all) =>
        all
          .filter((a) => (a.series_slug ?? a.slug.replace(/-bhag-\d+$/, '')) === seriesSlug)
          .sort((a, b) => (a.part_number ?? 0) - (b.part_number ?? 0))
      )
    );
  }

  getSiteSettings(): Observable<SiteSettings> {
    return this.site$.pipe(map((s) => (s ? { ...SITE_DEFAULTS, ...s } : SITE_DEFAULTS)));
  }
}
