import { NgFor } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-creators-page',
  imports: [NgFor, PageShellComponent, RouterLink],
  template: `
    <app-page-shell title="हमारे बारे में" subtitle="Ishqora टीम">
      <section class="editorLead">
        <img class="editorLead__photo" src="/vijaya-dalmia.png" alt="विजया डालमिया" loading="lazy" />
        <div class="editorLead__body">
          <p class="editorLead__label">संपादक</p>
          <h2 class="editorLead__name">विजया डालमिया</h2>
          <p class="editorLead__city">हैदराबाद</p>
          <p class="editorLead__bio">
            Ishqora — हर नारी की कहानी, हर भावना की ज़ुबानी।
          </p>
          <a class="editorLead__link" routerLink="/editorial">संपादकीय पढ़ें →</a>
        </div>
      </section>

      <section class="cta">
        <a class="btn" routerLink="/submit">रचना भेजें</a>
      </section>
    </app-page-shell>
  `,
  styles: [
    `
      .editorLead {
        margin-top: 1rem;
        display: flex;
        gap: 1.5rem;
        align-items: center;
        border: 1px solid #e8e8ee;
        background: #fff;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
      }
      .editorLead__photo {
        width: 140px;
        height: 140px;
        object-fit: cover;
        object-position: center top;
        border-radius: 50%;
        border: 3px solid #f5c6e0;
        flex-shrink: 0;
      }
      .editorLead__label {
        margin: 0 0 0.25rem;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #9d0a5d;
      }
      .editorLead__name {
        margin: 0;
        font-size: 1.45rem;
        font-weight: 900;
        color: #222;
      }
      .editorLead__city {
        margin: 0.25rem 0 0.65rem;
        font-weight: 700;
        color: #666;
      }
      .editorLead__bio {
        margin: 0 0 0.75rem;
        line-height: 1.55;
        color: #444;
      }
      .editorLead__link {
        color: #9d0a5d;
        font-weight: 800;
        text-decoration: none;
      }
      .editorLead__link:hover {
        text-decoration: underline;
      }
      .cta {
        margin-top: 1.25rem;
      }
      .btn {
        display: inline-flex;
        padding: 0.65rem 0.9rem;
        border-radius: 8px;
        background: #9d0a5d;
        color: #fff;
        text-decoration: none;
        font-weight: 900;
      }
      @media (max-width: 640px) {
        .editorLead {
          flex-direction: column;
          text-align: center;
        }
      }
    `
  ]
})
export class CreatorsPage {}
