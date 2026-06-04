# Meri Niharika — free daily automation (Windows)
$ErrorActionPreference = "Stop"
$Backend = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -LiteralPath $Backend
$env:PYTHONPATH = "."
& ".\.venv\Scripts\python.exe" ".\scripts\daily_automation.py"
exit $LASTEXITCODE
