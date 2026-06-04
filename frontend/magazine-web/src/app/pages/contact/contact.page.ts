import { Component } from '@angular/core';

import { SITE_EMAIL } from '../../core/site.config';
import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-contact-page',
  imports: [PageShellComponent],
  template: `
    <app-page-shell title="संपर्क सूत्र" subtitle="हमसे जुड़ें">
      <section class="grid">
        <div class="card">
          <div class="card__title">ईमेल</div>
          <p><a class="link" [href]="'mailto:' + siteEmail">{{ siteEmail }}</a></p>
        </div>
        <div class="card">
          <div class="card__title">फ़ोन</div>
          <p class="muted">+91-XXXXXXXXXX</p>
        </div>
        <div class="card">
          <div class="card__title">पता</div>
          <p class="muted">नई दिल्ली, भारत</p>
        </div>
      </section>
    </app-page-shell>
  `,
  styles: [
    `
      .grid {
        margin-top: 1rem;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
      }
      .card {
        border: 1px solid #e8e8ee;
        background: #fff;
        border-radius: 18px;
        padding: 1rem;
      }
      .card__title {
        font-weight: 900;
        margin-bottom: 0.25rem;
      }
      .muted {
        color: #6b7280;
      }
      .link {
        color: var(--magenta, #9d0a5d);
        font-weight: 800;
        text-decoration: none;
      }
      .link:hover {
        text-decoration: underline;
      }
      @media (max-width: 900px) {
        .grid {
          grid-template-columns: 1fr;
        }
      }
    `
  ]
})
export class ContactPage {
  protected readonly siteEmail = SITE_EMAIL;
}
