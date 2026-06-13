# Live site — GitHub Pages (free, automatic)

Render/Vercel ke bina site live ho sakti hai — sirf GitHub se.

## Live URL

**https://jitendra788.github.io/Meri-niharika/**

Har `main` push par site rebuild hoti hai. Roz 6 AM IST par RSS news auto-import hoti hai.

## Ek baar enable karein (30 sec) — **zaroori**

1. Is link par jayein: **https://github.com/Jitendra788/Meri-niharika/settings/pages**
2. **Build and deployment** → Source: **GitHub Actions**
3. **Actions** tab → **Deploy GitHub Pages** → green ✓ hone ka wait karein
4. Site: **https://jitendra788.github.io/Meri-niharika/**

## Daily update kaise chalta hai

| Jagah | Kya hota hai |
|-------|----------------|
| **GitHub Actions** (roz 6 AM IST) | RSS import → commit → **site rebuild + deploy** |
| **Aapka PC** (Task Scheduler 6 AM) | Same + `git push` (PC on hona chahiye) |

**Pehli baar (zaroori):** https://github.com/Jitendra788/Meri-niharika/settings/pages → Source: **GitHub Actions**

Manual test abhi: Actions → **Daily update and deploy** → **Run workflow**

## Story भाग (drip) alag se

Saare love-story भाग ab published hain. Roz naya भाग ke liye ek baar:

```powershell
cd backend
$env:PYTHONPATH='.'
python scripts/daily_automation.py --prepare
git add backend/uploads/articles_manifest.json
git commit -m "Enable love-story daily drip"
git push
```

## Custom domain (ishqora.com)

1. GitHub → Settings → Pages → **Custom domain** → `ishqora.com`
2. Domain registrar par DNS records GitHub jaisa bataye
3. Optional: Render backend baad mein add karein admin/PDF ke liye

## Render/Vercel (optional, baad mein)

PDF archive + admin upload ke liye `DEPLOY-BACKEND.md` aur `DEPLOY-VERCEL.md` dekhein.
