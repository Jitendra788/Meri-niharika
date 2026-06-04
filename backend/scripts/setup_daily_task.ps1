# Register Windows Task Scheduler — daily 6:00 AM IST (free, no cloud)
$ErrorActionPreference = "Stop"

$Backend = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Runner = Join-Path $Backend "scripts\run_daily_automation.ps1"
$TaskName = "MeriNiharikaDailyUpdate"

if (-not (Test-Path $Runner)) {
    Write-Error "Runner not found: $Runner"
}

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Runner`""

$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00"

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Meri Niharika: daily story part + RSS news (free)" `
    -Force | Out-Null

Write-Host "Task registered: $TaskName (daily 6:00 AM)"
Write-Host "Manual test: powershell -File `"$Runner`""
Write-Host "One-time setup: cd backend; `$env:PYTHONPATH='.'; python scripts/daily_automation.py --prepare"
