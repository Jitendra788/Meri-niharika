import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, map, of } from 'rxjs';

import { API_BASE_URL } from '../../core/api.tokens';
import { normalizeHeroSlides } from './hero-slides.util';
import { SiteSettings } from './site-settings.types';

export const SITE_DEFAULTS: SiteSettings = {
  hero_tagline_line1: 'हर नारी की कहानी, हर भावना की ज़ुबानी',
  hero_tagline_line2: 'Love Stories, Live Forever',
  hero_slides: [
    {
      image: '/uploads/images/hero-power-of-education.png',
      category_label: 'सोसायटी',
      title: 'धर्म नहीं ऐजुकेशन जरूरी',
      link: '/article/power-of-education'
    }
  ],
  intro_editorial_title: 'संपादक की बात',
  intro_editorial_text:
    'Ishqora में आपका स्वागत है। यह मंच हर नारी की आवाज़, हर रचनाकार की भावना और हर पाठक के लिए समर्पित है।',
  intro_editorial_image: '/hero-banner.png',
  intro_letter_title: 'खत लिख दो...',
  intro_letter_text: 'अपनी बात, सुझाव या रचना हमें लिखकर भेजें। आपका खत हमारे लिए महत्वपूर्ण है।',
  intro_letter_image: '/hero-banner.png',
  bottom_archive_title: 'बोलते पत्थर',
  bottom_archive_text: 'इतिहास की झाँकी — पुरानी यादें और किस्से...',
  bottom_newsletter_title: 'हमसे जुड़ें',
  bottom_newsletter_text: 'नई कहानियाँ और अपडेट ईमेल पर पाएँ।',
  bottom_social_title: 'हमें फॉलो करें',
  bottom_social_text: 'सोशल मीडिया पर जुड़ें।',
  editorial_page_title: 'संपादकीय',
  editorial_page_body: 'यहाँ संपादक का संदेश दिखेगा।'
};

@Injectable({ providedIn: 'root' })
export class SiteSettingsApi {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);

  private withNormalizedSlides(s: SiteSettings): SiteSettings {
    return { ...s, hero_slides: normalizeHeroSlides(s.hero_slides) };
  }

  getPublic() {
    return this.http.get<SiteSettings>(`${this.base}/api/site`).pipe(
      map((s) => this.withNormalizedSlides(s)),
      catchError(() => of({ ...SITE_DEFAULTS }))
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
