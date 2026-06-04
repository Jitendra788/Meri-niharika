/** श्रेणी लेबल → URL segment (गृहशोभा जैसा: fashion/summer-sunglasses-tips) */
const CATEGORY_LABEL_SLUGS: Record<string, string> = {
  society: 'society',
  sosayati: 'society',
  sosaiti: 'society',
  'सोसायटी': 'society',
  'सोसाइटी': 'society',
  fashion: 'fashion',
  'फैशन': 'fashion',
  film: 'film',
  'फिल्म': 'film',
  beauty: 'beauty',
  'ब्यूटी': 'beauty',
  food: 'food',
  'फूड': 'food',
  health: 'health',
  'हेल्थ': 'health',
  lifestyle: 'lifestyle',
  'लाइफस्टाइल': 'lifestyle',
  kahani: 'kahani',
  'कहानी': 'kahani',
  'love-story': 'love-story',
  'love story': 'love-story',
  'Love Story': 'love-story',
  kavita: 'kavita',
  'कविता': 'kavita',
  lekh: 'lekh',
  'लेख': 'lekh'
};

const RESERVED_PATHS = new Set([
  'admin',
  'article',
  'category',
  'archive',
  'story',
  'editorial',
  'creators',
  'interviews',
  'kitchen',
  'beauty',
  'stars',
  'submit',
  'open-mic',
  'certificate',
  'contact',
  'special'
]);

/** शीर्षक से अंग्रेज़ी slug — summer जैसे शब्द जोड़े जाते हैं */
export function buildArticleSlugFromTitle(title: string): string {
  const t = title.trim();
  if (!t) return '';

  const parts: string[] = [];
  const lower = t.toLowerCase();

  if (/गर्मियों|गर्मी|garmi|summer/i.test(t)) {
    parts.push('summer');
  }

  const english = t.match(/[a-zA-Z]{2,}/g);
  if (english) {
    const skip = new Set(['for', 'the', 'and', 'are', 'you', 'your', 'with', 'that', 'this', 'from']);
    for (const w of english) {
      const s = w.toLowerCase();
      if (!skip.has(s) && !parts.includes(s)) parts.push(s);
    }
  }

  if (/सनग्लास|sunglass/i.test(t) && !parts.includes('sunglasses')) {
    parts.push('sunglasses');
  }
  if (/टिप|ध्यान|बात|सलाह|tips|care|guide/i.test(t) && !parts.includes('tips')) {
    parts.push('tips');
  }
  if (/ऐजुकेशन|education|शिक्षा/i.test(t) && !parts.includes('education')) {
    parts.push('education');
  }
  if (/धर्म|religion/i.test(t) && !parts.includes('religion')) {
    parts.push('religion');
  }

  if (!parts.includes('summer') && /summer/i.test(lower)) {
    parts.unshift('summer');
  }

  let slug = parts.join('-').replace(/-+/g, '-').replace(/^-|-$/g, '');
  if (!slug) {
    slug = t
      .toLowerCase()
      .replace(/[^a-z0-9\u0900-\u097F]+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 80);
  }

  return slug || 'story';
}

export function categorySlugFromLabel(label: string): string {
  const raw = label.trim();
  if (!raw) return '';

  const key = raw.toLowerCase();
  if (CATEGORY_LABEL_SLUGS[raw]) return CATEGORY_LABEL_SLUGS[raw];
  if (CATEGORY_LABEL_SLUGS[key]) return CATEGORY_LABEL_SLUGS[key];

  const ascii = raw
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\x00-\x7F]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  return ascii || '';
}

/** गृहशोभा स्टाइल: fashion/summer-sunglasses-tips */
export function autoSlideLink(categoryLabel: string, title: string): string {
  const cat = categorySlugFromLabel(categoryLabel);
  const articleSlug = buildArticleSlugFromTitle(title);
  if (!articleSlug) return '';

  if (cat) return `${cat}/${articleSlug}`;
  return `/article/${articleSlug}`;
}

export function isReservedCategoryPath(segment: string): boolean {
  return RESERVED_PATHS.has(segment.toLowerCase());
}

/** होम स्लाइड / राउटर के लिए */
export function slideLinkToRouterCommands(link: string): string | string[] {
  const raw = link.trim();
  if (!raw) return '/';
  if (/^https?:\/\//i.test(raw)) return raw;

  const path = raw.startsWith('/') ? raw.slice(1) : raw;
  const segments = path.split('/').filter(Boolean);

  if (segments.length === 2 && !isReservedCategoryPath(segments[0])) {
    return ['/', segments[0], segments[1]];
  }
  if (segments.length === 1) {
    return ['/article', segments[0]];
  }
  return raw.startsWith('/') ? raw : `/${raw}`;
}
