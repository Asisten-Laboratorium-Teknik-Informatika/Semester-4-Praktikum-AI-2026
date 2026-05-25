param(
  [switch]$WarmupTts
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not $WarmupTts) {
  $env:LIFELENS_TTS_WARMUP = "0"
}



if (-not $env:LIFELENS_DISABLE_SHAP) {
  $env:LIFELENS_DISABLE_SHAP = "1"
}

if (-not $env:LIFELENS_DISABLE_HF_NLP) {
  $env:LIFELENS_DISABLE_HF_NLP = "1"
}

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
