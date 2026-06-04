# localhost ठीक है — Vercel पर वही page कैसे लाएँ

## क्यों अंतर है?

| | localhost:4200 | meri-niharika.vercel.app |
|--|----------------|---------------------------|
| Website (Angular) | ✅ `npm start` | ✅ Vercel |
| API + images | ✅ `uvicorn` port 8000 | ❌ **अभी नहीं** |
| `/api/config` | — | `{"apiBaseUrl":""}` = **BACKEND_URL missing** |

Screenshot जैसा page = **दोनों** चलने चाहिए।

---

## 10 मिनट — पूरा fix

### 1) Neon (free database) — 2 min

1. https://console.neon.tech → Sign up
2. **New Project** → copy **Connection string** (Pooled)
   - जैसे: `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`

### 2) Render (backend) — 5 min

1. https://dashboard.render.com
2. **New +** → **Blueprint**
3. GitHub repo: **Jitendra788/Meri-niharika**
4. **Apply**
5. Service **ishqora-api** → **Environment**:
   - `DATABASE_URL` = Neon वाला string paste
   - `ALLOWED_ORIGINS` = `https://meri-niharika.vercel.app,http://localhost:4200`
6. **Save** → wait until **Live** (हरा)
7. ऊपर URL copy करें, जैसे: `https://ishqora-api.onrender.com`

**Test (browser):**

```
https://YOUR-RENDER-URL.onrender.com/api/health
```

`"status":"ok"` आना चाहिए।

```
https://YOUR-RENDER-URL.onrender.com/api/articles?limit=2
```

JSON articles आने चाहिए।

### 3) Vercel (connect) — 2 min

1. https://vercel.com → project **meri-niharika**
2. **Settings** → **Environment Variables**
3. **Add**:

| Key | Value |
|-----|--------|
| `BACKEND_URL` | `https://ishqora-api.onrender.com` |

(अपना **Render dashboard** वाला URL — ऊपर copy किया हुआ)

4. Environments: **Production** ✓
5. **Save**
6. **Deployments** → latest → **⋯** → **Redeploy**

### 4) Verify

| URL | सही हो तो |
|-----|-----------|
| https://meri-niharika.vercel.app/api/config | `"apiBaseUrl":"https://...onrender.com"` |
| https://meri-niharika.vercel.app/api/health | `"status":"ok"` |
| https://meri-niharika.vercel.app/ | पीला banner **नहीं**, खबरें + slider images |

---

## अभी भी नहीं?

- Render **sleep** (free): पहली visit 30–60 sec — दोबारा refresh
- `BACKEND_URL` typo / extra `/` अंत में
- Redeploy **नहीं** किया env के बाद
- Render deploy **failed** — Render → Logs देखें

Render URL मिल जाए तो WhatsApp/message में भेजें — exact `BACKEND_URL` confirm कर देंगे।
