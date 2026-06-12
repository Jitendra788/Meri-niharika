# One-shot: push code + print live setup checklist (Render + Vercel + cron)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Push-Location $Root
try {
    Write-Host "=== Git push ===" -ForegroundColor Cyan
    git add -A
    $status = git status --porcelain
    if ($status) {
        git commit -m "Enable live deploy: cron API, categories fallback, RSS sync, Render/Vercel config"
        git push origin main
        Write-Host "Pushed to GitHub." -ForegroundColor Green
    } else {
        Write-Host "Nothing to commit — already up to date." -ForegroundColor Yellow
        git push origin main
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== Render (backend) ===" -ForegroundColor Cyan
Write-Host "1. https://dashboard.render.com -> Blueprint -> Jitendra788/Meri-niharika"
Write-Host "2. Service ishqora-api -> Environment:"
Write-Host "   DATABASE_URL = Neon connection string - optional, files work without DB"
Write-Host "   ALLOWED_ORIGINS = already in render.yaml - Vercel + ishqora.com"
Write-Host "3. Copy service URL e.g. https://ishqora-api.onrender.com"
Write-Host "4. Test: https://YOUR-URL.onrender.com/api/health"

Write-Host ""
Write-Host "=== Vercel (frontend) ===" -ForegroundColor Cyan
Write-Host "1. https://vercel.com -> Import GitHub repo (root = repo root, uses vercel.json)"
Write-Host "2. Environment -> BACKEND_URL = your Render URL (no trailing slash)"
Write-Host "3. Redeploy Production"
Write-Host "4. Test: https://YOUR-VERCEL-URL/api/health"

Write-Host ""
Write-Host "=== Daily cron (free) ===" -ForegroundColor Cyan
Write-Host "cron-job.org -> POST https://YOUR-RENDER-URL.onrender.com/api/cron/daily"
Write-Host "Header: X-Cron-Secret = Render env CRON_SECRET"
Write-Host "Schedule: daily 6:00 AM IST"
Write-Host ""
Write-Host "OR GitHub -> Settings -> Secrets: RENDER_API_URL, CRON_SECRET - workflow runs daily"
