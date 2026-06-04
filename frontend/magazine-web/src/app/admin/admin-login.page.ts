import { NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { API_BASE_URL } from '../core/api.tokens';
import { AdminSession } from './admin.session';

@Component({
  standalone: true,
  selector: 'app-admin-login-page',
  imports: [NgIf, FormsModule, RouterLink],
  template: `
    <section class="wrap">
      <div class="authCard">
        <div class="body">
          <div class="logoRow">
            <img class="logo" src="/ishqora-logo.png" alt="Ishqora" />
          </div>
          <h1 class="title">Admin लॉगिन</h1>
          <p class="muted">उपयोगकर्ता नाम और पासवर्ड से प्रवेश करें</p>

          <label class="field">
            <span class="field__label">उपयोगकर्ता नाम</span>
            <input class="input" [(ngModel)]="username" placeholder="admin" />
          </label>

          <label class="field">
            <span class="field__label">पासवर्ड</span>
            <input class="input" type="password" [(ngModel)]="password" placeholder="••••••••" />
          </label>

          <p class="err" *ngIf="error">{{ error }}</p>

          <button class="btn" type="button" (click)="doLogin()">लॉगिन</button>

          <a class="back" routerLink="/">← वेबसाइट पर वापस</a>
        </div>
      </div>
    </section>
  `,
  styles: [
    `
      .wrap {
        min-height: calc(100dvh - 120px);
        display: grid;
        place-items: center;
        padding: 1rem 0.75rem 2rem;
        padding-bottom: max(2rem, env(safe-area-inset-bottom));
      }

      .authCard {
        width: min(520px, 100%);
        border-radius: 18px;
        border: 1px solid var(--border);
        background: var(--panel);
        overflow: hidden;
        box-shadow: var(--shadow);
      }

      .body {
        padding: 1.25rem;
      }

      .logoRow {
        display: flex;
        justify-content: center;
        margin-bottom: 0.75rem;
      }

      .logo {
        width: 220px;
        max-width: 90%;
        height: auto;
        max-height: 72px;
        object-fit: contain;
        display: block;
      }

      .title {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        text-align: center;
      }

      .field {
        margin-top: 0.75rem;
        display: grid;
        gap: 0.35rem;
      }
      .field__label {
        font-weight: 900;
        font-size: 0.95rem;
      }
      .input {
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.75rem 0.9rem;
        font: inherit;
        background: #fff;
      }

      .btn {
        width: 100%;
        margin-top: 1rem;
        border: 1px solid var(--ink);
        background: var(--ink);
        color: #fff;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        min-height: 44px;
        font-weight: 900;
        cursor: pointer;
      }

      @media (max-width: 480px) {
        .title {
          font-size: 1.25rem;
        }
        .body {
          padding: 1rem;
        }
      }

      .btn:active {
        transform: translateY(1px);
      }

      .muted {
        color: var(--muted);
      }

      .err {
        margin: 0.75rem 0 0 0;
        color: #b91c1c;
        font-weight: 900;
      }

      .back {
        display: inline-block;
        margin-top: 0.9rem;
        color: var(--muted);
        text-decoration: none;
        font-weight: 900;
      }

      .back:hover {
        text-decoration: underline;
      }
    `
  ]
})
export class AdminLoginPage {
  private readonly session = inject(AdminSession);
  private readonly router = inject(Router);
  private readonly apiBase = inject(API_BASE_URL);

  username = '';
  password = '';
  rememberMe = true;
  error = '';

  async doLogin() {
    this.error = '';
    if (!this.username.trim() || !this.password.trim()) return;
    try {
      const res = await fetch(`${this.apiBase}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: this.username.trim(), password: this.password })
      });
      if (!res.ok) {
        this.error = 'गलत उपयोगकर्ता नाम या पासवर्ड';
        return;
      }
      const data = (await res.json()) as { access_token: string };
      this.session.loginWithToken(data.access_token);
      void this.router.navigateByUrl('/admin/dashboard');
    } catch {
      this.error = 'सर्वर से कनेक्ट नहीं — पहले backend चालू करें (पोर्ट 8000)।';
    }
  }
}
