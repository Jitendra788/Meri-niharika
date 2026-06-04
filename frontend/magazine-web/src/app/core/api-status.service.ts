import { inject, Injectable, signal } from '@angular/core';

import { API_BASE_URL } from './api.tokens';

@Injectable({ providedIn: 'root' })
export class ApiStatusService {
  private readonly apiBase = inject(API_BASE_URL);
  readonly backendMissing = signal(false);
  readonly checked = signal(false);

  async check(): Promise<void> {
    try {
      const cfg = await fetch('/api/config', { cache: 'no-store' });
      if (cfg.ok) {
        const j = (await cfg.json()) as { apiBaseUrl?: string };
        if (!(j.apiBaseUrl || '').trim()) {
          this.backendMissing.set(true);
          this.checked.set(true);
          return;
        }
      }
    } catch {
      /* not on Vercel */
    }

    const healthUrl = this.apiBase?.trim()
      ? `${this.apiBase.replace(/\/$/, '')}/api/health`
      : '/api/health';

    try {
      const res = await fetch(healthUrl, { cache: 'no-store' });
      this.backendMissing.set(!res.ok);
    } catch {
      this.backendMissing.set(true);
    }
    this.checked.set(true);
  }
}
