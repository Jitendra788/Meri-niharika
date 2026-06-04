# Ishqora — Vercel पर deploy

Vercel पर **Angular site** चलती है। **FastAPI + uploads + PostgreSQL** Vercel पर ठीक से नहीं चलते (फाइलें गायब, PDF heavy) — API के लिए **Render** (free) use करें।

## Architecture

```
Visitor → ishqora.vercel.app (Angular)
              ↓ API calls (CORS)
         Render FastAPI (BACKEND_URL)
```

---

## Step 1 — GitHub

1. https://github.com → New repository
2. पूरा project push करें (**नहीं** डालें: `backend/.env`, `backend/.venv`, `node_modules`)

---

## Step 2 — Backend (Render Blueprint)

पूरी guide: **`DEPLOY-BACKEND.md`**

संक्षेप:

1. Neon.tech → free DB → connection string copy
2. Render → **New → Blueprint** → repo → `render.yaml` apply
3. Render env: `DATABASE_URL`, `ALLOWED_ORIGINS` (Vercel URL)
4. Test: `https://ishqora-api.onrender.com/api/health`
5. URL copy → Vercel `BACKEND_URL`

---

## Step 3 — Vercel (frontend)

1. https://vercel.com → **Add New → Project** → GitHub repo
2. **Root Directory:** `frontend/magazine-web`
3. **Framework Preset:** Angular (या Other)
4. **Build Command:** `npm run vercel-build` (Vercel इसे अपने आप पहचान लेता है)
5. **Output Directory:** `dist/magazine-web/browser`
6. **Environment Variables** (Vercel → Settings → Environment):

   | Name | Value |
   |------|--------|
   | `BACKEND_URL` | `https://ishqora-api.onrender.com` (बिना trailing `/`) |

7. **Deploy**

पहली बार `BACKEND_URL` खाली हो तो सिर्फ HTML दिखेगा; env add करके **Redeploy** करें।

---

## Step 4 — नया domain (Vercel)

1. Vercel project → **Settings → Domains**
2. `ishqora.com` add करें
3. Registrar (Cloudflare / Namecheap) में DNS records Vercel जैसा बताए वैसे लगाएँ
4. Render `ALLOWED_ORIGINS` में `https://ishqora.com,https://www.ishqora.com` जोड़ें

---

## Local test (Vercel जैसा)

```powershell
cd "e:\Meri niharika\frontend\magazine-web"
$env:BACKEND_URL="http://127.0.0.1:8000"
npm run vercel-build
npx serve dist/magazine-web/browser -l 5000
```

Backend अलग terminal में `uvicorn` चलाएँ।  
Note: `serve` proxy नहीं करता — असली proxy सिर्फ Vercel पर। Local के लिए `ng serve` + `proxy.conf.json` use करें।

---

## समस्याएँ

| समस्या | हल |
|--------|-----|
| साइट खाली / कोई article नहीं | Vercel में `BACKEND_URL` set + Redeploy |
| Admin login fail | Render `ALLOWED_ORIGINS` में Vercel URL |
| Images नहीं | `BACKEND_URL` सही; Render पर `uploads` मौजूद |
| API slow | Render free sleep — पहली visit 30s |

---

## क्या Vercel पर backend नहीं?

FastAPI + 85MB uploads + PyMuPDF Vercel serverless के लिए उपयुक्त नहीं। सब कुछ एक जगह चाहिए तो Oracle Cloud free VM।
