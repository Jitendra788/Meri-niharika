import { DatePipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { API_BASE_URL } from '../../core/api.tokens';
import { ADMIN_CATEGORIES, categoryLabel } from '../../pages/category/category-labels';
import { AdminApi, ArchiveItem } from '../admin.api';
import { AdminSession } from '../admin.session';
import { pingBackend, publishArchiveFetch, uploadCoverXhr, uploadPdfXhr } from '../admin.upload';

@Component({
  standalone: true,
  selector: 'app-admin-archive',
  imports: [NgIf, NgFor, DatePipe, FormsModule, RouterLink],
  templateUrl: './archive.page.html',
  styleUrls: ['../admin.shared.scss', '../admin.page.scss', './archive.page.scss']
})
export class AdminArchivePage implements OnInit {
  protected readonly session = inject(AdminSession);
  protected readonly apiBase = inject(API_BASE_URL);
  private readonly api = inject(AdminApi);
  private readonly cdr = inject(ChangeDetectorRef);
  private publishAbort: AbortController | null = null;

  readonly categories = ADMIN_CATEGORIES;
  readonly pdfCategories = ADMIN_CATEGORIES.filter((c) =>
    ['kahani', 'love-story', 'kavita', 'lekh', 'swasthya', 'manoranjan', 'dharm', 'sahitya', 'sbi'].includes(c.slug)
  );

  file: File | null = null;
  fileName = '';
  error = '';
  success = '';
  published = '';
  uploading = false;
  uploadPct = 0;
  uploadStatus = '';
  fileSizeLabel = '';
  backendOk = true;
  publishing = false;
  publishStatus = '';
  lastPdfUrl = '';

  pubTitle = '';
  pubLang = 'hi';
  pubCategory = 'kahani';
  coverFile: File | null = null;
  coverPreview = '';
  lastCoverUrl = '';

  listLoading = false;
  items: ArchiveItem[] = [];
  listFilter = 'all';
  editingId: string | null = null;
  editTitle = '';
  editCategory = 'kahani';
  editLang = 'hi';
  savingEdit = false;

  ngOnInit() {
    void this.checkBackend();
    this.loadList();
  }

  categoryName(slug: string | null | undefined): string {
    return categoryLabel(slug ?? 'kahani');
  }

  async checkBackend() {
    this.backendOk = await pingBackend(this.apiBase);
    if (!this.backendOk) {
      this.error = 'Backend बंद है — uvicorn app.main:app --port 8000';
    }
  }

  loadList() {
    const token = this.session.getToken();
    if (!token) {
      this.items = [];
      return;
    }
    this.listLoading = true;
    this.api.listArchive(200, token).subscribe({
      next: (rows) => {
        this.items = rows;
        this.listLoading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'अंक सूची लोड नहीं हुई — backend चालू करें।';
        this.listLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  filteredItems(): ArchiveItem[] {
    if (this.listFilter === 'all') return this.items;
    return this.items.filter((it) => (it.category_slug || 'kahani') === this.listFilter);
  }

  onFile(evt: Event) {
    this.error = '';
    this.success = '';
    this.published = '';
    const input = evt.target as HTMLInputElement;
    const f = input.files?.[0] ?? null;
    if (!f) {
      this.file = null;
      this.fileName = '';
      return;
    }
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      this.error = 'केवल PDF फ़ाइल चुनें।';
      input.value = '';
      return;
    }
    if (f.size > 50 * 1024 * 1024) {
      this.error = 'PDF 50MB से बड़ी है।';
      input.value = '';
      return;
    }
    this.file = f;
    this.fileName = f.name;
    this.fileSizeLabel = this.formatSize(f.size);
    if (!this.pubTitle.trim()) {
      this.pubTitle = f.name.replace(/\.pdf$/i, '');
    }
  }

  async upload() {
    if (!this.file) return;
    const token = this.session.getToken();
    if (!token) {
      this.error = 'सत्र समाप्त — दोबारा लॉगिन करें।';
      return;
    }
    if (!(await pingBackend(this.apiBase))) {
      this.error = 'Backend से कनेक्ट नहीं हो रहा।';
      return;
    }

    this.uploading = true;
    this.uploadPct = 0;
    this.error = '';
    this.success = '';
    const file = this.file;
    try {
      const data = await uploadPdfXhr(this.apiBase, file, token, (pct) => {
        this.uploadPct = pct;
        this.uploadStatus = `अपलोड… ${pct}%`;
      });
      this.lastPdfUrl = data.pdf_url;
      if (data.cover_url) {
        this.lastCoverUrl = data.cover_url;
        this.coverPreview = `${this.apiBase}${data.cover_url}`;
      }
      this.file = null;
      this.fileName = '';
      let msg = 'PDF अपलोड हो गई! कवर पेज तैयार। अब शीर्षक, श्रेणी चुनकर प्रकाशित करें।';
      if (data.original_bytes && data.compressed_bytes && data.compressed_bytes < data.original_bytes) {
        const saved = Math.round((1 - data.compressed_bytes / data.original_bytes) * 100);
        msg += ` (PDF ${saved}% छोटी)`;
      }
      this.success = msg;
    } catch (e: unknown) {
      this.error = e instanceof Error ? e.message : 'अपलोड विफल।';
    } finally {
      this.uploading = false;
      this.uploadStatus = '';
      this.cdr.markForCheck();
    }
  }

  onCover(evt: Event) {
    const input = evt.target as HTMLInputElement;
    const f = input.files?.[0] ?? null;
    if (!f) return;
    if (!/\.(jpe?g|png|webp)$/i.test(f.name)) {
      this.error = 'कवर: JPG, PNG या WebP।';
      return;
    }
    this.coverFile = f;
    this.coverPreview = URL.createObjectURL(f);
  }

  cancelPublish() {
    this.publishAbort?.abort();
    this.publishing = false;
    this.error = 'प्रकाशन रद्द।';
    this.cdr.markForCheck();
  }

  async publish() {
    if (!this.lastPdfUrl || !this.pubTitle.trim()) return;
    const token = this.session.getToken();
    if (!token) return;

    this.publishAbort = new AbortController();
    this.publishing = true;
    this.publishStatus = 'प्रकाशित हो रहा है…';
    this.error = '';
    this.published = '';

    try {
      let coverUrl = this.lastCoverUrl;
      if (this.coverFile) {
        const coverRes = await uploadCoverXhr(this.apiBase, this.coverFile, this.lastPdfUrl, token);
        coverUrl = coverRes.cover_url;
        this.lastCoverUrl = coverUrl;
        this.coverFile = null;
      }

      await publishArchiveFetch(
        this.apiBase,
        {
          title: this.pubTitle.trim(),
          language: this.pubLang,
          pdf_url: this.lastPdfUrl,
          cover_url: coverUrl || undefined,
          category_slug: this.pubCategory
        },
        token,
        { signal: this.publishAbort.signal, timeoutMs: 8_000 }
      );

      this.published = `"${this.pubTitle}" ${this.categoryName(this.pubCategory)} में प्रकाशित!`;
      this.lastPdfUrl = '';
      this.pubTitle = '';
      this.loadList();
    } catch (e: unknown) {
      this.error = e instanceof Error ? e.message : 'प्रकाशन विफल।';
    } finally {
      this.publishing = false;
      this.publishStatus = '';
      this.publishAbort = null;
      this.cdr.markForCheck();
    }
  }

  startEdit(item: ArchiveItem) {
    this.editingId = item.id;
    this.editTitle = item.title;
    this.editCategory = item.category_slug || 'kahani';
    this.editLang = item.language || 'hi';
    this.error = '';
    this.success = '';
  }

  cancelEdit() {
    this.editingId = null;
  }

  saveEdit() {
    const token = this.session.getToken();
    if (!token || !this.editingId || !this.editTitle.trim()) return;

    this.savingEdit = true;
    this.api
      .updateArchive(
        this.editingId,
        {
          title: this.editTitle.trim(),
          category_slug: this.editCategory,
          language: this.editLang
        },
        token
      )
      .subscribe({
        next: () => {
          this.success = 'अंक अपडेट हो गया।';
          this.savingEdit = false;
          this.editingId = null;
          this.loadList();
        },
        error: () => {
          this.error = 'अपडेट विफल।';
          this.savingEdit = false;
          this.cdr.markForCheck();
        }
      });
  }

  remove(item: ArchiveItem) {
    if (!confirm(`"${item.title}" हटाएँ?\n\nPDF फ़ाइल और कवर स्थायी रूप से हट जाएँगे।`)) return;
    const token = this.session.getToken();
    if (!token) return;

    this.api.deleteArchive(item.id, token).subscribe({
      next: () => {
        if (this.editingId === item.id) this.editingId = null;
        this.success = `"${item.title}" हटा दिया गया।`;
        this.error = '';
        this.loadList();
      },
      error: (err) => {
        this.error = err?.error?.detail ?? 'हटाना विफल — backend restart करें।';
        this.cdr.markForCheck();
      }
    });
  }

  storyLink(item: ArchiveItem): string {
    return `/story/${item.slug}`;
  }

  private formatSize(bytes: number): string {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
}
