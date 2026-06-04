/** Split Hindi/Devanagari text without breaking combining marks (ं, ि, etc.). */

const COMBINING_RANGES: ReadonlyArray<[number, number]> = [
  [0x0900, 0x0903],
  [0x093a, 0x094f],
  [0x0951, 0x0957],
  [0x0962, 0x0963],
  [0x1cd0, 0x1cfe]
];

function isCombiningCodePoint(cp: number): boolean {
  if (cp === 0x094d) return true;
  return COMBINING_RANGES.some(([start, end]) => cp >= start && cp <= end);
}

export function splitFirstGrapheme(text: string): { first: string; rest: string } {
  const t = text.trim();
  if (!t) return { first: '', rest: '' };

  if (typeof Intl !== 'undefined' && 'Segmenter' in Intl) {
    try {
      const seg = new Intl.Segmenter('hi', { granularity: 'grapheme' });
      const segments = [...seg.segment(t)];
      if (segments.length > 0) {
        const first = segments[0].segment;
        const rest = t.slice(segments[0].index + first.length);
        return { first, rest };
      }
    } catch {
      /* fallback below */
    }
  }

  const chars = [...t];
  let end = 1;
  while (end < chars.length) {
    const cp = chars[end].codePointAt(0);
    if (cp === undefined || !isCombiningCodePoint(cp)) break;
    end++;
  }

  return {
    first: chars.slice(0, end).join(''),
    rest: chars.slice(end).join('')
  };
}
