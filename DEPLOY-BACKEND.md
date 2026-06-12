# Backend Render पर कैसे चलेगा

FastAPI server **24/7 नहीं** (free plan) — 15 मिनट बाद sleep; पहली request 30–60 सेकंड लग सकती है।

```
Browser (Vercel)  --HTTPS-->  Render (uvicorn + FastAPI)  --HTTPS-->  Neon (PostgreSQL)
                                    |
                              backend/uploads/  (images, PDF, JSON manifest)
```

---

## Step 1 — GitHub पर code

```powershell
cd "e:\Meri niharika"
git init
git add .
git commit -m "Ishqora site deploy"
git remote add origin https://github.com/AAPKA-USER/ishqora.git
git push -u origin main
```

**ज़रूरी:** `backend/uploads` folder commit में हो (≈85MB) — वरना images/stories नहीं दिखेंगी।

**मत डालें:** `backend/.env`, `backend/.venv`

---

## Step 2 — Neon (free PostgreSQL)

1. https://neon.tech → Sign up → **New Project**
2. Dashboard → **Connection string** → **Pooled** copy करें  
   Example: `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`
3. यही बाद में Render में `DATABASE_URL` के रूप में paste करेंगे  
   (app अपने आप `postgresql+asyncpg://` में बदल देता है)

---

## Step 3 — Render (Blueprint = एक क्लिक)

1. https://dashboard.render.com → **New +** → **Blueprint**
2. GitHub repo connect करें
3. `render.yaml` detect होगा → **Apply**
4. Deploy खत्म होने पर service URL मिलेगा, जैसे:  
   `https://ishqora-api.onrender.com`

### Dashboard में ये env खुद set करें

| Variable | Value |
|----------|--------|
| `DATABASE_URL` | Neon वाला connection string |
| `ALLOWED_ORIGINS` | `https://aapka-project.vercel.app,https://ishqora.com,http://localhost:4200` |
| `ADMIN_PASSWORD` | मजबूत password (Blueprint ने random दिया हो तो note कर लें) |

**Save** → **Manual Deploy** (Redeploy)

---

## Step 4 — Test API

Browser या PowerShell:

```powershell
curl https://ishqora-api.onrender.com/api/health
```

उम्मीद:

```json
{"status":"ok","database":"up"}
```

Articles:

```powershell
curl "https://ishqora-api.onrender.com/api/articles?limit=3"
```

---

## Step 5 — Vercel से जोड़ें

Vercel project → **Environment Variables**:

| Name | Value |
|------|--------|
| `BACKEND_URL` | `https://ishqora-api.onrender.com` |

→ **Redeploy** frontend

---

## Backend कैसे चलता है (technical)

| चीज़ | Detail |
|------|--------|
| Start | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Port | Render `$PORT` env देता है |
| Files | `backend/uploads` — articles JSON, images, PDF |
| DB | Startup पर tables बनते हैं; DB down हो तो JSON fallback |
| CORS | `ALLOWED_ORIGINS` — Vercel domain ज़रूरी |
| Admin | `POST /api/admin/login` — user/pass env से |

---

## Daily automation (live site पर खबरें + story भाग)

Windows Task सिर्फ **local PC** पर चलता है। Live (Render) पर **cron-job.org** (free) से trigger करें:

### 1) Render env

Dashboard → **ishqora-api** → **Environment** → `CRON_SECRET` copy करें (या नया set करें)।

### 2) cron-job.org (recommended)

1. https://cron-job.org → free account
2. **Create cronjob**
3. URL: `https://YOUR-RENDER-URL.onrender.com/api/cron/daily`
4. Schedule: **Daily 6:00 AM** (Asia/Kolkata)
5. Request method: **POST**
6. Headers: `X-Cron-Secret` = आपका `CRON_SECRET`
7. Save

Optional — पहली बार story drip चालू करने के लिए (भाग 2+ scheduled):

`POST .../api/cron/daily?prepare=true` (same header, एक बार)

### 3) Test (PowerShell)

```powershell
$secret = "YOUR_CRON_SECRET"
Invoke-RestMethod -Method Post -Uri "https://YOUR-RENDER-URL.onrender.com/api/cron/daily" `
  -Headers @{ "X-Cron-Secret" = $secret }
```

Status देखें:

```powershell
Invoke-RestMethod -Uri "https://YOUR-RENDER-URL.onrender.com/api/cron/status" `
  -Headers @{ "X-Cron-Secret" = $secret }
```

### 4) GitHub Actions (optional)

Repo → **Settings → Secrets**: `RENDER_API_URL`, `CRON_SECRET`  
Workflow: `.github/workflows/daily-cron.yml` (हर दिन 6:00 AM IST)

**ध्यान:** Vercel पर `BACKEND_URL` set होना चाहिए — तभी live site API से नई खबरें दिखेंगी।

---

## समस्याएँ

| समस्या | हल |
|--------|-----|
| `database: down` | `DATABASE_URL` सही? Neon project active? |
| CORS error browser में | `ALLOWED_ORIGINS` में exact Vercel URL |
| Images 404 | `uploads` GitHub पर push हुआ? |
| Build fail PyMuPDF | `render.yaml` में Python 3.12 |
| Slow first load | Render free sleep — normal |

---

## Local (वही code)

```powershell
cd "e:\Meri niharika\backend"
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`http://127.0.0.1:8000/api/health`
