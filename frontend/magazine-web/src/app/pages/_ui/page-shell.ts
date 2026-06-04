import { NgIf } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-page-shell',
  imports: [NgIf, RouterLink],
  template: `
    <section class="shell">
      <div class="shell__head" *ngIf="title">
        <nav class="shell__crumbs" aria-label="ब्रेडक्रंब">
          <a routerLink="/">मुखपृष्ठ</a>
          <span class="shell__sep">/</span>
          <span class="shell__cur">{{ title }}</span>
        </nav>
        <h1 class="shell__title">{{ title }}</h1>
        <p class="shell__subtitle" *ngIf="subtitle">{{ subtitle }}</p>
      </div>
      <div class="shell__body">
        <ng-content />
      </div>
    </section>
  `,
  styles: [
    `
      .shell {
        max-width: 1180px;
        margin: 0 auto;
        padding: 1.25rem 1rem 2.5rem;
      }

      .shell__head {
        margin-bottom: 1.35rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid var(--magenta, #9d0a5d);
      }

      .shell__crumbs {
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
        align-items: center;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: #777;
      }

      .shell__crumbs a {
        color: var(--magenta, #9d0a5d);
        text-decoration: none;
        font-weight: 700;
      }

      .shell__crumbs a:hover {
        text-decoration: underline;
      }

      .shell__sep {
        color: #ccc;
      }

      .shell__cur {
        color: #555;
        font-weight: 600;
      }

      .shell__title {
        margin: 0;
        font-size: clamp(1.55rem, 3vw, 2rem);
        font-weight: 900;
        letter-spacing: -0.02em;
        color: #111;
        line-height: 1.25;
      }

      .shell__subtitle {
        margin: 0.45rem 0 0;
        color: #666;
        font-size: 0.98rem;
        line-height: 1.5;
        max-width: 52rem;
      }

      .shell__body {
        min-width: 0;
      }

      @media (max-width: 640px) {
        .shell {
          padding: 1rem 0.75rem 2rem;
        }

        .shell__head {
          margin-bottom: 1rem;
          padding-bottom: 0.75rem;
        }

        .shell__title {
          font-size: 1.35rem;
        }

        .shell__subtitle {
          font-size: 0.9rem;
        }
      }
    `
  ]
})
export class PageShellComponent {
  @Input() title?: string;
  @Input() subtitle?: string;
}
