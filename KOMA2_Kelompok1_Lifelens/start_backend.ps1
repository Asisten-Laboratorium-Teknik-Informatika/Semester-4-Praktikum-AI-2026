param(
  [switch]$WarmupTts
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not $WarmupTts) {
  $env:LIFELENS_TTS_WARMUP = "0"
}

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
