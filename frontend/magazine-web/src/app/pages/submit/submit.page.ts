import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-submit-page',
  imports: [PageShellComponent, RouterLink],
  template: `
    <app-page-shell title="रचना भेजें" subtitle="Online Submission Form (demo)">
      <section class="card">
        <div class="grid">
          <label class="field">
            <span class="field__label">नाम</span>
            <input class="input" placeholder="Your name" />
          </label>
          <label class="field">
            <span class="field__label">ईमेल</span>
            <input class="input" placeholder="Email" />
          </label>
          <label class="field">
            <span class="field__label">मोबाइल</span>
            <input class="input" placeholder="Phone" />
          </label>
          <label class="field">
            <span class="field__label">श्रेणी</span>
            <select class="input">
              <option>कविता</option>
              <option>कहानी</option>
              <option>लेख</option>
              <option>बाल साहित्य</option>
            </select>
          </label>
        </div>

        <label class="field" style="margin-top: 0.75rem">
          <span class="field__label">शीर्षक</span>
          <input class="input" placeholder="Title" />
        </label>

        <label class="field" style="margin-top: 0.75rem">
          <span class="field__label">रचना</span>
          <textarea class="input" rows="9" placeholder="Apni रचना yahan paste karein..."></textarea>
        </label>

        <button class="btn" type="button" disabled>Submit (demo)</button>

        <p class="muted note">
          Open Mic ke liye alag form: <a class="link" routerLink="/open-mic">Open Mic Registration</a>
        </p>
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
      .grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
      }
      .field {
        display: grid;
        gap: 0.35rem;
      }
      .field__label {
        font-weight: 900;
        font-size: 0.9rem;
      }
      .input {
        border: 1px solid #e8e8ee;
        border-radius: 14px;
        padding: 0.7rem 0.9rem;
        font: inherit;
        background: #fff;
      }
      .btn {
        margin-top: 0.9rem;
        border: 1px solid #2b3a95;
        background: #2b3a95;
        color: #fff;
        border-radius: 14px;
        padding: 0.75rem 0.95rem;
        font-weight: 900;
        width: 100%;
      }
      .note {
        margin-top: 0.75rem;
      }
      .link {
        color: #2b3a95;
        font-weight: 900;
        text-decoration: none;
      }
      .link:hover {
        text-decoration: underline;
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
export class SubmitPage {}
