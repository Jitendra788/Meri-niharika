import { environment } from '../../environments/environment';

export async function loadApiBaseUrl(): Promise<string> {
  if (!environment.production) {
    return environment.apiBaseUrl;
  }

  try {
    const res = await fetch('/api/config', { cache: 'no-store' });
    if (res.ok) {
      const data = (await res.json()) as { apiBaseUrl?: string };
      const url = (data.apiBaseUrl || '').trim().replace(/\/$/, '');
      if (url) return '';
    }
  } catch {
    /* offline or not on Vercel */
  }

  return environment.apiBaseUrl;
}
