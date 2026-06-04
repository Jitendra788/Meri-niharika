import { inject, Injectable, signal } from '@angular/core';

import { API_BASE_URL } from './api.tokens';

@Injectable({ providedIn: 'root' })
export class ApiStatusService {
  private readonly apiBase = inject(API_BASE_URL);
  readonly backendMissing = signal(false);
  readonly checked = signal(false);

  async check(): Promise<void> {
    const base = this.apiBase?.trim();
    if (!base) {
      this.backendMissing.set(true);
      this.checked.set(true);
      return;
    }
    try {
      const res = await fetch(`${base}/api/health`, { cache: 'no-store' });
      this.backendMissing.set(!res.ok);
    } catch {
      this.backendMissing.set(true);
    }
    this.checked.set(true);
  }
}
