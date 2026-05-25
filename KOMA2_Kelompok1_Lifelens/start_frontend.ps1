$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $root "frontend")

$vite = Join-Path (Get-Location) "node_modules\.bin\vite.cmd"
if (-not (Test-Path -LiteralPath $vite)) {
  Write-Host "node_modules belum ada. Jalankan dulu: npm install"
  exit 1
}

& $vite --host 127.0.0.1
