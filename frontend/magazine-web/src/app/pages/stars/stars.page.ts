import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-stars-page',
  imports: [PageShellComponent, RouterLink],
  template: `
    <app-page-shell title="तारे-सितारे" subtitle="ज्योतिष, वास्तु, अंक शास्त्र (demo)">
      <section class="grid">
        <a class="card" *ngFor="let r of items" [routerLink]="['/article', r.slug]">
          <div class="card__title">{{ r.title }}</div>
          <div class="muted">{{ r.excerpt }}</div>
        </a>
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
        display: block;
        border: 1px solid #e8e8ee;
        background: #fff;
        border-radius: 18px;
        padding: 1rem;
        text-decoration: none;
        color: inherit;
      }
      .card:hover {
        border-color: #d7d7ee;
        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
      }
      .card__title {
        font-weight: 900;
      }
      .muted {
        color: #6b7280;
      }
      @media (max-width: 900px) {
        .grid {
          grid-template-columns: 1fr;
        }
      }
    `
  ]
})
export class StarsPage {
  protected readonly items = [
    { slug: 'stars-1', title: 'आज का राशिफल', excerpt: 'ज्योतिष सेक्शन का डेमो...' },
    { slug: 'stars-2', title: 'वास्तु टिप्स', excerpt: 'घर के लिए...' }
  ];
}

