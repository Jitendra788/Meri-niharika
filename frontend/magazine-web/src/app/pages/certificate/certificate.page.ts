import { Component } from '@angular/core';
import { PageShellComponent } from '../_ui/page-shell';

@Component({
  standalone: true,
  selector: 'app-certificate-page',
  imports: [PageShellComponent],
  template: `
    <app-page-shell title="ई-सर्टिफिकेट Download" subtitle="प्रतियोगिता प्रतिभागियों हेतु (demo)">
      <section class="card">
        <p class="muted">
          Yahan participant ID / email dal ke certificate download hoga. Abhi backend integration pending hai.
        </p>
        <div class="row">
          <input class="input" placeholder="Participant ID / Email" disabled />
          <button class="btn" type="button" disabled>Download</button>
        </div>
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
      .row {
        margin-top: 0.75rem;
        display: flex;
        gap: 0.5rem;
      }
      .input {
        flex: 1;
        border: 1px solid #e8e8ee;
        border-radius: 14px;
        padding: 0.7rem 0.9rem;
      }
      .btn {
        border: 1px solid #2b3a95;
        background: #2b3a95;
        color: #fff;
        border-radius: 14px;
        padding: 0.7rem 0.9rem;
        font-weight: 900;
      }
      .muted {
        color: #6b7280;
      }
    `
  ]
})
export class CertificatePage {}
