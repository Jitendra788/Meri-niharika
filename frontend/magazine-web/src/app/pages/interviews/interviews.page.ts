import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-interviews-page',
  imports: [PageShellComponent, RouterLink],
  template: `
    <app-page-shell title="साक्षात्कार" subtitle="आमने-सामने (demo)">
      <section class="list">
        <a class="row" *ngFor="let i of items" [routerLink]="['/article', i.slug]">
          <div class="row__title">{{ i.title }}</div>
          <div class="row__meta muted">{{ i.excerpt }}</div>
        </a>
      </section>
    </app-page-shell>
  `,
  styles: [
    `
      .list {
        margin-top: 1rem;
        border: 1px solid #e8e8ee;
        border-radius: 18px;
        overflow: hidden;
        background: #fff;
      }
      .row {
        display: block;
        padding: 0.9rem 1rem;
        text-decoration: none;
        color: inherit;
        border-top: 1px solid #f0f0f5;
      }
      .row:first-child {
        border-top: 0;
      }
      .row:hover {
        background: #fafafa;
      }
      .row__title {
        font-weight: 900;
      }
      .row__meta {
        margin-top: 0.25rem;
        font-size: 0.92rem;
      }
      .muted {
        color: #6b7280;
      }
    `
  ]
})
export class InterviewsPage {
  protected readonly items = [
    { slug: 'interview-1', title: 'साहित्यकार से बातचीत', excerpt: 'इंटरव्यू सेक्शन का डेमो कार्ड...' },
    { slug: 'interview-2', title: 'कलाकार के अनुभव', excerpt: 'आमने-सामने बातचीत...' }
  ];
}

