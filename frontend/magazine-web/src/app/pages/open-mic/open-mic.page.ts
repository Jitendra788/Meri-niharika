import { Component } from '@angular/core';
import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-open-mic-page',
  imports: [PageShellComponent],
  template: `
    <app-page-shell title="Open Mic Registration" subtitle="कार्यक्रम के लिए Registration (demo)">
      <section class="card">
        <p class="muted">Is form ko backend se connect karke submissions store kiye jayenge.</p>

        <div class="grid">
          <label class="field">
            <span class="field__label">नाम</span>
            <input class="input" placeholder="Your name" />
          </label>
          <label class="field">
            <span class="field__label">मोबाइल</span>
            <input class="input" placeholder="Phone" />
          </label>
          <label class="field">
            <span class="field__label">ईमेल</span>
            <input class="input" placeholder="Email" />
          </label>
          <label class="field">
            <span class="field__label">शहर</span>
            <input class="input" placeholder="City" />
          </label>
        </div>

        <label class="field" style="margin-top: 0.75rem">
          <span class="field__label">प्रस्तुति (कविता/कहानी)</span>
          <textarea class="input" rows="5" placeholder="Apni प्रस्तुति ka short text..."></textarea>
        </label>

        <button class="btn" type="button" disabled>Register (demo)</button>
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
        margin-top: 0.75rem;
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
export class OpenMicPage {}
