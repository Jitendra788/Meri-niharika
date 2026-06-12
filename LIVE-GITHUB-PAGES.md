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

## Kya automatic chalta hai

| Workflow | Kaam |
|----------|------|
| `deploy-github-pages.yml` | Har push par site build + deploy |
| `daily-cron.yml` | Roz subah RSS + story update → commit → redeploy |

## Custom domain (ishqora.com)

1. GitHub → Settings → Pages → **Custom domain** → `ishqora.com`
2. Domain registrar par DNS records GitHub jaisa bataye
3. Optional: Render backend baad mein add karein admin/PDF ke liye

## Render/Vercel (optional, baad mein)

PDF archive + admin upload ke liye `DEPLOY-BACKEND.md` aur `DEPLOY-VERCEL.md` dekhein.
