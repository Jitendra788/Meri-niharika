import { DatePipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';

import { AdminApi, ArchiveItem } from '../../admin/admin.api';
import { slugFromPdfUrl } from '../../admin/admin.upload';
import { API_BASE_URL } from '../../core/api.tokens';
import { pdfCoverImage } from '../../core/pdf-cover';
import { ArticlesApi } from '../../features/articles/articles.api';
import { Article } from '../../features/articles/articles.types';
import { PageShellComponent } from '../_ui/page-shell';
import { categoryLabel } from './category-labels';

export type CategoryCard = {
  kind: 'article' | 'pdf';
  title: string;
  slug: string;
  series_slug?: string;
  excerpt?: string;
  cover_url?: string;
  published_at?: string;
  author?: string;
  tag?: string;
  parts?: string;
  readers?: string;
  link: string;
  pdf_url?: string;
};

const LOVE_STORY_INTRO =
  'हमारे पास प्रेम कहानियों का विशाल संग्रह है — स्कूल-कॉलेज की यादें, अरेंज मैरिज से प्यार, दूरी और मिलन, और दिल को छू जाने वाले रोमांटिक किस्से। ' +
  'ये सभी कहानियाँ Ishqora के लिए मूल रूप से लिखी गई हैं; पढ़ते समय आप अपनी यादों में भी खो सकते हैं।';

@Component({
  standalone: true,
  selector: 'app-category-page',
  imports: [NgFor, NgIf, DatePipe, RouterLink, PageShellComponent],
  templateUrl: './category.page.html',
  styleUrl: './category.page.scss'
})
export class CategoryPage implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly articlesApi = inject(ArticlesApi);
  private readonly adminApi = inject(AdminApi);
  private readonly cdr = inject(ChangeDetectorRef);
  protected readonly apiBase = inject(API_BASE_URL);

  loading = true;
  categorySlug = '';
  categoryTitle = '';
  categoryIntro = '';
  items: CategoryCard[] = [];
  readonly itemsPerPage = 12;
  listPage = 1;

  ngOnInit() {
    this.route.paramMap.subscribe((p) => {
      this.categorySlug = p.get('slug') ?? '';
      this.categoryTitle = categoryLabel(this.categorySlug);
      this.categoryIntro =
        this.categorySlug === 'love-story'
          ? LOVE_STORY_INTRO
          : this.categorySlug === 'lekh'
            ? 'ताज़ा हिंदी समाचार — रोज़ अपडेट। संक्षेप यहाँ, पूरा पढ़ने के लिए मूल स्रोत पर जाएँ।'
            : '';
      this.listPage = 1;
      this.load();
    });
  }

  private load() {
    this.loading = true;
    this.items = [];
    this.cdr.markForCheck();

    const slug = this.categorySlug;
    const pdfCategories = ['kahani', 'love-story', 'kavita', 'lekh', 'swasthya', 'manoranjan', 'dharm', 'sahitya', 'sbi'];
    const includePdf = pdfCategories.includes(slug);

    forkJoin({
      articles: this.articlesApi.listPublished(slug === 'love-story' ? 100 : slug === 'lekh' ? 120 : 50, 0, slug),
      archive: includePdf ? this.adminApi.listArchive(30) : of([] as ArchiveItem[])
    }).subscribe({
      next: ({ articles, archive }) => {
        const listed = articles.filter((a) => !a.part_number || a.part_number <= 1);
        const cards: CategoryCard[] = listed.map((a) => this.articleCard(a));
        if (includePdf) {
          const seen = new Set<string>();
          for (const pdf of archive as ArchiveItem[]) {
            const cat = pdf.category_slug || 'kahani';
            if (cat !== slug) continue;
            const key = pdf.pdf_url || pdf.id;
            if (seen.has(key)) continue;
            seen.add(key);
            cards.push(this.pdfCard(pdf, slug));
          }
        }
        cards.sort((a, b) => {
          const da = a.published_at ? Date.parse(a.published_at) : 0;
          const db = b.published_at ? Date.parse(b.published_at) : 0;
          return db - da;
        });
        this.items = cards;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  private isNewsArticle(a: Article): boolean {
    return a.category_slug === 'lekh' || (a.tags?.includes('समाचार') ?? false);
  }

  private isMoralKahani(a: Article): boolean {
    return a.tags?.includes('नैतिक कहानी') ?? false;
  }

  private articleCard(a: Article): CategoryCard {
    const author = a.tags?.[0];
    const partsTag =
      a.parts_total && a.parts_total > 1
        ? `${a.parts_total} भाग`
        : a.tags?.find((t) => /भाग/.test(t));
    const defaultTag =
      a.category_slug === 'love-story' ? 'Love Story' : this.isNewsArticle(a) ? 'समाचार' : 'कहानी';
    const readers = this.fakeReaders(a.slug);
    const seriesKey = a.series_slug ?? a.slug.replace(/-bhag-\d+$/, '');
    let cover = a.cover_url ?? undefined;
    if (!cover && a.category_slug === 'love-story') {
      cover = this.defaultLoveCover(seriesKey);
    }
    if (!cover && this.isMoralKahani(a)) {
      cover = this.defaultKahaniCover(a.slug);
    }
    if (!cover && this.isNewsArticle(a)) {
      cover = '/uploads/images/news-card.svg';
    }
    if (!cover && a.category_slug === 'kahani') {
      cover = this.defaultKahaniCover(a.slug);
    }
    return {
      kind: 'article',
      title: a.title.replace(/\s*—\s*भाग\s*\d+\s*$/, '').trim() || a.title,
      slug: a.slug,
      series_slug: seriesKey,
      excerpt: a.excerpt ?? undefined,
      cover_url: cover,
      published_at: a.published_at ?? a.created_at,
      author,
      tag: defaultTag,
      parts: partsTag,
      readers,
      link: `/article/${a.slug}`
    };
  }

  /** Decorative read count for listing (stable per slug). */
  private fakeReaders(slug: string): string {
    let n = 0;
    for (let i = 0; i < slug.length; i++) n += slug.charCodeAt(i);
    const k = 1 + (n % 80);
    return k >= 50 ? '1L+ पाठक' : `${k}K+ पाठक`;
  }

  private pdfCard(i: ArchiveItem, categorySlug: string): CategoryCard {
    const slug = i.slug || slugFromPdfUrl(i.pdf_url);
    let excerpt = (i.excerpt ?? '').trim();
    excerpt = excerpt.replace(/\s*—\s*ई-मैगज़ीन.*$/i, '').replace(/\s*—\s*.*पढ़ें.*$/i, '').trim();
    return {
      kind: 'pdf',
      title: i.title,
      slug,
      excerpt: excerpt || undefined,
      cover_url: i.cover_url,
      published_at: i.published_at ?? i.created_at,
      tag: categoryLabel(categorySlug),
      link: `/story/${slug}`,
      pdf_url: i.pdf_url
    };
  }

  private defaultLoveCover(seriesSlug: string): string {
    return `/uploads/images/love-story/${seriesSlug}.jpg`;
  }

  private defaultKahaniCover(slug: string): string {
    return `/uploads/images/kahani/${slug}.jpg`;
  }

  cardImage(item: CategoryCard): string {
    if (item.kind === 'pdf') {
      return pdfCoverImage(this.apiBase, item) || `${this.apiBase}/uploads/images/news-card.svg`;
    }
    const url = item.cover_url || '';
    if (!url && item.tag === 'कहानी') {
      return `${this.apiBase}/uploads/images/kahani/${item.slug}.jpg`;
    }
    if (!url) return `${this.apiBase}/uploads/images/news-card.svg`;
    if (url.startsWith('http')) return url;
    return `${this.apiBase}${url}`;
  }

  onCoverError(ev: Event, item: CategoryCard): void {
    const img = ev.target as HTMLImageElement;
    if (img.dataset['fallback'] === '1') return;
    img.dataset['fallback'] = '1';
    if (item.tag === 'समाचार' || this.categorySlug === 'lekh') {
      img.src = `${this.apiBase}/uploads/images/news-card.svg`;
      return;
    }
    if (item.tag === 'कहानी' && item.slug) {
      img.src = `${this.apiBase}/uploads/images/kahani/${item.slug}.jpg`;
      return;
    }
    const key = item.series_slug || item.slug;
    if (key && this.categorySlug === 'love-story') {
      img.src = `${this.apiBase}/uploads/images/love-story/${key}.svg`;
    }
  }

  get totalListPages(): number {
    return Math.max(1, Math.ceil(this.items.length / this.itemsPerPage));
  }

  get pagedItems(): CategoryCard[] {
    const start = (this.listPage - 1) * this.itemsPerPage;
    return this.items.slice(start, start + this.itemsPerPage);
  }

  get listRangeLabel(): string {
    const start = (this.listPage - 1) * this.itemsPerPage + 1;
    const end = Math.min(this.listPage * this.itemsPerPage, this.items.length);
    return `${start}–${end} / ${this.items.length}`;
  }

  goListPage(page: number): void {
    this.listPage = Math.min(Math.max(1, page), this.totalListPages);
    this.cdr.markForCheck();
    try {
      document.querySelector('.catPage')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch {
      /* ignore */
    }
  }
}
