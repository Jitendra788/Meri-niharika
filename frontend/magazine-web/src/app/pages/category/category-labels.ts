export const CATEGORY_LABELS: Record<string, string> = {
  kahani: 'कहानी',
  'love-story': 'Love Story',
  kavita: 'कविता',
  lekh: 'लेख',
  swasthya: 'स्वास्थ्य',
  sambandh: 'संबंध',
  yatra: 'यात्रा',
  dharm: 'धर्म-आस्था',
  sahitya: 'साहित्य',
  manoranjan: 'मनोरंजन',
  fashion: 'फैशन',
  society: 'सोसायटी',
  sbi: 'SBI'
};

/** Admin dropdown + public category pages — slug must match article category_slug */
export const ADMIN_CATEGORIES: { slug: string; label: string }[] = [
  { slug: 'kahani', label: 'कहानी' },
  { slug: 'love-story', label: 'Love Story' },
  { slug: 'kavita', label: 'कविता' },
  { slug: 'lekh', label: 'लेख' },
  { slug: 'swasthya', label: 'स्वास्थ्य' },
  { slug: 'manoranjan', label: 'मनोरंजन' },
  { slug: 'fashion', label: 'फैशन' },
  { slug: 'dharm', label: 'धर्म-आस्था' },
  { slug: 'sahitya', label: 'साहित्य' },
  { slug: 'sambandh', label: 'संबंध' },
  { slug: 'yatra', label: 'यात्रा' },
  { slug: 'society', label: 'सोसायटी' },
  { slug: 'sbi', label: 'SBI' }
];

export function categoryLabel(slug: string): string {
  return CATEGORY_LABELS[slug] ?? slug;
}
