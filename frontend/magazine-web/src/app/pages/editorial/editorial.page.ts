import { AsyncPipe, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';

import { SiteSettingsApi } from '../../features/site/site-settings.api';
import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-editorial-page',
  imports: [AsyncPipe, NgIf, PageShellComponent],
  template: `
    <app-page-shell *ngIf="site$ | async as s" [title]="s.editorial_page_title" subtitle="संपादकीय">
      <section class="card">
        <p class="body">{{ s.editorial_page_body }}</p>
      </section>
    </app-page-shell>
  `,
  styles: [
    `
      .card {
        margin-top: 1rem;
        border: 1px solid #e8e8ee;
        background: #fff;
        border-radius: 18px;
        padding: 1rem;
        line-height: 1.7;
      }
      .body {
        margin: 0;
        white-space: pre-wrap;
      }
    `
  ]
})
export class EditorialPage {
  private readonly siteApi = inject(SiteSettingsApi);
  protected readonly site$ = this.siteApi.getPublic();
}
