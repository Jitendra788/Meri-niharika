/** Proxies /api and /uploads to Render (BACKEND_URL on Vercel). */
export default async function middleware(request) {
  const backend = (process.env.BACKEND_URL || '').trim().replace(/\/$/, '');
  const url = new URL(request.url);

  if (url.pathname === '/api/config') {
    return;
  }

  if (!backend) {
    return;
  }

  const proxy =
    url.pathname.startsWith('/api/') || url.pathname.startsWith('/uploads/');
  if (!proxy) {
    return;
  }

  const dest = `${backend}${url.pathname}${url.search}`;
  const headers = new Headers(request.headers);
  headers.delete('host');

  const init = {
    method: request.method,
    headers,
    redirect: 'follow'
  };
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = request.body;
  }

  const res = await fetch(dest, init);
  const outHeaders = new Headers(res.headers);
  outHeaders.set('access-control-allow-origin', '*');
  return new Response(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers: outHeaders
  });
}

export const config = {
  matcher: ['/api/:path*', '/uploads/:path*']
};
