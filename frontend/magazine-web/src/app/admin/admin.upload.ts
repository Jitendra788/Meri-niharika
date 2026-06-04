export type ArchivePublishBody = {
  title: string;
  language: string;
  pdf_url: string;
  cover_url?: string;
  category_slug?: string;
};

export type ArchiveItemResponse = {
  id: string;
  slug?: string;
  title: string;
  excerpt?: string;
  category_slug?: string;
  language?: string;
  pdf_url: string;
  cover_url?: string;
  published_at?: string;
  created_at: string;
};

/** XHR upload — reliable progress + timeout (HttpClient often stuck at 0%). */
export function uploadPdfXhr(  apiBase: string,
  file: File,
  token: string,
  onProgress: (pct: number, loaded: number) => void,
  timeoutMs = 180_000
): Promise<{ pdf_url: string; cover_url?: string; original_bytes?: number; compressed_bytes?: number }> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const fd = new FormData();
    fd.append('file', file);

    const timer = window.setTimeout(() => {
      xhr.abort();
      reject(
        new Error(
          'Upload timeout — backend slow/stuck. Backend restart karein: uvicorn app.main:app --port 8000'
        )
      );
    }, timeoutMs);

    xhr.upload.addEventListener('progress', (e) => {
      const total = e.lengthComputable ? e.total : file.size;
      if (total > 0) {
        onProgress(Math.min(99, Math.round((100 * e.loaded) / total)), e.loaded);
      } else if (e.loaded > 0) {
        onProgress(Math.min(99, Math.round((100 * e.loaded) / file.size)), e.loaded);
      }
    });

    xhr.addEventListener('load', () => {
      window.clearTimeout(timer);
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(
            JSON.parse(xhr.responseText) as {
              pdf_url: string;
              cover_url?: string;
              original_bytes?: number;
              compressed_bytes?: number;
            }
          );
        } catch {
          reject(new Error('Invalid server response'));
        }
        return;
      }
      reject(new Error(`Upload failed (${xhr.status}): ${xhr.responseText || xhr.statusText}`));
    });

    xhr.addEventListener('error', () => {
      window.clearTimeout(timer);
      reject(
        new Error(
          'Network error — kya backend chal raha hai? http://127.0.0.1:8000/api/health browser me kholo.'
        )
      );
    });

    xhr.addEventListener('abort', () => {
      window.clearTimeout(timer);
      reject(new Error('Upload cancel / timeout'));
    });

    xhr.open('POST', `${apiBase.replace(/\/$/, '')}/api/admin/upload/pdf`);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    onProgress(0, 0);
    xhr.send(fd);
  });
}

export async function publishArchiveFetch(
  apiBase: string,
  body: ArchivePublishBody,
  token: string,
  opts?: { timeoutMs?: number; signal?: AbortSignal }
): Promise<ArchiveItemResponse> {
  const base = apiBase.replace(/\/$/, '');
  const timeoutMs = opts?.timeoutMs ?? 8_000;
  const timeoutCtrl = new AbortController();
  const timer = window.setTimeout(() => timeoutCtrl.abort(), timeoutMs);

  const onParentAbort = () => timeoutCtrl.abort();
  opts?.signal?.addEventListener('abort', onParentAbort, { once: true });

  try {
    const res = await fetch(`${base}/api/admin/archive`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body),
      signal: timeoutCtrl.signal
    });
    const text = await res.text();
    if (!res.ok) {
      throw new Error(`Publish failed (${res.status}): ${text || res.statusText}`);
    }
    return JSON.parse(text) as ArchiveItemResponse;
  } catch (e: unknown) {
    if (e instanceof DOMException && e.name === 'AbortError') {
      throw new Error('Publish timeout — backend restart karein (port 8000), phir dubara try karein.');
    }
    throw e;
  } finally {
    window.clearTimeout(timer);
    opts?.signal?.removeEventListener('abort', onParentAbort);
  }
}

export function uploadCoverXhr(
  apiBase: string,
  file: File,
  pdfUrl: string,
  token: string,
  timeoutMs = 30_000
): Promise<{ cover_url: string }> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const fd = new FormData();
    fd.append('file', file);
    fd.append('pdf_url', pdfUrl);

    const timer = window.setTimeout(() => {
      xhr.abort();
      reject(new Error('Cover upload timeout'));
    }, timeoutMs);

    xhr.addEventListener('load', () => {
      window.clearTimeout(timer);
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText) as { cover_url: string });
        } catch {
          reject(new Error('Invalid server response'));
        }
        return;
      }
      reject(new Error(`Cover upload failed (${xhr.status}): ${xhr.responseText || xhr.statusText}`));
    });

    xhr.addEventListener('error', () => {
      window.clearTimeout(timer);
      reject(new Error('Cover upload network error'));
    });

    xhr.addEventListener('abort', () => {
      window.clearTimeout(timer);
      reject(new Error('Cover upload cancel / timeout'));
    });

    xhr.open('POST', `${apiBase.replace(/\/$/, '')}/api/admin/upload/cover`);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(fd);
  });
}

export async function fetchArchiveList(
  apiBase: string,
  timeoutMs = 10_000
): Promise<ArchiveItemResponse[]> {
  const base = apiBase.replace(/\/$/, '');
  const ctrl = new AbortController();
  const t = window.setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${base}/api/archive`, { signal: ctrl.signal });
    if (!res.ok) return [];
    return (await res.json()) as ArchiveItemResponse[];
  } catch {
    return [];
  } finally {
    window.clearTimeout(t);
  }
}

export async function fetchArchiveBySlug(
  apiBase: string,
  slug: string,
  timeoutMs = 8_000
): Promise<ArchiveItemResponse | null> {
  const base = apiBase.replace(/\/$/, '');
  const ctrl = new AbortController();
  const t = window.setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${base}/api/archive/${encodeURIComponent(slug)}`, {
      signal: ctrl.signal
    });
    if (!res.ok) return null;
    return (await res.json()) as ArchiveItemResponse;
  } catch {
    return null;
  } finally {
    window.clearTimeout(t);
  }
}

/** Match backend slug_from_pdf_url for fallback when API has no slug field. */
export function slugFromPdfUrl(pdfUrl: string): string {
  const name = pdfUrl.split('/').pop() || '';
  const stem = name.replace(/\.pdf$/i, '');
  const m = stem.match(/^(.+)-(\d{8,})$/);
  const base = (m ? m[1] : stem).toLowerCase();
  return base.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'issue';
}

export async function pingBackend(apiBase: string, timeoutMs = 5000): Promise<boolean> {
  const ctrl = new AbortController();
  const t = window.setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${apiBase.replace(/\/$/, '')}/api/health`, { signal: ctrl.signal });
    return res.ok;
  } catch {
    return false;
  } finally {
    window.clearTimeout(t);
  }
}
