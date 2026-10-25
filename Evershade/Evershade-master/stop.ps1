# Unified Workflow — Stop Script (Windows PowerShell)

[CmdletBinding()]
param(
    [ValidateSet("minimal", "standard", "full")]
    [string]$Profile = "full"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host "Stopping all services (profile: $Profile)..." -ForegroundColor Cyan

docker compose --profile $Profile down

Write-Host "Services stopped." -ForegroundColor Green
Write-Host ""
Write-Host "To remove volumes and data: docker compose --profile $Profile down -v" -ForegroundColor Gray
Write-Host "To start again: .\start.ps1 -Profile $Profile" -ForegroundColor Gray
