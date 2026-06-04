import { inject, Injectable, signal } from '@angular/core';

import { StaticDataService } from './static-data.service';
import { API_BASE_URL } from './api.tokens';

@Injectable({ providedIn: 'root' })
export class ApiStatusService {
  private readonly apiBase = inject(API_BASE_URL);
  private readonly staticData = inject(StaticDataService);
  readonly backendMissing = signal(false);
  readonly usingStaticData = signal(false);
  readonly checked = signal(false);

  async check(): Promise<void> {
    let hasBackendEnv = false;
    try {
      const cfg = await fetch('/api/config', { cache: 'no-store' });
      if (cfg.ok) {
        const j = (await cfg.json()) as { apiBaseUrl?: string };
        hasBackendEnv = !!(j.apiBaseUrl || '').trim();
      }
    } catch {
      /* local */
    }

    const healthUrl = this.apiBase?.trim()
      ? `${this.apiBase.replace(/\/$/, '')}/api/health`
      : '/api/health';

    let apiOk = false;
    try {
      const res = await fetch(healthUrl, { cache: 'no-store' });
      apiOk = res.ok;
    } catch {
      apiOk = false;
    }

    if (apiOk) {
      this.backendMissing.set(false);
      this.usingStaticData.set(false);
      this.checked.set(true);
      return;
    }

    let staticOk = false;
    try {
      staticOk = await new Promise<boolean>((resolve) => {
        this.staticData.hasStaticArticles().subscribe((v) => resolve(v));
      });
    } catch {
      staticOk = false;
    }

    this.usingStaticData.set(staticOk);
    this.backendMissing.set(!staticOk);
    this.checked.set(true);

    if (!apiOk && staticOk && !hasBackendEnv) {
      /* bundled data — site works; optional Render later */
    }
  }
}
