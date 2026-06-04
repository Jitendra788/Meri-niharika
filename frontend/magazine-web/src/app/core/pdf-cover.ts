/** Cover image URL for archive PDF cards (first-page thumbnail). */
export function pdfCoverImage(
  apiBase: string,
  item: { cover_url?: string | null; pdf_url?: string }
): string {
  if (item.cover_url) {
    const url = item.cover_url;
    if (url.startsWith('http')) return url;
    return `${apiBase}${url}`;
  }
  if (item.pdf_url) {
    return `${apiBase}/api/pdf-thumb?pdf=${encodeURIComponent(item.pdf_url)}`;
  }
  return '';
}
