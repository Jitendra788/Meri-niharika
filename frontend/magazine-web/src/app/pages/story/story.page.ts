import { DatePipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { AdminApi, ArchiveItem } from '../../admin/admin.api';
import { slugFromPdfUrl } from '../../admin/admin.upload';
import { API_BASE_URL } from '../../core/api.tokens';
import { pdfCoverImage } from '../../core/pdf-cover';

@Component({
  standalone: true,
  selector: 'app-story-page',
  imports: [NgFor, NgIf, DatePipe, RouterLink],
  templateUrl: './story.page.html',
  styleUrl: './story.page.scss'
})
export class StoryPage implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly api = inject(AdminApi);
  protected readonly apiBase = inject(API_BASE_URL);

  loading = true;
  loadError = '';
  issue: ArchiveItem | null = null;
  related: ArchiveItem[] = [];
  paragraphs: string[] = [];
  pageHasMore = false;
  pageNextSkip = 0;
  pageTotal = 0;
  loadingMore = false;
  shareOk: 'ig' | '' = '';
  brokenCovers = new Set<string>();
  readonly pageBatchSize = 2;
  readonly skeletonLines = [1, 2, 3, 4, 5, 6];
  readonly skeletonSides = [1, 2, 3];

  ngOnInit() {
    this.route.paramMap.subscribe((p) => {
      const slug = p.get('slug') ?? '';
      if (slug) this.load(slug);
    });
  }

  private load(slug: string) {
    this.loading = true;
    this.loadError = '';
    this.issue = null;
    this.paragraphs = [];
    this.pageHasMore = false;
    this.pageNextSkip = 0;
    this.pageTotal = 0;
    this.brokenCovers = new Set();
    this.cdr.markForCheck();

    this.api.getArchiveBySlug(slug).subscribe({
      next: (issue) => {
        this.issue = issue;
        this.paragraphs = issue.paragraphs ?? [];
        this.pageHasMore = issue.page_has_more ?? false;
        this.pageNextSkip = this.pageBatchSize;
        this.pageTotal = issue.page_total ?? 0;
        this.loading = false;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.cdr.markForCheck();
        this.loadRelated();
      },
      error: () => {
        this.loadError = 'यह अंक नहीं मिला।';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  private loadRelated() {
    this.api.listArchive(12).subscribe({
      next: (list) => {
        this.related = list;
        this.cdr.markForCheck();
      }
    });
  }

  leadText(item: ArchiveItem): string {
    const ex = (item.excerpt ?? '').trim();
    if (!ex) return '';
    return ex.replace(/\s*—\s*ई-मैगज़ीन.*$/i, '').replace(/\s*—\s*.*पढ़ें.*$/i, '').trim();
  }

  bodyKicker(): string {
    const t = this.issue?.title?.trim() ?? '';
    if (t.includes(':')) {
      return t.split(':')[0].trim() + ' :';
    }
    return 'कहानी :';
  }

  loadMore() {
    if (!this.issue || this.loadingMore || !this.pageHasMore) return;

    const slug = this.issue.slug || slugFromPdfUrl(this.issue.pdf_url);
    this.loadingMore = true;
    this.cdr.markForCheck();

    this.api.getArchivePages(slug, this.pageNextSkip, this.pageBatchSize).subscribe({
      next: (batch) => {
        this.paragraphs = [...this.paragraphs, ...(batch.paragraphs ?? [])];
        this.pageHasMore = batch.has_more;
        this.pageNextSkip = batch.next_skip;
        this.pageTotal = batch.total_pages;
        this.loadingMore = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loadingMore = false;
        this.cdr.markForCheck();
      }
    });
  }

  shareUrl(): string {
    if (typeof window === 'undefined') return '';
    return window.location.href;
  }

  shareMessage(item: ArchiveItem): string {
    return `${item.title} — Ishqora\n${this.shareUrl()}`;
  }

  facebookShareUrl(): string {
    return `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(this.shareUrl())}`;
  }

  whatsappShareUrl(item: ArchiveItem): string {
    return `https://wa.me/?text=${encodeURIComponent(this.shareMessage(item))}`;
  }

  async shareInstagram(item: ArchiveItem) {
    try {
      await navigator.clipboard.writeText(this.shareMessage(item));
      this.shareOk = 'ig';
      this.cdr.markForCheck();
      window.open('https://www.instagram.com/', '_blank', 'noopener,noreferrer');
      setTimeout(() => {
        this.shareOk = '';
        this.cdr.markForCheck();
      }, 3000);
    } catch {
      window.open('https://www.instagram.com/', '_blank', 'noopener,noreferrer');
    }
  }

  coverImage(item: ArchiveItem): string {
    return pdfCoverImage(this.apiBase, item);
  }

  sidebarCover(item: ArchiveItem): string {
    return pdfCoverImage(this.apiBase, item);
  }

  onCoverError(id: string) {
    this.brokenCovers.add(id);
    this.cdr.markForCheck();
  }

  storyLink(item: ArchiveItem): string {
    const s = item.slug || slugFromPdfUrl(item.pdf_url);
    return `/story/${s}`;
  }

  relatedItems(current: ArchiveItem): ArchiveItem[] {
    const cur = current.slug || slugFromPdfUrl(current.pdf_url);
    const seen = new Set<string>();
    const out: ArchiveItem[] = [];
    for (const x of this.related) {
      const slug = x.slug || slugFromPdfUrl(x.pdf_url);
      if (slug === cur) continue;
      const key = x.pdf_url || slug;
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(x);
      if (out.length >= 5) break;
    }
    return out;
  }
}
