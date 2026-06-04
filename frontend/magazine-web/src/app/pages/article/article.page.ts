import { DatePipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { API_BASE_URL } from '../../core/api.tokens';
import { ArticlesApi } from '../../features/articles/articles.api';
import { Article } from '../../features/articles/articles.types';
import { categoryLabel } from '../category/category-labels';

@Component({
  standalone: true,
  selector: 'app-article-page',
  imports: [NgFor, NgIf, DatePipe, RouterLink],
  templateUrl: './article.page.html',
  styleUrl: './article.page.scss'
})
export class ArticlePage implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(ArticlesApi);
  private readonly cdr = inject(ChangeDetectorRef);
  protected readonly apiBase = inject(API_BASE_URL);

  loading = true;
  notFound = false;
  article: Article | null = null;
  related: Article[] = [];
  seriesParts: Article[] = [];
  paragraphs: string[] = [];
  prevPart: Article | null = null;
  nextPart: Article | null = null;
  /** Sidebar: भाग list pagination (4 per page so controls show for 5+ भाग) */
  readonly partsPerPage = 4;
  partsPage = 1;

  ngOnInit() {
    this.route.paramMap.subscribe((p) => {
      const slug = p.get('slug') ?? '';
      this.load(slug);
    });
  }

  private load(slug: string) {
    this.loading = true;
    this.notFound = false;
    this.article = null;
    this.related = [];
    this.seriesParts = [];
    this.prevPart = null;
    this.nextPart = null;
    this.partsPage = 1;
    this.cdr.markForCheck();

    this.api.getBySlug(slug).subscribe({
      next: (a) => {
        if (!a?.id || a.title === 'Not found') {
          this.notFound = true;
          this.loading = false;
          this.cdr.markForCheck();
          return;
        }
        this.article = a;
        this.paragraphs = this.splitParagraphs(a.content ?? '');
        if (a.series_slug) {
          this.loadSeries(a);
        } else {
          this.loadRelated(a);
        }
      },
      error: () => {
        this.notFound = true;
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  private loadSeries(a: Article) {
    const key = a.series_slug!;
    this.api.listSeriesParts(key).subscribe({
      next: (parts) => {
        this.seriesParts = parts;
        const cur = a.part_number ?? 1;
        const prev = parts.find((p) => (p.part_number ?? 0) === cur - 1);
        const next = parts.find((p) => (p.part_number ?? 0) === cur + 1);
        this.prevPart = prev ?? null;
        this.nextPart = next ?? null;
        this.related = parts;
        this.partsPage = Math.max(1, Math.ceil(cur / this.partsPerPage));
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loadRelated(a);
      }
    });
  }

  private loadRelated(a: Article) {
    const cat = a.category_slug ?? 'kahani';
    this.api.listPublished(12, 0, cat).subscribe({
      next: (list) => {
        this.related = list.filter((x) => x.slug !== a.slug).slice(0, 6);
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  private splitParagraphs(content: string): string[] {
    const trimmed = content.trim();
    if (!trimmed) return [];
    return trimmed.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
  }

  partLabel(a: Article): string {
    if (a.part_number && a.parts_total) {
      return `भाग ${a.part_number} / ${a.parts_total}`;
    }
    const tag = a.tags?.find((t) => /भाग/.test(t));
    return tag ?? '';
  }

  authorName(a: Article): string {
    return a.tags?.[0] ?? 'Ishqora';
  }

  storyTag(a: Article): string {
    const t = a.tags?.[1] ?? a.tags?.[0];
    return t ?? 'कहानी';
  }

  categoryTitle(slug: string | null | undefined): string {
    return categoryLabel(slug ?? '');
  }

  assetFull(url: string | undefined | null): string {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return `${this.apiBase}${url}`;
  }

  get totalPartsPages(): number {
    return Math.max(1, Math.ceil(this.seriesParts.length / this.partsPerPage));
  }

  get pagedSeriesParts(): Article[] {
    const start = (this.partsPage - 1) * this.partsPerPage;
    return this.seriesParts.slice(start, start + this.partsPerPage);
  }

  get partsRangeLabel(): string {
    const start = (this.partsPage - 1) * this.partsPerPage + 1;
    const end = Math.min(this.partsPage * this.partsPerPage, this.seriesParts.length);
    return `भाग ${start}–${end} / ${this.seriesParts.length}`;
  }

  goPartsPage(page: number): void {
    this.partsPage = Math.min(Math.max(1, page), this.totalPartsPages);
    this.cdr.markForCheck();
    try {
      document.querySelector('.readerSide__panel')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch {
      /* ignore */
    }
  }

  partCover(r: Article): string {
    if (r.cover_url) return this.assetFull(r.cover_url);
    const key = (r.series_slug ?? r.slug).replace(/-bhag-\d+$/, '');
    return `${this.apiBase}/uploads/images/love-story/${key}.jpg`;
  }

  onPartCoverError(ev: Event, r: Article): void {
    const img = ev.target as HTMLImageElement;
    const key = (r.series_slug ?? r.slug).replace(/-bhag-\d+$/, '');
    if (img.dataset['fallback'] === '1') return;
    img.dataset['fallback'] = '1';
    img.src = `${this.apiBase}/uploads/images/love-story/${key}.svg`;
  }
}
