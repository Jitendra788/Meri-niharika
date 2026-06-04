import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { map } from 'rxjs';

import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-special-page',
  imports: [AsyncPipe, RouterLink, PageShellComponent],
  template: `
    <app-page-shell [title]="(slug$ | async) ?? 'विशेषांक'" subtitle="Special issue landing page (demo)">
      <section class="card">
        <p class="muted">
          Is special issue ke articles yahan list honge. Abhi backend wiring pending hai.
        </p>
        <a class="link" routerLink="/submit">अपनी रचना भेजें →</a>
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
      }
      .link {
        display: inline-block;
        margin-top: 0.75rem;
        color: #2b3a95;
        text-decoration: none;
        font-weight: 800;
      }
      .link:hover {
        text-decoration: underline;
      }
      .muted {
        color: #6b7280;
      }
    `
  ]
})
export class SpecialPage {
  private readonly route = inject(ActivatedRoute);
  protected readonly slug$ = this.route.paramMap.pipe(map((p) => p.get('slug') ?? ''));
}
