import { NgFor, NgIf } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';

import { AdminApi, AdminStats } from '../admin.api';
import { AdminSession } from '../admin.session';

const EMPTY_STATS: AdminStats = {
  articles_total: 0,
  articles_published: 0,
  articles_draft: 0,
  archive_total: 0,
  users_total: 1,
  categories_total: 0
};

@Component({
  standalone: true,
  selector: 'app-admin-dashboard',
  imports: [NgFor, NgIf, RouterLink],
  templateUrl: './dashboard.page.html',
  styleUrls: ['../admin.shared.scss', './dashboard.page.scss']
})
export class AdminDashboardPage implements OnInit {
  private readonly api = inject(AdminApi);
  private readonly session = inject(AdminSession);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  error = '';
  warn = '';
  stats: AdminStats = { ...EMPTY_STATS };

  ngOnInit() {
    void this.load();
  }

  reload() {
    void this.load();
  }

  private async load() {
    const token = this.session.getToken();
    if (!token) {
      this.loading = false;
      this.error = 'Login expire — dubara login karein.';
      this.cdr.markForCheck();
      return;
    }

    this.loading = true;
    this.error = '';
    this.warn = '';

    this.api.getStats(token).subscribe({
      next: (s) => {
        this.stats = s;
        this.loading = false;
        if (s.articles_total === 0 && s.archive_total === 0) {
          this.warn = 'MongoDB band ho sakta hai — PDF/archive phir bhi kaam karega.';
        }
        this.cdr.markForCheck();
      },
      error: () => {
        this.stats = { ...EMPTY_STATS };
        this.loading = false;
        this.error = 'Stats load fail — Reload try karein ya backend start karein (port 8000).';
        this.cdr.markForCheck();
      }
    });

    // Archive count from public API if stats slow
    this.api.listArchive().subscribe({
      next: (items) => {
        if (items.length && this.stats.archive_total < items.length) {
          this.stats = { ...this.stats, archive_total: items.length };
          this.cdr.markForCheck();
        }
      }
    });
  }
}
