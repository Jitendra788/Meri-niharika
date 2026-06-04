import { UrlMatchResult, UrlSegment } from '@angular/router';

import { isReservedCategoryPath } from './features/site/slide-link.util';

/** fashion/summer-sunglasses-tips — गृहशोभा जैसे दो-स्तरीय लेख URL */
export function categoryArticleMatcher(segments: UrlSegment[]): UrlMatchResult | null {
  if (segments.length !== 2) return null;
  if (isReservedCategoryPath(segments[0].path)) return null;

  return {
    consumed: segments,
    posParams: {
      category: segments[0],
      slug: segments[1]
    }
  };
}
