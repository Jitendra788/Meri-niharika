import { DatePipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { SiteSettingsApi } from '../../features/site/site-settings.api';
import { ADMIN_CATEGORIES, categoryLabel } from '../../pages/category/category-labels';
import { AdminApi, ArticleInput } from '../admin.api';
import { AdminSession } from '../admin.session';
import { Article } from '../../features/articles/articles.types';

@Component({
  standalone: true,
  selector: 'app-admin-articles',
  imports: [NgFor, NgIf, DatePipe, FormsModule, RouterLink],
  templateUrl: './articles.page.html',
  styleUrls: ['../admin.shared.scss', './articles.page.scss']
})
export class AdminArticlesPage implements OnInit {
  private readonly api = inject(AdminApi);
  private readonly siteApi = inject(SiteSettingsApi);
  private readonly session = inject(AdminSession);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly categories = ADMIN_CATEGORIES;

  loading = true;
  saving = false;
  uploadingCover = false;
  error = '';
  success = '';
  filter = 'all';
  categoryFilter = 'all';
  articles: Article[] = [];
  editingId: string | null = null;

  form: ArticleInput = this.emptyForm();

  ngOnInit() {
    this.load();
  }

  categoryName(slug: string | null | undefined): string {
    return categoryLabel(slug ?? '');
  }

  load() {
    const token = this.session.getToken();
    if (!token) {
      this.loading = false;
      this.error = 'सत्र समाप्त — दोबारा लॉगिन करें।';
      this.cdr.markForCheck();
      return;
    }
    this.loading = true;
    this.error = '';
    this.api.listArticles(token, this.filter, this.categoryFilter).subscribe({
      next: (rows) => {
        this.articles = rows;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'पोस्ट लोड नहीं हुए — backend (पोर्ट 8000) चालू करें।';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  coverPreview(url: string) {
    return this.siteApi.resolveAsset(url);
  }

  onCoverUpload(evt: Event) {
    const token = this.session.getToken();
    const file = (evt.target as HTMLInputElement).files?.[0];
    if (!token || !file) return;
    this.uploadingCover = true;
    this.siteApi.uploadImage(file, token).subscribe({
      next: (res) => {
        this.form.cover_url = res.url;
        this.uploadingCover = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'चित्र अपलोड विफल।';
        this.uploadingCover = false;
        this.cdr.markForCheck();
      }
    });
  }

  newArticle(categorySlug = 'lekh') {
    this.editingId = null;
    this.form = this.emptyForm(categorySlug);
    this.success = '';
    this.error = '';
  }

  edit(article: Article) {
    this.editingId = article.id;
    this.form = {
      title: article.title,
      slug: article.slug,
      excerpt: article.excerpt ?? '',
      content: article.content ?? '',
      cover_url: article.cover_url ?? '',
      category_slug: article.category_slug ?? 'lekh',
      language: article.language ?? 'hi',
      status: article.status
    };
    this.success = '';
    this.error = '';
  }

  save() {
    const token = this.session.getToken();
    if (!token || !this.form.title.trim()) return;

    this.saving = true;
    this.error = '';
    this.success = '';

    const body: ArticleInput = {
      ...this.form,
      title: this.form.title.trim(),
      excerpt: this.form.excerpt?.trim() || undefined,
      content: this.form.content?.trim() || undefined,
      cover_url: this.form.cover_url?.trim() || undefined,
      category_slug: this.form.category_slug?.trim() || undefined
    };

    const req = this.editingId
      ? this.api.updateArticle(this.editingId, body, token)
      : this.api.createArticle(body, token);

    req.subscribe({
      next: () => {
        this.success = this.editingId
          ? `"${body.title}" अपडेट हो गया (${this.categoryName(body.category_slug)})`
          : `"${body.title}" बन गया — प्रकाशित पोस्ट /category/${body.category_slug} पर दिखेगा।`;
        this.saving = false;
        this.newArticle(body.category_slug ?? 'lekh');
        this.load();
      },
      error: (err) => {
        const detail = err?.error?.detail;
        this.error = typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(', ')
            : 'सेव विफल — शीर्षक भरें और backend चालू रखें।';
        this.saving = false;
        this.cdr.markForCheck();
      }
    });
  }

  remove(article: Article) {
    if (!confirm(`"${article.title}" हटाएँ?`)) return;
    const token = this.session.getToken();
    if (!token) return;
    this.api.deleteArticle(article.id, token).subscribe({
      next: () => {
        if (this.editingId === article.id) this.newArticle(article.category_slug ?? 'lekh');
        this.load();
      },
      error: () => {
        this.error = 'हटाना विफल।';
        this.cdr.markForCheck();
      }
    });
  }

  private emptyForm(categorySlug = 'lekh'): ArticleInput {
    return {
      title: '',
      slug: '',
      excerpt: '',
      content: '',
      cover_url: '',
      category_slug: categorySlug,
      language: 'hi',
      status: 'draft'
    };
  }
}
