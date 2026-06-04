import { HeroSlide } from './site-settings.types';
import { SITE_DEFAULTS } from './site-settings.api';

/** API may return legacy string URLs or rich slide objects. */
export function normalizeHeroSlides(raw: unknown): HeroSlide[] {
  if (!Array.isArray(raw) || !raw.length) {
    return SITE_DEFAULTS.hero_slides.map((s) => ({ ...s }));
  }

  const out: HeroSlide[] = [];
  for (const item of raw) {
    if (typeof item === 'string') {
      const image = item.trim();
      if (image) out.push({ image, category_label: '', title: '', link: '' });
      continue;
    }
    if (item && typeof item === 'object') {
      const row = item as Record<string, string>;
      const image = (row['image'] || row['url'] || '').trim();
      if (!image) continue;
      out.push({
        image,
        category_label: (row['category_label'] || '').trim(),
        title: (row['title'] || '').trim(),
        link: (row['link'] || '').trim()
      });
    }
  }

  return out.length ? out : SITE_DEFAULTS.hero_slides.map((s) => ({ ...s }));
}

export function isExternalLink(link: string): boolean {
  return /^https?:\/\//i.test(link.trim());
}
