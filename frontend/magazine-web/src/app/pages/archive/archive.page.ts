import { NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';

import { AdminApi, ArchiveItem } from '../../admin/admin.api';
import { slugFromPdfUrl } from '../../admin/admin.upload';
import { API_BASE_URL } from '../../core/api.tokens';
import { pdfCoverImage } from '../../core/pdf-cover';
import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-archive-page',
  imports: [NgFor, NgIf, RouterLink, PageShellComponent],
  templateUrl: './archive.page.html',
  styleUrl: './archive.page.scss'
})
export class ArchivePage implements OnInit {
  protected readonly apiBase = inject(API_BASE_URL);
  private readonly api = inject(AdminApi);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  apiError = '';
  items: ArchiveItem[] = [];

  ngOnInit() {
    this.load();
  }

  reload() {
    this.load();
  }

  load() {
    this.loading = true;
    this.apiError = '';
    this.cdr.markForCheck();

    this.api.listArchive(30).subscribe({
      next: (list) => {
        this.items = list;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.items = [];
        this.loading = false;
        this.apiError =
          'PDF list load nahi hui. Backend start karein: cd backend → uvicorn app.main:app --port 8000';
        this.cdr.markForCheck();
      }
    });
  }

  storyLink(item: ArchiveItem): string {
    const slug = item.slug || slugFromPdfUrl(item.pdf_url);
    return `/story/${slug}`;
  }

  assetFull(url: string): string {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return `${this.apiBase}${url}`;
  }

  coverImage(item: ArchiveItem): string {
    return pdfCoverImage(this.apiBase, item);
  }

  openPdf(item: ArchiveItem, event: Event) {
    event.preventDefault();
    event.stopPropagation();
    window.open(this.assetFull(item.pdf_url), '_blank', 'noopener');
  }
}
