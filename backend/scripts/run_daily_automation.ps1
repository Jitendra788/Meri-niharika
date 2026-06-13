# Meri Niharika — daily automation (Windows) + push to GitHub for live site
$ErrorActionPreference = "Stop"
$Backend = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Root = Split-Path -Parent $Backend

Set-Location -LiteralPath $Backend
$env:PYTHONPATH = "."
& ".\.venv\Scripts\python.exe" ".\scripts\daily_automation.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Set-Location -LiteralPath $Root
git add backend/uploads/articles_manifest.json `
        backend/uploads/automation_state.json `
        backend/uploads/images/rss 2>$null

$staged = git diff --staged --name-only
if (-not $staged) {
    Write-Host "No new articles to push."
    exit 0
}

git commit -m "chore: daily RSS update [local automation]"
git push origin main
Write-Host "Pushed to GitHub — live site will rebuild via Actions."
