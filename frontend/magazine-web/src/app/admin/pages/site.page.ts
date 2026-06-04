import { NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { normalizeHeroSlides } from '../../features/site/hero-slides.util';
import { SITE_DEFAULTS, SiteSettingsApi } from '../../features/site/site-settings.api';
import { HeroSlide, SiteSettings } from '../../features/site/site-settings.types';
import { AdminSession } from '../admin.session';

type SlideRow = HeroSlide;

@Component({
  standalone: true,
  selector: 'app-admin-site',
  imports: [NgFor, NgIf, FormsModule, RouterLink],
  templateUrl: './site.page.html',
  styleUrls: ['../admin.shared.scss', './site.page.scss']
})
export class AdminSitePage implements OnInit {
  private readonly api = inject(SiteSettingsApi);
  private readonly session = inject(AdminSession);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  saving = false;
  uploading = false;
  uploadTarget: string | null = null;
  error = '';
  success = '';
  canSave = false;

  form: SiteSettings = { ...SITE_DEFAULTS, hero_slides: [...SITE_DEFAULTS.hero_slides] };
  slides: SlideRow[] = SITE_DEFAULTS.hero_slides.map((s) => ({ ...s }));
  previewSlide = 0;

  ngOnInit() {
    this.canSave = this.session.isLoggedIn();
    void this.reload();
  }

  reload() {
    void this.load();
  }

  private async load() {
    this.loading = true;
    this.error = '';
    try {
      const publicSettings = await new Promise<SiteSettings>((resolve, reject) => {
        this.api.getPublic().subscribe({ next: resolve, error: reject });
      });
      this.applySettings(publicSettings);

      const token = this.session.getToken();
      if (token) {
        const adminSettings = await new Promise<SiteSettings | null>((resolve) => {
          this.api.getAdmin(token).subscribe({ next: resolve, error: () => resolve(null) });
        });
        if (adminSettings) this.applySettings(adminSettings);
      } else {
        this.error = 'Save ke liye dubara login karein.';
      }
    } catch {
      this.applySettings({ ...SITE_DEFAULTS, hero_slides: [...SITE_DEFAULTS.hero_slides] });
      this.error = 'Server se load nahi hua — default form dikha rahe hain. Backend check karein.';
    } finally {
      this.loading = false;
      this.cdr.markForCheck();
    }
  }

  private applySettings(s: SiteSettings) {
    this.form = { ...s };
    const normalized = normalizeHeroSlides(s.hero_slides);
    this.slides = normalized.map((slide) => ({ ...slide }));
    if (this.previewSlide >= this.slides.length) this.previewSlide = 0;
  }

  addSlide() {
    this.slides.push({ image: '', category_label: '', title: '', link: '' });
    this.previewSlide = this.slides.length - 1;
  }

  removeSlide(i: number) {
    if (this.slides.length <= 1) {
      this.error = 'Kam se kam 1 slider slide chahiye.';
      return;
    }
    this.slides.splice(i, 1);
    if (this.previewSlide >= this.slides.length) this.previewSlide = this.slides.length - 1;
    this.error = '';
  }

  moveSlide(i: number, dir: -1 | 1) {
    const j = i + dir;
    if (j < 0 || j >= this.slides.length) return;
    const tmp = this.slides[i];
    this.slides[i] = this.slides[j];
    this.slides[j] = tmp;
    this.previewSlide = j;
  }

  onSlideFile(evt: Event, index: number) {
    const token = this.session.getToken();
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!token) {
      this.error = 'Upload ke liye login zaroori hai.';
      return;
    }
    if (!file) return;
    this.uploading = true;
    this.uploadTarget = `slide-${index}`;
    this.api.uploadImage(file, token).subscribe({
      next: (res) => {
        this.slides[index].image = res.url;
        this.uploading = false;
        this.uploadTarget = null;
        input.value = '';
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'Image upload fail.';
        this.uploading = false;
        this.uploadTarget = null;
        this.cdr.markForCheck();
      }
    });
  }

  onImage(evt: Event, field: 'intro_editorial_image' | 'intro_letter_image') {
    const token = this.session.getToken();
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!token || !file) return;
    this.uploading = true;
    this.uploadTarget = field;
    this.api.uploadImage(file, token).subscribe({
      next: (res) => {
        this.form[field] = res.url;
        this.uploading = false;
        this.uploadTarget = null;
        input.value = '';
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'Image upload fail.';
        this.uploading = false;
        this.uploadTarget = null;
        this.cdr.markForCheck();
      }
    });
  }

  save() {
    const token = this.session.getToken();
    if (!token) {
      this.error = 'Login expire — dubara login karein.';
      return;
    }

    const hero_slides = this.slides
      .map((s) => ({
        image: s.image.trim(),
        category_label: s.category_label.trim(),
        title: s.title.trim(),
        link: s.link.trim()
      }))
      .filter((s) => s.image);

    if (!hero_slides.length) {
      this.error = 'Kam se kam 1 slider (image) add karein.';
      return;
    }

    this.saving = true;
    this.error = '';
    this.success = '';

    this.api.update({ ...this.form, hero_slides }, token).subscribe({
      next: (s) => {
        this.applySettings(s);
        this.success = 'Homepage save ho gaya! Public site: Ctrl+F5 karein.';
        this.saving = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.error = err?.error?.detail ?? 'Save failed — backend chal raha hai?';
        this.saving = false;
        this.cdr.markForCheck();
      }
    });
  }

  previewUrl(path: string): string {
    return path ? this.api.resolveAsset(path) : '';
  }

  activePreview(): SlideRow | undefined {
    return this.slides[this.previewSlide];
  }
}
