import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, map, of } from 'rxjs';

import { API_BASE_URL } from '../../core/api.tokens';
import { StaticDataService } from '../../core/static-data.service';
import { normalizeHeroSlides } from './hero-slides.util';
import { SITE_DEFAULTS } from './site-settings.defaults';
import { SiteSettings } from './site-settings.types';

export { SITE_DEFAULTS } from './site-settings.defaults';

@Injectable({ providedIn: 'root' })
export class SiteSettingsApi {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);
  private readonly staticData = inject(StaticDataService);

  private withNormalizedSlides(s: SiteSettings): SiteSettings {
    return { ...s, hero_slides: normalizeHeroSlides(s.hero_slides) };
  }

  getPublic() {
    return this.http.get<SiteSettings>(`${this.base}/api/site`).pipe(
      map((s) => this.withNormalizedSlides(s)),
      catchError(() =>
        this.staticData.getSiteSettings().pipe(map((s) => this.withNormalizedSlides(s)))
      )
    );
  }

  getAdmin(token: string) {
    return this.http
      .get<SiteSettings>(`${this.base}/api/admin/site`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .pipe(
        map((s) => (s ? this.withNormalizedSlides(s) : null)),
        catchError(() => of(null))
      );
  }

  update(patch: Partial<SiteSettings>, token: string) {
    return this.http
      .patch<SiteSettings>(`${this.base}/api/admin/site`, patch, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .pipe(map((s) => this.withNormalizedSlides(s)));
  }

  uploadImage(file: File, token: string) {
    const fd = new FormData();
    fd.append('file', file);
    return this.http.post<{ url: string }>(`${this.base}/api/admin/upload/image`, fd, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }

  resolveAsset(path: string): string {
    if (!path) return '';
    if (path.startsWith('http')) return path;
    if (path.startsWith('/uploads')) return `${this.base}${path}`;
    return path;
  }
}
